#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides features to manage event classes. These
features include:

* general event classes listing
* detailed event class view
* creating new event classes
* updating existing event classes
* deleting existing event classes
"""

__author__ = "Jakub Judiny <jakub.judiny@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)

from typing import Any, cast

import flask
import markupsafe
from flask_babel import gettext, lazy_gettext
from sqlalchemy import or_

from ransack import Parser, RansackError

import hawat.acl
import hawat.db
import hawat.events
import hawat.menu
from hawat.base import HawatBlueprint
from hawat.blueprints.event_classes.forms import (
    CreateEventClassForm,
    EventClassSearchForm,
    UpdateEventClassForm,
)
from hawat.const import tr_
from hawat.utils import URLParamsBuilder
from hawat.view import (
    ItemCreateView,
    ItemDeleteView,
    ItemListView,
    ItemShowView,
    ItemUpdateView,
)
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin
from mentat.datatype.sqldb import EventClassModel, EventClassState, ItemChangeLogModel

_PARSER = Parser()

BLUEPRINT_NAME = "event_classes"
"""Name of the blueprint as module global constant."""


def get_event_class(name: str) -> EventClassModel:
    """
    Returns event class with the given name,
    or None if there is no such event class.
    """
    # Get event class name from whole class. (whole class = event_class/subclass)
    if "/" in name:
        name = name.split("/")[0]
    return cast(
        EventClassModel,
        hawat.db.db_get().session.query(EventClassModel).filter(EventClassModel.name == name).one_or_none(),
    )


def to_tree(rule: str) -> Any:
    """
    Parse given filtering rule to object tree.
    """
    if rule:
        try:
            return _PARSER.parse(rule)
        except RansackError:
            return None
    return None


def validate_syntax(event_class_obj: EventClassModel) -> None:
    """
    Validates the rule used to assign the event_class.

    Validation is assumed to be handled by the form validator. However, this function still performs
    parsing to catch any unexpected errors, such as changes in the language syntax or unforeseen issues.
    """
    try:
        _PARSER.parse(event_class_obj.rule)
        if event_class_obj.subclassing:
            _PARSER.parse(event_class_obj.subclassing)
    except RansackError as e:
        flask.current_app.logger.error(e)


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General event classes listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    has_help = True

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Event class management")

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return EventClassModel

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "create",
            endpoint="event_classes.create",
            resptitle=True,
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="event_classes.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="event_classes.update",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="event_classes.delete",
            hidetitle=True,
        )
        return action_menu

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return EventClassSearchForm(
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
                    model.rule.ilike("%{}%".format(form_args["search"])),
                    model.label_en.ilike("%{}%".format(form_args["search"])),
                    model.label_cz.ilike("%{}%".format(form_args["search"])),
                )
            )
        # Adjust query based on lower time boundary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.createtime >= form_args["dt_from"])
        # Adjust query based on upper time boundary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.createtime <= form_args["dt_to"])
        # Adjust query based on item state selection.
        if form_args.get("state") and form_args["state"] in list(EventClassState):
            query = query.filter(model.state == form_args["state"])
        # Adjust query based on upper time boundary selection.
        if form_args.get("severity"):
            query = query.filter(model.severity == form_args["severity"])
        # Adjust query based on subclassing.
        if "type" in form_args and form_args["type"] is not None and form_args["type"] != "":
            query = query.filter(model.source_based.is_(form_args["type"].lower() == "source-based"))
        if form_args.get("sortby"):
            sortmap = {
                "createtime.desc": lambda x, y: x.order_by(y.createtime.desc()),
                "createtime.asc": lambda x, y: x.order_by(y.createtime.asc()),
                "name.desc": lambda x, y: x.order_by(y.name.desc()),
                "name.asc": lambda x, y: x.order_by(y.name.asc()),
            }
            query = sortmap[form_args["sortby"]](query, model)
        return query


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed event class view.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    has_help = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of event class &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show event class details")

    @property
    def dbmodel(self):
        return EventClassModel

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="event_classes.update",
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="event_classes.delete",
        )
        action_menu.add_entry(
            "endpoint",
            "playground",
            endpoint="filters.playground",
            url=lambda **x: flask.url_for("filters.playground", rule=x["item"].rule),
        )
        action_menu.add_entry(
            "endpoint",
            "related_events",
            title="Search events",
            endpoint="events.search",
            url=lambda **x: flask.url_for("events.search", classes=x["item"].name.lower(), submit=tr_("Search"))
            if x["item"].is_source_based()
            else flask.url_for(
                "events.search",
                target_classes=x["item"].name.lower(),
                submit=tr_("Search"),
            ),
        )
        return action_menu

    def do_before_response(self, **kwargs):
        item = self.response_context["item"]
        self.response_context.update(
            filter_tree=to_tree(item.rule),
        )

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
    Detailed event class view by event class name.
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
    View for creating new event classes.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    has_help = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create event class")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new event classes")

    @property
    def dbmodel(self):
        return EventClassModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Event class <strong>%(item_id)s</strong> was successfully created.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext("Unable to create new event class.")

    @staticmethod
    def get_item_form(item):
        return CreateEventClassForm()

    def do_before_action(self, item):
        validate_syntax(item)

    def do_before_response(self, **kwargs):
        item = self.response_context.get("item", None)
        if item:
            self.response_context.update(
                filter_tree=to_tree(item.rule),
                referrer=self.get_url_cancel(),
            )


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing event classes.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    has_help = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of event class &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update event class details")

    @property
    def dbmodel(self):
        return EventClassModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Event class <strong>%(item_id)s</strong> was successfully updated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to update event class <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_item_form(item):
        return UpdateEventClassForm(obj=item)

    def do_before_action(self, item):
        validate_syntax(item)

    def do_before_response(self, **kwargs):
        item = self.response_context["item"]
        self.response_context.update(
            filter_tree=to_tree(item.rule),
            referrer=self.get_url_cancel(),
        )


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing event classes.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    has_help = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Delete event class &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @property
    def dbmodel(self):
        return EventClassModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Event class <strong>%(item_id)s</strong> was successfully and permanently deleted.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to permanently delete event class <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )


# -------------------------------------------------------------------------------


class EventClassesBlueprint(HawatBlueprint):
    """Pluggable module - event class management (*event_classes*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Event class management pluggable module")

    def register_app(self, app):
        app.menu_main.add_entry("view", f"admin.{BLUEPRINT_NAME}", position=55, view=ListView)

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.CSAG_CLASS,
            tr_("View event class details"),
            ShowByNameView,
            URLParamsBuilder().add_rule("item_id"),
        )


# -------------------------------------------------------------------------------


def get_blueprint() -> EventClassesBlueprint:
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = EventClassesBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(ListView, "/list")
    hbp.register_view_class(CreateView, "/create")
    hbp.register_view_class(ShowView, "/<int:item_id>/show")
    hbp.register_view_class(ShowByNameView, "/<item_id>/show")
    hbp.register_view_class(UpdateView, "/<int:item_id>/update")
    hbp.register_view_class(DeleteView, "/<int:item_id>/delete")

    return hbp
