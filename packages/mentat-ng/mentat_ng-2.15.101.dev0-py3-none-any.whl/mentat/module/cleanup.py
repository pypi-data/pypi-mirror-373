#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing database and cache cleanup functions and
features.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-cleanup.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-cleanup.py --debug

    # Run with increased logging level.
    mentat-cleanup.py --log-level debug


Available script commands
-------------------------

``cleanup`` (*default*)
    Perform cleanup of configured database collections and directory caches.


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--db-path dir-name``
    Path to database files (for disk usage measurements).

    *Type:* ``string``, *default:* ``/var/lib/postgresql``

``--simulate``
    Perform simulation, do not remove anything (*flag*).

    *Type:* ``boolean``, *default:* ``False``

Available cleanup thresholds
----------------------------

* ``3y``:  items older than three years
* ``2y``:  items older than two years
* ``y``:   items older than one year
* ``9m``:  items older than nine months
* ``6m``:  items older than six months
* ``4m``:  items older than four months
* ``3m``:  items older than three months
* ``16w``: items older than sixteen weeks
* ``12w``: items older than twelwe weeks
* ``8w``:  items older than eight weeks
* ``4w``:  items older than four weeks
* ``2w``:  items older than two weeks
* ``w``:   items older than one week
* ``6d``:  items older than six days
* ``5d``:  items older than five days
* ``4d``:  items older than four days
* ``3d``:  items older than three days
* ``2d``:  items older than two days
* ``d``:   items older than one day
* ``12h``: items older than twelve hours
* ``8h``:  items older than eight hours
* ``6h``:  items older than six hours
* ``4h``:  items older than four hours
* ``3h``:  items older than three hours
* ``2h``:  items older than two hours
* ``h``:   items older than one hour
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import glob
import json
import os
from typing import TypedDict

import pydgets.widgets

import mentat.const
import mentat.script.fetcher

#
# Global variables.
#
SECS_YEAR = 31556926
"""Number of seconds in a year (approximate)."""


class ThresholdDictType(TypedDict):
    l: str
    d: datetime.timedelta


THRESHOLDS: dict[str, ThresholdDictType] = {
    "3y": {
        "l": "items older than three years",
        "d": datetime.timedelta(seconds=int(SECS_YEAR * 3)),
    },
    "2y": {
        "l": "items older than two years",
        "d": datetime.timedelta(seconds=int(SECS_YEAR * 2)),
    },
    "y": {
        "l": "items older than one year",
        "d": datetime.timedelta(seconds=int(SECS_YEAR)),
    },
    "9m": {
        "l": "items older than nine months",
        "d": datetime.timedelta(seconds=int((SECS_YEAR / 4) * 3)),
    },
    "6m": {
        "l": "items older than six months",
        "d": datetime.timedelta(seconds=int(SECS_YEAR / 2)),
    },
    "4m": {
        "l": "items older than four months",
        "d": datetime.timedelta(seconds=int(SECS_YEAR / 3)),
    },
    "3m": {
        "l": "items older than three months",
        "d": datetime.timedelta(seconds=int(SECS_YEAR / 4)),
    },
    "16w": {"l": "items older than sixteen weeks", "d": datetime.timedelta(weeks=16)},
    "12w": {"l": "items older than twelve weeks", "d": datetime.timedelta(weeks=12)},
    "8w": {"l": "items older than eight weeks", "d": datetime.timedelta(weeks=8)},
    "4w": {"l": "items older than four weeks", "d": datetime.timedelta(weeks=4)},
    "2w": {"l": "items older than two weeks", "d": datetime.timedelta(weeks=2)},
    "w": {"l": "items older than one week", "d": datetime.timedelta(weeks=1)},
    "6d": {"l": "items older than six days", "d": datetime.timedelta(days=6)},
    "5d": {"l": "items older than five days", "d": datetime.timedelta(days=5)},
    "4d": {"l": "items older than four days", "d": datetime.timedelta(days=4)},
    "3d": {"l": "items older than three days", "d": datetime.timedelta(days=3)},
    "2d": {"l": "items older than two days", "d": datetime.timedelta(days=2)},
    "d": {"l": "items older than one day", "d": datetime.timedelta(days=1)},
    "12h": {"l": "items older than twelve hours", "d": datetime.timedelta(hours=12)},
    "8h": {"l": "items older than eight hours", "d": datetime.timedelta(hours=8)},
    "6h": {"l": "items older than six hours", "d": datetime.timedelta(hours=6)},
    "4h": {"l": "items older than four hours", "d": datetime.timedelta(hours=4)},
    "3h": {"l": "items older than three hours", "d": datetime.timedelta(hours=3)},
    "2h": {"l": "items older than two hours", "d": datetime.timedelta(hours=2)},
    "h": {"l": "items older than one hour", "d": datetime.timedelta(hours=1)},
}
"""List of possible cleanup thresholds."""


def json_dump_cbk(obj):
    """
    Callback method for serializing objects into JSON.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    return repr(obj)


class MentatCleanupScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing database and cache cleanup
    functions and features.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_DB_PATH = "db_path"
    CONFIG_SIMULATE = "simulate"
    CONFIG_EVENTS = "events"
    CONFIG_TABLES = "tables"
    CONFIG_CACHES = "caches"
    CONFIG_RUNLOGS = "runlogs"

    def __init__(self):
        """
        Initialize cleanup script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.eventservice = None
        self.sqlservice = None

        super().__init__(description="mentat-cleanup.py - Mentat system database and cache cleanup script")

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser. This method overrides the
        base implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this script object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for custom script arguments.
        #
        arggroup_script = argparser.add_argument_group("custom script arguments")

        arggroup_script.add_argument(
            "--db-path",
            help="filesystem path to database files",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--simulate",
            help="perform simulation, do not remove anything (flag)",
            action="store_true",
            default=None,
        )

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default script configurations. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_DB_PATH, "/var/lib/postgresql"),
            (self.CONFIG_SIMULATE, False),
            (self.CONFIG_EVENTS, []),
            (self.CONFIG_TABLES, []),
            (self.CONFIG_CACHES, []),
            (self.CONFIG_RUNLOGS, []),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _sub_stage_init(self, **kwargs):
        """
        **SUBCLASS HOOK**: Perform additional custom initialization actions.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from constructor.
        """
        # Override default 'interval' value.
        self.config[self.CONFIG_INTERVAL] = "daily"

    # ---------------------------------------------------------------------------

    def _sub_runlog_analyze(self, runlog, analysis):
        """
        Analyze given runlog (hook for subclasses).
        """
        command = runlog.get(self.RLANKEY_COMMAND, None)
        if command == "cleanup":
            analysis[command] = {
                "caches": {},
                "events": {},
                "runlogs": {},
                "tables": {},
            }
            for rule in runlog[command].get("events", []):
                for counter in ("removed_cnt",):
                    analysis[command]["events"][counter] = analysis[command]["events"].get(counter, 0) + rule.get(
                        counter, 0
                    )
            for table in runlog[command].get("tables", []):
                for counter in ("removed_cnt",):
                    analysis[command]["tables"][counter] = analysis[command]["tables"].get(counter, 0) + table.get(
                        counter, 0
                    )
            for cachedir in runlog[command].get("caches", []):
                for counter in (
                    "files_cnt",
                    "files_bytes",
                    "kept_cnt",
                    "kept_bytes",
                    "removed_cnt",
                    "removed_bytes",
                    "error_cnt",
                ):
                    analysis[command]["caches"][counter] = analysis[command]["caches"].get(counter, 0) + cachedir.get(
                        counter, 0
                    )
            for runlogdir in runlog[command].get("runlogs", []):
                for counter in (
                    "files_cnt",
                    "files_bytes",
                    "kept_cnt",
                    "kept_bytes",
                    "removed_cnt",
                    "removed_bytes",
                    "error_cnt",
                ):
                    analysis[command]["runlogs"][counter] = analysis[command]["runlogs"].get(
                        counter, 0
                    ) + runlogdir.get(counter, 0)
        return analysis

    def _sub_runlog_format_analysis(self, analysis):
        """
        Format runlog analysis (hook for subclasses).
        """
        if analysis.get(self.RLANKEY_COMMAND) == "cleanup":
            tablew = pydgets.widgets.TableWidget()
            table_columns = [
                {"label": "Filter"},
                {"label": "Removed [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Count [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "DB size [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Storage size [MB]", "data_type": "sizemb", "align": ">"},
            ]
            table_data = []
            for rule in analysis[self.RLANKEY_RUNLOG]["cleanup"]["events"]:
                table_data.append(
                    [
                        rule["filter"],
                        int(rule["removed_cnt"]),
                        int(rule["stats_post"]["tables"]["events"]["row_estimate"]),
                        rule["stats_post"]["tables"]["events"]["table_bytes"],
                        rule["stats_post"]["tables"]["events"]["total_bytes"],
                    ]
                )
            self.p("")
            self.p("Event cleanup statistics:")
            self.p("\n".join(tablew.render(table_data, columns=table_columns)))

            tablew = pydgets.widgets.TableWidget()
            table_columns = [
                {"label": "Table"},
                {"label": "Removed [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Count [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "DB size [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Storage size [MB]", "data_type": "sizemb", "align": ">"},
            ]
            table_data = []
            for rule in analysis[self.RLANKEY_RUNLOG]["cleanup"]["tables"]:
                table_data.append(
                    [
                        rule["table"],
                        int(rule["removed_cnt"]),
                        int(rule["stats_post"]["tables"][rule["table"]]["row_estimate"]),
                        rule["stats_post"]["tables"][rule["table"]]["table_bytes"],
                        rule["stats_post"]["tables"][rule["table"]]["total_bytes"],
                    ]
                )
            self.p("")
            self.p("Table cleanup statistics:")
            self.p("\n".join(tablew.render(table_data, columns=table_columns)))

            table_columns = [
                {"label": "Cache"},
                {"label": "Removed [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Removed [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Files [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Size [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Errors [#]", "data_formating": "{:,d}", "align": ">"},
            ]
            table_data = []
            for cachedir in analysis[self.RLANKEY_RUNLOG]["cleanup"]["caches"]:
                table_data.append(
                    [
                        cachedir["cache"],
                        cachedir["removed_cnt"],
                        cachedir["removed_bytes"],
                        cachedir["kept_cnt"],
                        cachedir["kept_bytes"],
                        cachedir["error_cnt"],
                    ]
                )
            self.p("")
            self.p("Cache cleanup statistics:")
            self.p("\n".join(tablew.render(table_data, columns=table_columns)))

            table_columns = [
                {"label": "Runlogdir"},
                {"label": "Removed [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Removed [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Files [#]", "data_formating": "{:,d}", "align": ">"},
                {"label": "Size [MB]", "data_type": "sizemb", "align": ">"},
                {"label": "Errors [#]", "data_formating": "{:,d}", "align": ">"},
            ]
            table_data = []
            for runlogdir in analysis[self.RLANKEY_RUNLOG]["cleanup"]["runlogs"]:
                table_data.append(
                    [
                        runlogdir["runlogdir"],
                        runlogdir["removed_cnt"],
                        runlogdir["removed_bytes"],
                        runlogdir["kept_cnt"],
                        runlogdir["kept_bytes"],
                        runlogdir["error_cnt"],
                    ]
                )
            self.p("")
            self.p("Runlog cleanup statistics:")
            self.p("\n".join(tablew.render(table_data, columns=table_columns)))

    def _sub_runlogs_format_evaluation(self, evaluation):
        """
        Format runlog evaluations (hook for subclasses).
        """
        tablew = pydgets.widgets.TableWidget()

        table_columns = [
            {"label": "Date"},
            {"label": "DB removed [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "TB removed [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "FS removed [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "RL removed [#]", "data_formating": "{:,d}", "align": ">"},
        ]
        table_data = []
        for anl in evaluation[self.RLEVKEY_ANALYSES]:
            clrslt = anl.get("cleanup", None)
            if clrslt:
                table_data.append(
                    [
                        anl["label"],
                        anl["cleanup"]["events"].get("removed_cnt", 0),
                        anl["cleanup"]["tables"].get("removed_cnt", 0),
                        anl["cleanup"]["caches"].get("removed_cnt", 0),
                        anl["cleanup"]["runlogs"].get("removed_cnt", 0),
                    ]
                )
            else:
                table_data.append(
                    [
                        anl["label"],
                        0,
                        0,
                        0,
                        0,
                    ]
                )
        self.p("")
        self.p("Result overview for 'cleanup' command:")
        self.p("\n".join(tablew.render(table_data, columns=table_columns)))

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "cleanup"

    def cbk_command_cleanup(self):
        """
        Implementation of the **cleanup** command (*default*).

        Perform cleanup of configured database collections and directory caches.
        """
        dt_current = datetime.datetime.utcnow()
        self.logger.info("Cleanup started with reference time '%s'.", dt_current.isoformat())

        if self.c(self.CONFIG_SIMULATE):
            self.logger.warning("Running in simulation mode, no data will be actually removed")

        result = {}
        # Measure disk usage before cleanup.
        result["fsstats_pre"] = self._fsstats(self.c(self.CONFIG_DB_PATH))

        # Perform cleanup of event table according to selected rules.
        result["events"] = []
        for rule in self.c(self.CONFIG_EVENTS):
            res = self._cleanup_events(dt_current, **rule)
            result["events"].append(res)

        # Perform cleanup of various other tables according to selected rules.
        result["tables"] = []
        for rule in self.c(self.CONFIG_TABLES):
            res = self._cleanup_table(dt_current, **rule)
            result["tables"].append(res)

        # Perform cleanup of selected folder caches.
        result["caches"] = []
        for cachedir in self.c(self.CONFIG_CACHES):
            res = self._cleanup_cachedir(dt_current, **cachedir)
            result["caches"].append(res)

        # Perform cleanup of selected runlog folder.
        result["runlogs"] = []
        for runlogdir in self.c(self.CONFIG_RUNLOGS):
            res = self._cleanup_runlogdir(dt_current, **runlogdir)
            result["runlogs"].append(res)

        # Measure disk usage after cleanup.
        result["fsstats_post"] = self._fsstats(self.c(self.CONFIG_DB_PATH))

        return result

    # ---------------------------------------------------------------------------

    @staticmethod
    def _fsstats(fpath):
        """
        Calculate the filesystem statistics.
        """
        fsstats = os.statvfs(fpath)
        return dict(
            zip(
                (
                    "f_bsize",
                    "f_frsize",
                    "f_blocks",
                    "f_bfree",
                    "f_bavail",
                    "f_files",
                    "f_ffree",
                    "f_favail",
                    "f_flag",
                    "f_namemax",
                ),
                fsstats,
            )
        )

    def _cleanup_events(self, dt_current, threshold_type, filter_spec=None):
        """
        Cleanup event table according to given rule.
        """
        # Determine the time threshold for cleanup operation.
        threshold = THRESHOLDS[threshold_type]
        dt_threshold = dt_current - threshold["d"]

        # Build the cleanup filter
        if not filter_spec:
            filter_spec = {}
        filter_spec["st_to"] = dt_threshold

        # Prepare the result object
        result = {
            "threshold": threshold_type,
            "threshold_int": dt_threshold.timestamp(),
            "threshold_str": dt_threshold.isoformat(),
            "threshold_lbl": threshold["l"],
            "filter": json.dumps(filter_spec, default=json_dump_cbk),
        }

        # Attempt to clean the collection
        self.logger.info(
            "Event table cleanup started with threshold '%s': '%s' and with filter '%s'",
            result["threshold"],
            result["threshold_str"],
            result["filter"],
        )

        result["stats_pre"] = self.eventservice.database_status(brief=True)

        if not self.c("simulate"):
            deleted_count = self.eventservice.delete_events(filter_spec)
            result["removed_cnt"] = int(deleted_count)
        else:
            deleted_count = self.eventservice.count_events(filter_spec)
            result["removed_cnt"] = int(deleted_count)

        result["stats_post"] = self.eventservice.database_status(brief=True)

        self.logger.info(
            "Event table cleanup done, removed: {:,d} | kept: {:,d}".format(
                result["removed_cnt"],
                int(result["stats_post"]["tables"]["events"]["row_estimate"]),
            )
        )

        return result

    def _cleanup_table(self, dt_current, table, column, threshold_type):
        """
        Cleanup given table according to given rule.
        """
        # Determine the time threshold for cleanup operation.
        threshold = THRESHOLDS[threshold_type]
        dt_threshold = dt_current - threshold["d"]

        # Prepare the result object
        result = {
            "threshold": threshold_type,
            "threshold_int": dt_threshold.timestamp(),
            "threshold_str": dt_threshold.isoformat(),
            "threshold_lbl": threshold["l"],
            "removed_cnt": 0,
        }

        # Attempt to clean the collection
        self.logger.info(
            "Table '%s' cleanup started according to column '%s' with threshold '%s': '%s'",
            table,
            column,
            result["threshold"],
            result["threshold_str"],
        )

        result["stats_pre"] = self.eventservice.database_status(brief=True)

        if not self.c("simulate"):
            deleted_count = self.eventservice.table_cleanup(table=table, column=column, ttl=dt_threshold)
            result["removed_cnt"] = int(deleted_count)
        else:
            self.logger.warning(
                "Table cleanup does not support simulation, unable to detect number of deleted records.",
            )

        result["stats_post"] = self.eventservice.database_status(brief=True)

        self.logger.info(
            "Table {:s} cleanup done, removed: {:,d} | kept: {:,d}".format(
                table,
                result["removed_cnt"],
                int(result["stats_post"]["tables"][table]["row_estimate"]),
            )
        )

        return result

    def _cleanup_cachedir(self, dt_current, cachedir, threshold_type):
        """
        Cleanup given filesystem cache.
        """
        # Determine the time threshold for cleanup operation.
        threshold = THRESHOLDS[threshold_type]
        dt_threshold = dt_current - threshold["d"]

        result = {
            "cache": cachedir,
            "threshold": threshold_type,
            "threshold_int": dt_threshold.timestamp(),
            "threshold_str": dt_threshold.isoformat(),
            "threshold_lbl": threshold["l"],
            "files_cnt": 0,
            "files_bytes": 0,
            "kept_cnt": 0,
            "kept_bytes": 0,
            "removed_cnt": 0,
            "removed_bytes": 0,
            "error_cnt": 0,
            "errors": [],
        }

        self.logger.info(
            "Cache '%s' cleanup started with threshold '%s': '%s'",
            result["cache"],
            result["threshold"],
            result["threshold_str"],
        )
        for root, dir_list, file_list in os.walk(cachedir, topdown=False):
            for fln in file_list:
                flp = os.path.join(root, fln)
                fst = os.stat(flp)
                result["files_cnt"] += 1
                result["files_bytes"] += fst.st_size

                if fst.st_mtime < result["threshold_int"]:
                    try:
                        if not self.c("simulate"):
                            os.remove(flp)
                            self.logger.debug(
                                "Cache '%s': Permanently removed file '%s'",
                                result["cache"],
                                flp,
                            )
                        else:
                            self.logger.debug(
                                "Cache '%s': File '%s' would be permanently removed",
                                result["cache"],
                                flp,
                            )
                        result["removed_cnt"] += 1
                        result["removed_bytes"] += fst.st_size

                    except Exception as exc:  # pylint: disable=locally-disabled,broad-except
                        self.error(f"Unable to remove cache file '{flp}': {exc!s}")
                        result["error_cnt"] += 1
                        result["errors"].append(flp)
                else:
                    result["kept_cnt"] += 1
                    result["kept_bytes"] += fst.st_size

            for drn in dir_list:
                drp = os.path.join(root, drn)
                if not os.listdir(drp):
                    if not self.c("simulate"):
                        os.rmdir(drp)
                        self.logger.debug(
                            "Cache '%s': Permanently removed empty subdirectory '%s'",
                            result["cache"],
                            drp,
                        )
                    else:
                        self.logger.debug(
                            "Cache '%s': Empty subdirectory '%s' would be removed",
                            result["cache"],
                            drp,
                        )

        self.logger.info(
            "Cache '{}' cleanup done, removed: {:,d} | kept: {:,d} | errors: {:,d}".format(
                result["cache"],
                result["removed_cnt"],
                result["kept_cnt"],
                result["error_cnt"],
            )
        )
        return result

    def _cleanup_runlogdir(self, dt_current, runlogdir, threshold_type):
        """
        Cleanup given filesystem cache.
        """
        # Determine the time threshold for cleanup operation.
        threshold = THRESHOLDS[threshold_type]
        dt_threshold = dt_current - threshold["d"]

        result = {
            "runlogdir": runlogdir,
            "threshold": threshold_type,
            "threshold_int": dt_threshold.timestamp(),
            "threshold_str": dt_threshold.isoformat(),
            "threshold_lbl": threshold["l"],
            "files_cnt": 0,
            "files_bytes": 0,
            "kept_cnt": 0,
            "kept_bytes": 0,
            "removed_cnt": 0,
            "removed_bytes": 0,
            "error_cnt": 0,
            "errors": [],
        }

        self.logger.info(
            "Runlogdir '%s' cleanup started with threshold '%s': '%s'",
            result["runlogdir"],
            result["threshold"],
            result["threshold_str"],
        )
        for flp in glob.iglob(f"{runlogdir}/**/*.runlog"):
            if os.path.isfile(flp):
                fst = os.stat(flp)
                result["files_cnt"] += 1
                result["files_bytes"] += fst.st_size
                if fst.st_mtime < result["threshold_int"]:
                    try:
                        if not self.c("simulate"):
                            os.remove(flp)
                            self.logger.debug(
                                "Runlogdir '%s': Permanently removed runlog '%s'",
                                result["runlogdir"],
                                flp,
                            )
                        else:
                            self.logger.debug(
                                "Runlogdir '%s': Runlog '%s' would be permanently removed",
                                result["runlogdir"],
                                flp,
                            )
                        result["removed_cnt"] += 1
                        result["removed_bytes"] += fst.st_size

                    except Exception as exc:  # pylint: disable=locally-disabled,broad-except
                        self.error(f"Unable to remove runlog file '{flp}': {exc!s}")
                        result["error_cnt"] += 1
                        result["errors"].append(flp)
                else:
                    result["kept_cnt"] += 1
                    result["kept_bytes"] += fst.st_size

        self.logger.info(
            "Runlogdir '{}' cleanup done, removed: {:,d} | kept: {:,d} | errors: {:,d}".format(
                result["runlogdir"],
                result["removed_cnt"],
                result["kept_cnt"],
                result["error_cnt"],
            )
        )
        return result
