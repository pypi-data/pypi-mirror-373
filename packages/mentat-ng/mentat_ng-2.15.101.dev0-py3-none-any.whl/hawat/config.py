#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains default configurations for Hawat application. One of the
classes defined in this module may be passed as argument to :py:func:`hawat.app.create_app_full`
factory function to bootstrap Hawat default configurations. These values may be
then optionally overwritten by external configuration file and/or additional
configuration file defined indirrectly via environment variable. Please refer to
the documentation of :py:func:`hawat.app.create_app_full` factory function for more
details on this process.

There are following predefined configuration classess available:

:py:class:`hawat.config.ProductionConfig`
    Default configuration suite for production environments.

:py:class:`hawat.config.DevelopmentConfig`
    Default configuration suite for development environments.

:py:class:`hawat.config.TestingConfig`
    Default configuration suite for testing environments.

There is also following constant structure containing mapping of simple configuration
names to configuration classess:

:py:const:`CONFIG_MAP`

It is used from inside :py:func:`hawat.app.create_app` factory method to pick
and apply correct configuration class to application. Please refer to the documentation
of :py:func:`hawat.app.create_app` factory function for more details on this process.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import collections
import os
import socket
from datetime import timedelta
from typing import Optional

from flask_babel import lazy_gettext

import pyzenkit.jsonconf
import pyzenkit.utils

import hawat.const
import mentat.const
from mentat.datatype.sqldb import (
    EventClassModel,
    GroupModel,
    ItemChangeLogModel,
    UserModel,
)


def _get_cleanup_threshold() -> Optional[timedelta]:
    """
    Extract the smallest event cleanup threshold from cleanup module configuration.
    If module not present, return None
    """
    try:
        from mentat.module.cleanup import (  # pylint: disable=locally-disabled,import-outside-toplevel
            THRESHOLDS,
            MentatCleanupScript,
        )

        cleanup_cfg = pyzenkit.jsonconf.json_load(
            pyzenkit.utils.get_resource_path(os.path.join(mentat.const.PATH_CFG, "mentat-cleanup.py.conf"))
        )
    except (ImportError, FileNotFoundError):
        return None

    cfg_key = MentatCleanupScript.CONFIG_EVENTS

    return min(THRESHOLDS[rule["threshold_type"]]["d"] for rule in cleanup_cfg[cfg_key])


class Config:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Base class for default configurations of Hawat application. You are free to
    extend and customize contents of this class to provide better default values
    for your particular environment.

    The configuration keys must be a valid Flask configuration, and so they must
    be written in UPPERCASE to be correctly recognized.
    """

    APPLICATION_NAME = "Mentat"
    APPLICATION_ID = "mentat"

    # ---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    # ---------------------------------------------------------------------------

    DEBUG = False
    TESTING = False
    SECRET_KEY = "default-secret-key"

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ---------------------------------------------------------------------------
    # Flask extension configurations. Please refer to the documentation of that
    # particular Flask extension for more details.
    # ---------------------------------------------------------------------------

    #
    # Flask-WTF configurations.
    #
    WTF_CSRF_ENABLED = True

    #
    # Custom mail configurations.
    #
    MAIL_DEFAULT_SENDER = f"{APPLICATION_ID}@{socket.getfqdn()}"
    MAIL_SUBJECT_PREFIX = f"[{APPLICATION_NAME}]"

    DISABLE_MAIL_LOGGING = False

    #
    # Flask-Babel configurations.
    #
    BABEL_DEFAULT_LOCALE = hawat.const.DEFAULT_LOCALE
    BABEL_DEFAULT_TIMEZONE = hawat.const.DEFAULT_TIMEZONE
    BABEL_DETECT_LOCALE = True
    """Custom configuration, make detection of best possible locale optional to enable forcing default."""

    #
    # Flask-SQLAlchemy configurations.
    #
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_SETUP_ARGS = {
        "model_class": mentat.datatype.sqldb.MODEL,
        "query_class": mentat.services.sqlstorage.RetryingQuery,
    }

    #
    # Flask-Migrate configurations.
    #
    MIGRATE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

    # ---------------------------------------------------------------------------
    # Custom application configurations.
    # ---------------------------------------------------------------------------

    ROLES = hawat.const.ROLES
    """List of all valid user roles supported by the application."""

    MODELS = {
        hawat.const.MODEL_USER: UserModel,
        hawat.const.MODEL_GROUP: GroupModel,
        hawat.const.MODEL_EVENT_CLASS: EventClassModel,
        hawat.const.MODEL_ITEM_CHANGELOG: ItemChangeLogModel,
    }
    """Models to be used within the application."""

    SUPPORTED_LOCALES = collections.OrderedDict([("en", "English"), ("cs", "Česky")])
    """List of all languages (locales) supported by the application."""

    ENABLED_BLUEPRINTS = [
        "hawat.blueprints.auth",
        "hawat.blueprints.auth_api",
        "hawat.blueprints.design_bs3",
        "hawat.blueprints.devtools",
        "hawat.blueprints.changelogs",
        "hawat.blueprints.auth_env",
        "hawat.blueprints.auth_pwd",
        "hawat.blueprints.home",
        "hawat.blueprints.reports",
        "hawat.blueprints.events",
        "hawat.blueprints.detectors",
        "hawat.blueprints.timeline",
        "hawat.blueprints.dnsr",
        # 'hawat.blueprints.pdnsr',
        "hawat.blueprints.geoip",
        # 'hawat.blueprints.nerd',
        "hawat.blueprints.performance",
        "hawat.blueprints.status",
        "hawat.blueprints.dbstatus",
        "hawat.blueprints.users",
        "hawat.blueprints.groups",
        "hawat.blueprints.settings_reporting",
        "hawat.blueprints.filters",
        "hawat.blueprints.networks",
        "hawat.blueprints.event_classes",
        "hawat.blueprints.host_info",
        "hawat.blueprints.cross_table",
    ]
    """List of requested application blueprints to be loaded during setup."""

    DISABLED_ENDPOINTS: list[str] = []
    """List of endpoints disabled on application level."""

    ENDPOINT_LOGIN = "auth.login"
    """
    Default login view. Users will be redirected to this view in case they are not
    authenticated, but the authentication is required for the requested endpoint.
    """

    LOGIN_MSGCAT = "info"
    """Default message category for messages related to user authentication."""

    ENDPOINT_HOME = "home.index"
    """Homepage endpoint."""

    ENDPOINT_LOGIN_REDIRECT = "home.index"
    """Default redirection endpoint after login."""

    ENDPOINT_LOGOUT_REDIRECT = "home.index"
    """Default redirection endpoint after logout."""

    MENU_MAIN_SKELETON = [
        {
            "entry_type": "submenu",
            "ident": "dashboards",
            "position": 100,
            "title": lazy_gettext("Dashboards"),
            "resptitle": True,
            "icon": "section-dashboards",
        },
        {
            "entry_type": "submenu",
            "ident": "admin",
            "position": 300,
            "authentication": True,
            "authorization": ["power"],
            "title": lazy_gettext("Administration"),
            "resptitle": True,
            "icon": "section-administration",
        },
    ]
    """Configuration of application menu skeleton."""

    EMAIL_ADMINS = [f"root@{socket.getfqdn()}"]
    """List of system administrator emails."""

    EMAIL_MAINTAINERS: list[str] = []
    """Overrides maintainer emails for sending notifications."""

    HAWAT_REPORT_FEEDBACK_MAILS = [f"root@{socket.getfqdn()}"]
    """List of system administrator emails, that receive feedback messages for reports."""

    HAWAT_CHART_TIMELINE_MAXSTEPS = 200
    """Maximal number of steps (bars) displayed in timeline chart."""

    HAWAT_LIMIT_AODS = 20
    """Limit for number of objects for which to automatically fetch additional data services."""

    HAWAT_SEARCH_QUERY_QUOTA = 7
    """Event search query quota per each user."""

    PRIVACY_POLICY_LINK = None
    """URL for the privacy policy in English."""

    PRIVACY_POLICY_LINK_CZ = None
    """URL for the privacy policy in Czech."""

    LOG_DEFAULT_LEVEL = "info"
    """
    Default logging level, case insensitive.
    One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.
    """

    LOG_FILE_LEVEL = "info"
    """
    File logging level, case insensitive.
    One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.
    """

    LOG_EMAIL_LEVEL = "error"
    """
    File logging level, case insensitive.
    One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``.
    """

    ICONS = hawat.const.ICONS

    EVENT_CLEANUP_THRESHOLD = _get_cleanup_threshold()
    """
    Smallest event cleanup threshold from mentat-cleanup.py configuration
    """

    LARGE_FOOTER_ENDPOINTS = [
        ENDPOINT_HOME,
        "auth.register",
        "auth_dev.register",
        "auth_env.register",
        "auth_pwd.register",
    ]
    """
    List of endpoints that should have a large footer.
    """


class ProductionConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *production* environment.
    """


class DevelopmentConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *development* environment.
    """

    DEBUG = True

    # EXPLAIN_TEMPLATE_LOADING = True

    # DEBUG_TB_PROFILER_ENABLED = True

    # ---------------------------------------------------------------------------
    # Custom application configurations.
    # ---------------------------------------------------------------------------

    ENDPOINT_LOGIN = "auth_dev.login"

    ENABLED_BLUEPRINTS = [
        "hawat.blueprints.auth",
        "hawat.blueprints.auth_api",
        "hawat.blueprints.design_bs3",
        "hawat.blueprints.devtools",
        "hawat.blueprints.changelogs",
        "hawat.blueprints.auth_env",
        "hawat.blueprints.auth_dev",
        "hawat.blueprints.auth_pwd",
        "hawat.blueprints.home",
        "hawat.blueprints.reports",
        "hawat.blueprints.events",
        "hawat.blueprints.detectors",
        "hawat.blueprints.timeline",
        "hawat.blueprints.dnsr",
        # 'hawat.blueprints.pdnsr',
        "hawat.blueprints.geoip",
        # 'hawat.blueprints.nerd',
        "hawat.blueprints.performance",
        "hawat.blueprints.status",
        "hawat.blueprints.dbstatus",
        "hawat.blueprints.users",
        "hawat.blueprints.groups",
        "hawat.blueprints.settings_reporting",
        "hawat.blueprints.filters",
        "hawat.blueprints.networks",
        "hawat.blueprints.event_classes",
        "hawat.blueprints.host_info",
        "hawat.blueprints.cross_table",
    ]

    LOG_DEFAULT_LEVEL = "debug"

    LOG_FILE_LEVEL = "debug"


class TestingConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *testing* Hawat applications` configurations.
    """

    TESTING = True

    EXPLAIN_TEMPLATE_LOADING = False

    # ---------------------------------------------------------------------------
    # Custom application configurations.
    # ---------------------------------------------------------------------------

    ENDPOINT_LOGIN = "auth_dev.login"

    ENABLED_BLUEPRINTS = [
        "hawat.blueprints.auth",
        "hawat.blueprints.auth_api",
        "hawat.blueprints.design_bs3",
        "hawat.blueprints.devtools",
        "hawat.blueprints.changelogs",
        "hawat.blueprints.auth_env",
        "hawat.blueprints.auth_dev",
        "hawat.blueprints.auth_pwd",
        "hawat.blueprints.home",
        "hawat.blueprints.reports",
        "hawat.blueprints.events",
        "hawat.blueprints.detectors",
        "hawat.blueprints.timeline",
        "hawat.blueprints.dnsr",
        # 'hawat.blueprints.pdnsr',
        "hawat.blueprints.geoip",
        # 'hawat.blueprints.nerd',
        "hawat.blueprints.performance",
        "hawat.blueprints.status",
        "hawat.blueprints.dbstatus",
        "hawat.blueprints.users",
        "hawat.blueprints.groups",
        "hawat.blueprints.settings_reporting",
        "hawat.blueprints.filters",
        "hawat.blueprints.networks",
        "hawat.blueprints.event_classes",
        "hawat.blueprints.host_info",
        "hawat.blueprints.cross_table",
    ]


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": ProductionConfig,
}
"""Configuration map for easy mapping of configuration aliases to config objects."""


def get_app_root_relative_config():
    """
    These configurations are relative to APP_ROOT_PATH environment setting and
    must be handled separately.
    """
    return {
        "MENTAT_CORE": pyzenkit.jsonconf.config_load_dir(pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG_CORE)),
        "MENTAT_PATHS": {
            "path_crn": pyzenkit.utils.get_resource_path(mentat.const.PATH_CRN),
            "path_cfg": pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG),
            "path_var": pyzenkit.utils.get_resource_path(mentat.const.PATH_VAR),
            "path_log": pyzenkit.utils.get_resource_path(mentat.const.PATH_LOG),
            "path_run": pyzenkit.utils.get_resource_path(mentat.const.PATH_RUN),
            "path_tmp": pyzenkit.utils.get_resource_path(mentat.const.PATH_TMP),
        },
        "MENTAT_CACHE_DIR": pyzenkit.utils.get_resource_path(os.path.join(mentat.const.PATH_VAR, "cache")),
        "MENTAT_CONTROLLER_CFG": pyzenkit.utils.get_resource_path(
            os.path.join(mentat.const.PATH_CFG, "mentat-controller.py.conf")
        ),
        "LOG_FILE": pyzenkit.utils.get_resource_path(os.path.join(mentat.const.PATH_LOG, "mentat-hawat.py.log")),
    }


def get_default_config_file():
    """
    Get path to default configuration file based on the environment.
    """
    return os.path.join(
        pyzenkit.utils.get_resource_path(mentat.const.PATH_CFG),
        "mentat-hawat.py.conf",
    )
