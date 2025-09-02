#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains various `IDEA <https://idea.cesnet.cz/en/index>`__ event
database search forms for Hawat application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import wtforms
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
from hawat.forms import EventSearchFormBase


class SimpleEventSearchForm(EventSearchFormBase):
    """
    Class representing simple event search form.
    """

    sortby = wtforms.SelectField(
        lazy_gettext("Sort by:"),
        validators=[wtforms.validators.DataRequired()],
        choices=[
            ("detecttime.desc", lazy_gettext("by detection time descending")),
            ("detecttime.asc", lazy_gettext("by detection time ascending")),
            ("storagetime.desc", lazy_gettext("by storage time descending")),
            ("storagetime.asc", lazy_gettext("by storage time ascending")),
        ],
        default="detecttime.desc",
    )

    @classmethod
    def is_csag_context_excluded(cls, field_name):
        return field_name in ("sortby",) or super().is_csag_context_excluded(field_name)


class EventDashboardForm(hawat.forms.HawatBaseForm):
    """
    Class representing event dashboard search form.
    """

    dt_from = hawat.forms.SmartDateTimeField(
        lazy_gettext("From:"),
        validators=[
            wtforms.validators.Optional(),
            hawat.forms.validate_datetime_order(prefix="dt"),
        ],
        description=lazy_gettext(
            "Lower time boundary for event detection time as provided by event detector. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event detectors are usually outside of the control of Mentat system administrators and may sometimes emit events with invalid detection times, for example timestamps in the future."
        ),
        default=lambda: hawat.forms.default_dt_with_delta(hawat.const.DEFAULT_RESULT_TIMEDELTA),
    )
    dt_to = hawat.forms.SmartDateTimeField(
        lazy_gettext("To:"),
        validators=[wtforms.validators.Optional()],
        description=lazy_gettext(
            "Upper time boundary for event detection time as provided by event detector. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event detectors are usually outside of the control of Mentat system administrators and may sometimes emit events with invalid detection times, for example timestamps in the future."
        ),
        default=hawat.forms.default_dt,
    )
    submit = wtforms.SubmitField(lazy_gettext("Search"))

    @classmethod
    def is_csag_context_excluded(cls, field_name):
        return field_name in ("submit",) or super().is_csag_context_excluded(field_name)

    @classmethod
    def is_csag_context_insignificant(cls, field_name):
        return field_name in (
            "dt_from",
            "dt_to",
        ) or super().is_csag_context_insignificant(field_name)
