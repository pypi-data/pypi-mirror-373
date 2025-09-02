#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains global application-wide constants for Hawat user interface.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime
import re


def tr_(val):
    """
    Method for marking translatable strings according to the documentation
    recipe at https://docs.python.org/3/library/gettext.html#deferred-translations.
    """
    return val


CRE_LOGIN = re.compile("^[-_@.a-zA-Z0-9]+$")
"""Compiled regular expression for login validation."""

CRE_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
"""Compiled regular expression for email address format validation."""

CRE_GROUP_NAME = re.compile("^[-_@.a-zA-Z0-9]+$")
"""Compiled regular expression for group name validation."""

CRE_COUNTRY_CODE = re.compile("^[a-zA-Z]{2,3}$")
"""Compiled regular expression for validating language/country codes."""

CRE_LANG_CODE = re.compile("^[a-zA-Z]{2}(_[a-zA-Z]{2})?$")
"""Compiled regular expression for validating language codes."""

DEFAULT_LOCALE = "en"
"""Default application locale."""

DEFAULT_TIMEZONE = "UTC"
"""Default application timezone."""

FLASH_INFO = "info"
"""Class for *info* flash messages."""

FLASH_SUCCESS = "success"
"""Class for *success* flash messages."""

FLASH_WARNING = "warning"
"""Class for *warning* flash messages."""

FLASH_FAILURE = "danger"
"""Class for *failure* flash messages."""

FORM_ACTION_SUBMIT = "submit"
"""Name of the item form *submit* button."""

ACTION_ITEM_CREATE = "create"
"""Name of the item *create* action."""

ACTION_ITEM_CREATEFOR = "createfor"
"""Name of the item *createfor* action."""

ACTION_ITEM_UPDATE = "update"
"""Name of the item *update* action."""

ACTION_ITEM_ENABLE = "enable"
"""Name of the item *enable* action."""

ACTION_ITEM_DISABLE = "disable"
"""Name of the item *disable* action."""

ACTION_ITEM_DELETE = "delete"
"""Name of the item *delete* action."""

ACTION_USER_LOGIN = "login"
"""Name of the user *login* action."""

ACTION_USER_LOGOUT = "logout"
"""Name of the user *logout* action."""

ACTION_USER_REGISTER = "register"
"""Name of the user *register* action."""

MODEL_USER = "user"
"""Name of the 'user' model."""

MODEL_GROUP = "group"
"""Name of the 'user' model."""

MODEL_EVENT_CLASS = "event_class"
"""Name of the 'user' model."""

MODEL_DETECTOR = "detector"
"""Name of the 'detector' model."""

MODEL_ITEM_CHANGELOG = "item_changelog"
"""Name of the 'user' model."""

ROLE_USER = "user"
"""Name of the 'user' role."""

ROLE_DEVELOPER = "developer"
"""Name of the 'developer' role."""

ROLE_MAINTAINER = "maintainer"
"""Name of the 'maintainer' role."""

ROLE_ADMIN = "admin"
"""Name of the 'admin' role."""

ROLES = [ROLE_USER, ROLE_DEVELOPER, ROLE_MAINTAINER, ROLE_ADMIN]
"""List of valid user roles."""

NO_ROLE = "__NO_ROLE__"
"""Special constant for selecting users with no roles."""

CFGKEY_MENU_MAIN_SKELETON = "MENU_MAIN_SKELETON"
"""Configuration key name: Default application main menu skeleton."""

CFGKEY_ENABLED_BLUEPRINTS = "ENABLED_BLUEPRINTS"
"""Configuration key name: List of all requested blueprints."""

CFGKEY_MODELS = "MODELS"
"""Configuration key name: List of all requested blueprints."""

DEFAULT_PAGER_LIMIT = 100
"""Default page limit for pager/paginator."""

PAGER_LIMIT_CHOICES = [
    (5, 5),
    (10, 10),
    (20, 20),
    (25, 25),
    (50, 50),
    (100, 100),
    (200, 200),
    (250, 250),
    (500, 500),
    (1000, 1000),
    (2500, 2500),
    (5000, 5000),
    (10000, 10000),
    (25000, 25000),
    (50000, 50000),
    (100000, 100000),
]
"""List of available valid pager limit choices."""

MAX_NUMBER_OF_PAGES = 2**32 - 1
"""Maximum number of pages that the pager/paginator can handle."""

DEFAULT_RESULT_TIMEDELTA = 7
"""Default result time delta for searching various objects."""

RESOURCE_BABEL = "babel"
"""Name for the ``flask_babel.Babel`` object within the application resources."""

RESOURCE_LOGIN_MANAGER = "login_manager"
"""Name for the ``flask_login.LoginManager`` object within the application resources."""

RESOURCE_MIGRATE = "migrate"
"""Name for the ``flask_migrate.Migrate`` object within the application resources."""

RESOURCE_PRINCIPAL = "principal"
"""Name for the ``flask_principal.Principal`` object within the application resources."""

CFGKEY_MENTAT_CORE = "MENTAT_CORE"
"""Configuration key name: Core Mentat configurations."""


#
# List of all existing Context Search Action Group names (CSAG).
#
CSAG_ABUSE = "abuses"
CSAG_ADDRESS = "ips"
CSAG_CATEGORY = "categories"
CSAG_CLASS = "classes"
CSAG_DETECTOR = "detectors"
CSAG_DETTYPE = "detector_types"
CSAG_HOSTNAMES = "hostnames"
CSAG_HOSTTYPE = "host_types"
CSAG_PORT = "ports"
CSAG_PROTOCOL = "protocols"
CSAG_SEVERITY = "severities"

#
# List of all existing Additional Object Data Service names (AODS).
#
AODS_IP4 = "ip4"
AODS_IP6 = "ip6"
AODS_HOSTNAME = "host"

ICON_NAME_MISSING_ICON = "missing-icon"
"""Name of the icon to display instead of missing icons."""

ICONS = {
    #
    # General icons.
    #
    "login": '<i class="fas fa-fw fa-sign-in-alt"></i>',
    "logout": '<i class="fas fa-fw fa-sign-out-alt"></i>',
    "register": '<i class="fas fa-fw fa-user-plus"></i>',
    "help": '<i class="fas fa-fw fa-question-circle"></i>',
    "language": '<i class="fas fa-fw fa-globe"></i>',
    "role-anonymous": '<i class="fas fa-fw fa-user-secret"></i>',
    "role-user": '<i class="fas fa-fw fa-user"></i>',
    "role-developer": '<i class="fas fa-fw fa-user-md"></i>',
    "role-maintainer": '<i class="fas fa-fw fa-user-tie"></i>',
    "role-admin": '<i class="fas fa-fw fa-user-ninja"></i>',
    #
    # Main site section icons.
    #
    "section-home": '<i class="fas fa-fw fa-home"></i>',
    "section-dashboards": '<i class="fas fa-fw fa-tachometer-alt"></i>',
    "section-administration": '<i class="fas fa-fw fa-cogs"></i>',
    #
    # Built-in module icons.
    #
    "module-home": '<i class="fas fa-fw fa-home"></i>',
    "module-auth-api": '<i class="fas fa-fw fa-id-card-alt"></i>',
    "module-auth-dev": '<i class="fas fa-fw fa-id-card-alt"></i>',
    "module-auth-env": '<i class="fas fa-fw fa-id-card-alt"></i>',
    "module-changelogs": '<i class="fas fa-fw fa-clipboard-list"></i>',
    "module-dashboards": '<i class="fas fa-fw fa-tachometer-alt"></i>',
    "module-dbstatus": '<i class="fas fa-fw fa-database"></i>',
    "module-design": '<i class="fas fa-fw fa-palette"></i>',
    "module-detectors": '<i class="fas fa-fw fa-user-secret"></i>',
    "module-devtools": '<i class="fas fa-fw fa-bug"></i>',
    "module-dnsr": '<i class="fas fa-fw fa-directions"></i>',
    "module-events": '<i class="fas fa-fw fa-bell"></i>',
    "module-event-classes": '<i class="fas fa-fw fa-tag"></i>',
    "module-filters": '<i class="fas fa-fw fa-filter"></i>',
    "module-geoip": '<i class="fas fa-fw fa-map-marked-alt"></i>',
    "module-groups": '<i class="fas fa-fw fa-users"></i>',
    "module-help": '<i class="fas fa-fw fa-question-circle"></i>',
    "module-networks": '<i class="fas fa-fw fa-sitemap"></i>',
    "module-host-info": '<i class="fas fa-fw fa-circle-info"></i>',
    "module-nerd": '<i class="fas fa-fw fa-certificate"></i>',
    "module-pdnsr": '<i class="fas fa-fw fa-compass"></i>',
    "module-performance": '<i class="fas fa-fw fa-chart-bar"></i>',
    "module-reports": '<i class="fas fa-fw fa-newspaper"></i>',
    "module-settings-reporting": '<i class="fas fa-fw fa-sliders-h"></i>',
    "module-skeleton": '<i class="fas fa-fw fa-skull"></i>',
    "module-status": '<i class="fas fa-fw fa-heartbeat"></i>',
    "module-timeline": '<i class="fas fa-fw fa-chart-line"></i>',
    "module-users": '<i class="fas fa-fw fa-user"></i>',
    "module-cross-table": '<i class="fa-solid fa-table"></i>',
    "profile": '<i class="fas fa-fw fa-id-card"></i>',
    "modal-question": '<i class="fas fa-fw fa-question-circle"></i>',
    "missing-icon": '<i class="fas fa-fw fa-question" title="Missing icon"></i>',
    #
    # Action icons.
    #
    "action-sort": '<i class="fas fa-fw fa-sort"></i>',
    "action-sort-asc": '<i class="fas fa-fw fa-sort-up"></i>',
    "action-sort-desc": '<i class="fas fa-fw fa-sort-down"></i>',
    "action-more": '<i class="fas fa-fw fa-cubes"></i>',
    "action-search": '<i class="fas fa-fw fa-search"></i>',
    "action-show": '<i class="fas fa-fw fa-eye"></i>',
    "action-show-user": '<i class="fas fa-fw fa-user-circle"></i>',
    "action-create": '<i class="fas fa-fw fa-plus-circle"></i>',
    "action-create-user": '<i class="fas fa-fw fa-user-plus"></i>',
    "action-update": '<i class="fas fa-fw fa-edit"></i>',
    "action-update-user": '<i class="fas fa-fw fa-user-edit"></i>',
    "action-enable": '<i class="fas fa-fw fa-unlock"></i>',
    "action-enable-user": '<i class="fas fa-fw fa-user-check"></i>',
    "action-disable": '<i class="fas fa-fw fa-lock"></i>',
    "action-disable-user": '<i class="fas fa-fw fa-user-lock"></i>',
    "action-delete": '<i class="fas fa-fw fa-trash"></i>',
    "action-delete-user": '<i class="fas fa-fw fa-user-slash"></i>',
    "action-add-member": '<i class="fas fa-fw fa-user-plus"></i>',
    "action-rej-member": '<i class="fas fa-fw fa-user-minus"></i>',
    "action-rem-member": '<i class="fas fa-fw fa-user-times"></i>',
    "action-add-manager": '<i class="fas fa-fw fa-user-plus"></i>',
    "action-rem-manager": '<i class="fas fa-fw fa-user-times"></i>',
    "action-save": '<i class="fas fa-fw fa-save"></i>',
    "action-download": '<i class="fas fa-fw fa-file-download"></i>',
    "action-download-zip": '<i class="fas fa-fw fa-file-archive"></i>',
    "action-download-csv": '<i class="fas fa-fw fa-file-csv"></i>',
    "action-download-svg": '<i class="fas fa-fw fa-file-image"></i>',
    "action-download-js": '<i class="fab fa-fw fa-js"></i>',
    "action-download-html": '<i class="fas fa-fw fa-file-code"></i>',
    "action-mail": '<i class="fas fa-fw fa-envelope"></i>',
    "action-reload": '<i class="fas fa-fw fa-sync-alt"></i>',
    "action-genkey": '<i class="fas fa-fw fa-key"></i>',
    "action-stop": '<i class="fas fa-fw fa-stop-circle"></i>',
    "alert-success": '<i class="fas fa-fw fa-check-circle"></i>',
    "alert-info": '<i class="fas fa-fw fa-info-circle"></i>',
    "alert-warning": '<i class="fas fa-fw fa-exclamation-circle"></i>',
    "alert-danger": '<i class="fas fa-fw fa-exclamation-triangle"></i>',
    "item-enabled": '<i class="fas fa-fw fa-toggle-on"></i>',
    "item-disabled": '<i class="fas fa-fw fa-toggle-off"></i>',
    "r-t-summary": '<i class="fas fa-fw fa-archive"></i>',
    "r-t-extra": '<i class="fas fa-fw fa-file-alt"></i>',
    "r-t-target": '<i class="fa-regular fa-circle-dot"></i>',
    "r-s-unknown": '<i class="fas fa-fw fa-thermometer-empty"></i>',
    "r-s-info": '<i class="fas fa-fw fa-thermometer-empty"></i>',
    "r-s-low": '<i class="fas fa-fw fa-thermometer-quarter"></i>',
    "r-s-medium": '<i class="fas fa-fw fa-thermometer-half"></i>',
    "r-s-high": '<i class="fas fa-fw fa-thermometer-three-quarters"></i>',
    "r-s-critical": '<i class="fas fa-fw fa-thermometer-full"></i>',
    "report-data-relapsed": '<i class="fas fa-fw fa-sync-alt"></i>',
    "report-data-filtered": '<i class="fas fa-fw fa-filter"></i>',
    "report-data-test": '<i class="fas fa-fw fa-bug"></i>',
    "report-data-mailed": '<i class="fas fa-fw fa-envelope"></i>',
    "ajax-loader": '<i class="fas fa-fw fa-spinner fa-spin fa-4x"></i>',
    "caret-down": '<i class="fas fa-fw fa-caret-square-down"></i>',
    "unassigned": '<i class="fas fa-fw fa-minus"></i>',
    "undisclosed": '<i class="fas fa-fw fa-minus"></i>',
    "calendar": '<i class="fas fa-fw fa-calendar-alt"></i>',
    "stopwatch": '<i class="fas fa-fw fa-stopwatch"></i>',
    "clock": '<i class="fas fa-fw fa-clock"></i>',
    "domain": '<i class="fas fa-fw fa-tag"></i>',
    "time-from": '<i class="fas fa-fw fa-hourglass-start"></i>',
    "time-to": '<i class="fas fa-fw fa-hourglass-end"></i>',
    "debug": '<i class="fas fa-fw fa-bug"></i>',
    "eventclss": '<i class="fas fa-fw fa-book"></i>',
    "reference": '<i class="fas fa-fw fa-external-link-alt"></i>',
    "anchor": '<i class="fas fa-fw fa-anchor"></i>',
    "search": '<i class="fas fa-fw fa-search"></i>',
    "weight": '<i class="fas fa-fw fa-weight"></i>',
    "list": '<i class="fas fa-fw fa-list-ul"></i>',
    "mail": '<i class="fas fa-fw fa-envelope"></i>',
    "redirect": '<i class="fas fa-fw fa-share"></i>',
    "unredirect": '<span class="fa-layers fa-fw"><i class="fas fa-fw fa-share"></i><i class="fas fa-fw fa-ban"></i></span>',
    "mute": '<i class="fas fa-fw fa-volume-off"></i>',
    "unmute": '<i class="fas fa-fw fa-volume-up"></i>',
    "compress": '<i class="fas fa-fw fa-gift"></i>',
    "uncompress": '<span class="fa-layers fa-fw"><i class="fas fa-fw fa-gift"></i><i class="fas fa-fw fa-ban"></i></span>',
    "import": '<i class="fas fa-fw fa-cloud-upload"></i>',
    "export": '<i class="fas fa-fw fa-cloud-download"></i>',
    "validate": '<i class="fas fa-fw fa-check-circle"></i>',
    "min": '<i class="fas fa-fw fa-angle-double-down"></i>',
    "max": '<i class="fas fa-fw fa-angle-double-up"></i>',
    "sum": '<i class="fas fa-fw fa-plus"></i>',
    "cnt": '<i class="fas fa-fw fa-hashtag"></i>',
    "avg": '<i class="fas fa-fw fa-dot-circle"></i>',
    "med": '<i class="fas fa-fw fa-bullseye"></i>',
    "na": '<i class="fas fa-fw fa-times"></i>',
    "stats": '<i class="fas fa-fw fa-bar-chart"></i>',
    "structure": '<i class="fas fa-fw fa-tree"></i>',
    "actions": '<i class="fas fa-fw fa-wrench"></i>',
    "cog": '<i class="fas fa-fw fa-cog"></i>',
    "check": '<i class="fas fa-fw fa-check-square"></i>',
    "check_blank": '<i class="far fa-fw fa-square"></i>',
    "ok": '<i class="fas fa-fw fa-check"></i>',
    "ko": '<i class="fas fa-fw fa-times"></i>',
    "sortasc": '<i class="fas fa-fw fa-sort-asc"></i>',
    "sortdesc": '<i class="fas fa-fw fa-sort-desc"></i>',
    "backtotop": '<i class="fas fa-fw fa-level-up-alt"></i>',
    "first": '<i class="fas fa-fw fa-angle-double-left"></i>',
    "previous": '<i class="fas fa-fw fa-angle-left"></i>',
    "next": '<i class="fas fa-fw fa-angle-right"></i>',
    "last": '<i class="fas fa-fw fa-angle-double-right" aria-hidden="true"></i>',
    "liitem": '<i class="fas fa-li fa-asterisk" aria-hidden="true"></i>',
    "expand": '<i class="fas fa-fw fa-angle-left" aria-hidden="true"></i>',
    "collapse": '<i class="fas fa-fw fa-angle-down" aria-hidden="true"></i>',
    "form-error": '<i class="fas fa-fw fa-exclamation-triangle" aria-hidden="true"></i>',
    "table": '<i class="fas fa-fw fa-table"></i>',
    "quicksearch": '<i class="fab fa-fw fa-searchengin"></i>',
    "playground": '<i class="fas fa-fw fa-gamepad"></i>',
}
"""
Predefined list of selected `font-awesome <https://fontawesome.io/icons/>`__ icons
that are used in this application.
"""

TIME_WINDOWS = {
    "1h": {
        "current": lambda x: (x - datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "next": lambda x: (x + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "2h": {
        "current": lambda x: (x - datetime.timedelta(hours=2)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=2)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "next": lambda x: (x + datetime.timedelta(hours=2)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "3h": {
        "current": lambda x: (x - datetime.timedelta(hours=3)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=3)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "next": lambda x: (x + datetime.timedelta(hours=3)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "4h": {
        "current": lambda x: (x - datetime.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "next": lambda x: (x + datetime.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "6h": {
        "current": lambda x: (x - datetime.timedelta(hours=6)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=6)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "next": lambda x: (x + datetime.timedelta(hours=6)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "12h": {
        "current": lambda x: (x - datetime.timedelta(hours=12)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(hours=12)).replace(
            minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(hours=12)).replace(minute=0, second=0, microsecond=0, tzinfo=None),
    },
    "1d": {
        "current": lambda x: (x - datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "2d": {
        "current": lambda x: (x - datetime.timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "3d": {
        "current": lambda x: (x - datetime.timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=3)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "1w": {
        "current": lambda x: (x - datetime.timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(weeks=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "2w": {
        "current": lambda x: (x - datetime.timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(weeks=2)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "4w": {
        "current": lambda x: (x - datetime.timedelta(weeks=4)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(weeks=4)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(weeks=4)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "12w": {
        "current": lambda x: (x - datetime.timedelta(weeks=12)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(weeks=12)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(weeks=12)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "td": {
        "current": lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "tw": {
        "current": lambda x: (x - datetime.timedelta(days=x.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "previous": lambda x: (x - datetime.timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=7)).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "tm": {
        "current": lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: (x - datetime.timedelta(days=1)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: (x + datetime.timedelta(days=32)).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
    "ty": {
        "current": lambda x: x.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None),
        "previous": lambda x: x.replace(
            year=x.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
        "next": lambda x: x.replace(
            year=x.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None
        ),
    },
}
"""Default list of time windows for 'by time' quicksearch lists."""
