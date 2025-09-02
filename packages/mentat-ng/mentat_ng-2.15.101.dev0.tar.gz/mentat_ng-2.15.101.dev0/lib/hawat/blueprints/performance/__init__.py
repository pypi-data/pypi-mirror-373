#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to system performance statistics.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import collections

import flask
from flask_babel import gettext, lazy_gettext

from pyzenkit.utils import get_resource_path_fr

import hawat.acl
import mentat.const
import mentat.stats.rrd
from hawat.base import HawatBlueprint
from hawat.view import FileNameView, SimpleView
from hawat.view.mixin import HTMLMixin

BLUEPRINT_NAME = "performance"
"""Name of the blueprint as module global constant."""


class ViewView(HTMLMixin, SimpleView):
    """
    View responsible for presenting system performance in using RRD charts.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_name(cls):
        return "view"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("System performance")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("System processing performance")

    def do_before_response(self, **kwargs):
        chartdict = collections.OrderedDict()
        try:
            rrd_stats = mentat.stats.rrd.RrdStats(
                get_resource_path_fr(
                    flask.current_app.mconfig[mentat.const.CKEY_CORE_STATISTICS][
                        mentat.const.CKEY_CORE_STATISTICS_RRDSDIR
                    ]
                ),
                get_resource_path_fr(
                    flask.current_app.mconfig[mentat.const.CKEY_CORE_STATISTICS][
                        mentat.const.CKEY_CORE_STATISTICS_REPORTSDIR
                    ]
                ),
            )
            charts = rrd_stats.lookup()

            # Convert list of all existing charts to a structure more appropriate
            # for display.
            for chrt in charts:
                key = chrt["ds_type"]
                if chrt["totals"]:
                    key += "_t"
                if key not in chartdict:
                    chartdict[key] = []
                chartdict[key].append(chrt)
            for key, val in chartdict.items():
                chartdict[key] = sorted(val, key=lambda x: x["size"])

        except FileNotFoundError:
            self.flash(gettext("Error when displaying system performance, encountered file not found error."))
            # flask.current_app.log_exception_with_label(
            #    traceback.TracebackException(*sys.exc_info()),
            #    "Error when displaying system performance"
            # )

        self.response_context["chartdict"] = chartdict


class DataView(FileNameView):
    """
    View responsible for accessing raw performance data in RRD databases.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_name(cls):
        return "data"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("System performance data")

    @classmethod
    def get_directory_path(cls):
        return flask.current_app.mconfig[mentat.const.CKEY_CORE_STATISTICS][
            mentat.const.CKEY_CORE_STATISTICS_REPORTSDIR
        ]


class RRDDBView(FileNameView):
    """
    View responsible for accessing performance RRD databases.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_name(cls):
        return "rrds"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("System performance databases")

    @classmethod
    def get_directory_path(cls):
        return flask.current_app.mconfig[mentat.const.CKEY_CORE_STATISTICS][mentat.const.CKEY_CORE_STATISTICS_RRDSDIR]


# -------------------------------------------------------------------------------


class PerformanceBlueprint(HawatBlueprint):
    """Pluggable module - system processing performance (*performance*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("System performance")

    def register_app(self, app):
        app.menu_main.add_entry(
            "view",
            f"admin.{BLUEPRINT_NAME}",
            position=35,
            view=ViewView,
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = PerformanceBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        static_folder="static",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(ViewView, "/view")
    hbp.register_view_class(DataView, "/data/<filename>")
    hbp.register_view_class(RRDDBView, "/rrds/<filename>")

    return hbp
