#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom reporting filter management forms for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_wtf
import wtforms
from flask_babel import gettext, lazy_gettext

import hawat.db
import hawat.forms
from mentat.const import REPORTING_FILTER_ADVANCED, REPORTING_FILTER_BASIC
from mentat.idea.internal import Idea


def check_event(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating IDEA event JSON.
    """
    try:
        Idea.from_json(field.data)
    except Exception as err:
        raise wtforms.validators.ValidationError(
            gettext('Event JSON parse error: "%(error)s".', error=str(err))
        ) from err


# -------------------------------------------------------------------------------


class BaseFilterForm(hawat.forms.BaseItemForm):
    """
    Class representing base reporting filter form.
    """

    name = wtforms.StringField(
        lazy_gettext("Name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            hawat.forms.check_null_character,
        ],
    )
    source_based = wtforms.RadioField(
        lazy_gettext("Filtering:"),
        validators=[
            wtforms.validators.InputRequired(),
        ],
        choices=[
            (True, lazy_gettext("summary and extra reports")),
            (False, lazy_gettext("target reports")),
        ],
        default=True,
        filters=[hawat.forms.str_to_bool],
        coerce=hawat.forms.str_to_bool,
        description=lazy_gettext(
            "Choose what type of reports will this filter apply to. You can find the type of the "
            "report on the top of the page after opening the report in the web interface.<br/><br/>"
            "Most of the time, summary and extra reports are the correct choice."
        ),
    )
    type = wtforms.SelectField(
        lazy_gettext("Type:"),
        validators=[
            wtforms.validators.DataRequired(),
        ],
        choices=[
            (REPORTING_FILTER_BASIC, lazy_gettext("Basic")),
            (REPORTING_FILTER_ADVANCED, lazy_gettext("Advanced")),
        ],
        description=lazy_gettext(
            "Basic filters allow you to define the rule based on a couple of commonly used "
            "fields from the events.<br/><br/>"
            "Advanced filters allow you to write arbitrarily complex filtering rules."
        ),
    )
    description = wtforms.TextAreaField(
        lazy_gettext("Description:"),
        validators=[
            wtforms.validators.DataRequired(),
        ],
    )
    filter = wtforms.TextAreaField(
        lazy_gettext("Filter:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_filter],
    )
    detectors = wtforms.SelectMultipleField(
        lazy_gettext("Detectors:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    categories = wtforms.SelectMultipleField(
        lazy_gettext("Categories:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    event_classes = wtforms.SelectMultipleField(
        lazy_gettext("Event classes:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    sources = hawat.forms.CommaListField(
        lazy_gettext("Source IPs:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.check_network_record_list,
        ],
        filters=[
            lambda x: x or [],
            lambda lst: [source.replace("[.]", ".") for source in lst],
        ],
        widget=wtforms.widgets.TextArea(),
    )
    targets = hawat.forms.CommaListField(
        lazy_gettext("Target IPs:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.check_network_record_list,
        ],
        filters=[
            lambda x: x or [],
            lambda lst: [source.replace("[.]", ".") for source in lst],
        ],
        widget=wtforms.widgets.TextArea(),
    )
    protocols = wtforms.SelectMultipleField(
        lazy_gettext("Protocols:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        filters=[lambda x: x or []],
    )
    valid_from = hawat.forms.SmartDateTimeField(
        lazy_gettext("Valid from:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.validate_datetime_order(prefix="valid"),
        ],
    )
    valid_to = hawat.forms.SmartDateTimeField(
        lazy_gettext("Valid to:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    enabled = wtforms.RadioField(
        lazy_gettext("State:"),
        validators=[
            wtforms.validators.InputRequired(),
        ],
        choices=[(True, lazy_gettext("Enabled")), (False, lazy_gettext("Disabled"))],
        default=True,
        filters=[hawat.forms.str_to_bool],
        coerce=hawat.forms.str_to_bool,
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Submit"),
    )
    preview = wtforms.SubmitField(
        lazy_gettext("Preview"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detectors.choices = kwargs["choices_detectors"]
        self.categories.choices = kwargs["choices_categories"]
        self.event_classes.choices = [(str(cls), str(cls)) for cls in hawat.forms.get_event_classes()]
        self.protocols.choices = kwargs["choices_protocols"]


class AdminFilterForm(BaseFilterForm):
    """
    Class representing reporting filter create form.
    """

    group = wtforms.SelectField(
        lazy_gettext("Group:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[("", lazy_gettext("Nothing selected"))],
        coerce=hawat.forms.coerce_group,
        description=lazy_gettext(
            "Choose a group that this filter will apply to. If you don't choose any group, this "
            "will be a global filter and will be applied to all groups."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = hawat.forms.get_available_groups()
        self.group.choices[1:] = [(group, group.name) for group in groups]


class PlaygroundFilterForm(flask_wtf.FlaskForm):
    """
    Class representing IP geolocation search form.
    """

    filter = wtforms.TextAreaField(
        lazy_gettext("Filtering rule:"),
        validators=[wtforms.validators.DataRequired(), hawat.forms.check_filter],
    )
    event = wtforms.TextAreaField(
        lazy_gettext("IDEA event:"),
        validators=[wtforms.validators.DataRequired(), check_event],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Check"),
    )


class FilterSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing simple user search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Name, filter, description:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
        filters=[lambda x: x or "", str.strip],
        description=lazy_gettext(
            "Filter`s name, content or description. Search is performed even in the middle of the strings."
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

    type = wtforms.SelectField(
        lazy_gettext("Type:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            (REPORTING_FILTER_BASIC, lazy_gettext("Basic")),
            (REPORTING_FILTER_ADVANCED, lazy_gettext("Advanced")),
        ],
        default="",
        description=lazy_gettext("Search for filters of particular type."),
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
        description=lazy_gettext("Search for filters with particular state."),
    )
    group = wtforms.SelectField(
        lazy_gettext("Group:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("", lazy_gettext("Nothing selected")),
            ("_GLOBAL", lazy_gettext("Global filters (all groups)")),
        ],
        description=lazy_gettext("Search for filters belonging to particular group."),
    )

    filtering = wtforms.SelectField(
        lazy_gettext("Filtering:"),
        choices=[
            ("", lazy_gettext("Nothing selected")),
            ("source", lazy_gettext("summary and extra reports")),
            ("target", lazy_gettext("target reports")),
        ],
        default="",
        description=lazy_gettext("Search for filters that are filtering a particular type of reports."),
    )
    validity = wtforms.SelectField(
        lazy_gettext("Validity:"),
        choices=[
            ("", lazy_gettext("Nothing selected")),
            ("valid", lazy_gettext("valid")),
            ("expired", lazy_gettext("expired")),
            ("future", lazy_gettext("future")),
        ],
        default="",
        description=lazy_gettext("Search for filters that are valid, already expired or will be valid in the future."),
    )
    hits = wtforms.IntegerField(
        lazy_gettext("Number of hits is at least:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        default=0,
        description=lazy_gettext("Search for filters that have at least the specified number of hits."),
    )

    sortby = wtforms.SelectField(
        lazy_gettext("Sort by:"),
        validators=[wtforms.validators.DataRequired()],
        choices=[
            ("createtime.desc", lazy_gettext("by creation time descending")),
            ("createtime.asc", lazy_gettext("by creation time ascending")),
            ("name.desc", lazy_gettext("by netname descending")),
            ("name.asc", lazy_gettext("by netname ascending")),
            ("hits.desc", lazy_gettext("by number of hits descending")),
            ("hits.asc", lazy_gettext("by number of hits ascending")),
            ("last_hit.desc", lazy_gettext("by time of last hit descending")),
            ("last_hit.asc", lazy_gettext("by time of last hit ascending")),
        ],
        default="name.asc",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = hawat.forms.get_available_groups()
        self.group.choices[2:] = [(group.id, group.name) for group in groups]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False
