#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom `IDEA <https://idea.cesnet.cz/en/index>`__ event
timeline search form for Hawat application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime

import wtforms
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms


class SimpleAbstractTimelineSearchForm(hawat.forms.EventSearchFormBase):
    """
    Class representing simple event timeline search form.
    """

    section = wtforms.SelectField(
        lazy_gettext("Calculate section:"),
        validators=[wtforms.validators.Optional()],
        filters=[lambda x: x or None],
        default="",
    )
    limit = wtforms.IntegerField(
        lazy_gettext("Toplist limit:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=1, max=1000),
        ],
        default=20,
        description=lazy_gettext(
            "Perform toplisting to given limit for certain calculations like IP addresses and ports."
        ),
    )
    bucket_size = hawat.forms.TimedeltaField(
        lazy_gettext("Bucket size in seconds: "),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.TimedeltaRangeValidator(min_=datetime.timedelta(seconds=1)),
        ],
        default=None,
        description=lazy_gettext(
            "This value is used to group events into buckets for aggregation calculations. The smaller the bucket size, the more detailed the aggregation calculations will be."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.section.choices = kwargs["choices_sections"]

    @classmethod
    def is_csag_context_insignificant(cls, field_name):
        return field_name in (
            "limit",
            "section",
        ) or super().is_csag_context_insignificant(field_name)


class SimpleTimelineSearchForm(SimpleAbstractTimelineSearchForm):
    aggregations = wtforms.SelectMultipleField(
        lazy_gettext("Restrict only to selected aggregations:"),
        validators=[wtforms.validators.Optional()],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Choose only which aggregation calculations to perform. When left empty all calculations will be performed."
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aggregations.choices = kwargs["choices_aggregations"]

    @classmethod
    def is_multivalue(cls, field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return field_name in ("aggregations",) or super().is_multivalue(field_name)

    @classmethod
    def is_csag_context_excluded(cls, field_name):
        return field_name in ("aggregations",) or super().is_csag_context_excluded(field_name)


class SimpleTimelineTabSearchForm(SimpleAbstractTimelineSearchForm):
    pass
