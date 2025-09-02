#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides default home page.


Provided endpoints
------------------

``/``
    Page providing home page.

    * *Authentication:* no authentication
    * *Methods:* ``GET``
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from flask_babel import lazy_gettext

from hawat.base import HawatBlueprint
from hawat.view import SimpleView
from hawat.view.mixin import HTMLMixin

BLUEPRINT_NAME = "home"
"""Name of the blueprint as module global constant."""


class IndexView(HTMLMixin, SimpleView):
    """
    View presenting home page.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "index"

    @classmethod
    def get_view_icon(cls):
        return "module-home"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Welcome!")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Home")


# -------------------------------------------------------------------------------


class HomeBlueprint(HawatBlueprint):
    """Pluggable module - home page (*home*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Home page")


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = HomeBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
    )

    hbp.register_view_class(
        IndexView,
        "/",
    )

    return hbp
