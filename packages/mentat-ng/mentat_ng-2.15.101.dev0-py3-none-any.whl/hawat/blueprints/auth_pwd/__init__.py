#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides classical web login form with password authentication
method.


Provided endpoints
--------------------------------------------------------------------------------

``/auth_pwd/login``
    Page providing classical web login form.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
from flask_babel import lazy_gettext

import hawat.const
import hawat.forms
from hawat.base import HawatBlueprint
from hawat.blueprints.auth_pwd.forms import LoginForm, PasswordRegisterUserAccountForm
from hawat.view import BaseLoginView, BaseRegisterView
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin

BLUEPRINT_NAME = "auth_pwd"
"""Name of the blueprint as module global constant."""


class LoginView(HTMLMixin, SQLAlchemyMixin, BaseLoginView):
    """
    View enabling classical password login.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Password login")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Login (pwd)")

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

    def authenticate_user(self, user):
        return user.check_password(self.response_context["form"].password.data)


class RegisterView(HTMLMixin, SQLAlchemyMixin, BaseRegisterView):
    """
    View enabling classical password login.
    """

    methods = ["GET", "POST"]

    @classmethod
    def get_menu_title(cls, **kwargs):
        return lazy_gettext("Register (pwd)")

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("User account registration (pwd)")

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_USER)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @property
    def search_by(self):
        return self.dbmodel.login

    @staticmethod
    def get_item_form(item):
        locales = list(flask.current_app.config["SUPPORTED_LOCALES"].items())
        return PasswordRegisterUserAccountForm(choices_locales=locales)

    def do_before_action(self, item):  # pylint: disable=locally-disabled,unused-argument
        super().do_before_action(item)
        item.set_password(item.password)


# -------------------------------------------------------------------------------


class PwdAuthBlueprint(HawatBlueprint):
    """Pluggable module - classical authentication service (*auth_pwd*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("Password authentication service")


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = PwdAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(LoginView, "/login")
    hbp.register_view_class(RegisterView, "/register")

    return hbp
