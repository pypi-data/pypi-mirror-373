#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides access to group reporting settings management features.
These features include:

* detailed reporting settings view
* creating new reporting settings
* updating existing reporting settings
* deleting existing reporting settings
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import os

import flask
import flask_principal
import markupsafe
from babel import Locale
from flask_babel import gettext, lazy_gettext

import pyzenkit.utils

import hawat.acl
import hawat.db
import hawat.menu
import mentat.const
import mentat.reports.utils
from hawat.base import HawatBlueprint
from hawat.blueprints.settings_reporting.forms import (
    BaseSettingsReportingForm,
    MaintainerSettingsReportingForm,
)
from hawat.view import ItemShowView, ItemUpdateView
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin
from mentat.datatype.sqldb import ItemChangeLogModel, SettingsReportingModel

BLUEPRINT_NAME = "settings_reporting"
"""Name of the blueprint as module global constant."""


def get_available_locales():
    """
    Get list available report translations.
    This method must be called with Flask app context.
    """
    locale_list = [["en", "en"]]

    templates_dir = flask.current_app.mconfig[mentat.const.CKEY_CORE_REPORTER][
        mentat.const.CKEY_CORE_REPORTER_TEMPLATESDIR
    ]
    translations_dir = pyzenkit.utils.get_resource_path_fr(os.path.join(templates_dir, "translations"))
    if os.path.isdir(translations_dir):
        for translation in os.listdir(translations_dir):
            if translation[0] == ".":
                continue
            if os.path.isdir(os.path.join(translations_dir, translation)):
                locale_list.append([translation, translation])

    locale_list = sorted(locale_list, key=lambda x: x[0])

    for translation in locale_list:
        locale_obj = Locale.parse(translation[0])
        translation[1] = locale_obj.language_name.lower()

    return locale_list


class ShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed reporting settings view.
    """

    methods = ["GET"]

    authentication = True

    @classmethod
    def get_view_icon(cls):
        return "module-settings-reporting"

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Reporting settings")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Show reporting settings")

    @property
    def dbmodel(self):
        return SettingsReportingModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_mm = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_mm.can()

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
            "list",
            endpoint="groups.list",
        )
        action_menu.add_entry(
            "endpoint",
            "pshow",
            endpoint="groups.show",
        )
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint=f"{cls.module_name}.show",
        )

        return action_menu

    @classmethod
    def get_action_menu(cls):
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "showgroup",
            endpoint="groups.show",
            title=lazy_gettext("Group"),
        )
        action_menu.add_entry(
            "endpoint",
            "update",
            endpoint="settings_reporting.update",
        )
        return action_menu

    def do_before_response(self, **kwargs):
        item = self.response_context["item"]
        default_locale = flask.current_app.mconfig[mentat.const.CKEY_CORE_REPORTER][
            mentat.const.CKEY_CORE_REPORTER_DEFAULTLOCALE
        ]
        default_timezone = flask.current_app.mconfig[mentat.const.CKEY_CORE_REPORTER][
            mentat.const.CKEY_CORE_REPORTER_DEFAULTTIMEZONE
        ]
        system_default_repsettings = mentat.reports.utils.ReportingSettings(
            item.group,
            hawat.db.db_get(),
            default_locale=default_locale,
            default_timezone=default_timezone,
        )
        self.response_context.update(system_default_repsettings=system_default_repsettings)

        if self.can_access_endpoint("settings_reporting.update", item=item) and self.has_endpoint("changelogs.search"):
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


class UpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing reporting settings.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_menu_legend(cls, **kwargs):
        return lazy_gettext(
            "Update details of reporting settings for group &quot;%(item)s&quot;",
            item=markupsafe.escape(kwargs["item"].group.name),
        )

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Update reporting settings details")

    @property
    def dbmodel(self):
        return SettingsReportingModel

    @property
    def dbchlogmodel(self):
        return ItemChangeLogModel

    @classmethod
    def authorize_item_action(cls, **kwargs):
        permission_m = flask_principal.Permission(
            hawat.acl.MembershipNeed(kwargs["item"].group.id),
            hawat.acl.ManagementNeed(kwargs["item"].group.id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_m.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "Reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong> were successfully updated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to update reporting settings <strong>%(item_id)s</strong> for group <strong>%(parent_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
            parent_id=markupsafe.escape(str(kwargs["item"].group)),
        )

    @staticmethod
    def get_item_form(item):
        if hawat.acl.PERMISSION_POWER.can():
            return MaintainerSettingsReportingForm(
                obj=item,
                locales=get_available_locales(),
            )
        return BaseSettingsReportingForm(
            obj=item,
            locales=get_available_locales(),
        )


# -------------------------------------------------------------------------------


class SettingsReportingBlueprint(HawatBlueprint):
    """Pluggable module - reporting settings. (*settings_reporting*)"""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Reporting settings management")


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = SettingsReportingBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(ShowView, "/<int:item_id>/show")
    hbp.register_view_class(UpdateView, "/<int:item_id>/update")

    return hbp
