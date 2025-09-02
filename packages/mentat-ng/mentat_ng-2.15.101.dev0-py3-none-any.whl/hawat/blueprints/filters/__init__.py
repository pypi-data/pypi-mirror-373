#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to reporting filter management features. These
features include:

* general reporting filter listing
* detailed reporting filter view
* creating new reporting filters
* updating existing reporting filters
* deleting existing reporting filters
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import sys
import traceback

import flask
import flask_login
import flask_principal
import markupsafe
from flask_babel import gettext, lazy_gettext
from sqlalchemy import and_, not_, nullsfirst, nullslast, or_
from sqlalchemy.exc import NoResultFound

import ipranges
from ransack import Filter, Parser, RansackError

import hawat.acl
import hawat.const
import hawat.db
import hawat.events
import hawat.menu
from hawat.base import HawatBlueprint, PsycopgMixin
from hawat.blueprints.event_classes import get_event_class
from hawat.blueprints.filters.forms import (
    AdminFilterForm,
    BaseFilterForm,
    FilterSearchForm,
    PlaygroundFilterForm,
)
from hawat.view import (
    ItemCreateForView,
    ItemCreateView,
    ItemDeleteView,
    ItemDisableView,
    ItemEnableView,
    ItemListView,
    ItemShowView,
    ItemUpdateView,
    RenderableView,
)
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin
from mentat.const import REPORTING_FILTER_BASIC
from mentat.datatype.sqldb import FilterModel, GroupModel, ItemChangeLogModel
from mentat.idea.internal import Idea

_PARSER = Parser()

BLUEPRINT_NAME = "filters"
"""Name of the blueprint as module global constant."""


def add_ips_rule(ips, section, rules):
    """
    Generates a rule for the given list of ips and for the section (Source/Target),
    and adds this rule to the rules list.
    """
    ip4s = []
    ip6s = []
    rule_ip4 = rule_ip6 = None
    for ipa in ips:
        ipobj = ipranges.from_str(ipa)
        if isinstance(ipobj, (ipranges.IP4, ipranges.IP4Range, ipranges.IP4Net)):
            ip4s.append(ipa)
        else:
            ip6s.append(ipa)
    if ip4s:
        rule_ip4 = section + ".IP4??[] in [{}]".format(",".join(ip4s))
    if ip6s:
        rule_ip6 = section + ".IP6??[] in [{}]".format(",".join(ip6s))
    if rule_ip4 and rule_ip6:
        rules.append(f"({rule_ip4} or {rule_ip6})")
    elif rule_ip4 or rule_ip6:
        rules.append(rule_ip4 if rule_ip4 else rule_ip6)


def add_event_classes_rules(event_classes, rules):
    """
    Generates a rule for the given list of event classes and adds this rule to the rules list.
    """
    # Split the event classes into target-based and source-based.
    source_classes, target_classes = [], []
    for ec in event_classes:
        ec_obj = get_event_class(ec)
        # If no such event class exists, ignore it.
        if ec_obj is None:
            continue
        if ec_obj.is_source_based():
            source_classes.append(ec)
        else:
            target_classes.append(ec)

    if source_classes and target_classes:
        rules.append(
            '(_Mentat.EventClass??[] in ["{}"] or _Mentat.TargetClass??[] in ["{}"])'.format(
                '","'.join(source_classes), '","'.join(target_classes)
            )
        )
    elif source_classes:
        rules.append('_Mentat.EventClass??[] in ["{}"]'.format('","'.join(source_classes)))
    else:
        rules.append('_Mentat.TargetClass??[] in ["{}"]'.format('","'.join(target_classes)))


def process_rule(item):
    """
    Process given event report filtering rule and generate advanced single rule
    string from simple filtering form data.
    """
    if item.type == REPORTING_FILTER_BASIC:
        rules = []
        if item.detectors:
            rules.append('["{}"] in Node.Name??[]'.format('","'.join(item.detectors)))

        if item.categories:
            rules.append('["{}"] in Category'.format('","'.join(item.categories)))

        if item.event_classes:
            add_event_classes_rules(item.event_classes, rules)

        if item.sources:
            add_ips_rule(item.sources, "Source", rules)

        if item.targets:
            add_ips_rule(item.targets, "Target", rules)

        if item.protocols:
            protocols = '","'.join(item.protocols)
            rules.append(f'(["{protocols}"] in Source.Proto??[] or ["{protocols}"] in Target.Proto??[])')

        item.filter = " and ".join(rules)


def to_tree(rule):
    """
    Parse given filtering rule to object tree.
    """
    if rule:
        try:
            return _PARSER.parse(rule)
        except RansackError:
            return None
    return None


def get_success_message(operation_message, **kwargs):
    """
    Returns success message for filter CRUD operations.
    This is to avoid code duplication.
    """
    item_id = markupsafe.escape(str(kwargs["item"]))
    group = kwargs["item"].group
    if not group:
        return gettext(
            "Global reporting filter <strong>%(item_id)s</strong> %(operation_message)s.",
            item_id=item_id,
            operation_message=operation_message,
        )
    return gettext(
        "Reporting filter <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> %(operation_message)s.",
        item_id=item_id,
        parent_id=markupsafe.escape(str(group)),
        operation_message=operation_message,
    )


def get_failure_message(operation_message, with_item_id=True, **kwargs):
    """
    Returns failure message for filter CRUD operations.
    This is to avoid code duplication.
    """
    group = kwargs["item"].group
    if with_item_id:
        item_id = markupsafe.escape(" " + str(kwargs["item"]))
    else:
        item_id = ""
    if not group:
        return gettext(
            "%(operation_message)s global reporting filter<strong>%(item_id)s</strong>.",
            operation_message=operation_message,
            item_id=item_id,
        )
    return gettext(
        "%(operation_message)s reporting filter<strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.",
        operation_message=operation_message,
        item_id=item_id,
        parent_id=markupsafe.escape(str(group)),
    )


def process_and_validate(filter_obj: FilterModel) -> None:
    """
    Generates the actual filtering rule if the 'basic' option is selected,
    then validates the filter expression.

    For advanced filters, validation is assumed to be handled by the form validator.
    Basic filters are expected to be valid, as they are constructed by developers familiar
    with the syntax. However, this function still performs parsing to catch any unexpected
    errors, such as changes in the language syntax or unforeseen issues.
    """
    process_rule(filter_obj)

    try:
        _PARSER.parse(filter_obj.filter)
    except RansackError as e:
        flask.current_app.logger.error(e)


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General reporting filter listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Filter management")

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return FilterModel

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "create",
            endpoint="filters.create",
            resptitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "playground",
            endpoint="filters.playground",
            resptitle=True,
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="filters.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="filters.update",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "disable",
            endpoint="filters.disable",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "enable",
            endpoint="filters.enable",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="filters.delete",
            hidetitle=True,
        )
        return action_menu

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return FilterSearchForm(request_args, meta={"csrf": False})

    @staticmethod
    def build_query(query, model, form_args):
        # Adjust query based on text search string.
        if form_args.get("search"):
            query = query.filter(
                or_(
                    model.name.ilike("%{}%".format(form_args["search"])),
                    model.filter.ilike("%{}%".format(form_args["search"])),
                    model.description.ilike("%{}%".format(form_args["search"])),
                )
            )
        # Adjust query based on lower time boudary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.createtime >= form_args["dt_from"])
        # Adjust query based on upper time boudary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.createtime <= form_args["dt_to"])
        # Adjust query based on item state selection.
        if form_args.get("state"):
            if form_args["state"] == "enabled":
                query = query.filter(model.enabled.is_(True))
            elif form_args["state"] == "disabled":
                query = query.filter(model.enabled.is_(False))
        # Adjust query based on upper time boudary selection.
        if form_args.get("type"):
            query = query.filter(model.type == form_args["type"])
        # Adjust query based on the validity of the filter.
        if form_args.get("validity"):
            if form_args["validity"] == "valid":
                query = query.filter(
                    and_(
                        or_(FilterModel.valid_to.is_(None), not_(FilterModel.is_expired)),
                        or_(
                            FilterModel.valid_from.is_(None),
                            not_(FilterModel.will_be_valid),
                        ),
                    )
                )
            elif form_args["validity"] == "expired":
                query = query.filter(FilterModel.is_expired)
            elif form_args["validity"] == "future":
                query = query.filter(FilterModel.will_be_valid)
        # Adjust query based on what reports is the filter filtering.
        if form_args.get("filtering"):
            if form_args["filtering"] == "source":
                query = query.filter(model.source_based.is_(True))
            elif form_args["filtering"] == "target":
                query = query.filter(model.source_based.is_(False))
        # Adjust query based on user membership selection.
        if form_args.get("group"):
            if form_args["group"] == "_GLOBAL":
                expected_value = None
            else:
                expected_value = int(form_args["group"])
            query = query.filter(model.group_id == expected_value)
        # Adjust query based on number of its hits.
        if form_args.get("hits"):
            query = query.filter(model.hits >= form_args["hits"])
        if form_args.get("sortby"):
            sortmap = {
                "createtime.desc": lambda x, y: x.order_by(y.createtime.desc()),
                "createtime.asc": lambda x, y: x.order_by(y.createtime.asc()),
                "name.desc": lambda x, y: x.order_by(y.name.desc()),
                "name.asc": lambda x, y: x.order_by(y.name.asc()),
                "hits.desc": lambda x, y: x.order_by(y.hits.desc()),
                "hits.asc": lambda x, y: x.order_by(y.hits.asc()),
                "last_hit.desc": lambda x, y: x.order_by(nullslast(y.last_hit.desc())),
                "last_hit.asc": lambda x, y: x.order_by(nullsfirst(y.last_hit.asc())),
            }
            query = sortmap[form_args["sortby"]](query, model)
        return query


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed reporting filter view.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of reporting filter &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show reporting filter details")

    @property
    def dbmodel(self):
        return FilterModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        if kwargs["item"].group is None:
            return hawat.acl.PERMISSION_POWER.can()
        permission_mm = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_mm.can()

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="filters.update",
        )
        action_menu.add_entry(
            "endpoint",
            "disable",
            endpoint="filters.disable",
        )
        action_menu.add_entry(
            "endpoint",
            "enable",
            endpoint="filters.enable",
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="filters.delete",
        )
        action_menu.add_entry(
            "endpoint",
            "playground",
            endpoint="filters.playground",
            url=lambda **x: flask.url_for("filters.playground", filter_id=x["item"].id),
        )
        return action_menu

    def do_before_response(self, **kwargs):
        filter_obj = self.response_context["item"]
        self.response_context.update(filter_tree=to_tree(filter_obj.filter))

        if self.can_access_endpoint("filters.update", item=filter_obj) and self.has_endpoint("changelogs.search"):
            self.response_context.update(
                context_action_menu_changelogs=self.get_endpoint_class("changelogs.search").get_context_action_menu()
            )

            filter_changelogs = (
                self.dbsession.query(ItemChangeLogModel)
                .filter(ItemChangeLogModel.model == filter_obj.__class__.__name__)
                .filter(ItemChangeLogModel.model_id == filter_obj.id)
                .order_by(ItemChangeLogModel.createtime.desc())
                .limit(100)
                .all()
            )
            self.response_context.update(item_changelog=filter_changelogs)


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new reporting filters for any groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create reporting filter")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new reporting filter")

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully created"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to create new"), with_item_id=False, **kwargs)

    @staticmethod
    def get_item_form(item):
        detectors = hawat.events.get_event_detectors()
        categories = hawat.events.get_event_categories()
        protocols = hawat.events.get_event_protocols()

        return AdminFilterForm(
            choices_detectors=list(zip(detectors, detectors)),
            choices_categories=list(zip(categories, categories)),
            choices_protocols=list(zip(protocols, protocols)),
        )

    def do_before_action(self, item):
        process_and_validate(item)

    def do_before_response(self, **kwargs):
        filter_obj = self.response_context.get("item", None)
        if filter_obj:
            self.response_context.update(
                filter_tree=to_tree(filter_obj.filter),
                referrer=self.get_url_cancel(),
            )


class CreateForView(HTMLMixin, SQLAlchemyMixin, ItemCreateForView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new reporting filters for given groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    module_name_par = "groups"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create reporting filter")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Create reporting filter for group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def get_view_url(cls, **kwargs):
        return flask.url_for(cls.get_view_endpoint(), parent_id=kwargs["item"].id)

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new reporting filter for group")

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbmodel_par(self):
        return GroupModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
            hawat.acl.MembershipNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully created"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to create new"), with_item_id=False, **kwargs)

    @staticmethod
    def get_item_form(item):
        detectors = hawat.events.get_event_detectors()
        categories = hawat.events.get_event_categories()
        protocols = hawat.events.get_event_protocols()

        return BaseFilterForm(
            choices_detectors=list(zip(detectors, detectors)),
            choices_categories=list(zip(categories, categories)),
            choices_protocols=list(zip(protocols, protocols)),
        )

    @staticmethod
    def add_parent_to_item(item, parent):
        item.group = parent

    def do_before_action(self, item):
        process_and_validate(item)

    def do_before_response(self, **kwargs):
        filter_obj = self.response_context.get("item", None)
        if filter_obj:
            self.response_context.update(
                filter_tree=to_tree(filter_obj.filter),
                referrer=self.get_url_cancel(),
            )


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing reporting filters.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of reporting filter &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update reporting filter details")

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        if kwargs["item"].group is None:
            return hawat.acl.PERMISSION_POWER.can()
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully updated"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to update"), **kwargs)

    @staticmethod
    def get_item_form(item):
        detectors_available = hawat.events.get_event_detectors()
        detectors = sorted(set(detectors_available).union(item.detectors))
        categories = hawat.events.get_event_categories()
        protocols = hawat.events.get_event_protocols()

        admin = flask_login.current_user.has_role("admin")
        if not admin:
            return BaseFilterForm(
                obj=item,
                choices_detectors=list(zip(detectors, detectors)),
                choices_categories=list(zip(categories, categories)),
                choices_protocols=list(zip(protocols, protocols)),
            )

        return AdminFilterForm(
            obj=item,
            choices_detectors=list(zip(detectors, detectors)),
            choices_categories=list(zip(categories, categories)),
            choices_protocols=list(zip(protocols, protocols)),
        )

    def do_before_action(self, item):
        process_and_validate(item)

    def do_before_response(self, **kwargs):
        filter_obj = self.response_context.get("item", None)
        if filter_obj:
            self.response_context.update(
                filter_tree=to_tree(filter_obj.filter),
                referrer=self.get_url_cancel(),
            )


class EnableView(HTMLMixin, SQLAlchemyMixin, ItemEnableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing reporting filters.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Enable reporting filter &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        if kwargs["item"].group is None:
            return hawat.acl.PERMISSION_POWER.can()
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully enabled"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to enable"), **kwargs)


class DisableView(HTMLMixin, SQLAlchemyMixin, ItemDisableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for disabling existing reporting filters.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Disable reporting filter &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    # ---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        if kwargs["item"].group is None:
            return hawat.acl.PERMISSION_POWER.can()
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully disabled"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to disable"), **kwargs)


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing reporting filters.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Delete reporting filter &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].name),
        )

    @property
    def dbmodel(self):
        return FilterModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        if kwargs["item"].group is None:
            return hawat.acl.PERMISSION_POWER.can()
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return get_success_message(gettext("was successfully and permanently deleted"), **kwargs)

    @staticmethod
    def get_message_failure(**kwargs):
        return get_failure_message(gettext("Unable to permanently delete"), **kwargs)


class PlaygroundView(HTMLMixin, RenderableView, PsycopgMixin):
    """
    Reporting filter playground view.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "playground"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Filter playground")

    @classmethod
    def get_view_icon(cls):
        return "playground"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext("Reporting filter playground")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Reporting filter rule playground")

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "list",
            endpoint="{}.{}".format(cls.module_name, "list"),
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "playground",
            endpoint=cls.get_view_endpoint(),
        )
        return breadcrumbs_menu

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        rule = flask.request.args.get("rule") or ""
        event = ""
        try:
            filter_id = flask.request.args.get("filter_id", default=None)
            if filter_id:
                if not filter_id.isnumeric():
                    self.flash(
                        markupsafe.Markup(gettext("Filter id must be a number.")),
                        hawat.const.FLASH_FAILURE,
                    )
                else:
                    try:
                        filter_obj = hawat.db.db_query(FilterModel).filter(FilterModel.id == filter_id).one().filter
                        if filter_obj:
                            rule = filter_obj
                    except NoResultFound:
                        self.flash(
                            markupsafe.Markup(
                                gettext(
                                    "There is no filter with id <strong>%(id)s</strong>.",
                                    id=filter_id,
                                )
                            ),
                            hawat.const.FLASH_FAILURE,
                        )

            event_id = flask.request.args.get("event_id", default=None)
            if event_id:
                event_obj = self.fetch(event_id)
                if event_obj:
                    event = event_obj.to_json(indent=4, sort_keys=True)
                else:
                    self.flash(
                        markupsafe.Markup(
                            gettext(
                                "There is no event with id <strong>%(id)s</strong>.",
                                id=event_id,
                            )
                        ),
                        hawat.const.FLASH_FAILURE,
                    )

        except Exception as err:  # pylint: disable=locally-disabled,broad-except
            self.flash(
                markupsafe.Markup(gettext("<strong>%(error)s</strong>.", error=str(err))),
                hawat.const.FLASH_FAILURE,
            )

            tbexc = traceback.TracebackException(*sys.exc_info())
            self.response_context.update(filter_exception=err, filter_exception_tb="".join(tbexc.format()))

        form = PlaygroundFilterForm(filter=rule, event=event)
        if form.validate_on_submit():
            form_data = form.data

            try:
                event = Idea.from_json(form.event.data)
                filter_tree = to_tree(form.filter.data)
                filter_result = Filter().eval(filter_tree, event)

                self.response_context.update(
                    form_data=form_data,
                    event=event,
                    filter_tree=filter_tree,
                    filter_result=filter_result,
                    flag_filtered=True,
                )

            except Exception as err:  # pylint: disable=locally-disabled,broad-except
                self.flash(
                    markupsafe.Markup(gettext("<strong>%(error)s</strong>.", error=str(err))),
                    hawat.const.FLASH_FAILURE,
                )

                tbexc = traceback.TracebackException(*sys.exc_info())
                self.response_context.update(filter_exception=err, filter_exception_tb="".join(tbexc.format()))

        self.response_context.update(
            form=form,
        )
        return self.generate_response()


# -------------------------------------------------------------------------------


class FiltersBlueprint(HawatBlueprint):
    """Pluggable module - reporting filter management (*filters*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Reporting filter management pluggable module")

    def register_app(self, app):
        app.menu_main.add_entry(
            "view",
            f"admin.{BLUEPRINT_NAME}",
            position=60,
            view=ListView,
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = FiltersBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(ListView, "/list")
    hbp.register_view_class(CreateView, "/create")
    hbp.register_view_class(CreateForView, "/createfor/<int:parent_id>")
    hbp.register_view_class(ShowView, "/<int:item_id>/show")
    hbp.register_view_class(UpdateView, "/<int:item_id>/update")
    hbp.register_view_class(EnableView, "/<int:item_id>/enable")
    hbp.register_view_class(DisableView, "/<int:item_id>/disable")
    hbp.register_view_class(DeleteView, "/<int:item_id>/delete")
    hbp.register_view_class(PlaygroundView, "/playground")

    return hbp
