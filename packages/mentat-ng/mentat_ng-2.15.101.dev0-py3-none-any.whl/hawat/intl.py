#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains useful internationalization utilities for *Hawat* application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
import flask_babel
import flask_login
from babel import Locale

BABEL = flask_babel.Babel()


def get_locale():  # pylint: disable=locally-disabled,unused-variable
    """
    Implementation of locale selector for :py:mod:`flask_babel`.
    """
    # If a user is logged in, try to use the locale from the user settings.
    if flask_login.current_user.is_authenticated:
        if hasattr(flask_login.current_user, "locale") and flask_login.current_user.locale:
            flask.session["locale"] = flask_login.current_user.locale

    # Store the best locale selection into the session.
    if "locale" not in flask.session or not flask.session["locale"]:
        if flask.current_app.config["BABEL_DETECT_LOCALE"]:
            flask.session["locale"] = flask.request.accept_languages.best_match(
                flask.current_app.config["SUPPORTED_LOCALES"].keys()
            )
        else:
            flask.session["locale"] = flask.current_app.config["BABEL_DEFAULT_LOCALE"]

    if flask.session.get("locale"):
        return flask.session["locale"]
    return flask.current_app.config["BABEL_DEFAULT_LOCALE"]


def get_timezone():  # pylint: disable=locally-disabled,unused-variable
    """
    Implementation of timezone selector for :py:mod:`flask_babel`.
    """
    # If a user is logged in, try to use the timezone from the user settings.
    if flask_login.current_user.is_authenticated:
        if hasattr(flask_login.current_user, "timezone") and flask_login.current_user.timezone:
            flask.session["timezone"] = flask_login.current_user.timezone

    # Store the default timezone selection into the session.
    if "timezone" not in flask.session or not flask.session["timezone"]:
        flask.session["timezone"] = flask.current_app.config["BABEL_DEFAULT_TIMEZONE"]

    if flask.session.get("timezone"):
        return flask.session["timezone"]
    return flask.current_app.config["BABEL_DEFAULT_TIMEZONE"]


def babel_format_bytes(size, unit="B", step_size=1024):
    """
    Format given numeric value to human-readable string describing size in
    B/KB/MB/GB/TB.

    :param int size: Number to be formatted
    :param enum unit: Starting unit, possible values are ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    :param int step_size: Size of the step between units
    :return: Formatted and localized string
    :rtype: string
    """
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    idx_max = len(units) - 1
    unit = unit.upper()
    for idx, val in enumerate(units):
        # Skip the last step, there is no next unit defined after exabyte.
        if idx == idx_max:
            break
        if size > step_size:
            if unit == val:
                size = size / step_size
                unit = units[idx + 1]
        else:
            break
    return f"{flask_babel.format_decimal(size)} {unit}"


def babel_translate_locale(locale_id, with_current=False):
    """
    Translate given locale language. By default, return language in locale`s
    language. Optionally return language in given locale`s language.
    """
    locale_obj = Locale.parse(locale_id)
    if not with_current:
        return locale_obj.language_name
    return locale_obj.get_language_name(flask_babel.get_locale())


def babel_language_in_locale(locale_id="en"):
    """
    Translate given locale language. By default, return language in locale`s
    language. Optionally return language in given locale`s language.
    """
    locale_obj = Locale.parse(flask_babel.get_locale())
    return locale_obj.get_language_name(locale_id)
