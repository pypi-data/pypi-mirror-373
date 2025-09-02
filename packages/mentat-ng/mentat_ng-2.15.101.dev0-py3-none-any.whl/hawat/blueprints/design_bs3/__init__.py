#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides default application design and style. Currently,
there are no views provided by this module.


.. note::

    To completely change the design of the whole application you can implement
    your own custom _design_ module and replace this one. However, this requires
    that you thoroughly study the design of this module and provide your own
    implementation for all API hooks, otherwise you may break the whole application.


Module content
--------------

#. Base Jinja2 template providing application layout.
#. Common macros for Jinja2 templates.
#. Common forms (delete, disable, enable).
#. HTML error pages (400, 403, 404, 410, 500).
#. Various images
#. Application CSS styles
#. Application Javascripts

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from flask_babel import lazy_gettext

from hawat.base import HawatBlueprint

#
# Name of the blueprint as module global constant.
#
BLUEPRINT_NAME = "design"


# -------------------------------------------------------------------------------


class DesignBlueprint(HawatBlueprint):
    """Pluggable module - application design and style (*design*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Application design and style template")


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """
    return DesignBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static/design",
    )
