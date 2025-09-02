#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Hawat pluggable module provides special authentication method, that is
particularly usable for developers and enables them to impersonate any user.

After enabling this module special authentication endpoint will be available
and will provide simple authentication form with list of all currently available
user accounts. It will be possible for that user to log in as any other user
without entering password.

This module is disabled by default in *production* environment and enabled by
default in *development* environment.

.. warning::

    This module must never ever be enabled on production systems, because it is
    a huge security risk and enables possible access control management violation.
    You have been warned!


Provided endpoints
--------------------------------------------------------------------------------

``/auth_dev/login``
    Page providing special developer login form.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
from hawat.base import HawatBlueprint
from hawat.blueprints.auth_dev.forms import DevRegisterUserAccountForm, LoginForm
from hawat.view import BaseLoginView, BaseRegisterView
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin

BLUEPRINT_NAME = "auth_dev"
"""Name of the blueprint as module global constant."""


class LoginView(HTMLMixin, SQLAlchemyMixin, BaseLoginView):
    """
    View enabling special developer login.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Developer login")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Login (dev)")

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_USER)

    @property
    def search_by(self):
        return self.dbmodel.login

    def get_user_login(self):
        form = LoginForm()
        self.response_context.update(form=form)
        if form.validate_on_submit():
            return form.login.data.lower()
        return None


class RegisterView(HTMLMixin, SQLAlchemyMixin, BaseRegisterView):
    """
    View responsible for registering new user account into application.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Register (dev)")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("User account registration (dev)")

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_USER)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @staticmethod
    def get_item_form(item):
        roles = list(
            zip(
                flask.current_app.config["ROLES"],
                flask.current_app.config["ROLES"],
            )
        )
        locales = list(flask.current_app.config["SUPPORTED_LOCALES"].items())

        return DevRegisterUserAccountForm(
            choices_roles=roles,
            choices_locales=locales,
        )


# -------------------------------------------------------------------------------


class DevAuthBlueprint(HawatBlueprint):
    """Pluggable module - developer authentication service (*auth_dev*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Developer authentication service")


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = DevAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(LoginView, "/login")
    hbp.register_view_class(RegisterView, "/register")

    return hbp
