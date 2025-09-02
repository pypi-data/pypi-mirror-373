#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom network record management forms for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_wtf
import wtforms
from flask_babel import lazy_gettext

import ipranges

import hawat.const
import hawat.db
import hawat.forms
from mentat.datatype.sqldb import NetworkModel


def get_available_sources():
    """
    Query the database for list of network record sources.
    """
    result = hawat.db.db_query(NetworkModel).distinct(NetworkModel.source).order_by(NetworkModel.source).all()
    return [x.source for x in result]


class BaseNetworkForm(hawat.forms.BaseItemForm):
    """
    Class representing base network record form.
    """

    netname = wtforms.StringField(
        lazy_gettext("Netname:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            hawat.forms.check_null_character,
        ],
    )
    source = wtforms.HiddenField(
        default="manual",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
        ],
    )
    network = wtforms.TextAreaField(
        lazy_gettext("Network:"),
        validators=[
            wtforms.validators.DataRequired(),
            hawat.forms.check_network_record,
        ],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
    )
    rank = wtforms.IntegerField(
        lazy_gettext("Rank:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=1, max=10000),
        ],
    )
    description = wtforms.TextAreaField(
        lazy_gettext("Description:"),
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Submit"),
    )
    cancel = wtforms.SubmitField(
        lazy_gettext("Cancel"),
    )

    def validate(self, extra_validators=None):
        is_valid = super().validate(extra_validators)
        if is_valid:
            # Transform IP nets which look like host (e.g. 192.168.0.1/16, see #7843)
            ip_obj = ipranges.from_str(self.network.data)
            self.network.data = f"{ip_obj.single(ip_obj.low())}-{ip_obj.single(ip_obj.high())}"
        return is_valid


class MaintainerNetworkForm(BaseNetworkForm):
    """
    Class representing maintainer network record create form.
    """

    local_id = wtforms.StringField(
        lazy_gettext("Local ID:"),
        validators=[wtforms.validators.Optional(), wtforms.validators.Length(max=20)],
        description=lazy_gettext("User defined local ID for the network."),
    )


class AdminNetworkForm(BaseNetworkForm):
    """
    Class representing network record create form.
    """

    group = wtforms.SelectField(
        lazy_gettext("Group:"),
        validators=[
            wtforms.validators.DataRequired(),
        ],
        choices=[("", lazy_gettext("Nothing selected"))],
        coerce=hawat.forms.coerce_group,
    )
    local_id = wtforms.StringField(
        lazy_gettext("Local ID:"),
        validators=[wtforms.validators.Optional(), wtforms.validators.Length(max=20)],
        description=lazy_gettext("User defined local ID for the network."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        groups = hawat.forms.get_available_groups()
        self.group.choices[1:] = [(group, group.name) for group in groups]


class NetworkSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing simple user search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Netname, network, description:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
        description=lazy_gettext(
            "Network`s name, address or description. Search is performed even in the middle of the strings."
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

    group = wtforms.SelectField(
        lazy_gettext("Group:"),
        validators=[wtforms.validators.Optional()],
        choices=[("", lazy_gettext("Nothing selected"))],
    )
    source = wtforms.SelectField(
        lazy_gettext("Record source:"),
        validators=[wtforms.validators.Optional()],
        default="",
    )

    sortby = wtforms.SelectField(
        lazy_gettext("Sort by:"),
        validators=[wtforms.validators.DataRequired()],
        choices=[
            ("createtime.desc", lazy_gettext("by creation time descending")),
            ("createtime.asc", lazy_gettext("by creation time ascending")),
            ("netname.desc", lazy_gettext("by netname descending")),
            ("netname.asc", lazy_gettext("by netname ascending")),
            ("network.desc", lazy_gettext("by network descending")),
            ("network.asc", lazy_gettext("by network ascending")),
            ("rank.asc", lazy_gettext("by rank ascending")),
            ("rank.desc", lazy_gettext("by rank descending")),
        ],
        default="netname.asc",
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
        source_list = get_available_sources()
        self.source.choices = [("", lazy_gettext("Nothing selected"))] + list(zip(source_list, source_list))
        groups = hawat.forms.get_available_groups()
        self.group.choices[1:] = [(group.id, group.name) for group in groups]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False


class NetworkResolverSearchForm(flask_wtf.FlaskForm):
    """
    Class representing network resolver search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Search group resolver:"),
        validators=[wtforms.validators.DataRequired(), hawat.forms.check_ip_record],
        filters=[lambda x: x or "", str.strip, lambda x: x.replace("[.]", ".")],
    )
    submit = wtforms.SubmitField(
        lazy_gettext("Search"),
    )
