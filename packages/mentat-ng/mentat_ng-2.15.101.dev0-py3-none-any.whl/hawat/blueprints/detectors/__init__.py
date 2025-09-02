#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to detectors management features. These
features include:

* general detectors listing
* detailed detector record view
* creating new detector records
* updating existing detector records
* deleting existing detector records
"""

__author__ = "Rajmund Hruška <rajmund.hruska@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)

import markupsafe
from flask_babel import gettext, lazy_gettext
from sqlalchemy import or_

import hawat.acl
import hawat.menu
from hawat.base import HawatBlueprint
from hawat.blueprints.detectors.forms import (
    AdminCreateDetectorForm,
    AdminUpdateDetectorForm,
    DetectorSearchForm,
)
from hawat.utils import URLParamsBuilder
from hawat.view import (
    ItemCreateView,
    ItemDeleteView,
    ItemListView,
    ItemShowView,
    ItemUpdateView,
)
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin
from mentat.const import tr_
from mentat.datatype.sqldb import DetectorModel, ItemChangeLogModel

BLUEPRINT_NAME = "detectors"
"""Name of the blueprint as module global constant."""


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General detector record listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Detector management")

    @property
    def dbmodel(self):
        return DetectorModel

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "create",
            endpoint="detectors.create",
            resptitle=True,
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="detectors.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="detectors.update",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="detectors.delete",
            hidetitle=True,
        )
        return action_menu

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return DetectorSearchForm(
            request_args,
            meta={"csrf": False},
        )

    @staticmethod
    def build_query(query, model, form_args):
        # Adjust query based on text search string.
        if form_args.get("search"):
            query = query.filter(
                or_(
                    model.name.ilike("%{}%".format(form_args["search"])),
                    model.description.ilike("%{}%".format(form_args["search"])),
                )
            )
        # Adjust query based on lower time boudary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.createtime >= form_args["dt_from"])
        # Adjust query based on upper time boudary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.createtime <= form_args["dt_to"])
        # Adjust query based on record source selection.
        if form_args.get("source"):
            query = query.filter(model.source == form_args["source"])
        if form_args.get("sortby"):
            sortmap = {
                "createtime.desc": lambda x, y: x.order_by(y.createtime.desc()),
                "createtime.asc": lambda x, y: x.order_by(y.createtime.asc()),
                "name.desc": lambda x, y: x.order_by(y.name.desc()),
                "name.asc": lambda x, y: x.order_by(y.name.asc()),
                "hits.desc": lambda x, y: x.order_by(y.hits.desc()),
                "hits.asc": lambda x, y: x.order_by(y.hits.asc()),
                "credibility.desc": lambda x, y: x.order_by(y.credibility.desc()),
                "credibility.asc": lambda x, y: x.order_by(y.credibility.asc()),
            }
            query = sortmap[form_args["sortby"]](query, model)
        return query


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed detector record view.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of detector record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show detector record details")

    @property
    def dbmodel(self):
        return DetectorModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()

        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="detectors.update",
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="detectors.delete",
        )

        return action_menu

    def do_before_response(self, **kwargs):
        item = self.response_context["item"]
        if self.can_access_endpoint("detectors.update", item=item) and self.has_endpoint("changelogs.search"):
            self.response_context.update(
                context_action_menu_changelogs=self.get_endpoint_class("changelogs.search").get_context_action_menu()
            )

            item_changelog = (
                self.dbsession.query(ItemChangeLogModel)
                .filter(ItemChangeLogModel.model == item.__class__.__name__)
                .filter(ItemChangeLogModel.model_id == item.id)
                .order_by(ItemChangeLogModel.createtime.desc())
                .limit(100)
                .all()
            )
            self.response_context.update(item_changelog=item_changelog)


class ShowByNameView(ShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed detector view by detector name.
    """

    @classmethod
    def get_view_name(cls):
        return "show_by_name"

    @classmethod
    def get_view_template(cls):
        return f"{cls.module_name}/show.html"

    @property
    def search_by(self):
        return self.dbmodel.name


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new detector records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create detector record")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new detector record")

    @property
    def dbmodel(self):
        return DetectorModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Detector record <strong>%(item_id)s</strong> was successfully created.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext("Unable to create new detector record.")

    @staticmethod
    def get_item_form(item):
        return AdminCreateDetectorForm()

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing detector records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of detector record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update detector record details")

    @property
    def dbmodel(self):
        return DetectorModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Detector record <strong>%(item_id)s</strong> was successfully updated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to update detector record <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_item_form(item):
        return AdminUpdateDetectorForm(db_item_id=item.id, obj=item)

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing detector records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Delete detector record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @property
    def dbmodel(self):
        return DetectorModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Detector record <strong>%(item_id)s</strong> was successfully deleted.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to delete detector record <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )


# -------------------------------------------------------------------------------


class DetectorsBlueprint(HawatBlueprint):
    """Pluggable module - detector management (*detectors*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Detector management")

    def register_app(self, app):
        app.menu_main.add_entry("view", f"admin.{BLUEPRINT_NAME}", position=71, view=ListView)

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.CSAG_DETECTOR,
            tr_("View detector details"),
            ShowByNameView,
            URLParamsBuilder().add_rule("item_id"),
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = DetectorsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(ListView, "/list")
    hbp.register_view_class(CreateView, "/create")
    hbp.register_view_class(ShowView, "/<int:item_id>/show")
    hbp.register_view_class(ShowByNameView, "/<item_id>/show_by_name")
    hbp.register_view_class(UpdateView, "/<int:item_id>/update")
    hbp.register_view_class(DeleteView, "/<int:item_id>/delete")

    return hbp
