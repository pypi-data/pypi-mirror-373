#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom item changelog search form for Hawat.
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


def get_item_operation_choices():
    """
    Return select choices for item changelog operations.
    """
    item_changelog_model = flask.current_app.get_model(hawat.const.MODEL_ITEM_CHANGELOG)
    operations_list = hawat.db.db_query(item_changelog_model).distinct(item_changelog_model.operation).all()
    return list(
        zip(
            [x.operation for x in operations_list],
            [lazy_gettext(x.operation) for x in operations_list],
        )
    )


def get_item_model_choices():
    """
    Return select choices for item changelog item models.
    """
    item_changelog_model = flask.current_app.get_model(hawat.const.MODEL_ITEM_CHANGELOG)
    models_list = hawat.db.db_query(item_changelog_model).distinct(item_changelog_model.model).all()
    return list(
        zip(
            [x.model for x in models_list],
            [lazy_gettext(x.model) for x in models_list],
        )
    )


class ItemChangeLogSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing item changelog search form.
    """

    authors = wtforms.SelectMultipleField(
        lazy_gettext("Authors:"),
        default=[],
        coerce=hawat.forms.coerce_user,
        filters=[hawat.forms.filter_none_from_list],
    )
    operations = wtforms.SelectMultipleField(
        lazy_gettext("Operations:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    imodel = wtforms.SelectField(
        lazy_gettext("Item model:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[("", lazy_gettext("Nothing selected"))],
        filters=[lambda x: x or None],
        default="",
    )
    imodel_id = wtforms.IntegerField(
        lazy_gettext("Model ID:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    dt_from = hawat.forms.SmartDateTimeField(
        lazy_gettext("From:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.validate_datetime_order(prefix="dt"),
        ],
        default=lambda: hawat.forms.default_dt_with_delta(hawat.const.DEFAULT_RESULT_TIMEDELTA),
    )
    dt_to = hawat.forms.SmartDateTimeField(
        lazy_gettext("To:"),
        validators=[wtforms.validators.Optional()],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.operations.choices = get_item_operation_choices()
        self.imodel.choices[1:] = get_item_model_choices()

        users = hawat.forms.get_available_users()
        self.authors.choices = [("__SYSTEM__", lazy_gettext("<< system change >>"))]
        self.authors.choices += [(user, hawat.forms.format_select_option_label_user(user)) for user in users]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multi-value field.

        :param str field_name: Name of the form field
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise
        :rtype: bool
        """
        return field_name in ("authors", "operations")


class ItemChangeLogDashboardForm(flask_wtf.FlaskForm):
    """
    Class representing item changelog dashboard search form.
    """

    dt_from = hawat.forms.SmartDateTimeField(
        lazy_gettext("From:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.validate_datetime_order(prefix="dt"),
        ],
        default=lambda: hawat.forms.default_dt_with_delta(hawat.const.DEFAULT_RESULT_TIMEDELTA),
    )
    dt_to = hawat.forms.SmartDateTimeField(
        lazy_gettext("To:"),
        validators=[wtforms.validators.Optional()],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Calculate"),
    )
