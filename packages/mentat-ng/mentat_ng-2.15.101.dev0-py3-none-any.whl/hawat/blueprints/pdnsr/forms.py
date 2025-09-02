#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom external PassiveDNS database search form for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_wtf
import wtforms
from flask_babel import lazy_gettext

import hawat.const
import hawat.forms


class PDNSRSearchForm(flask_wtf.FlaskForm):
    """
    Class representing PassiveDNS service search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Search PassiveDNS:"),
        validators=[wtforms.validators.DataRequired()],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
    )
    sortby = wtforms.SelectField(
        lazy_gettext("Sort by:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("", lazy_gettext("without explicit sorting")),
            ("domain.desc", lazy_gettext("by domain name descending")),
            ("domain.asc", lazy_gettext("by domain name ascending")),
            ("count.desc", lazy_gettext("by hit count descending")),
            ("count.asc", lazy_gettext("by hit count ascending")),
            ("firstseen.desc", lazy_gettext("by first seen time descending")),
            ("firstseen`.asc", lazy_gettext("by first seen time ascending")),
            ("lastseen.desc", lazy_gettext("by last seen time descending")),
            ("lastseen.asc", lazy_gettext("by last seen time ascending")),
        ],
        default="",
    )
    limit = wtforms.SelectField(
        lazy_gettext("Pager limit:"),
        validators=[wtforms.validators.Optional()],
        filters=[int],
        choices=[(0, lazy_gettext("without explicit limit"))] + hawat.const.PAGER_LIMIT_CHOICES,
        default=0,
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Search"),
    )
