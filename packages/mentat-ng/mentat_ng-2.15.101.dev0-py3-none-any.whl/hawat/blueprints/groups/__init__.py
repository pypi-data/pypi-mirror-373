#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This file contains pluggable module for Hawat web interface containing features
related to user group management. These features include:

* general group listing
* detailed group view
* creating new groups
* updating existing groups
* deleting existing groups
* enabling existing groups
* disabling existing groups
* adding group members
* removing group members
* rejecting group membership requests
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib

import flask
import flask_login
import flask_principal
import markupsafe
from flask_babel import gettext, lazy_gettext
from sqlalchemy import and_, func, or_

import hawat.acl
import hawat.const
import hawat.menu
from hawat.base import HawatBlueprint
from hawat.blueprints.groups.forms import (
    EMPTY,
    AdminCreateGroupForm,
    AdminUpdateGroupForm,
    GroupSearchForm,
    MaintainerUpdateGroupForm,
    UpdateGroupForm,
)
from hawat.utils import URLParamsBuilder
from hawat.view import (
    ItemCreateView,
    ItemDeleteView,
    ItemDisableView,
    ItemEnableView,
    ItemListView,
    ItemObjectRelationView,
    ItemShowView,
    ItemUpdateView,
)
from hawat.view.mixin import AJAXMixin, HTMLMixin, SQLAlchemyMixin
from mentat.const import tr_
from mentat.datatype.sqldb import (
    FilterModel,
    ItemChangeLogModel,
    NetworkModel,
    SettingsReportingModel,
)

BLUEPRINT_NAME = "groups"
"""Name of the blueprint as module global constant."""


class AbstractListView(SQLAlchemyMixin, ItemListView):
    """
    Abstract group listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return GroupSearchForm(request_args, meta={"csrf": False})

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
        # Adjust query based on lower time boundary selection.
        if form_args.get("dt_from"):
            query = query.filter(model.createtime >= form_args["dt_from"])
        # Adjust query based on upper time boundary selection.
        if form_args.get("dt_to"):
            query = query.filter(model.createtime <= form_args["dt_to"])
        # Adjust query based on user state selection.
        if form_args.get("state"):
            if form_args["state"] == "enabled":
                query = query.filter(model.enabled.is_(True))
            elif form_args["state"] == "disabled":
                query = query.filter(model.enabled.is_(False))
        # Adjust query based on record source selection.
        if form_args.get("source"):
            query = query.filter(model.source == form_args["source"])
        # Adjust query based on user membership selection.
        if form_args.get("member"):
            if form_args["member"] == EMPTY:
                query = query.filter(~model.members.any())
            else:
                query = query.filter(model.members.any(id=int(form_args["member"])))
        # Adjust query based on user management selection.
        if form_args.get("manager"):
            if form_args["manager"] == EMPTY:
                query = query.filter(~model.managers.any())
            else:
                query = query.filter(model.managers.any(id=int(form_args["manager"])))

        if form_args.get("sortby"):
            sortmap = {
                "createtime.desc": lambda x, y: x.order_by(y.createtime.desc()),
                "createtime.asc": lambda x, y: x.order_by(y.createtime.asc()),
                "name.desc": lambda x, y: x.order_by(y.name.desc()),
                "name.asc": lambda x, y: x.order_by(y.name.asc()),
                "network_count.desc": lambda x, y: (
                    x.outerjoin(y.networks).group_by(y.id).order_by(func.count(y.networks).desc())  # pylint: disable=locally-disabled,not-callable
                ),
                "network_count.asc": lambda x, y: (
                    x.outerjoin(y.networks).group_by(y.id).order_by(func.count(y.networks).asc())  # pylint: disable=locally-disabled,not-callable
                ),
            }
            query = sortmap[form_args["sortby"]](query, model)
        return query


class ListView(HTMLMixin, AbstractListView):
    """
    General group listing.
    """

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Group management")

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "create",
            endpoint="groups.create",
            resptitle=True,
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="groups.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="groups.update",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "disable",
            endpoint="groups.disable",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "enable",
            endpoint="groups.enable",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="groups.delete",
            hidetitle=True,
        )
        return action_menu


class APIListView(AJAXMixin, AbstractListView):
    """
    General group listing for API.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_name(cls):
        return "apilist"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Group list")

    def get_blocked_response_context_keys(self):
        return super().get_blocked_response_context_keys() + ["form"]


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed group view.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        if isinstance(kwargs["item"], cls.get_model(hawat.const.MODEL_GROUP)):
            return lazy_gettext(
                "View details of group &quot;%(item)s&quot;",
                item=markupsafe.escape(str(kwargs["item"])),
            )
        return lazy_gettext(
            "View details of group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"].group)),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show group details")

    @classmethod
    def get_view_url(cls, **kwargs):
        if isinstance(kwargs["item"], cls.get_model(hawat.const.MODEL_GROUP)):
            return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"].get_id())
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"].group.get_id())

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_mm = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs["item"].id),
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_mm.can()

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="groups.update",
            resptitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "disable",
            endpoint="groups.disable",
            resptitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "enable",
            endpoint="groups.enable",
            resptitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="groups.delete",
            resptitle=True,
        )
        return action_menu

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="users.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "submenu",
            "more",
            align_right=True,
            legend=gettext("More actions"),
        )
        action_menu.add_entry(
            "endpoint",
            "more.add_membership",
            endpoint="users.addmembership",
        )
        action_menu.add_entry(
            "endpoint",
            "more.reject_membership",
            endpoint="users.rejectmembership",
        )
        action_menu.add_entry(
            "endpoint",
            "more.remove_membership",
            endpoint="users.removemembership",
        )
        action_menu.add_entry(
            "endpoint",
            "more.add_management",
            endpoint="users.addmanagement",
        )
        action_menu.add_entry(
            "endpoint",
            "more.remove_management",
            endpoint="users.removemanagement",
        )
        action_menu.add_entry(
            "endpoint",
            "more.enable",
            endpoint="users.enable",
        )
        action_menu.add_entry(
            "endpoint",
            "more.disable",
            endpoint="users.disable",
        )
        action_menu.add_entry(
            "endpoint",
            "more.update",
            endpoint="users.update",
        )
        self.response_context.update(context_action_menu_users=action_menu)

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="networks.show",
            hidetitle=True,
        )
        self.response_context.update(context_action_menu_networks=action_menu)

        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="filters.show",
            hidetitle=True,
        )
        self.response_context.update(context_action_menu_filters=action_menu)

        item = self.response_context["item"]
        if self.can_access_endpoint("groups.update", item=item) and self.has_endpoint("changelogs.search"):
            self.response_context.update(
                context_action_menu_changelogs=self.get_endpoint_class("changelogs.search").get_context_action_menu()
            )

            item_changelog = (
                self.dbsession.query(ItemChangeLogModel)
                .filter(
                    or_(
                        # Changelogs related directly to group item.
                        and_(
                            ItemChangeLogModel.model == item.__class__.__name__,
                            ItemChangeLogModel.model_id == item.id,
                        ),
                        # Changelogs related to group reporting settings item.
                        and_(
                            ItemChangeLogModel.model == SettingsReportingModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(SettingsReportingModel.id).filter(
                                    SettingsReportingModel.group_id == item.id
                                )
                            ),
                        ),
                        # Changelogs related to all group reporting filters.
                        and_(
                            ItemChangeLogModel.model == FilterModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(FilterModel.id).filter(FilterModel.group_id == item.id)
                            ),
                        ),
                        # Changelogs related to all group network records.
                        and_(
                            ItemChangeLogModel.model == NetworkModel.__name__,
                            ItemChangeLogModel.model_id.in_(
                                self.dbsession.query(NetworkModel.id).filter(NetworkModel.group_id == item.id)
                            ),
                        ),
                    )
                )
                .order_by(ItemChangeLogModel.createtime.desc())
                .limit(100)
                .all()
            )
            self.response_context.update(item_changelog=item_changelog)


class ShowByNameView(ShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed group view by group name.
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
    View for creating new groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create group")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new group")

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Group <strong>%(item_id)s</strong> was successfully created.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext("Unable to create new group.")

    @staticmethod
    def get_item_form(item):
        return AdminCreateGroupForm()

    def do_before_action(self, item):
        # Create empty reporting settings object and assign it to the group.
        SettingsReportingModel(group=item)

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Update")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update group details")

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Group <strong>%(item_id)s</strong> was successfully updated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to update group <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_item_form(item):
        if flask_login.current_user.has_role("admin"):
            return AdminUpdateGroupForm(db_item_id=item.id, obj=item)
        if flask_login.current_user.has_role("maintainer"):
            return MaintainerUpdateGroupForm(obj=item)
        return UpdateGroupForm(obj=item)

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class AddMemberView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for adding group members.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "addmember"

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Add group member")

    @classmethod
    def get_view_icon(cls):
        return "action-add-member"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Add user &quot;%(user_id)s&quot; to group &quot;%(group_id)s&quot;",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def dbmodel_other(self):
        return self.get_model(hawat.const.MODEL_USER)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        # Reject item change in case given item is already enabled.
        return kwargs["other"] not in kwargs["item"].members

    @classmethod
    def change_item(cls, **kwargs):
        kwargs["item"].members.append(kwargs["other"])
        if kwargs["other"].is_state_disabled():
            kwargs["other"].set_state_enabled()
            flask.current_app.send_infomail(
                "users.enable",
                account=kwargs["other"],
            )

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User <strong>%(user_id)s</strong> was successfully added as a member to group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to add user <strong>%(user_id)s</strong> as a member to group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )


class RejectMemberView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for rejecting group membership reuests.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "rejectmember"

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Reject group member")

    @classmethod
    def get_view_icon(cls):
        return "action-rej-member"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Reject user`s &quot;%(user_id)s&quot; membership request for group &quot;%(group_id)s&quot;",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def dbmodel_other(self):
        return self.get_model(hawat.const.MODEL_USER)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        # Reject item change in case given item is already enabled.
        return kwargs["other"] in kwargs["item"].members_wanted

    @classmethod
    def change_item(cls, **kwargs):
        kwargs["item"].members_wanted.remove(kwargs["other"])

    # ---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User`s <strong>%(user_id)s</strong> membership request for group <strong>%(group_id)s</strong> was successfully rejected.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to reject user`s <strong>%(user_id)s</strong> membership request for group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )


class RemoveMemberView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for removing group members.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "removemember"

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Remove group member")

    @classmethod
    def get_view_icon(cls):
        return "action-rem-member"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Remove user &quot;%(user_id)s&quot; from group &quot;%(group_id)s&quot;",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def dbmodel_other(self):
        return self.get_model(hawat.const.MODEL_USER)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        # Reject item change in case given item is already enabled.
        return kwargs["other"] in kwargs["item"].members

    @classmethod
    def change_item(cls, **kwargs):
        kwargs["item"].members.remove(kwargs["other"])

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User <strong>%(user_id)s</strong> was successfully removed as a member from group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to remove user <strong>%(user_id)s</strong> as a member from group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )


class AddManagerView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for adding group managers.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "addmanager"

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Add group manager")

    @classmethod
    def get_view_icon(cls):
        return "action-add-manager"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Add user &quot;%(user_id)s&quot; to group &quot;%(group_id)s&quot; as manager",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def dbmodel_other(self):
        return self.get_model(hawat.const.MODEL_USER)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        # Reject item change in case given item is already manager.
        return kwargs["other"] not in kwargs["item"].managers

    @classmethod
    def change_item(cls, **kwargs):
        kwargs["item"].managers.append(kwargs["other"])
        if kwargs["other"].is_state_disabled():
            kwargs["other"].set_state_enabled()
            flask.current_app.send_infomail(
                "users.enable",
                account=kwargs["other"],
            )

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User <strong>%(user_id)s</strong> was successfully added as a manager to group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to add user <strong>%(user_id)s</strong> as a manager to group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )


class RemoveManagerView(HTMLMixin, SQLAlchemyMixin, ItemObjectRelationView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for removing group managers.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "removemanager"

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Remove group manager")

    @classmethod
    def get_view_icon(cls):
        return "action-rem-manager"

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Remove user &quot;%(user_id)s&quot; from group &quot;%(group_id)s&quot; as manager",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def dbmodel_other(self):
        return self.get_model(hawat.const.MODEL_USER)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.ManagementNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        # Reject item change in case given item is not already manager.
        return kwargs["other"] in kwargs["item"].managers

    @classmethod
    def change_item(cls, **kwargs):
        with contextlib.suppress(ValueError):
            kwargs["item"].managers.remove(kwargs["other"])

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User <strong>%(user_id)s</strong> was successfully removed as a manager from group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to remove user <strong>%(user_id)s</strong> as a manager from group <strong>%(group_id)s</strong>.",
            user_id=markupsafe.escape(str(kwargs["other"])),
            group_id=markupsafe.escape(str(kwargs["item"])),
        )


class EnableView(HTMLMixin, SQLAlchemyMixin, ItemEnableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Enable group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Group <strong>%(item_id)s</strong> was successfully enabled.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to enable group <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )


class DisableView(HTMLMixin, SQLAlchemyMixin, ItemDisableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for disabling groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Disable group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Group <strong>%(item_id)s</strong> was successfully disabled.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to disable group <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing groups.
    """

    methods = ["GET", "POST"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_ADMIN]

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Delete group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_GROUP)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Group <strong>%(item_id)s</strong> was successfully and permanently deleted.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to delete group <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )


# -------------------------------------------------------------------------------


class GroupsBlueprint(HawatBlueprint):
    """Pluggable module - user groups (*groups*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Group management")

    def register_app(self, app):
        def _fetch_my_groups():
            groups = {}
            for i in list(flask_login.current_user.memberships) + list(flask_login.current_user.managements):
                groups[str(i)] = i
            return sorted(groups.values(), key=str)

        app.menu_main.add_entry(
            "view",
            f"admin.{BLUEPRINT_NAME}",
            position=50,
            view=ListView,
        )
        app.menu_auth.add_entry(
            "submenudb",
            "my_groups",
            position=20,
            title=lazy_gettext("My groups"),
            resptitle=True,
            icon="module-groups",
            align_right=True,
            entry_fetcher=_fetch_my_groups,
            entry_builder=lambda x, y: hawat.menu.EndpointEntry(
                x,
                endpoint="groups.show",
                params={"item": y},
                title=x,
                icon="module-groups",
            ),
        )

        # Register context actions provided by this module.
        app.set_csag(
            hawat.const.CSAG_ABUSE,
            tr_("View group details"),
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

    hbp = GroupsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
    )

    hbp.register_view_class(ListView, f"/{BLUEPRINT_NAME}/list")
    hbp.register_view_class(CreateView, f"/{BLUEPRINT_NAME}/create")
    hbp.register_view_class(ShowView, f"/{BLUEPRINT_NAME}/<int:item_id>/show")
    hbp.register_view_class(ShowByNameView, f"/{BLUEPRINT_NAME}/<item_id>/show_by_name")
    hbp.register_view_class(UpdateView, f"/{BLUEPRINT_NAME}/<int:item_id>/update")
    hbp.register_view_class(AddMemberView, f"/{BLUEPRINT_NAME}/<int:item_id>/add_member/<int:other_id>")
    hbp.register_view_class(
        RejectMemberView,
        f"/{BLUEPRINT_NAME}/<int:item_id>/reject_member/<int:other_id>",
    )
    hbp.register_view_class(
        RemoveMemberView,
        f"/{BLUEPRINT_NAME}/<int:item_id>/remove_member/<int:other_id>",
    )
    hbp.register_view_class(AddManagerView, f"/{BLUEPRINT_NAME}/<int:item_id>/add_manager/<int:other_id>")
    hbp.register_view_class(
        RemoveManagerView,
        f"/{BLUEPRINT_NAME}/<int:item_id>/remove_manager/<int:other_id>",
    )
    hbp.register_view_class(EnableView, f"/{BLUEPRINT_NAME}/<int:item_id>/enable")
    hbp.register_view_class(DisableView, f"/{BLUEPRINT_NAME}/<int:item_id>/disable")
    hbp.register_view_class(DeleteView, f"/{BLUEPRINT_NAME}/<int:item_id>/delete")
    hbp.register_view_class(APIListView, f"/api/{BLUEPRINT_NAME}/list")

    return hbp
