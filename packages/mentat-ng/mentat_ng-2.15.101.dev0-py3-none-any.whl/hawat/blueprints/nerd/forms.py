#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom external NERD database search form for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_wtf
import wtforms
from flask_babel import lazy_gettext

import hawat.forms


class NerdSearchForm(flask_wtf.FlaskForm):
    """
    Class representing NERD database search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Search NERD:"),
        validators=[wtforms.validators.DataRequired(), hawat.forms.check_ip4_record],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Search"),
    )
