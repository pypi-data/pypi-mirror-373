#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to network record management features. These
features include:

* general network record listing
* network resolving using whois service
* detailed network record view
* creating new network records
* updating existing network records
* deleting existing network records
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
import flask_login
import flask_principal
import markupsafe
from flask_babel import gettext, lazy_gettext
from sqlalchemy import or_, text

from ipranges import IP4, IP6, IP4Net, IP4Range, from_str

import hawat.acl
import hawat.const
import hawat.menu
import mentat.services.whois
from hawat.base import HawatBlueprint
from hawat.blueprints.networks.forms import (
    AdminNetworkForm,
    BaseNetworkForm,
    MaintainerNetworkForm,
    NetworkResolverSearchForm,
    NetworkSearchForm,
)
from hawat.utils import URLParamsBuilder
from hawat.view import (
    ItemCreateForView,
    ItemCreateView,
    ItemDeleteView,
    ItemListView,
    ItemShowView,
    ItemUpdateView,
    RenderableView,
    SimpleView,
)
from hawat.view.mixin import AJAXMixin, HTMLMixin, SnippetMixin, SQLAlchemyMixin
from mentat.const import tr_
from mentat.datatype.sqldb import GroupModel, ItemChangeLogModel, NetworkModel

BLUEPRINT_NAME = "networks"
"""Name of the blueprint as module global constant."""


class ListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General network record listing.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Network management")

    @property
    def dbmodel(self):
        return NetworkModel

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "create",
            endpoint="networks.create",
            resptitle=True,
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint="networks.show",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="networks.update",
            hidetitle=True,
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="networks.delete",
            hidetitle=True,
        )
        return action_menu

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return NetworkSearchForm(
            request_args,
            meta={"csrf": False},
        )

    @staticmethod
    def build_query(query, model, form_args):
        # Adjust query based on text search string.
        if form_args.get("search"):
            # First of all, assume the user entered address/net/range.
            try:
                # Convert user input to ipranges object.
                net = from_str(form_args["search"])
                # 'a >>= b' means:  a contains b or is equal to b
                # So search for networks which contain the address/net/range from the user input.
                # Also, the user input is converted to range to solve issues with addresses such as 195.113.144.1/24
                query = query.filter(text(f"network >>= '{net.single(net.low())}-{net.single(net.high())}'"))
            except ValueError:
                # Try searching by the name of the network or the description.
                query = query.filter(
                    or_(
                        model.netname.ilike("%{}%".format(form_args["search"])),
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
        # Adjust query based on user membership selection.
        if form_args.get("group"):
            query = query.filter(model.group_id == int(form_args["group"]))
        if form_args.get("sortby"):
            sortmap = {
                "createtime.desc": lambda x, y: x.order_by(y.createtime.desc()),
                "createtime.asc": lambda x, y: x.order_by(y.createtime.asc()),
                "netname.desc": lambda x, y: x.order_by(y.netname.desc()),
                "netname.asc": lambda x, y: x.order_by(y.netname.asc()),
                "network.desc": lambda x, y: x.order_by(y.network.desc()),
                "network.asc": lambda x, y: x.order_by(y.network.asc()),
                "rank.desc": lambda x, y: x.order_by(y.rank.desc()),
                "rank.asc": lambda x, y: x.order_by(y.rank.asc()),
            }
            query = sortmap[form_args["sortby"]](query, model)
        return query


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed network record view.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "View details of network record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].netname),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show network record details")

    @property
    def dbmodel(self):
        return NetworkModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
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
            endpoint="networks.update",
        )
        action_menu.add_entry(
            "endpoint",
            "delete",
            endpoint="networks.delete",
        )

        return action_menu

    def do_before_response(self, **kwargs):
        item = self.response_context["item"]
        if self.can_access_endpoint("networks.update", item=item) and self.has_endpoint("changelogs.search"):
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


class CreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new network records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create network record")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new network record")

    @property
    def dbmodel(self):
        return NetworkModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully created.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to create new network record for group <strong>%(parent_id)s</strong>.",
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_item_form(item):
        return AdminNetworkForm()

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class CreateForView(HTMLMixin, SQLAlchemyMixin, ItemCreateForView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new network records.
    """

    methods = ["GET", "POST"]

    authentication = True

    module_name_par = "groups"

    @classmethod
    def get_view_icon(cls):
        return f"module-{BLUEPRINT_NAME}"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Create network record")

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Create network record for group &quot;%(item)s&quot;",
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def get_view_url(cls, **kwargs):
        return flask.url_for(cls.get_view_endpoint(), parent_id=kwargs["item"].id)

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Create new network record for group")

    @property
    def dbmodel(self):
        return NetworkModel

    @property
    def dbmodel_par(self):
        return GroupModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully created.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["parent"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to create new network record for group <strong>%(parent_id)s</strong>.",
            parent_id=markupsafe.escape(str(kwargs["parent"])),
        )

    @staticmethod
    def get_item_form(item):
        is_admin = flask_login.current_user.has_role("admin")
        is_maintainer = flask_login.current_user.has_role("maintainer")
        if is_admin or is_maintainer:
            return MaintainerNetworkForm()
        return BaseNetworkForm()

    @staticmethod
    def add_parent_to_item(item, parent):
        item.group = parent

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing network records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of network record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].netname),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update network record details")

    @property
    def dbmodel(self):
        return NetworkModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully updated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to update network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_item_form(item):
        if flask_login.current_user.has_role("admin"):
            return AdminNetworkForm(obj=item)
        if flask_login.current_user.has_role("maintainer"):
            return MaintainerNetworkForm(obj=item)
        return BaseNetworkForm(obj=item)

    def do_before_response(self, **kwargs):
        self.response_context.update(referrer=self.get_url_cancel())


class DeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing network records.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Delete network record &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].netname),
        )

    @property
    def dbmodel(self):
        return NetworkModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        return hawat.acl.PERMISSION_POWER.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> was successfully and permanently deleted.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to permanently delete network record <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )


class APINetworksView(AJAXMixin, SQLAlchemyMixin, SimpleView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for presenting the list of networks in the form of a JSON document.
    """

    methods = ["GET"]

    authentication = True

    authorization = [hawat.acl.PERMISSION_POWER]

    @classmethod
    def get_view_name(cls):
        return "apinetworks"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Networks")

    @property
    def dbmodel(self):
        return NetworkModel

    def _get_networks(self):
        return self.search(form_args={})

    def _get_resolved_abuses(self, network):
        settings = network.group.settings_rep
        if network.is_base:
            return {
                "fallback": next(
                    (
                        email
                        for email in [
                            settings.emails_info,
                            settings.emails_low,
                            settings.emails_medium,
                            settings.emails_high,
                            settings.emails_critical,
                        ]
                        if email
                    ),
                    [],
                )
            }
        out = {}
        if settings.emails_info:
            out["info"] = settings.emails_info
        if settings.emails_low:
            out["low"] = settings.emails_low
        if settings.emails_medium:
            out["medium"] = settings.emails_medium
        if settings.emails_high:
            out["high"] = settings.emails_high
        if settings.emails_critical:
            out["critical"] = settings.emails_critical
        return out

    def _get_ip_addresses(self, ip):
        out = {}
        ipobj = from_str(ip)
        if isinstance(ipobj, (IP4, IP4Range, IP4Net)):
            out["ip4_start"] = IP4(ipobj.low())
            out["ip4_end"] = IP4(ipobj.high())
        elif "/" in ip:
            out["ip6_addr"] = ip.split("/")[0]
            out["ip6_prefix"] = int(ip.split("/")[1])
        else:
            out["ip6_start"] = IP6(ipobj.low())
            out["ip6_end"] = IP6(ipobj.high())
        return out

    def do_before_response(self, **kwargs):
        networks = self._get_networks()
        out = []
        for network in networks:
            ip = self._get_ip_addresses(network.network)
            out.append(
                {
                    "rank": network.rank,
                    "source": network.source,
                    "netname": network.netname,
                    "descr": network.description,
                    "resolved_abuses": self._get_resolved_abuses(network),
                    "client_id": network.local_id,
                    **ip,
                }
            )
        self.response_context.update({"data": out})


# -------------------------------------------------------------------------------


class NetworkResolverBaseView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Application view providing base search capabilities for network resolver service.

    For now, the querying is implemented using :py:mod:`mentat.services.whois` module.
    """

    authentication = True

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Search network resolver")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Search network resolver")

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = NetworkResolverSearchForm(flask.request.args, meta={"csrf": False})

        if hawat.const.FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data
                whois_manager = mentat.services.whois.WhoisServiceManager(flask.current_app.mconfig)
                whois_service = whois_manager.service()
                self.response_context.update(search_item=form.search.data, form_data=form_data)
                try:
                    self.response_context.update(search_result=whois_service.lookup(form.search.data))
                except Exception as exc:
                    self.flash(str(exc), level="error")

        self.response_context.update(
            search_form=form,
            request_args=flask.request.args,
        )
        return self.generate_response()


class NetworkResolverSnippetView(SnippetMixin, NetworkResolverBaseView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View responsible for querying local WHOIS service and presenting the results
    in the form of JSON document containing ready to use HTML page snippets.
    """

    methods = ["GET", "POST"]

    renders = ["label", "full"]

    snippets = [{"name": "abuse", "condition": lambda x: x.get("search_result", False)}]

    @classmethod
    def get_view_name(cls):
        return "sptsearch"


# -------------------------------------------------------------------------------


class NetworksBlueprint(HawatBlueprint):
    """Pluggable module - network management (*networks*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Network record management")

    def register_app(self, app):
        app.menu_main.add_entry("view", f"admin.{BLUEPRINT_NAME}", position=70, view=ListView)

        # Register object additional data services provided by this module.
        app.set_oads(
            hawat.const.AODS_IP4,
            NetworkResolverSnippetView,
            URLParamsBuilder({"submit": tr_("Search")}).add_rule("search").add_kwrule("render", False, True),
        )
        app.set_oads(
            hawat.const.AODS_IP6,
            NetworkResolverSnippetView,
            URLParamsBuilder({"submit": tr_("Search")}).add_rule("search").add_kwrule("render", False, True),
        )


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = NetworksBlueprint(BLUEPRINT_NAME, __name__, template_folder="templates")

    hbp.register_view_class(ListView, f"/{BLUEPRINT_NAME}/list")
    hbp.register_view_class(CreateView, f"/{BLUEPRINT_NAME}/create")
    hbp.register_view_class(CreateForView, f"/{BLUEPRINT_NAME}/createfor/<int:parent_id>")
    hbp.register_view_class(ShowView, f"/{BLUEPRINT_NAME}/<int:item_id>/show")
    hbp.register_view_class(UpdateView, f"/{BLUEPRINT_NAME}/<int:item_id>/update")
    hbp.register_view_class(DeleteView, f"/{BLUEPRINT_NAME}/<int:item_id>/delete")
    hbp.register_view_class(APINetworksView, f"/api/{BLUEPRINT_NAME}/get")
    hbp.register_view_class(NetworkResolverSnippetView, f"/snippet/{BLUEPRINT_NAME}/resolver")

    return hbp
