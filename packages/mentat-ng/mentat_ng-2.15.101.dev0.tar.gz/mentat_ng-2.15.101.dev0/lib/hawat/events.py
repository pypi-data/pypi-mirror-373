#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains couple of simple helpers for working with IDEA messages.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from datetime import datetime, timedelta
from typing import Optional

import flask

import mentat.services.eventstorage

_DB = None


def _get_values(column):
    return db_get().fetch_enum_values(column)


def get_event_source_types():
    """
    Return list of all available event source types.
    """
    return _get_values("source_type")


def get_event_target_types():
    """
    Return list of all available event target types.
    """
    return _get_values("target_type")


def get_event_detector_types():
    """
    Return list of all available event detector types.
    """
    return _get_values("node_type")


def get_event_detectors():
    """
    Return list of all available event detectors.
    """
    return _get_values("node_name")


def get_event_categories():
    """
    Return list of all available event categories.
    """
    return _get_values("category")


def get_event_severities():
    """
    Return list of all available event severities.
    """
    return _get_values("eventseverity")


def get_target_severities():
    """
    Return list of all available target severities.
    """
    return _get_values("targetseverity")


def get_event_classes():
    """
    Return list of all available event classes.
    """
    return _get_values("eventclass")


def get_target_classes():
    """
    Return list of all available target classes.
    """
    return _get_values("targetclass")


def get_event_protocols():
    """
    Return list of all available event protocols.
    """
    return _get_values("protocol")


def get_event_inspection_errs():
    """
    Return list of all available event inspection errors.
    """
    return _get_values("inspectionerrors")


def get_event_TLPs():
    """
    Return list of all available event inspection errors.
    """
    return _get_values("tlp")


def db_settings(app):
    """
    Return database settings from Mentat core configurations.

    :return: Database settings.
    :rtype: dict
    """
    return app.mconfig


def get_event_enums():
    # Get lists of available options for various event search form select fields.
    enums = {}
    enums.update(
        source_types=get_event_source_types(),
        target_types=get_event_target_types(),
        detectors=get_event_detectors(),
        detector_types=get_event_detector_types(),
        categories=get_event_categories(),
        severities=get_event_severities(),
        target_severities=get_target_severities(),
        classes=get_event_classes(),
        target_classes=get_target_classes(),
        protocols=get_event_protocols(),
        inspection_errs=get_event_inspection_errs(),
        TLPs=get_event_TLPs(),
    )
    enums.update(
        host_types=sorted(set(enums["source_types"] + enums["target_types"])),
    )
    return enums


def get_event_form_choices():
    enums = get_event_enums()
    choices = {}
    for key, vals in enums.items():
        choices[key] = list(zip(vals, vals))
    return choices


def db_init(app):
    """
    Initialize connection to event database.
    """
    mentat.services.eventstorage.init(db_settings(app))
    app.eventdb = mentat.services.eventstorage.service()


def db_get():
    """
    Opens a new database connection if there is none yet for the
    current application context.

    :return: Database storage handler.
    :rtype: flask_sqlalchemy.SQLAlchemy
    """
    return mentat.services.eventstorage.service()


def db_cursor():
    """
    Convenience method.
    """
    return db_get().session


def get_after_cleanup(dt: datetime) -> bool:
    """
    Returns True if there is the cleanup module present and the provied time
    comes before the latest cleanup time derived from the cleanup module configuration.
    Otherwise returns False.

    Please note, that if the cleanup module is present, this function will return these
    values regardless of the running state of the module.
    """
    threshold: Optional[timedelta] = flask.current_app.config["EVENT_CLEANUP_THRESHOLD"]
    if threshold is None:
        return False
    return dt <= datetime.now() - threshold
