#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This file contains pluggable module for Hawat web interface containing features
related to `IDEA <https://idea.cesnet.cz/en/index>`__ events, database searching,
viewing event details and producing event dashboards.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional

import flask
import flask_login
import markupsafe
import pytz
from flask_babel import lazy_gettext

import hawat.acl
import hawat.const
import hawat.events
import hawat.forms
import hawat.menu
import mentat.services.eventstorage
import mentat.stats.idea
from hawat import charts
from hawat.base import CsagIdentifier, HawatBlueprint, PsycopgMixin
from hawat.blueprints.event_classes import get_event_class
from hawat.blueprints.events.forms import EventDashboardForm, SimpleEventSearchForm
from hawat.events import get_after_cleanup
from hawat.utils import URLParamsBuilder
from hawat.view import BaseSearchView, BaseView, ItemShowView, SimpleView
from hawat.view.mixin import AJAXMixin, HTMLMixin, SQLAlchemyMixin
from mentat.const import tr_
from mentat.datatype.sqldb import EventStatisticsModel

if TYPE_CHECKING:
    from mentat.idea.internal import Idea

BLUEPRINT_NAME = "events"
"""Name of the blueprint as module global constant."""

_EVENTS_SECTION = charts.ChartSection.new_common(
    mentat.stats.idea.ST_SKEY_CNT_EVENTS,
    lazy_gettext("events"),
    lazy_gettext("Total events processed"),
    lazy_gettext("This view shows total numbers of IDEA events related to given network."),
    charts.DataComplexity.NONE,
    lazy_gettext("Total events"),
)
_AGG_SECTIONS = [
    charts.COMMON_CHART_SECTIONS_MAP[key]
    for key in (
        mentat.stats.idea.ST_SKEY_ANALYZERS,
        mentat.stats.idea.ST_SKEY_ASNS,
        mentat.stats.idea.ST_SKEY_CATEGORIES,
        mentat.stats.idea.ST_SKEY_CATEGSETS,
        mentat.stats.idea.ST_SKEY_COUNTRIES,
        mentat.stats.idea.ST_SKEY_DETECTORS,
        mentat.stats.idea.ST_SKEY_DETECTORSWS,
        mentat.stats.idea.ST_SKEY_SOURCES,
        mentat.stats.idea.ST_SKEY_TARGETS,
        mentat.stats.idea.ST_SKEY_CLASSES,
        mentat.stats.idea.ST_SKEY_SEVERITIES,
        mentat.stats.idea.ST_SKEY_TLPS,
    )
]

# only include abuses in overall and internal statistics.
DASHBOARD_CHART_SECTIONS = [
    _EVENTS_SECTION,
    charts.COMMON_CHART_SECTIONS_MAP[mentat.stats.idea.ST_SKEY_ABUSES],
] + _AGG_SECTIONS
DASHBOARD_CHART_SECTIONS_EXTERNAL = _AGG_SECTIONS


def _get_search_form(request_args=None):
    choices = hawat.events.get_event_form_choices()

    form = SimpleEventSearchForm(
        request_args,
        meta={"csrf": False},
        choices_source_types=choices["source_types"],
        choices_target_types=choices["target_types"],
        choices_host_types=choices["host_types"],
        choices_detectors=choices["detectors"],
        choices_detector_types=choices["detector_types"],
        choices_categories=choices["categories"],
        choices_severities=choices["severities"],
        choices_target_severities=choices["target_severities"],
        choices_classes=choices["classes"],
        choices_target_classes=choices["target_classes"],
        choices_protocols=choices["protocols"],
        choices_inspection_errs=choices["inspection_errs"],
        choices_TLPs=choices["TLPs"],
    )

    # In case no time bounds were set adjust them manually.
    if request_args and not (
        "dt_from" in request_args or "dt_to" in request_args or "st_from" in request_args or "st_to" in request_args
    ):
        form.dt_from.process_data(hawat.forms.default_dt_with_delta())
        form.dt_to.process_data(hawat.forms.default_dt())

    return form


def _group_to_group_name(group):
    if isinstance(group, str):
        return group
    return group.name


def _get_report_search_context_from_form_data(
    form_data: dict[str, Any],
) -> dict[str, Any]:
    any_empty_values = {"__ANY__", "__EMPTY__"}  # not supported by report search

    res = {
        "dt_from": form_data.get("st_from") or form_data.get("dt_from"),
        "dt_to": form_data.get("st_to") or form_data.get("dt_to"),
    }

    for source, not_source, target, not_target in (
        ("groups", "not_groups", "target_groups", "not_target_groups"),
        ("severities", "not_severities", "target_severities", "not_target_severities"),
        ("categories", "not_categories", None, None),
        ("classes", "not_classes", "target_classes", "not_target_classes"),
        ("detectors", "not_detectors", None, None),
    ):
        if source in form_data or target in form_data:
            if not form_data.get(not_source) and not (not_target and form_data.get(not_target)):
                source_values = set(form_data.get(source, []) if source else [])
                target_values = set(form_data.get(target, []) if target else [])
                res[source] = list((source_values | target_values) - any_empty_values)
            elif source in form_data:
                res[source] = []

    if "source_addrs" in form_data:
        res["source_ips"] = form_data["source_addrs"]
    elif "target_addrs" in form_data:
        res["target_ips"] = form_data["target_addrs"]
    elif "host_addrs" in form_data:
        pass  # not supported

    return form_data | res


def _add_not_none(res: dict[str, Any], key: str, *values: Any, as_list: bool = False) -> None:
    assert as_list or len(values) <= 1

    for value in set(values):
        if value is None:
            continue
        if as_list:
            res.setdefault(key, []).append(value)
        else:
            res[key] = value


def _get_report_search_context_from_idea(
    event: "Idea", additional_context: Optional[Literal["source", "target"]]
) -> dict[str, Any]:
    res = {}
    dt_from = event.get_jpath_value("_Mentat.StorageTime")
    if dt_from:
        res["dt_from"] = dt_from.replace(microsecond=0, tzinfo=pytz.utc).isoformat()

    _add_not_none(res, "categories", event.get_jpath_value("Category"), as_list=True)
    _add_not_none(res, "detectors", *event.get_jpath_values("Node[*].Name"), as_list=True)

    if additional_context == "source":
        _add_not_none(res, "groups", event.get_jpath_value("_Mentat.ResolvedAbuses"), as_list=True)
        _add_not_none(
            res,
            "severities",
            event.get_jpath_value("_Mentat.EventSeverity"),
            as_list=True,
        )
        _add_not_none(
            res,
            "source_ips",
            *event.get_jpath_values("Source[*].IP4"),
            *event.get_jpath_values("Source[*].IP6"),
            as_list=True,
        )
        _add_not_none(res, "classes", event.get_jpath_value("_Mentat.EventClass"), as_list=True)

    elif additional_context == "target":
        _add_not_none(res, "groups", event.get_jpath_value("_Mentat.TargetAbuses"), as_list=True)
        _add_not_none(
            res,
            "severities",
            event.get_jpath_value("_Mentat.TargetSeverity"),
            as_list=True,
        )
        _add_not_none(
            res,
            "target_ips",
            *event.get_jpath_values("Target[*].IP4"),
            *event.get_jpath_values("Target[*].IP6"),
            as_list=True,
        )
        _add_not_none(res, "classes", event.get_jpath_value("_Mentat.TargetClass"), as_list=True)
    else:
        _add_not_none(
            res,
            "groups",
            event.get_jpath_value("_Mentat.ResolvedAbuses"),
            event.get_jpath_value("_Mentat.TargetAbuses"),
            as_list=True,
        )

        _add_not_none(
            res,
            "severities",
            event.get_jpath_value("_Mentat.EventSeverity"),
            event.get_jpath_value("_Mentat.TargetSeverity"),
            as_list=True,
        )
        _add_not_none(
            res,
            "classes",
            event.get_jpath_value("_Mentat.EventClass"),
            event.get_jpath_value("_Mentat.TargetClass"),
            as_list=True,
        )

    return res


def _get_event_search_context_from_idea(event: "Idea") -> dict[str, Any]:
    res = {}

    dt: datetime.datetime = event.get_jpath_value("DetectTime")
    if dt:
        res["dt_from"] = dt.replace(microsecond=0, tzinfo=pytz.utc).isoformat()
        res["dt_to"] = (dt.replace(microsecond=0, tzinfo=pytz.utc) + datetime.timedelta(seconds=1)).isoformat()

    _add_not_none(
        res,
        "source_ips",
        *event.get_jpath_values("Source[*].IP4"),
        *event.get_jpath_values("Source[*].IP6"),
        as_list=True,
    )
    _add_not_none(
        res,
        "target_ips",
        *event.get_jpath_values("Target[*].IP4"),
        *event.get_jpath_values("Target[*].IP6"),
        as_list=True,
    )

    _add_not_none(res, "source_ports", *event.get_jpath_values("Source[*].Port"), as_list=True)
    _add_not_none(res, "target_ports", *event.get_jpath_values("Target[*].Port"), as_list=True)

    _add_not_none(res, "source_types", *event.get_jpath_values("Source[*].Type"), as_list=True)
    _add_not_none(res, "target_types", *event.get_jpath_values("Target[*].Type"), as_list=True)

    _add_not_none(res, "categories", event.get_jpath_value("Category"), as_list=True)
    _add_not_none(
        res,
        "protocols",
        *event.get_jpath_values("Source[*].Proto"),
        *event.get_jpath_values("Target[*].Proto"),
        as_list=True,
    )
    _add_not_none(res, "description", event.get_jpath_value("Description"))

    _add_not_none(res, "groups", event.get_jpath_value("_Mentat.ResolvedAbuses"), as_list=True)
    _add_not_none(
        res,
        "target_groups",
        event.get_jpath_value("_Mentat.TargetAbuses"),
        as_list=True,
    )

    _add_not_none(res, "severities", event.get_jpath_value("_Mentat.EventSeverity"), as_list=True)
    _add_not_none(
        res,
        "target_severities",
        event.get_jpath_value("_Mentat.TargetSeverity"),
        as_list=True,
    )

    _add_not_none(res, "classes", event.get_jpath_value("_Mentat.EventClass"), as_list=True)
    _add_not_none(
        res,
        "target_classes",
        event.get_jpath_value("_Mentat.TargetClass"),
        as_list=True,
    )

    _add_not_none(res, "detectors", *event.get_jpath_values("Node[*].Name"), as_list=True)
    _add_not_none(res, "detector_types", *event.get_jpath_values("Node[*].Type"), as_list=True)

    return res


def is_event_authorized(**kwargs):
    """
    Returns if the user that is correctly logged in should have
    access to particular event based on event's TLP.
    Note: used by many Views to avoid code duplication.
    """
    if not kwargs["item"].has_restricted_access():
        return True

    event_groups = kwargs["item"].get_all_groups()
    user = flask_login.current_user
    for user_group_name in user.get_all_group_names():
        if user_group_name in event_groups:
            return True
    return hawat.acl.PERMISSION_POWER.can()


class AbstractSearchView(PsycopgMixin, BaseSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for all views responsible for searching `IDEA <https://idea.cesnet.cz/en/index>`__
    event database.
    """

    authentication = True

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Search event database")

    @classmethod
    def get_view_icon(cls):
        return f"module-{cls.module_name}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Events")

    @staticmethod
    def get_search_form(request_args):
        return _get_search_form(request_args)

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,unused-argument
        form_data["groups"] = [_group_to_group_name(item) for item in form_data["groups"]]
        form_data["target_groups"] = [_group_to_group_name(item) for item in form_data["target_groups"]]

        from_time = form_data["st_from"] or form_data["dt_from"]  # It is possible both are defined

        if from_time is None:
            is_after_cleanup = True
        else:
            is_after_cleanup = get_after_cleanup(from_time)

        self.response_context.update(after_cleanup=is_after_cleanup)

    def do_before_response(self, **kwargs):
        self.response_context.update(quicksearch_list=self.get_quicksearch_by_time())

    def get_csag_context(self, csag_identifier: CsagIdentifier, additional_context: Any) -> Optional[dict[str, Any]]:
        match csag_identifier, additional_context:
            case ([_, "reports", "search", _], _):
                return _get_report_search_context_from_form_data(self.response_context["form_data"])
            case _:
                return super().get_csag_context(csag_identifier, additional_context)


class SearchView(HTMLMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for searching the `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of HTML page.
    """

    methods = ["GET"]

    has_help = True

    @staticmethod
    def get_qtype():
        """
        Get type of the event select query.
        """
        return mentat.services.eventstorage.QTYPE_SELECT_GHOST

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "search",
            endpoint=f"{cls.module_name}.search",
        )
        return breadcrumbs_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="events.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "download",
            endpoint="events.download",
            hidetitle=True,
        )
        return action_menu


class APISearchView(AJAXMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for searching the `IDEA <https://idea.cesnet.cz/en/index>`__
    event database and presenting the results in the form of JSON document.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "apisearch"


class AbstractShowView(PsycopgMixin, ItemShowView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class responsible for fetching and presenting single `IDEA <https://idea.cesnet.cz/en/index>`__
    event.
    """

    authentication = True

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show event")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Show")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of event &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].get_id()),
        )

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return is_event_authorized(**kwargs)

    def get_csag_context(self, csag_identifier: CsagIdentifier, additional_context: Any) -> Optional[dict[str, Any]]:
        match csag_identifier, additional_context:
            case ([_, "reports", "search", _], ac):
                return _get_report_search_context_from_idea(self.response_context["item"], ac)
            case ([_, "events" | "timeline", "search", _], _):
                return _get_event_search_context_from_idea(self.response_context["item"])
            case _:
                return super().get_csag_context(csag_identifier, additional_context)


class ShowView(HTMLMixin, AbstractShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed `IDEA <https://idea.cesnet.cz/en/index>`__ event view that presents
    the result as HTML page.
    """

    methods = ["GET"]

    has_help = True

    @classmethod
    def get_action_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "json",
            endpoint="events.json",
        )
        action_menu.add_entry(
            "endpoint",
            "download",
            endpoint="events.download",
        )
        action_menu.add_entry(
            "endpoint",
            "playground",
            endpoint="filters.playground",
            url=lambda **x: flask.url_for("filters.playground", event_id=x["item"].get_id()),
        )
        return action_menu

    def do_before_response(self, **kwargs):
        self.response_context.update(get_event_class=get_event_class)


class APIShowView(AJAXMixin, AbstractShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed `IDEA <https://idea.cesnet.cz/en/index>`__ event view that presents
    the result as HTML page.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "apishow"


class JSONShowView(HTMLMixin, PsycopgMixin, ItemShowView):  # pylint: disable=locally-disabled,abstract-method
    """
    Presenting idea `IDEA <https://idea.cesnet.cz/en/index>`__ event as the original JSON.
    """

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "json"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show event as JSON")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Show as JSON")

    @classmethod
    def get_view_template(cls):
        return f"{cls.module_name}/{cls.get_view_name()}.html"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View JSON of event &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].get_id()),
        )

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return is_event_authorized(**kwargs)

    @classmethod
    def get_action_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "json",
            endpoint="events.show",
        )
        action_menu.add_entry(
            "endpoint",
            "download",
            endpoint="events.download",
        )
        action_menu.add_entry(
            "endpoint",
            "playground",
            endpoint="filters.playground",
            url=lambda **x: flask.url_for("filters.playground", event_id=x["item"].get_id()),
        )
        return action_menu


class DownloadView(PsycopgMixin, BaseView):
    """
    Download `IDEA <https://idea.cesnet.cz/en/index>`__ event as JSON file.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "download"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Download event")

    @classmethod
    def get_view_url(cls, **kwargs):
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"].get_id())

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Download")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Download event &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].get_id()),
        )

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return is_event_authorized(**kwargs)

    # ---------------------------------------------------------------------------

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item = self.fetch(item_id)
        if not item:
            flask.abort(404)

        if not self.authorize_item_action(item=item):
            flask.abort(403)

        self.logger.debug("Event %s is being downloaded as a standalone file.", item["ID"])

        response = flask.make_response(
            item.to_json(
                indent=4,
                sort_keys=True,
            )
        )
        response.mimetype = "application/json"
        response.headers["Content-Disposition"] = f"attachment; filename={item_id}.idea.json"
        return response


class AttachmentDownloadView(HTMLMixin, PsycopgMixin, BaseView):
    """
    Download an attachment from `IDEA <https://idea.cesnet.cz/en/index>`__ event as a file.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "attachmentdownload"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Download attachment")

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return is_event_authorized(**kwargs)

    # ---------------------------------------------------------------------------

    def dispatch_request(self, item_id, attachment_number):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """

        def _parse_attachment_number(number):
            try:
                return int(attachment_number)
            except ValueError:
                return None

        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        attachment_number = _parse_attachment_number(attachment_number)
        if attachment_number is None:
            self.abort(400, lazy_gettext("Attachment number must be a valid number."))

        attachment = item.get_attachment(attachment_number)
        if not attachment:
            flask.abort(404)

        self.logger.debug(
            "%s event's attachment with index %s is being downloaded as a standalone file.",
            item["ID"],
            attachment_number,
        )
        attachment_content = item.get_attachment_content(attachment_number)
        if attachment_content is None:
            self.flash(
                lazy_gettext(
                    "Something went wrong and the content of this attachment could not be loaded. Please look at it in the JSON view."
                ),
                "error",
            )
            self.abort(500)
        else:
            content, extension, mimetype = attachment_content

            if attachment.get("FileName"):
                # In IDEA, FileName field is a list.
                name = ",".join(attachment.get("FileName"))
                # The original name should be modified by adding an extension only if
                # it's a binary, to warn the user about possibly malicious content.
                if extension.upper() == "BIN":
                    name = f"{name}.{extension}"
            else:
                name = f"attachment{attachment_number}.{extension}"

            response = flask.make_response(content)
            response.mimetype = mimetype
            response.headers["Content-Disposition"] = f"attachment; filename={name}"
            return response
        return None


class AbstractDashboardView(SQLAlchemyMixin, BaseSearchView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for presenting overall `IDEA <https://idea.cesnet.cz/en/index>`__
    event statistics dashboard.
    """

    authentication = True

    always_include_charts = False

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Events")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Overall event dashboards")

    @classmethod
    def get_view_template(cls):
        return f"{cls.module_name}/{cls.get_view_name()}.html"

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return EventStatisticsModel

    @staticmethod
    def get_search_form(request_args):
        return EventDashboardForm(request_args, meta={"csrf": False})

    @staticmethod
    def build_query(query, model, form_args):
        # Adjust query based on lower time boudary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.dt_from >= form_args["dt_from"])
        # Adjust query based on upper time boudary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.dt_to <= form_args["dt_to"])

        # Return the result sorted by interval.
        return query.order_by(model.interval)

    def _add_chart_section_data(self, chsections, grp_key, stats, timeline_cfg):
        for i, chsection in enumerate(chsections):
            if chsection.key in (mentat.stats.idea.ST_SKEY_CNT_EVENTS,):
                data_format = charts.InputDataFormat.WIDE_SIMPLE
            else:
                data_format = charts.InputDataFormat.WIDE_COMPLEX

            chart_data = []
            for chart_config in chsection.chart_configs:
                match chart_config:
                    case charts.TimelineChartConfig():
                        timeline_chart_data = charts.TimelineChartData(
                            stats[grp_key][mentat.stats.idea.ST_SKEY_TIMELINE],
                            chart_config,
                            timeline_cfg,
                            data_format,
                            add_rest=True,
                            x_axis_label_override=lazy_gettext("time"),
                        )
                        chart_data.append(timeline_chart_data)
                    case charts.SecondaryChartConfig():
                        secondary_chart_data = charts.SecondaryChartData(
                            stats[grp_key], chart_config, data_format, add_rest=True, sort=True
                        )
                        chart_data.append(secondary_chart_data)

            chsection = chsection.add_data(*chart_data)
            chsections[i] = chsection

    def do_after_search(self, items):
        self.logger.debug("Calculating event dashboard overview from %d records.", len(items))
        if items:
            dt_from = self.response_context["form_data"].get("dt_from", None)
            if not dt_from:
                dt_from = self.dbcolumn_min(self.dbmodel.dt_from)

            dt_to = self.response_context["form_data"].get("dt_to", None)
            if not dt_to:
                dt_to = datetime.datetime.utcnow()

            timeline_cfg = mentat.stats.idea.TimelineCFG.get_optimized(
                time_from=dt_from,
                time_to=dt_to,
                max_count=flask.current_app.config["HAWAT_CHART_TIMELINE_MAXSTEPS"],
                min_step_seconds=300,
                user_timezone=pytz.timezone(flask.session.get("timezone", "UTC")),
            )

            self.response_context.update(statistics=mentat.stats.idea.aggregate_timeline_groups(items, timeline_cfg))

            if self.always_include_charts:
                self.response_context.update(
                    chart_sections_overall=DASHBOARD_CHART_SECTIONS.copy(),
                    chart_sections_internal=DASHBOARD_CHART_SECTIONS.copy(),
                    chart_sections_external=DASHBOARD_CHART_SECTIONS_EXTERNAL.copy(),
                )
                chsections_sections = (
                    self.response_context["chart_sections_internal"],
                    self.response_context["chart_sections_external"],
                    self.response_context["chart_sections_overall"],
                )
                for chsections, grp_key in zip(chsections_sections, mentat.stats.idea.LIST_STAT_GROUPS):
                    self._add_chart_section_data(
                        chsections,
                        grp_key,
                        self.response_context["statistics"],
                        timeline_cfg,
                    )

    def do_before_response(self, **kwargs):
        self.response_context.update(quicksearch_list=self.get_quicksearch_by_time())


class DashboardView(HTMLMixin, AbstractDashboardView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for presenting overall `IDEA <https://idea.cesnet.cz/en/index>`__
    event statistics dashboard in the form of HTML page.
    """

    methods = ["GET"]

    always_include_charts = True

    @classmethod
    def get_view_name(cls):
        return "dashboard"


class APIDashboardView(AJAXMixin, AbstractDashboardView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for presenting overall `IDEA <https://idea.cesnet.cz/en/index>`__
    event statistics dashboard in the form of JSON document.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "apidashboard"

    def process_response_context(self):
        super().process_response_context()
        # Prevent certain response context keys to appear in final response.
        for key in ("items", "quicksearch_list"):
            with contextlib.suppress(KeyError):
                del self.response_context[key]
        return self.response_context


class APIMetadataView(AJAXMixin, SimpleView):
    """
    Application view providing access event metadata information.
    """

    authentication = True

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "metadata"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Event metadata")

    def do_before_response(self, **kwargs):
        self.response_context.update(**hawat.events.get_event_enums())


# -------------------------------------------------------------------------------


class EventsBlueprint(HawatBlueprint):
    """Pluggable module - `IDEA <https://idea.cesnet.cz/en/index>`__ event database (*events*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext('<a href="https://idea.cesnet.cz/en/index">IDEA</a> event database')

    def register_app(self, app):
        app.menu_main.add_entry(
            "view",
            f"dashboards.{BLUEPRINT_NAME}",
            position=10,
            view=DashboardView,
        )
        app.menu_main.add_entry(
            "view",
            BLUEPRINT_NAME,
            position=140,
            view=SearchView,
            resptitle=True,
        )

        def _get_upb_for_host() -> URLParamsBuilder:
            return URLParamsBuilder(
                {
                    "submit": tr_("Search"),
                    "source_addrs": URLParamsBuilder.EXCLUDE,
                    "target_addrs": URLParamsBuilder.EXCLUDE,
                    "source_ports": URLParamsBuilder.EXCLUDE,
                    "target_ports": URLParamsBuilder.EXCLUDE,
                    "source_types": URLParamsBuilder.EXCLUDE,
                    "target_types": URLParamsBuilder.EXCLUDE,
                }
            )

        def _get_upb_for_source_target() -> URLParamsBuilder:
            return URLParamsBuilder(
                {
                    "submit": tr_("Search"),
                    "host_addrs": URLParamsBuilder.EXCLUDE,
                    "host_ports": URLParamsBuilder.EXCLUDE,
                    "host_types": URLParamsBuilder.EXCLUDE,
                }
            )

        def _get_upb_for_reversible(key: str) -> URLParamsBuilder:
            """
            Get URLParamsBuilder for csag groups for which the context
            could potentially contain the reversing 'not_*' parameter.
            """
            return URLParamsBuilder(
                {
                    "submit": tr_("Search"),
                    f"not_{key}": URLParamsBuilder.EXCLUDE,
                }
            )

        # Register context search actions provided by this module.
        app.set_csag(
            hawat.const.CSAG_ABUSE,
            tr_("as <strong>source group</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("groups").add_rule("groups", True).add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source group</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source group</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_ABUSE,
            tr_("as <strong>target group</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("target_groups")
            .add_rule("target_groups", True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target group</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target group</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_ADDRESS,
            tr_("as <strong>source</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("source_addrs", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_ADDRESS,
            tr_("as <strong>target</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("target_addrs", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_ADDRESS,
            tr_("as <strong>host</strong> and keep context"),
            SearchView,
            _get_upb_for_host()
            .add_rule("host_addrs", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>host</strong> only"),
            title_context_nonrelevant=tr_("as <strong>host</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_CATEGORY,
            tr_("as <strong>category</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("categories")
            .add_rule("categories", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>category</strong> only"),
            title_context_nonrelevant=tr_("as <strong>category</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_CLASS,
            tr_("as <strong>source class</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("classes")
            .add_rule("classes", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source class</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source class</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_CLASS,
            tr_("as <strong>target class</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("target_classes")
            .add_rule("target_classes", True)
            .add_kwrule("target_groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target class</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target class</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_DETECTOR,
            tr_("as <strong>detector</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("detectors")
            .add_rule("detectors", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>detector</strong> only"),
            title_context_nonrelevant=tr_("as <strong>detector</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_DETTYPE,
            tr_("as <strong>detector type</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("detector_types")
            .add_rule("detector_types", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>detector type</strong> only"),
            title_context_nonrelevant=tr_("as <strong>detector type</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_HOSTTYPE,
            tr_("as <strong>source type</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("source_types", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source type</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source type</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_HOSTTYPE,
            tr_("as <strong>target type</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("target_types", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target type</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target type</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_HOSTTYPE,
            tr_("as <strong>host type</strong> and keep context"),
            SearchView,
            _get_upb_for_host()
            .add_rule("host_types", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>host type</strong> only"),
            title_context_nonrelevant=tr_("as <strong>host type</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_PORT,
            tr_("as <strong>source port</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("source_ports", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source port</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source port</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_PORT,
            tr_("as <strong>target port</strong> and keep context"),
            SearchView,
            _get_upb_for_source_target()
            .add_rule("target_ports", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target port</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target port</strong>"),
        )
        app.set_csag(
            hawat.const.CSAG_PORT,
            tr_("as <strong>host port</strong> and keep context"),
            SearchView,
            _get_upb_for_host()
            .add_rule("host_ports", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>host port</strong> only"),
            title_context_nonrelevant=tr_("as <strong>host port</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_PROTOCOL,
            tr_("as <strong>protocol</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("protocols")
            .add_rule("protocols", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>protocol</strong> only"),
            title_context_nonrelevant=tr_("as <strong>protocol</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_SEVERITY,
            tr_("as <strong>source severity</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("severities")
            .add_rule("severities", True)
            .add_kwrule("groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>source severity</strong> only"),
            title_context_nonrelevant=tr_("as <strong>source severity</strong>"),
        )

        app.set_csag(
            hawat.const.CSAG_SEVERITY,
            tr_("as <strong>target severity</strong> and keep context"),
            SearchView,
            _get_upb_for_reversible("target_severities")
            .add_rule("target_severities", True)
            .add_kwrule("target_groups", True, True)
            .add_kwrules_from_form(SimpleEventSearchForm),
            title_contextless=tr_("as <strong>target severity</strong> only"),
            title_context_nonrelevant=tr_("as <strong>target severity</strong>"),
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = EventsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path=f"/{BLUEPRINT_NAME}/static",
    )

    hbp.register_view_class(SearchView, f"/{BLUEPRINT_NAME}/search")
    hbp.register_view_class(ShowView, f"/{BLUEPRINT_NAME}/<item_id>/show")
    hbp.register_view_class(JSONShowView, f"/{BLUEPRINT_NAME}/<item_id>/json")
    hbp.register_view_class(DownloadView, f"/{BLUEPRINT_NAME}/<item_id>/download")
    hbp.register_view_class(
        AttachmentDownloadView,
        f"/{BLUEPRINT_NAME}/<item_id>/attachments/<attachment_number>/download",
    )
    hbp.register_view_class(DashboardView, f"/{BLUEPRINT_NAME}/dashboard")
    hbp.register_view_class(APISearchView, f"/api/{BLUEPRINT_NAME}/search")
    hbp.register_view_class(APIShowView, f"/api/{BLUEPRINT_NAME}/<item_id>/show")
    hbp.register_view_class(APIDashboardView, f"/api/{BLUEPRINT_NAME}/dashboard")
    hbp.register_view_class(APIMetadataView, f"/api/{BLUEPRINT_NAME}/metadata")

    return hbp
