#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to item changelogs.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
from flask_babel import lazy_gettext
from sqlalchemy import or_

import hawat.acl
import hawat.const
import hawat.menu
from hawat.base import HawatBlueprint
from hawat.blueprints.changelogs.forms import ItemChangeLogSearchForm
from hawat.view import BaseSearchView, ItemShowView
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin

BLUEPRINT_NAME = "changelogs"
"""Name of the blueprint as module global constant."""


class SearchView(HTMLMixin, SQLAlchemyMixin, BaseSearchView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    General item changelog record listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Changelogs")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Search item changelogs")

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_search_form(request_args):
        return ItemChangeLogSearchForm(request_args, meta={"csrf": False})

    @staticmethod
    def build_query(query, model, form_args):
        # Adjust query based on lower time boundary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.createtime >= form_args["dt_from"])
        # Adjust query based on upper time boundary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.createtime <= form_args["dt_to"])
        # Adjust query based on changelog author selection.
        if form_args.get("authors"):
            if "__SYSTEM__" in form_args["authors"]:
                query = query.filter(
                    or_(
                        model.author_id.is_(None),
                        model.author_id.in_([x.id for x in form_args["authors"] if x != "__SYSTEM__"]),
                    )
                )
            else:
                query = query.filter(model.author_id.in_([x.id for x in form_args["authors"]]))
        # Adjust query based on changelog operation selection.
        if form_args.get("operations"):
            query = query.filter(model.operation.in_(form_args["operations"]))
        # Adjust query based on changelog model selection.
        if form_args.get("imodel"):
            query = query.filter(model.model == form_args["imodel"])
        # Adjust query based on changelog model ID selection.
        if form_args.get("imodel_id"):
            query = query.filter(model.model_id == form_args["imodel_id"])

        # Return the result sorted by creation time in descending order.
        return query.order_by(model.createtime.desc())

    @classmethod
    def get_context_action_menu(cls):
        context_action_menu = super().get_context_action_menu()
        context_action_menu.add_entry(
            "submenu",
            "more",
            align_right=True,
            legend=lazy_gettext("More actions"),
        )
        context_action_menu.add_entry(
            "endpoint",
            "more.searchauthor",
            endpoint="changelogs.search",
            title=lazy_gettext("Other changes by the same author"),
            url=lambda **x: flask.url_for(
                "changelogs.search",
                authors=x["item"].author or "__SYSTEM__",
                dt_from="",
                submit="Search",
            ),
            icon="action-search",
            hidelegend=True,
        )
        context_action_menu.add_entry(
            "endpoint",
            "more.searchmodel",
            endpoint="changelogs.search",
            title=lazy_gettext("Other changes of the same item"),
            url=lambda **x: flask.url_for(
                "changelogs.search",
                imodel=x["item"].model,
                imodel_id=x["item"].model_id,
                dt_from="",
                submit="Search",
            ),
            icon="action-search",
            hidelegend=True,
        )
        context_action_menu.add_entry(
            "endpoint",
            "more.searchboth",
            endpoint="changelogs.search",
            title=lazy_gettext("Other changes of the same item by the same author"),
            url=lambda **x: flask.url_for(
                "changelogs.search",
                authors=x["item"].author or "__SYSTEM__",
                imodel=x["item"].model,
                imodel_id=x["item"].model_id,
                dt_from="",
                submit="Search",
            ),
            icon="action-search",
            hidelegend=True,
        )
        return context_action_menu


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed network record view.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Show item changelog record")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of item changelog record &quot;%(item)s&quot;",
            item=str(kwargs["item"]),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show item changelog record details")

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @classmethod
    def get_breadcrumbs_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        action_menu.add_entry(
            "endpoint",
            "search",
            endpoint=f"{cls.module_name}.search",
        )
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint=f"{cls.module_name}.show",
        )
        return action_menu


# -------------------------------------------------------------------------------


class ItemChangeLogsBlueprint(HawatBlueprint):
    """Pluggable module - item changelog record management (*changelogs*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Item changelog record management")

    def register_app(self, app):
        app.menu_main.add_entry(
            "view",
            f"admin.{BLUEPRINT_NAME}",
            position=80,
            view=SearchView,
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = ItemChangeLogsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(SearchView, "/search")
    hbp.register_view_class(ShowView, "/<int:item_id>/show")

    return hbp
