#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to database status information. The
following information is provided:

* general statistics of event database:

  * general statistics of *events* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

  * general statistics of *event_thresholds* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

  * general statistics of *thresholds* table

    * estimated number of records
    * table size, index size, tablespace size and total size
    * oldest and youngest record timestamp, record timespan

* PostgreSQL configurations


Provided endpoints
------------------

``/dbstatus/view``
    Page providing read-only access various database status characteristics.

    *Authentication:* login required
    *Authorization:* ``admin`` role only
    *Methods:* ``GET``

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import sys
import traceback

import flask
import flask_login
import markupsafe
import werkzeug.routing
from flask_babel import format_decimal, gettext, lazy_gettext

import hawat.acl
import hawat.const
import hawat.db
import hawat.menu
import mentat.const
import mentat.system
from hawat import charts
from hawat.base import RE_UQUERY, HawatBlueprint, PsycopgMixin
from hawat.forms import ItemActionConfirmForm
from hawat.utils import fallback_formatter, get_format_byte_size_function
from hawat.view import RenderableView, SimpleView
from hawat.view.mixin import AJAXMixin, HTMLMixin
from mentat.datatype.sqldb import (
    UserModel,
)

BLUEPRINT_NAME = "dbstatus"
"""Name of the blueprint as module global constant."""

CHART_SECTIONS = [
    charts.ChartSection(
        "row_estimate",
        lazy_gettext("Row counts"),
        lazy_gettext("Row counts"),
        None,
        (
            charts.SecondaryChartConfig(
                key="row_estimate",
                data_complexity=charts.DataComplexity.SINGLE,
                table_type=charts.TableType.COLUMNS,
                column_name=lazy_gettext("Table name"),
            ),
        ),
    ),
    charts.ChartSection(
        "total_bytes",
        lazy_gettext("Total sizes"),
        lazy_gettext("Total sizes"),
        None,
        (
            charts.SecondaryChartConfig(
                key="total_bytes",
                data_complexity=charts.DataComplexity.SINGLE,
                table_type=charts.TableType.COLUMNS,
                column_name=lazy_gettext("Table name"),
                value_name=lazy_gettext("Total table size"),
                allow_table_aggregation=False,
                format_function=fallback_formatter(get_format_byte_size_function(format_decimal)),
            ),
        ),
    ),
    charts.ChartSection(
        "table_bytes",
        lazy_gettext("Table sizes"),
        lazy_gettext("Table sizes"),
        None,
        (
            charts.SecondaryChartConfig(
                key="table_bytes",
                data_complexity=charts.DataComplexity.SINGLE,
                table_type=charts.TableType.COLUMNS,
                column_name=lazy_gettext("Table name"),
                value_name=lazy_gettext("Table size"),
                allow_table_aggregation=False,
                format_function=fallback_formatter(get_format_byte_size_function(format_decimal)),
            ),
        ),
    ),
    charts.ChartSection(
        "index_bytes",
        lazy_gettext("Index sizes"),
        lazy_gettext("Index sizes"),
        None,
        (
            charts.SecondaryChartConfig(
                key="index_bytes",
                data_complexity=charts.DataComplexity.SINGLE,
                table_type=charts.TableType.COLUMNS,
                column_name=lazy_gettext("Table name"),
                value_name=lazy_gettext("Index size"),
                allow_table_aggregation=False,
                format_function=fallback_formatter(get_format_byte_size_function(format_decimal)),
            ),
        ),
    ),
]


class ViewView(HTMLMixin, PsycopgMixin, SimpleView):
    """
    Application view providing access event database status information.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        return "view"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Database status")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Database status")

    def _enrich_result_queries(self, result):
        """
        Enrich query status result with information about the user running the query.
        """
        cache = {}
        for record in result:
            if "query_name" not in record:
                continue
            user_id, query_id = self.parse_qname(record["query_name"])
            record["user_id"] = user_id
            record["query_id"] = query_id
            if user_id not in cache:
                cache[user_id] = (
                    hawat.db.db_get().session.query(UserModel).filter(UserModel.id == int(user_id)).one_or_none()
                )
            record["user"] = cache[user_id]
        return result

    def _add_chart_section_data(self, stats):
        for i, chsection in enumerate(self.response_context["chart_sections"]):
            chart_data = charts.SecondaryChartData(
                stats, chsection.chart_configs[0], charts.InputDataFormat.WIDE_COMPLEX, sort=True
            )
            self.response_context["chart_sections"][i] = chsection.add_data(chart_data)

    def do_before_response(self, **kwargs):
        self.response_context.update(
            query_status_events=self._enrich_result_queries(
                self.get_db().queries_status(discard_parallel_workers=False)
            ),
            database_status_events=self.get_db().database_status(),
            sw_versions=mentat.system.analyze_versions(),
            chart_sections=CHART_SECTIONS.copy(),
        )

        dbstatistics_events = {
            "total_bytes": {
                x: y["total_bytes"] for x, y in self.response_context["database_status_events"]["tables"].items()
            },
            "table_bytes": {
                x: y["table_bytes"] for x, y in self.response_context["database_status_events"]["tables"].items()
            },
            "index_bytes": {
                x: y["index_bytes"] for x, y in self.response_context["database_status_events"]["tables"].items()
            },
            "row_estimate": {
                x: y["row_estimate"] for x, y in self.response_context["database_status_events"]["tables"].items()
            },
        }
        self.response_context.update(database_statistics_events=dbstatistics_events)
        self._add_chart_section_data(dbstatistics_events)

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "stop",
            endpoint="dbstatus.query-stop",
            hidetitle=True,
            legend=lambda **x: lazy_gettext("Stop user query &quot;%(item)s&quot;", item=x["item"]["query_name"]),
            cssclass="action-ajax",
        )
        self.response_context["context_action_menu_query"] = action_menu


class MyQueriesView(HTMLMixin, PsycopgMixin, SimpleView):
    """
    Application view providing access status information of given single query.
    """

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "queries_my"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("My queries")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("My currently running queries")

    def _enrich_result_queries(self, result):
        """
        Enrich query status result with information about the user running the query.
        """
        cache = {}
        for record in result:
            if "query_name" not in record:
                continue
            user_id, query_id = self.parse_qname(record["query_name"])
            record["user_id"] = user_id
            record["query_id"] = query_id
            if user_id not in cache:
                cache[user_id] = (
                    hawat.db.db_get().session.query(UserModel).filter(UserModel.id == int(user_id)).one_or_none()
                )
            record["user"] = cache[user_id]
        return result

    def do_before_response(self, **kwargs):
        self.response_context.update(
            query_status_events=self._enrich_result_queries(
                self.get_db().queries_status(
                    RE_UQUERY.format(int(flask_login.current_user.get_id())),
                    discard_parallel_workers=True,
                )
            )
        )

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "stop",
            endpoint="dbstatus.query-stop",
            hidetitle=True,
            legend=lambda **x: lazy_gettext("Stop user query &quot;%(item)s&quot;", item=x["item"]["query_name"]),
            cssclass="action-ajax",
        )
        self.response_context["context_action_menu_query"] = action_menu


class QueryStatusView(AJAXMixin, PsycopgMixin, RenderableView):
    """
    Application view providing access status information of given single query.
    """

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "query-status"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Query status")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Query status")

    @classmethod
    def get_view_url(cls, **kwargs):
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"]["query_name"])

    def do_before_response(self, **kwargs):
        query_status = self.get_db().query_status(kwargs["item_id"])
        if not query_status:
            self.abort(404)

        self.response_context.update(
            user_id=kwargs["user_id"],
            query_name=kwargs["item_id"],
            query_status=query_status,
        )

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        user_id, _ = self.parse_qname(item_id)
        if flask_login.current_user.get_id() != user_id and not hawat.acl.PERMISSION_POWER.can():
            self.abort(403, gettext("You are not allowed to view status of this query."))

        self.do_before_response(item_id=item_id, user_id=user_id)
        return self.generate_response()


class AbstractQueryStopView(PsycopgMixin, RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Application view providing ability to stop given query.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_icon(cls):
        return "action-stop"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Stop query")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Stop query")

    @classmethod
    def get_view_url(cls, **kwargs):
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"]["query_name"])

    @classmethod
    def authorize_item_action(cls, **kwargs):
        user_id, _ = cls.parse_qname(kwargs["item"]["query_name"])
        return hawat.acl.PERMISSION_POWER.can() or flask_login.current_user.get_id() == user_id

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Query <strong>%(item_id)s</strong> was successfully stopped.",
            item_id=markupsafe.escape(str(kwargs["item"]["query_name"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to stop query <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"]["query_name"])),
        )

    def get_url_next(self):
        try:
            return flask.url_for("{}.{}".format(self.module_name, "view"))
        except werkzeug.routing.BuildError:
            return flask.url_for(flask.current_app.config["ENDPOINT_HOME"])

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        item = self.get_db().query_status(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        form = ItemActionConfirmForm()

        if form.validate_on_submit():
            form_data = form.data

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    action_status = self.get_db().query_cancel(item_id)
                    if action_status:
                        self.flash(
                            markupsafe.Markup(self.get_message_success(item=item)),
                            hawat.const.FLASH_SUCCESS,
                        )
                    else:
                        self.flash(
                            markupsafe.Markup(self.get_message_failure(item=item)),
                            hawat.const.FLASH_FAILURE,
                        )
                    self.get_db().commit()
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.get_db().commit()
                    self.flash(
                        markupsafe.Markup(self.get_message_failure(item=item)),
                        hawat.const.FLASH_FAILURE,
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item=item),
                    )
                    return self.redirect(default_url=self.get_url_next())

        self.response_context.update(
            confirm_form=form,
            confirm_url=flask.url_for(f"{self.module_name}.{self.get_view_name()}", item_id=item_id),
            item_id=item_id,
            item=item,
            referrer=self.get_url_cancel(),
        )

        self.do_before_response()
        return self.generate_response()


class QueryStopView(HTMLMixin, AbstractQueryStopView):
    """
    Application view providing ability to stop given query.
    """

    @classmethod
    def get_view_name(cls):
        return "query-stop"

    @classmethod
    def get_view_template(cls):
        return f"{cls.module_name}/query_stop.html"


class ApiQueryStopView(AJAXMixin, AbstractQueryStopView):
    """
    Application view providing ability to stop given query.
    """

    @classmethod
    def get_view_name(cls):
        return "api-query-stop"


# -------------------------------------------------------------------------------


class DatabaseStatusBlueprint(HawatBlueprint):
    """Pluggable module - database status overview (*dbstatus*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Database status overview")

    def register_app(self, app):
        app.menu_main.add_entry(
            "view",
            f"admin.{BLUEPRINT_NAME}",
            position=33,
            view=ViewView,
        )
        app.menu_auth.add_entry(
            "view",
            "queries_my",
            position=50,
            view=MyQueriesView,
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = DatabaseStatusBlueprint(BLUEPRINT_NAME, __name__, template_folder="templates")

    hbp.register_view_class(ViewView, f"/{BLUEPRINT_NAME}/view")
    hbp.register_view_class(MyQueriesView, f"/{BLUEPRINT_NAME}/query/my")
    hbp.register_view_class(QueryStatusView, f"/api/{BLUEPRINT_NAME}/query/<item_id>/status")
    hbp.register_view_class(QueryStopView, f"/{BLUEPRINT_NAME}/query/<item_id>/stop")
    hbp.register_view_class(ApiQueryStopView, f"/api/{BLUEPRINT_NAME}/query/<item_id>/stop")

    return hbp
