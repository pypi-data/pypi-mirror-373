#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom reporting settings management forms for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import pytz
import wtforms
from flask_babel import lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
import mentat.const


class BaseSettingsReportingForm(hawat.forms.BaseItemForm):
    """
    Class representing base reporting settings form.
    """

    emails_info = hawat.forms.CommaListField(
        lazy_gettext("Target e-mails - severity info and above:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_email_list],
    )
    emails_low = hawat.forms.CommaListField(
        lazy_gettext("Target e-mails - severity low and above:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_email_list],
    )
    emails_medium = hawat.forms.CommaListField(
        lazy_gettext("Target e-mails - severity medium and above:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_email_list],
    )
    emails_high = hawat.forms.CommaListField(
        lazy_gettext("Target e-mails - severity high and above:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_email_list],
    )
    emails_critical = hawat.forms.CommaListField(
        lazy_gettext("Target e-mails - critical severity:"),
        validators=[wtforms.validators.Optional(), hawat.forms.check_email_list],
    )
    locale = wtforms.SelectField(
        lazy_gettext("Locale:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[("", lazy_gettext("<< system default >>"))],
        filters=[lambda x: x or None],
    )
    timezone = wtforms.SelectField(
        lazy_gettext("Timezone:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[("", lazy_gettext("<< system default >>"))] + list(zip(pytz.common_timezones, pytz.common_timezones)),
        filters=[lambda x: x or None],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Submit"),
    )
    cancel = wtforms.SubmitField(
        lazy_gettext("Cancel"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        # Handle additional custom keywords.
        #
        self.locale.choices[1:] = kwargs["locales"]


class MaintainerSettingsReportingForm(BaseSettingsReportingForm):
    """
    Class representing reporting settings form for maintainers.
    """

    redirect = hawat.forms.RadioFieldWithNone(
        lazy_gettext("Report redirection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            (None, lazy_gettext("System default")),
            (True, lazy_gettext("Enabled")),
            (False, lazy_gettext("Disabled")),
        ],
        filters=[hawat.forms.str_to_bool_with_none],
        coerce=hawat.forms.str_to_bool_with_none,
    )
    mode = wtforms.SelectField(
        lazy_gettext("Reporting mode:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("", lazy_gettext("<< system default >>")),
            (mentat.const.REPORTING_MODE_SUMMARY, lazy_gettext("summary")),
            (mentat.const.REPORTING_MODE_EXTRA, lazy_gettext("extra")),
            (mentat.const.REPORTING_MODE_BOTH, lazy_gettext("both")),
            (mentat.const.REPORTING_MODE_NONE, lazy_gettext("none")),
        ],
        filters=[lambda x: x or None],
    )
