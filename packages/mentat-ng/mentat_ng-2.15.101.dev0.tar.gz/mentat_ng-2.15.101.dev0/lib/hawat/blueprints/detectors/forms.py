#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom detector management forms for Hawat.
"""

__author__ = "Rajmund Hruška <rajmund.hruska@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)

import wtforms
from flask_babel import gettext, lazy_gettext

import hawat.const
import hawat.db
import hawat.forms
from mentat.datatype.sqldb import DetectorModel


def get_available_sources():
    """
    Query the database for list of network record sources.
    """
    result = hawat.db.db_query(DetectorModel).distinct(DetectorModel.source).order_by(DetectorModel.source).all()
    return [x.source for x in result]


def check_name_uniqueness(form, field):
    """
    Callback for validating names during detector update action.
    """
    item = (
        hawat.db.db_get()
        .session.query(DetectorModel)
        .filter(DetectorModel.name == field.data)
        .filter(DetectorModel.id != form.db_item_id)
        .all()
    )
    if not item:
        return
    raise wtforms.validators.ValidationError(gettext("Detector with this name already exists."))


class BaseDetectorForm(hawat.forms.BaseItemForm):
    """
    Class representing base detector record form.
    """

    source = wtforms.HiddenField(
        default="manual",
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=50),
        ],
    )
    credibility = wtforms.FloatField(
        lazy_gettext("Credibility:"),
        default=1.0,
        validators=[wtforms.validators.NumberRange(min=0, max=1)],
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


class AdminCreateDetectorForm(BaseDetectorForm):
    """
    Class representing detector record create form.
    """

    name = wtforms.StringField(
        lazy_gettext("Name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            hawat.forms.check_null_character,
            check_name_uniqueness,
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db_item_id = None


class AdminUpdateDetectorForm(BaseDetectorForm):
    """
    Class representing detector record create form.
    """

    name = wtforms.StringField(
        lazy_gettext("Name:"),
        validators=[
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min=3, max=250),
            hawat.forms.check_null_character,
            check_name_uniqueness,
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store the ID of original item in database to enable the ID uniqueness
        # check with check_name_uniqueness() validator.
        self.db_item_id = kwargs["db_item_id"]


class DetectorSearchForm(hawat.forms.BaseSearchForm):
    """
    Class representing simple user search form.
    """

    search = wtforms.StringField(
        lazy_gettext("Name, description:"),
        validators=[
            wtforms.validators.Optional(),
            wtforms.validators.Length(min=3, max=100),
            hawat.forms.check_null_character,
        ],
        filters=[lambda x: x or "", str.strip],
        description=lazy_gettext(
            "Detector`s name or description. Search is performed even in the middle of the strings."
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
            ("name.desc", lazy_gettext("by name descending")),
            ("name.asc", lazy_gettext("by name ascending")),
            ("hits.desc", lazy_gettext("by number of hits descending")),
            ("hits.asc", lazy_gettext("by number of hits ascending")),
            ("credibility.asc", lazy_gettext("by credibility ascending")),
            ("credibility.desc", lazy_gettext("by credibility descending")),
        ],
        default="name.asc",
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

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False
