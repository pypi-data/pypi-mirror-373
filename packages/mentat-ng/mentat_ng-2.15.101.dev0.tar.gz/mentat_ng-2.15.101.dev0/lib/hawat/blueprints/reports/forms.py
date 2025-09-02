#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom event report search form for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from typing import Any, cast

import flask_login
import flask_wtf
import wtforms
from flask_babel import LazyString, lazy_gettext
from sqlalchemy import or_

import hawat.acl
import hawat.const
import hawat.db
import hawat.forms
import mentat.const
from mentat.datatype.sqldb import GroupModel, UserModel


def get_available_groups() -> list[GroupModel]:
    """
    Query the database for list of all available groups.
    """
    # In case the current user is maintainer or administrator provide list of all groups.
    if hawat.acl.PERMISSION_POWER.can():
        return cast(list[GroupModel], hawat.db.db_query(GroupModel).order_by(GroupModel.name).all())
    # Otherwise, provide only list of groups current user is a member or a manager of.
    return cast(
        list[GroupModel],
        hawat.db.db_query(GroupModel)
        .filter(
            or_(
                GroupModel.members.any(UserModel.id == flask_login.current_user.id),
                GroupModel.managers.any(UserModel.id == flask_login.current_user.id),
            )
        )
        .order_by(GroupModel.name)
        .all(),
    )


def get_severity_choices() -> list[tuple[str, LazyString]]:
    """
    Return select choices for report severities.
    """
    return list(
        zip(
            mentat.const.REPORT_SEVERITIES,
            [lazy_gettext(x) for x in mentat.const.REPORT_SEVERITIES],
        )
    )


def get_type_choices() -> list[tuple[str, LazyString]]:
    """
    Return select choices for report severities.
    """
    return list(
        zip(
            mentat.const.REPORT_TYPES,
            [lazy_gettext(x) for x in mentat.const.REPORT_TYPES],
        )
    )


class EventReportSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing event report search form.
    """

    label = wtforms.StringField(
        lazy_gettext("Label:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_null_character],
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
        default=hawat.forms.default_dt,
    )
    groups = wtforms.SelectMultipleField(
        lazy_gettext("Groups:"),
        default=[],
        coerce=hawat.forms.coerce_group,
        filters=[hawat.forms.filter_none_from_list],
    )
    severities = wtforms.SelectMultipleField(
        lazy_gettext("Severities:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=get_severity_choices(),
        filters=[lambda x: x or []],
    )
    types = wtforms.SelectMultipleField(
        lazy_gettext("Types:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=get_type_choices(),
        filters=[lambda x: x or []],
    )
    categories = wtforms.SelectMultipleField(
        lazy_gettext("Categories:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    classes = wtforms.SelectMultipleField(
        lazy_gettext("Event classes:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    detectors = wtforms.SelectMultipleField(
        lazy_gettext("Detectors:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    source_ips = hawat.forms.CommaListField(
        lazy_gettext("Source IP addresses:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.check_network_record_list,
        ],
        filters=[lambda lst: [source.replace("[.]", ".") for source in lst]],
    )
    target_ips = hawat.forms.CommaListField(
        lazy_gettext("Target IP addresses:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.check_network_record_list,
        ],
        filters=[lambda lst: [source.replace("[.]", ".") for source in lst]],
    )

    # Admin panel
    shadow_type = wtforms.SelectField(
        lazy_gettext("Shadow report type:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("", lazy_gettext("All reports")),
            ("normal", lazy_gettext("Normal reports only")),
            ("shadow", lazy_gettext("Shadow reports only")),
        ],
        default="",
        filters=[lambda x: x or []],
    )
    relapse_type = wtforms.SelectField(
        lazy_gettext("Relapse report type:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("", lazy_gettext("All reports")),
            ("relapsed", lazy_gettext("Reports with relapse only")),
            ("non_relapsed", lazy_gettext("Reports without relapse only")),
        ],
        default="",
        filters=[lambda x: x or []],
    )

    @classmethod
    def is_multivalue(cls, field_name: str) -> bool:
        """
        Check, if given form field is a multivalue field.

        :param field_name: Name of the form field
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        """
        if field_name in (
            "groups",
            "severities",
            "types",
            "categories",
            "classes",
            "detectors",
        ):
            return True
        return super().is_multivalue(field_name)

    @classmethod
    def is_csag_context_insignificant(cls, field_name: str) -> bool:
        return field_name in (
            "dt_from",
            "dt_to",
        ) or super().is_csag_context_insignificant(field_name)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        groups = get_available_groups()
        self.groups.choices = [(group, str(group.name)) for group in groups]

        self.categories.choices = kwargs["choices_categories"]
        self.classes.choices = kwargs["choices_classes"]
        self.detectors.choices = kwargs["choices_detectors"]


class ReportingDashboardForm(hawat.forms.HawatBaseForm):
    """
    Class representing event reporting dashboard search form.
    """

    groups = wtforms.SelectMultipleField(
        lazy_gettext("Groups:"),
        default=[],
        coerce=hawat.forms.coerce_group,
        filters=[hawat.forms.filter_none_from_list],
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
        default=hawat.forms.default_dt,
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Search"),
    )

    @classmethod
    def is_multivalue(cls, field_name: str) -> bool:
        """
        Check, if given form field is a multivalue field.

        :param field_name: Name of the form field
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        """
        return field_name in ["groups"]

    @classmethod
    def is_csag_context_insignificant(cls, field_name: str) -> bool:
        return field_name in (
            "dt_from",
            "dt_to",
        ) or super().is_csag_context_insignificant(field_name)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        groups = get_available_groups()
        self.groups.choices = [(group, str(group.name)) for group in groups]


class FeedbackForm(flask_wtf.FlaskForm):  # type: ignore
    """
    Class representing feedback form for reports.
    """

    ip = wtforms.HiddenField()  # Not mandatory because of target reports
    text = wtforms.TextAreaField(
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=3)],
    )
    section = wtforms.HiddenField(
        validators=[wtforms.validators.DataRequired(), wtforms.validators.Length(min=1)],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Send feedback"),
    )
