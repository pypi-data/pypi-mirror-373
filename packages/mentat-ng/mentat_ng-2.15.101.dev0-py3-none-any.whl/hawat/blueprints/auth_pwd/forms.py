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

import flask_wtf
import wtforms
from flask_babel import lazy_gettext

import hawat.forms
from hawat.blueprints.users.forms import BaseRegisterUserAccountForm
from hawat.forms import check_login, check_null_character


class LoginForm(flask_wtf.FlaskForm):
    """
    Class representing classical password authentication login form.
    """

    login = wtforms.StringField(
        lazy_gettext("Login:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
            check_null_character,
            check_login,
        ],
    )
    password = wtforms.PasswordField(
        lazy_gettext("Password:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=8),
        ],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Login"),
    )


class PasswordRegisterUserAccountForm(BaseRegisterUserAccountForm):
    """
    Class representing account password registration form using password.
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
    password = wtforms.PasswordField(
        lazy_gettext("Password:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=8),
        ],
    )
    password2 = wtforms.PasswordField(
        lazy_gettext("Repeat Password:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.EqualTo("password"),
        ],
    )
