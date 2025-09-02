#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains host info forms for Hawat.
"""

__author__ = "Jakub Judiny <jakub.judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_wtf
import wtforms
from flask_babel import lazy_gettext


class HostInfoSearchForm(flask_wtf.FlaskForm):
    """
    Class representing a host info search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Hostname, IPv4 or IPv6 address"),
        validators=[wtforms.validators.DataRequired()],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Search"),
    )
