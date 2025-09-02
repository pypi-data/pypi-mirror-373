#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom group management forms for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import sqlalchemy
import wtforms
from flask_babel import gettext, lazy_gettext

import hawat.db
import hawat.forms
from mentat.datatype.sqldb import GroupModel

EMPTY = "__EMPTY__"


def check_name_existence(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating user logins during account create action.
    """
    try:
        hawat.db.db_get().session.query(GroupModel).filter(GroupModel.name == field.data).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return
    except:  # pylint: disable=locally-disabled,bare-except
        pass
    raise wtforms.validators.ValidationError(gettext("Group with this name already exists."))


def check_name_uniqueness(form, field):
    """
    Callback for validating user logins during account update action.
    """
    item = (
        hawat.db.db_get()
        .session.query(GroupModel)
        .filter(GroupModel.name == field.data)
        .filter(GroupModel.id != form.db_item_id)
        .all()
    )
    if not item:
        return
    raise wtforms.validators.ValidationError(gettext("Group with this name already exists."))


def check_parent_not_self(form, field):
    """
    Callback for validating that parent group is not self.
    """
    if field.data and form.db_item_id == field.data.id:
        raise wtforms.validators.ValidationError(
            gettext("You must not select a group as its own parent! Naughty, naughty you!")
        )


class BaseGroupForm(hawat.forms.BaseItemForm):
    """
    Class representing base group form.
    """

    description = wtforms.StringField(
        lazy_gettext("Description:"),
        validators=[
            wtforms.validators.DataRequired(),
            hawat.forms.check_null_character,
        ],
        description=lazy_gettext("Additional and more extensive group description."),
    )
    source = wtforms.HiddenField(
        default="manual",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
        ],
        description=lazy_gettext(
            "Origin of the group record, whether it was added manually, or via some automated mechanism from data from some third party system."
        ),
    )
    members = wtforms.SelectMultipleField(
        lazy_gettext("Members:"),
        default=[],
        coerce=hawat.forms.coerce_user,
        filters=[hawat.forms.filter_none_from_list],
        description=lazy_gettext("List of group members."),
    )
    managers = wtforms.SelectMultipleField(
        lazy_gettext("Managers:"),
        default=[],
        coerce=hawat.forms.coerce_user,
        filters=[hawat.forms.filter_none_from_list],
        description=lazy_gettext(
            "List of users acting as group managers. These users may change various group settings."
        ),
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Submit"),
    )
    cancel = wtforms.SubmitField(
        lazy_gettext("Cancel"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        users = hawat.forms.get_available_users()
        self.members.choices = [(user, hawat.forms.format_select_option_label_user(user)) for user in users]
        self.managers.choices = [(user, hawat.forms.format_select_option_label_user(user)) for user in users]


class UpdateGroupForm(BaseGroupForm):
    """
    Class representing group update form for regular users.
    """


class MaintainerUpdateGroupForm(BaseGroupForm):
    """
    Class representing group update form for maintainers.
    """

    local_id = wtforms.StringField(
        lazy_gettext("Local ID:"),
        validators=[wtforms.validators.Optional(), wtforms.validators.Length(max=20)],
        description=lazy_gettext("User defined local ID for the group."),
    )


class AdminBaseGroupForm(BaseGroupForm):
    """
    Class representing group create form.
    """

    enabled = wtforms.RadioField(
        lazy_gettext("State:"),
        validators=[
            wtforms.validators.InputRequired(),
        ],
        choices=[(True, lazy_gettext("Enabled")), (False, lazy_gettext("Disabled"))],
        filters=[hawat.forms.str_to_bool],
        coerce=hawat.forms.str_to_bool,
        description=lazy_gettext(
            "Boolean flag whether the group is enabled or disabled. Disabled groups are hidden to the most of the system features."
        ),
    )
    parent = wtforms.SelectField(
        lazy_gettext("Parent group:"),
        validators=[wtforms.validators.Optional(), check_parent_not_self],
        choices=[("", lazy_gettext("<< no selection >>"))],
        coerce=hawat.forms.coerce_group,
        description=lazy_gettext(
            "Parent group for this group. This feature enables the posibility to create structured group hierarchy."
        ),
    )
    local_id = wtforms.StringField(
        lazy_gettext("Local ID:"),
        validators=[wtforms.validators.Optional(), wtforms.validators.Length(max=20)],
        description=lazy_gettext("User defined local ID for the group."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = hawat.forms.get_available_groups()
        self.parent.choices[1:] = [(group, group.name) for group in groups]


class AdminCreateGroupForm(AdminBaseGroupForm):
    """
    Class representing group create form for administrators.
    """

    name = wtforms.StringField(
        lazy_gettext("Name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_group_name,
            hawat.forms.check_unique_group,
        ],
        description=lazy_gettext("System-wide unique name for the group."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_item_id = None


class AdminUpdateGroupForm(AdminBaseGroupForm):
    """
    Class representing group update form for administrators.
    """

    name = wtforms.StringField(
        lazy_gettext("Name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
            hawat.forms.check_group_name,
            check_name_uniqueness,
        ],
        description=lazy_gettext("System-wide unique name for the group."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store the ID of original item in database to enable the ID uniqueness
        # check with check_name_uniqueness() validator.
        self.db_item_id = kwargs["db_item_id"]


class GroupSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing simple user search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Name, description:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
        filters=[lambda x: x or "", str.strip],
        description=lazy_gettext(
            "Group`s full name or description. Search is performed even in the middle of the strings."
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
        description=lazy_gettext("Search for groups with particular state."),
    )
    source = wtforms.SelectField(
        lazy_gettext("Record source:"),
        validators=[wtforms.validators.Optional()],
        default="",
        description=lazy_gettext("Search for groups coming from particular source/feed."),
    )
    member = wtforms.SelectField(
        lazy_gettext("Group member:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            (EMPTY, lazy_gettext("<< without members >>")),
        ],
        description=lazy_gettext("Search for groups with particular member."),
    )
    manager = wtforms.SelectField(
        lazy_gettext("Group manager:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            (EMPTY, lazy_gettext("<< without managers >>")),
        ],
        description=lazy_gettext("Search for groups with particular manager."),
    )

    sortby = wtforms.SelectField(
        lazy_gettext("Sort by:"),
        validators=[wtforms.validators.DataRequired()],
        choices=[
            ("createtime.desc", lazy_gettext("by creation time descending")),
            ("createtime.asc", lazy_gettext("by creation time ascending")),
            ("name.desc", lazy_gettext("by name descending")),
            ("name.asc", lazy_gettext("by name ascending")),
            ("network_count.desc", lazy_gettext("by network count descending")),
            ("network_count.asc", lazy_gettext("by network count ascending")),
        ],
        default="name.asc",
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
        source_list = hawat.forms.get_available_group_sources()
        self.source.choices = [("", lazy_gettext("Nothing selected"))] + list(zip(source_list, source_list))
        users = hawat.forms.get_available_users()
        self.member.choices += [(user.id, user.email) for user in users]
        self.manager.choices += [(user.id, user.email) for user in users]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False
