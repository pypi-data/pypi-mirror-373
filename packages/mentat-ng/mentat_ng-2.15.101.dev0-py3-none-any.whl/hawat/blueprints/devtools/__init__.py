#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides various utility and development tools.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_debugtoolbar
from flask_babel import lazy_gettext

import hawat.acl
from hawat.base import HawatBlueprint
from hawat.view import SimpleView
from hawat.view.mixin import HTMLMixin

BLUEPRINT_NAME = "devtools"
"""Name of the blueprint as module global constant."""


class ConfigView(HTMLMixin, SimpleView):
    """
    View for displaying current application configuration and environment.
    """

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_view_name(cls):
        return "config"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("System configuration")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("System configuration")


# -------------------------------------------------------------------------------


class DevtoolsBlueprint(HawatBlueprint):
    """Pluggable module - development tools (*devtools*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Development tools")

    def register_app(self, app):
        self.developer_toolbar.init_app(app)

        app.menu_main.add_entry("view", "admin.devconfig", position=35, view=ConfigView)


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = DevtoolsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.developer_toolbar = flask_debugtoolbar.DebugToolbarExtension()  # pylint: disable=locally-disabled,attribute-defined-outside-init

    hbp.register_view_class(ConfigView, "/config")

    return hbp
