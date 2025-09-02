#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom developer login form for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
import flask_wtf
import wtforms
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
from hawat.blueprints.users.forms import BaseRegisterUserAccountForm
from hawat.forms import check_login


class LoginForm(flask_wtf.FlaskForm):
    """
    Class representing developer authentication login form. This form provides
    list of all currently existing user accounts in simple selectbox, so that
    the developer can quickly login as different user.
    """

    login = wtforms.SelectField(
        lazy_gettext("User account:"),
        validators=[wtforms.validators.DataRequired(), check_login],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Login"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_choices()

    def set_choices(self):
        """
        Load list of all user accounts and populate the ``choices`` attribute of
        the ``login`` selectbox.
        """
        dbsess = hawat.db.db_get().session
        user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
        users = dbsess.query(user_model).order_by(user_model.login).all()

        choices = []
        for usr in users:
            choices.append((usr.login, f"{usr.fullname} ({usr.login}, #{usr.id})"))
        choices = sorted(choices, key=lambda x: x[1])
        self.login.choices = choices


class DevRegisterUserAccountForm(BaseRegisterUserAccountForm):
    """
    Class representing user account registration form (for developers).
    """

    login = wtforms.StringField(
        lazy_gettext("Login:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
            hawat.forms.check_null_character,
            check_login,
            hawat.forms.check_unique_login,
        ],
    )
