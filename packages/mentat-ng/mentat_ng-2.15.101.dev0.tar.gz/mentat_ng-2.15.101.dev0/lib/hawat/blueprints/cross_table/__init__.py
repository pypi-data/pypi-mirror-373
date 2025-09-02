#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
This file contains pluggable module for Hawat web interface that provides cross
table search and visualization functionality.
"""

from typing import Any, cast

from flask_babel import lazy_gettext
from flask_babel.speaklater import LazyString

import hawat.events
import hawat.forms
import mentat.services.eventstorage
import mentat.stats.idea
from .forms import SimpleCrossTableSearchForm
from .model import AggColumn
from hawat.base import HawatApp, HawatBlueprint, PsycopgMixin
from hawat.charts.const import PivotItems, TableColoring
from hawat.charts.model import PivotTableChartConfig, PivotTableChartData
from hawat.view import BaseSearchView
from hawat.view.mixin import AJAXMixin, HTMLMixin
from mentat.datatype.sqldb import GroupModel

BLUEPRINT_NAME = "cross_table"

AGG_COLUMNS: list[AggColumn] = [
    AggColumn(mentat.stats.idea.ST_SKEY_CATEGORIES, lazy_gettext("Categories"), "category"),
    AggColumn(mentat.stats.idea.ST_SKEY_SRCTYPES, lazy_gettext("Source types"), "source_type"),
    AggColumn(mentat.stats.idea.ST_SKEY_TGTTYPES, lazy_gettext("Target types"), "target_type"),
    AggColumn(mentat.stats.idea.ST_SKEY_PROTOCOLS, lazy_gettext("Protocols"), "protocol"),
    AggColumn(mentat.stats.idea.ST_SKEY_DETECTORS, lazy_gettext("Detectors"), "node_name"),
    AggColumn(mentat.stats.idea.ST_SKEY_DETECTORTPS, lazy_gettext("Detector types"), "node_type"),
    AggColumn(mentat.stats.idea.ST_SKEY_ABUSES, lazy_gettext("Source groups"), "resolvedabuses"),
    AggColumn(mentat.stats.idea.ST_SKEY_CLASSES, lazy_gettext("Source classes"), "eventclass"),
    AggColumn(mentat.stats.idea.ST_SKEY_SEVERITIES, lazy_gettext("Source severities"), "eventseverity"),
    AggColumn("target_abuses", lazy_gettext("Target groups"), "targetabuses"),
    AggColumn("target_classes", lazy_gettext("Target classes"), "targetclass"),
    AggColumn("target_severities", lazy_gettext("Target severities"), "targetseverity"),
    AggColumn(mentat.stats.idea.ST_SKEY_TLPS, lazy_gettext("TLP"), "tlp"),
]

_AGG_COLUMN_MAP = {agg_column.key: agg_column for agg_column in AGG_COLUMNS}


def _get_search_form(request_args: Any = None) -> SimpleCrossTableSearchForm:
    choices = hawat.events.get_event_form_choices()

    agg_column_choices = [(agg_column.key, agg_column.display_name) for agg_column in AGG_COLUMNS]

    form = SimpleCrossTableSearchForm(
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
        choices_agg_columns=agg_column_choices,
    )

    # In case no time bounds were set adjust them manually.
    if request_args and not (
        "dt_from" in request_args or "dt_to" in request_args or "st_from" in request_args or "st_to" in request_args
    ):
        form.dt_from.process_data(hawat.forms.default_dt_with_delta())
        form.dt_to.process_data(hawat.forms.default_dt())

    return form


def _group_to_group_name(group: str | GroupModel) -> str:
    if isinstance(group, str):
        return group
    return cast(str, group.name)


class AbstractSearchView(PsycopgMixin, BaseSearchView):
    """
    Base class for all views responsible for searching and displaying cross table results.
    """

    authentication = True

    @classmethod
    def get_view_title(cls, **kwargs: Any) -> str | LazyString:
        return lazy_gettext("Calculate event cross table")

    @classmethod
    def get_view_icon(cls) -> str:
        return f"module-{cls.module_name}".replace("_", "-")

    @classmethod
    def get_menu_title(cls, **kwargs: Any) -> str | LazyString:
        return lazy_gettext("Cross table")

    @staticmethod
    def get_search_form(request_args: Any) -> SimpleCrossTableSearchForm:
        return _get_search_form(request_args)

    @staticmethod
    def get_qtype() -> str:
        return mentat.services.eventstorage.QTYPE_PIVOT

    def do_before_search(self, form_data: dict[str, Any]) -> None:
        form_data["groups"] = [_group_to_group_name(item) for item in form_data["groups"]]
        form_data["target_groups"] = [_group_to_group_name(item) for item in form_data["target_groups"]]

        form_data["col_agg"] = _AGG_COLUMN_MAP[form_data["col_agg_column"]].column_name
        form_data["row_agg"] = _AGG_COLUMN_MAP[form_data["row_agg_column"]].column_name
        form_data["include_residuals"] = form_data["table_coloring"] in (
            TableColoring.RESIDUAL,
            TableColoring.RESIDUAL_DIVERGING,
        )

        from_time = form_data["st_from"] or form_data["dt_from"]  # It is possible both are defined

        if from_time is None:
            is_after_cleanup = True
        else:
            is_after_cleanup = hawat.events.get_after_cleanup(from_time)

        self.response_context.update(after_cleanup=is_after_cleanup)


class SearchView(HTMLMixin, AbstractSearchView):
    """
    View responsible for searching and displaying cross table search results
    in the form of HTML page.
    """

    methods = ["GET"]

    @classmethod
    def get_view_name(cls) -> str:
        return "search"

    def do_after_search(self, items: PivotItems) -> None:
        pivot_table_config = PivotTableChartConfig(
            column_name="Value",
            value_name="Event Count",
            table_coloring=self.response_context["form_data"]["table_coloring"],
        )
        self.response_context.update(
            result_data=PivotTableChartData(
                items,
                pivot_table_config,
            )
        )

        super().do_after_search(items)


class APISearchView(AJAXMixin, AbstractSearchView):
    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls) -> str:
        return "apisearch"


class CrossTableBlueprint(HawatBlueprint):
    """
    Blueprint for the cross table module.
    """

    @classmethod
    def get_module_title(cls) -> str | LazyString:
        return lazy_gettext("Event cross table")

    def register_app(self, app: HawatApp) -> None:
        app.menu_main.add_entry(
            "view",
            BLUEPRINT_NAME,
            position=200,
            view=SearchView,
            resptitle=True,
        )


# -------------------------------------------------------------------------------


def get_blueprint() -> CrossTableBlueprint:
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """
    hbp = CrossTableBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
    )

    hbp.register_view_class(SearchView, f"/{BLUEPRINT_NAME}/search")
    hbp.register_view_class(APISearchView, f"/api/{BLUEPRINT_NAME}/search")
    return hbp
