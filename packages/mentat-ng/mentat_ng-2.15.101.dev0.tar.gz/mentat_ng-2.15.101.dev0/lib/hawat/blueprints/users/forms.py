#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom user account management forms for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import pytz
import sqlalchemy
import wtforms
from flask_babel import gettext, lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
from hawat.forms import check_login
from mentat.datatype.sqldb import UserModel

EMPTY = "__EMPTY__"


def check_id_existence(form, field):
    """
    Callback for validating user logins during account create action.
    """
    try:
        hawat.db.db_get().session.query(UserModel).filter(UserModel.login == field.data).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return
    except:  # pylint: disable=locally-disabled,bare-except
        pass
    raise wtforms.validators.ValidationError(gettext("User account with this login already exists."))


def check_id_uniqueness(form, field):
    """
    Callback for validating user logins during account update action.
    """
    user = (
        hawat.db.db_get()
        .session.query(UserModel)
        .filter(UserModel.login == field.data)
        .filter(UserModel.id != form.db_item_id)
        .all()
    )
    if not user:
        return
    raise wtforms.validators.ValidationError(gettext("User account with this login already exists."))


class BaseUserAccountForm(hawat.forms.BaseItemForm):
    """
    Class representing base user account form.
    """

    fullname = wtforms.StringField(
        lazy_gettext("Full name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
    )
    email = wtforms.StringField(
        lazy_gettext("E-mail:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            wtforms.validators.Email(),
        ],
    )
    organization = wtforms.StringField(
        lazy_gettext("Home organization:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            hawat.forms.check_null_character,
        ],
    )
    locale = hawat.forms.SelectFieldWithNone(
        lazy_gettext("Preferred locale:"),
        validators=[wtforms.validators.Optional()],
        choices=[("", lazy_gettext("<< no preference >>"))],
        filters=[lambda x: x or None],
        default="",
    )
    timezone = hawat.forms.SelectFieldWithNone(
        lazy_gettext("Preferred timezone:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[("", lazy_gettext("<< no preference >>"))] + list(zip(pytz.common_timezones, pytz.common_timezones)),
        filters=[lambda x: x or None],
        default="",
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Submit"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        # Handle additional custom keywords.
        #

        # The list of choices for 'locale' attribute comes from outside of the
        # form to provide as loose tie as possible to the outer application.
        # Another approach would be to load available choices here with:
        #
        #   locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())
        #
        # That would mean direct dependency on flask.Flask application.
        self.locale.choices[1:] = kwargs["choices_locales"]


class AdminUserAccountForm(BaseUserAccountForm):
    """
    Class representing base user account form for admins.
    """

    enabled = wtforms.RadioField(
        lazy_gettext("State:"),
        validators=[
            wtforms.validators.InputRequired(),
        ],
        choices=[(True, lazy_gettext("Enabled")), (False, lazy_gettext("Disabled"))],
        filters=[hawat.forms.str_to_bool],
        coerce=hawat.forms.str_to_bool,
    )
    roles = wtforms.SelectMultipleField(
        lazy_gettext("Roles:"),
        validators=[wtforms.validators.Optional()],
    )
    memberships = wtforms.SelectMultipleField(
        lazy_gettext("Group memberships:"),
        default=[],
        coerce=hawat.forms.coerce_group,
        filters=[hawat.forms.filter_none_from_list],
    )
    managements = wtforms.SelectMultipleField(
        lazy_gettext("Group managements:"),
        default=[],
        coerce=hawat.forms.coerce_group,
        filters=[hawat.forms.filter_none_from_list],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # Handle additional custom keywords.
        #

        # The list of choices for 'roles' attribute comes from outside of the
        # form to provide as loose tie as possible to the outer application.
        # Another approach would be to load available choices here with:
        #
        #   roles = flask.current_app.config['ROLES']
        #
        # That would mean direct dependency on flask.Flask application.
        self.roles.choices = kwargs["choices_roles"]
        groups = hawat.forms.get_available_groups()
        self.memberships.choices = [(group, group.name) for group in groups]
        self.managements.choices = [(group, group.name) for group in groups]


class CreateUserAccountForm(AdminUserAccountForm):
    """
    Class representing user account create form.
    """

    login = wtforms.StringField(
        lazy_gettext("Login:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
            hawat.forms.check_null_character,
            check_login,
            check_id_existence,
        ],
    )


class UpdateUserAccountForm(BaseUserAccountForm):
    """
    Class representing user account update form for regular users.
    """


class AdminUpdateUserAccountForm(AdminUserAccountForm):
    """
    Class representing user account update form for administrators.
    """

    login = wtforms.StringField(
        lazy_gettext("Login:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
            hawat.forms.check_login,
            hawat.forms.check_null_character,
            check_id_uniqueness,
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        # Handle additional custom keywords.
        #

        # Store the ID of original item in database to enable the ID uniqueness
        # check with check_id_uniqueness() validator.
        self.db_item_id = kwargs["db_item_id"]


class BaseRegisterUserAccountForm(BaseUserAccountForm):
    """
    Class representing universal account registration form.
    """

    memberships_wanted = wtforms.SelectMultipleField(
        lazy_gettext("Choose a group to join:"),
        validators=[
            wtforms.validators.InputRequired(),
        ],
        default=[],
        coerce=hawat.forms.coerce_group,
        filters=[hawat.forms.filter_none_from_list, hawat.forms.filter_no_group_from_list],
    )
    justification = wtforms.TextAreaField(
        lazy_gettext("Justification:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=10, max=500),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = hawat.forms.get_available_groups()
        self.memberships_wanted.choices = [(group, group.name) for group in groups]
        self.memberships_wanted.choices.append(
            ("__NO_GROUP__", lazy_gettext("No group (state the reason in justification)"))
        )


class UserSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing simple user search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Login, name, e-mail:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
        filters=[lambda x: x or "", str.strip],
        description=lazy_gettext(
            "User`s login, full name or e-mail address. Search is performed even in the middle of the strings, so for example you may lookup by domain."
        ),
    )
    dt_from = hawat.forms.SmartDateTimeField(
        lazy_gettext("Creation time from:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.validate_datetime_order(prefix="dt"),
        ],
        description=lazy_gettext(
            "Lower time boundary for item creation time. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences."
        ),
    )
    dt_to = hawat.forms.SmartDateTimeField(
        lazy_gettext("Creation time to:"),
        validators=[wtforms.validators.Optional()],
        description=lazy_gettext(
            "Upper time boundary for item creation time. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences."
        ),
    )

    state = wtforms.SelectField(
        lazy_gettext("State:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            ("enabled", lazy_gettext("Enabled")),
            ("disabled", lazy_gettext("Disabled")),
        ],
        default="",
        description=lazy_gettext("Search for users with particular account state."),
    )
    role = wtforms.SelectField(
        lazy_gettext("Role:"),
        validators=[wtforms.validators.Optional()],
        default="",
        description=lazy_gettext("Search for users with particular role, or without any assigned roles."),
    )
    membership = wtforms.SelectField(
        lazy_gettext("Group membership:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            (EMPTY, lazy_gettext("<< without group >>")),
        ],
        description=lazy_gettext("Search for users with membership with particular group."),
    )
    management = wtforms.SelectField(
        lazy_gettext("Group management:"),
        validators=[wtforms.validators.Optional()],
        choices=[("", lazy_gettext("Nothing selected"))],
        description=lazy_gettext("Search for users with management rights to particular group."),
    )

    sortby = wtforms.SelectField(
        lazy_gettext("Sort result by:"),
        validators=[wtforms.validators.DataRequired()],
        choices=[
            ("createtime.desc", lazy_gettext("by creation time descending")),
            ("createtime.asc", lazy_gettext("by creation time ascending")),
            ("login.desc", lazy_gettext("by login descending")),
            ("login.asc", lazy_gettext("by login ascending")),
            ("fullname.desc", lazy_gettext("by name descending")),
            ("fullname.asc", lazy_gettext("by name ascending")),
            ("email.desc", lazy_gettext("by e-mail descending")),
            ("email.asc", lazy_gettext("by e-mail ascending")),
            ("logintime.desc", lazy_gettext("by login time descending")),
            ("logintime.asc", lazy_gettext("by login time ascending")),
        ],
        default="fullname.asc",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # Handle additional custom keywords.
        #

        # The list of choices for 'roles' attribute comes from outside of the
        # form to provide as loose tie as possible to the outer application.
        # Another approach would be to load available choices here with:
        #
        #   roles = flask.current_app.config['ROLES']
        #
        # That would mean direct dependency on flask.Flask application.
        self.role.choices = [
            ("", lazy_gettext("Nothing selected")),
            (hawat.const.NO_ROLE, lazy_gettext("<< without roles >>")),
        ] + kwargs["choices_roles"]
        groups = hawat.forms.get_available_groups()
        self.membership.choices += [(group.id, group.name) for group in groups]
        self.management.choices += [(group.id, group.name) for group in groups]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False
