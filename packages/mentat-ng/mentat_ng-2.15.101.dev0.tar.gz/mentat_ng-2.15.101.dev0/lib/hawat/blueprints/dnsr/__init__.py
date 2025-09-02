#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to DNS service. It is implemented upon custom
:py:mod:`mentat.services.dnsr` module.


Provided endpoints
------------------

``/snippet/dnsr/search``
    Endpoint providing API search form for querying DNS service and formatting
    result as JSON document containing HTML snippets.

    * *Authentication:* login required
    * *Authorization:* any role
    * *Methods:* ``GET``, ``POST``
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
from flask_babel import lazy_gettext

import hawat.acl
import hawat.const
import hawat.db
import mentat.services.dnsr
from hawat.base import HawatBlueprint
from hawat.blueprints.dnsr.forms import DnsrSearchForm
from hawat.utils import URLParamsBuilder
from hawat.view import RenderableView
from hawat.view.mixin import SnippetMixin
from mentat.const import tr_

BLUEPRINT_NAME = "dnsr"
"""Name of the blueprint as module global constant."""


class AbstractSearchView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Application view providing base search capabilities for DNS service.

    The resolving is implemented using :py:mod:`mentat.services.dnsr` module.
    """

    authentication = True

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Search DNS")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Search DNS")

    # ---------------------------------------------------------------------------

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = DnsrSearchForm(flask.request.args, meta={"csrf": False})

        if hawat.const.FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data
                dnsr_service = mentat.services.dnsr.service()
                self.response_context.update(search_item=form.search.data, form_data=form_data)
                try:
                    self.response_context.update(search_result=dnsr_service.lookup(form.search.data))
                except Exception as exc:
                    self.flash(str(exc), level="error")

        self.response_context.update(
            search_form=form,
            request_args=flask.request.args,
        )
        return self.generate_response()


class SnippetSearchView(SnippetMixin, AbstractSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying DNS service and presenting the results in the
    form of JSON document containing ready to use HTML page snippets.
    """

    methods = ["GET", "POST"]

    renders = ["label", "full"]

    snippets = [{"name": "hostnames", "condition": lambda x: x.get("search_result", False)}]

    @classmethod
    def get_view_name(cls):
        return "sptsearch"


# -------------------------------------------------------------------------------


class DnsrBlueprint(HawatBlueprint):
    """Pluggable module - DNS service (*dnsr*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("DNS service")

    def register_app(self, app):
        mentat.services.dnsr.init(app.mconfig)

        # Register object additional data services provided by this module.
        app.set_oads(
            hawat.const.AODS_IP4,
            SnippetSearchView,
            URLParamsBuilder({"submit": tr_("Search")}).add_rule("search").add_kwrule("render", False, True),
        )
        app.set_oads(
            hawat.const.AODS_IP6,
            SnippetSearchView,
            URLParamsBuilder({"submit": tr_("Search")}).add_rule("search").add_kwrule("render", False, True),
        )
        app.set_oads(
            hawat.const.AODS_HOSTNAME,
            SnippetSearchView,
            URLParamsBuilder({"submit": tr_("Search")}).add_rule("search").add_kwrule("render", False, True),
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = DnsrBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
    )

    hbp.register_view_class(SnippetSearchView, f"/snippet/{BLUEPRINT_NAME}/search")

    return hbp
