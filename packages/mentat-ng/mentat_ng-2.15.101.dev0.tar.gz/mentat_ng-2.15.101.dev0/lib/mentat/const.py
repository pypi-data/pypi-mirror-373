#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Global constants and utilities for Mentat system.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import random
import re
import string
from enum import StrEnum

# -------------------------------------------------------------------------------


def tr_(val: str) -> str:
    """
    Method for marking translatable strings according to the documentation
    recipe at https://docs.python.org/3/library/gettext.html#deferred-translations.
    """
    return val


def random_str(length=10, letters=string.ascii_lowercase):
    """
    Generate a random string of fixed length from given set of letters.
    """
    return "".join(random.choice(letters) for i in range(length))


# -------------------------------------------------------------------------------


PATH_BIN = "usr/local/bin"
PATH_CRN = "etc/cron.d"
PATH_CFG = "etc/mentat"
PATH_CFG_CORE = os.path.join(PATH_CFG, "core")
PATH_VAR = "var/mentat"
PATH_LOG = os.path.join(PATH_VAR, "log")
PATH_RUN = os.path.join(PATH_VAR, "run")
PATH_TMP = os.path.join(PATH_VAR, "tmp")

# -------------------------------------------------------------------------------

DFLT_EVENT_START = "start"
"""Default name for the *start* event."""
DFLT_EVENT_LOG_STATISTICS = "log_statistics"
"""Default name for the *log_statistics* event."""
DFLT_EVENT_SAVE_RUNLOG = "save_runlog"
"""Default name for the *save_runlog* event."""
DFLT_EVENT_RELOAD = "reload"
"""Default name for the *reload* event."""

DFLT_INTERVAL_RELOAD = 300
"""Default time interval in seconds for reloading internal caches."""
DFLT_INTERVAL_STATISTICS = 20
"""Default time interval in seconds for calculating processing statistics."""
DFLT_INTERVAL_RUNLOG = 60
"""Default time interval in seconds for saving currrent processing runlog."""

DFLT_QUEUE_SIZE_LIMIT = 5000
"""Default limit for number of messages in the queue."""
DFLT_QUEUE_IN_PERMS = 0o775
"""Default interval in seconds for checking the input queue for new messages."""
DFLT_QUEUE_IN_CHECK_INTERVAL = 3
"""Default interval in seconds for checking the input queue for new messages."""
DFLT_QUEUE_OUT_CHECK_INTERVAL = 10
"""Default interval in seconds for checking whether the output queue is full."""

INSPECTOR_DB_CHECK_INTERVAL = 240
"""Default interval in seconds for checking the changes in event classes database in mentat-inspector."""

# -------------------------------------------------------------------------------

CKEY_CORE_DATABASE = "__core__database"
"""Name of the configuration key for ``core database`` configurations."""
CKEY_CORE_DATABASE_SQLSTORAGE = "sqlstorage"
"""Name of the configuration subkey key for ``sqlservice`` configuration in ``core database`` configurations."""
CKEY_CORE_DATABASE_EVENTSTORAGE = "eventstorage"
"""Name of the configuration subkey key for ``eventservice`` configuration in ``core database`` configurations."""
CKEY_CORE_DATABASE_CONNECTION = "connection"
"""Name of the configuration subkey key for ``connection`` configuration in ``core database`` configurations."""
CKEY_CORE_DATABASE_CONFIG = "config"
"""Name of the configuration subkey key for ``config`` configuration in ``core database`` configurations."""
CKEY_CORE_DATABASE_SCHEMA = "schema"
"""Name of the configuration subkey key for ``schema`` configuration in ``core database`` configurations."""

# -------------------------------------------------------------------------------

CKEY_CORE_SERVICES = "__core__services"
"""Name of the configuration key for ``core services`` configurations."""
CKEY_CORE_SERVICES_DNS = "dns"
"""Name of the configuration subkey key for ``DNS`` configuration in ``core services`` configurations."""
CKEY_CORE_SERVICES_PDNS = "pdns"
"""Name of the configuration subkey key for ``PassiveDNS`` configuration in ``core services`` configurations."""
CKEY_CORE_SERVICES_GEOIP = "geoip"
"""Name of the configuration subkey key for ``GeoIP`` configuration in ``core services`` configurations."""
CKEY_CORE_SERVICES_NERD = "nerd"
"""Name of the configuration subkey key for ``NERD`` configuration in ``core services`` configurations."""
CKEY_CORE_SERVICES_WHOIS = "whois"
"""Name of the configuration subkey key for ``whois`` configuration in ``core services`` configurations."""
CKEY_CORE_SERVICES_CACHE = "cache"
"""Name of the configuration subkey key for ``cache`` configuration in ``core services`` configurations."""

# -------------------------------------------------------------------------------

CKEY_CORE_REPORTER = "__core__reporter"
"""Name of the configuration key for ``core reporter`` configurations."""
CKEY_CORE_REPORTER_REPORTSDIR = "reports_dir"
"""Name of the configuration subkey key for ``reports dir`` configuration in ``core reporter`` configurations."""
CKEY_CORE_REPORTER_TEMPLATESDIR = "templates_dir"
"""Name of the configuration subkey key for ``templates dir`` configuration in ``core reporter`` configurations."""
CKEY_CORE_REPORTER_TEMPLATEVARS = "template_vars"
"""Name of the configuration subkey key for ``template vars`` configuration in ``core reporter`` configurations."""
CKEY_CORE_REPORTER_FALLBACK = "fallback"
"""Name of the configuration subkey key for ``fallback`` configuration in ``core reporter`` configurations."""
CKEY_CORE_REPORTER_DEFAULTLOCALE = "default_reporting_locale"
"""Name of the configuration subkey key for ``default_reporting_locale`` configuration in ``core reporter`` configurations."""
CKEY_CORE_REPORTER_DEFAULTTIMEZONE = "default_reporting_timezone"
"""Name of the configuration subkey key for ``default_reporting_timezone`` configuration in ``core reporter`` configurations."""

CKEY_CORE_INFORMANT = "__core__informant"
"""Name of the configuration key for ``core informant`` configurations."""
CKEY_CORE_INFORMANT_REPORTSDIR = "reports_dir"
"""Name of the configuration subkey key for ``reports dir`` configuration in ``core informant`` configurations."""

CKEY_CORE_STATISTICS = "__core__statistics"
"""Name of the configuration key for ``core statistics`` configurations."""
CKEY_CORE_STATISTICS_RRDSDIR = "rrds_dir"
"""Name of the configuration subkey key for ``RRDs dir`` configuration in ``core statistics`` configurations."""
CKEY_CORE_STATISTICS_REPORTSDIR = "reports_dir"
"""Name of the configuration subkey key for ``reports dir`` configuration in ``core statistics`` configurations."""

# -------------------------------------------------------------------------------

EVENT_SEVERITY_INFO = tr_("info")
EVENT_SEVERITY_LOW = tr_("low")
EVENT_SEVERITY_MEDIUM = tr_("medium")
EVENT_SEVERITY_HIGH = tr_("high")
EVENT_SEVERITY_CRITICAL = tr_("critical")

EVENT_SEVERITIES = (
    EVENT_SEVERITY_INFO,
    EVENT_SEVERITY_LOW,
    EVENT_SEVERITY_MEDIUM,
    EVENT_SEVERITY_HIGH,
    EVENT_SEVERITY_CRITICAL,
)

REPORTING_MODE_SUMMARY = tr_("summary")
REPORTING_MODE_EXTRA = tr_("extra")
REPORTING_MODE_BOTH = tr_("both")
REPORTING_MODE_NONE = tr_("none")

REPORTING_MODES = (
    REPORTING_MODE_SUMMARY,
    REPORTING_MODE_EXTRA,
    REPORTING_MODE_BOTH,
    REPORTING_MODE_NONE,
)

REPORTING_TIMING_DEFAULT = tr_("default")
REPORTING_TIMING_CUSTOM = tr_("custom")

REPORTING_TIMING_DEFAULT_INFO_PER = tr_("1day")
REPORTING_TIMING_DEFAULT_INFO_THR = tr_("4weeks")
REPORTING_TIMING_DEFAULT_INFO_REL = tr_("1week")
REPORTING_TIMING_DEFAULT_LOW_PER = tr_("1day")
REPORTING_TIMING_DEFAULT_LOW_THR = tr_("6days")
REPORTING_TIMING_DEFAULT_LOW_REL = tr_("2days")
REPORTING_TIMING_DEFAULT_MEDIUM_PER = tr_("2hrs")
REPORTING_TIMING_DEFAULT_MEDIUM_THR = tr_("6days")
REPORTING_TIMING_DEFAULT_MEDIUM_REL = tr_("2days")
REPORTING_TIMING_DEFAULT_HIGH_PER = tr_("10mins")
REPORTING_TIMING_DEFAULT_HIGH_THR = tr_("1day")
REPORTING_TIMING_DEFAULT_HIGH_REL = tr_("12hrs")
REPORTING_TIMING_DEFAULT_CRITICAL_PER = tr_("10mins")
REPORTING_TIMING_DEFAULT_CRITICAL_THR = tr_("2hrs")
REPORTING_TIMING_DEFAULT_CRITICAL_REL = tr_("none")

REPORTING_TIMING_TARGET_INFO_THR = tr_("none")
REPORTING_TIMING_TARGET_INFO_REL = tr_("none")
REPORTING_TIMING_TARGET_LOW_THR = tr_("none")
REPORTING_TIMING_TARGET_LOW_REL = tr_("none")
REPORTING_TIMING_TARGET_MEDIUM_THR = tr_("none")
REPORTING_TIMING_TARGET_MEDIUM_REL = tr_("none")
REPORTING_TIMING_TARGET_HIGH_THR = tr_("none")
REPORTING_TIMING_TARGET_HIGH_REL = tr_("none")
REPORTING_TIMING_TARGET_CRITICAL_THR = tr_("none")
REPORTING_TIMING_TARGET_CRITICAL_REL = tr_("none")

REPORTING_TIMINGS = (REPORTING_TIMING_DEFAULT, REPORTING_TIMING_CUSTOM)

REPORTING_FILTER_BASIC = tr_("basic")
REPORTING_FILTER_ADVANCED = tr_("advanced")

REPORTING_FILTERS = (REPORTING_FILTER_BASIC, REPORTING_FILTER_ADVANCED)

REPORTING_INTERVALS = {
    "none": 0,
    "5mins": 300,
    "10mins": 600,
    "15mins": 900,
    "20mins": 1200,
    "30mins": 1800,
    "1hr": 3600,
    "2hrs": (3600 * 2),
    "3hrs": (3600 * 3),
    "4hrs": (3600 * 4),
    "6hrs": (3600 * 6),
    "8hrs": (3600 * 8),
    "12hrs": (3600 * 12),
    "1day": 86400,
    "2days": (86400 * 2),
    "3days": (86400 * 3),
    "4days": (86400 * 4),
    "5days": (86400 * 5),
    "6days": (86400 * 6),
    "1week": 604800,
    "8days": (86400 * 8),
    "9days": (86400 * 9),
    "10days": (86400 * 10),
    "11days": (86400 * 10),
    "12days": (86400 * 10),
    "13days": (86400 * 10),
    "2weeks": (604800 * 2),
    "3weeks": (604800 * 3),
    "4weeks": (604800 * 4),
}

DFLT_REPORTING_MODE = REPORTING_MODE_EXTRA
DFLT_REPORTING_TEMPLATE = "default"
DFLT_REPORTING_LOCALE = "en"
DFLT_REPORTING_TIMEZONE = "UTC"
DFLT_REPORTING_TIMING = REPORTING_TIMING_DEFAULT
DFLT_REPORTING_MUTE = False
DFLT_REPORTING_REDIRECT = False

REPORTING_INTERVALS_INV = {v: k for k, v in REPORTING_INTERVALS.items()}

REPORT_TYPE_SUMMARY = REPORTING_MODE_SUMMARY
REPORT_TYPE_EXTRA = REPORTING_MODE_EXTRA
REPORT_TYPE_TARGET = tr_("target")
REPORT_TYPES = (REPORT_TYPE_SUMMARY, REPORT_TYPE_EXTRA, REPORT_TYPE_TARGET)

REPORT_SEVERITIES = (
    EVENT_SEVERITY_INFO,
    EVENT_SEVERITY_LOW,
    EVENT_SEVERITY_MEDIUM,
    EVENT_SEVERITY_HIGH,
    EVENT_SEVERITY_CRITICAL,
)


class EventSections(StrEnum):
    """
    Represents key sections of the event, which is used
    for e.g. event aggregation in reporting.
    """

    MAIN = "Main"
    SOURCE = "Source"
    TARGET = "Target"


NAGIOS_PLUGIN_RC_OK = 0
NAGIOS_PLUGIN_RC_WARNING = 1
NAGIOS_PLUGIN_RC_CRITICAL = 2
NAGIOS_PLUGIN_RC_UNKNOWN = 3


RE_REPORT_FILE_TIMESTAMP = re.compile(r"^[^\d]*([\d]{8})")
"""Regular expression for parsing out the report timestamp from attachment file name."""


def construct_report_dirpath(basedirpath, filename, check=False):
    r"""
    Construct target report directory path based on given base path and file name.

    If filename contains timestamp information ([\d]{8}), place that file
    into another subdirectory. This approach is a solution to report directory
    containing hundreds of thousands of files.
    """
    try:
        subdirname = RE_REPORT_FILE_TIMESTAMP.match(filename).group(1)
        dirpath = os.path.join(basedirpath, subdirname)
        if check and not os.path.isdir(dirpath):
            return basedirpath
        return dirpath
    except:  # pylint: disable=locally-disabled,bare-except
        return basedirpath
