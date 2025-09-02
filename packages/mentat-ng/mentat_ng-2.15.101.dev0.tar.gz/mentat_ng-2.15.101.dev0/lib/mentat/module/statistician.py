#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing statistical functions and features for
message processing performance analysis.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-statistician.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-statistician.py --debug

    # Run with increased logging level.
    mentat-statistician.py --log-level debug


Available script commands
-------------------------

``calculate`` (*default*)
    Calculate statistics for messages stored into database within configured
    time interval thresholds.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import time

from pyzenkit.utils import get_resource_path_fr

import mentat.const
import mentat.datatype.sqldb
import mentat.script.fetcher
import mentat.stats.idea
import mentat.stats.rrd

# Current time (second precission)
TS = int(time.time())


class MentatStatisticianScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing statistical functions and
    features for message processing performance analysis.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CORECFG_STATISTICS = "__core__statistics"
    CONFIG_RRDS_DIR = "rrds_dir"
    CONFIG_REPORTS_DIR = "reports_dir"

    def __init__(self):
        """
        Initialize statistician script object. This method overrides the base
        implementation in :py:func:`mentat.script.fetcher.FetcherScript.__init__`
        and it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        # Declare private attributes.
        self.stats_rrd = None
        self.sqlservice = None

        super().__init__(
            description="mentat-statistician.py - Mentat system statistical script",
        )

    def _sub_stage_init(self, **kwargs):
        """
        **SUBCLASS HOOK**: Perform additional custom initialization actions.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from constructor.
        """
        # Override default 'interval' value.
        self.config[self.CONFIG_INTERVAL] = "5_minutes"

        # Override default 'adjust_thresholds' value.
        self.config[self.CONFIG_ADJUST_THRESHOLDS] = True

    def _sub_stage_setup(self):
        """
        **SUBCLASS HOOK**: Perform additional custom setup actions.

        This method is called from the main setup method :py:func:`pyzenkit.baseapp.BaseApp._stage_setup`
        as a part of the **setup** stage of application`s life cycle.
        """
        self.stats_rrd = mentat.stats.rrd.RrdStats(
            rrds_dir=get_resource_path_fr(self.config[self.CORECFG_STATISTICS][self.CONFIG_RRDS_DIR]),
            reports_dir=get_resource_path_fr(self.config[self.CORECFG_STATISTICS][self.CONFIG_REPORTS_DIR]),
        )

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "calculate"

    def cbk_command_calculate(self):
        """
        Implementation of the **calculate** command (*default*).

        Calculate statistics for messages stored into database within configured
        time interval thresholds.
        """
        result = {}

        (time_low, time_high) = self.calculate_interval_thresholds(
            time_high=self.c(self.CONFIG_TIME_HIGH),
            interval=self.c(self.CONFIG_INTERVAL),
            adjust=self.c(self.CONFIG_REGULAR),
        )
        self.logger.info(
            "Lower statistics calculation time interval threshold: %s (%s)",
            time_low.strftime("%FT%T"),
            time_low.timestamp(),
        )
        self.logger.info(
            "Upper statistics calculation time interval threshold: %s (%s)",
            time_high.strftime("%FT%T"),
            time_high.timestamp(),
        )

        result["ts_from_s"] = time_low.strftime("%FT%T")
        result["ts_to_s"] = time_high.strftime("%FT%T")
        result["ts_from"] = int(time_low.timestamp())
        result["ts_to"] = int(time_high.timestamp())
        result["interval"] = "{}_{}".format(result["ts_from_s"], result["ts_to_s"])

        messages = self.fetch_messages(time_low, time_high)

        result = mentat.stats.idea.evaluate_event_groups(messages, result)

        self._update_rrds(result, time_high)

        self._generate_charts(time_high)

        result = mentat.stats.idea.truncate_evaluations(result)

        return self._update_db(result, time_low, time_high)

    # ---------------------------------------------------------------------------

    def _update_rrds(self, stats, tstamp):
        """
        Update add RRD database files with given statistics and timestamp.

        :param dict stats: Calculated message statistics.
        :param datetime.datetime tstamp: Update timestamp.
        """
        # We are interested only in overall statistics.
        stats_oa = stats[mentat.stats.idea.ST_OVERALL]

        utstamp = int(tstamp.timestamp())

        # In case there are no messages at all update all existing databases with
        # value '0'
        if not stats_oa["cnt_alerts"] > 0:
            self._rrd_update_all(tstamp)
            return

        rrds = self.stats_rrd.find_dbs()

        for itm in (
            ("nodename", "detectors"),
            ("nodesw", "analyzers"),
            ("category", "categories"),
        ):
            total = 0
            updated = {}

            for stat_key, stat_value in stats_oa[itm[1]].items():
                try:
                    db_name = self.stats_rrd.clean(stat_key)
                    self.logger.info(
                        "Updating RRD DB '%s.%s' statistics with value '%d' and timestamp '%s':'%d'",
                        itm[0],
                        stat_key,
                        stat_value,
                        str(tstamp),
                        utstamp,
                    )
                    self._rrd_update_database(itm[0], stat_key, tstamp, stat_value)
                    updated[db_name] = 1
                    total += stat_value
                except mentat.stats.rrd.RrdsUpdateException as exc:
                    self.logger.error(str(exc))

            try:
                self.logger.info(
                    "Updating RRD DB '%s.%s' total statistics with value '%d' and timestamp '%s':'%d'",
                    itm[0],
                    mentat.stats.rrd.DB_TOTALS_NAME,
                    total,
                    str(tstamp),
                    utstamp,
                )
                self._rrd_update_database(itm[0], mentat.stats.rrd.DB_TOTALS_NAME, tstamp, total)
                updated[mentat.stats.rrd.DB_TOTALS_NAME] = 1
            except mentat.stats.rrd.RrdsUpdateException as exc:
                self.logger.error(str(exc))

            if itm[0] not in rrds:
                continue

            for rrddb in rrds[itm[0]]:
                if rrddb[2] in updated or rrddb[2] == mentat.stats.rrd.DB_TOTALS_NAME:
                    continue

                try:
                    self.logger.info(
                        "Updating RRD DB '%s.%s' statistics with default value '0' and timestamp '%s':'%d'",
                        itm[0],
                        rrddb[2],
                        str(tstamp),
                        utstamp,
                    )
                    self._rrd_update_database(itm[0], rrddb[2], tstamp, 0)
                except mentat.stats.rrd.RrdsUpdateException as exc:
                    self.logger.error(str(exc))

    def _generate_charts(self, tstamp):
        """
        Generate charts and export files.

        :param datetime.datetime tstamp: Update timestamp.
        """
        utstamp = int(tstamp.timestamp())

        result = self.stats_rrd.generate(utstamp)

        self.runlog["generated_files"] = result

    def _update_db(self, stats, time_low, time_high):
        """
        Store given event statistics into database.

        :param dict stats: Event statistics to store.
        """
        stats["ts"] = int(time.time())

        try:
            sql_stats = mentat.datatype.sqldb.EventStatisticsModel(
                dt_from=time_low,
                dt_to=time_high,
                count=stats[mentat.stats.idea.ST_SKEY_COUNT],
                stats_overall=stats.get(mentat.stats.idea.ST_OVERALL, {}),
                stats_internal=stats.get(mentat.stats.idea.ST_INTERNAL, {}),
                stats_external=stats.get(mentat.stats.idea.ST_EXTERNAL, {}),
            )
            sql_stats.calculate_interval()
            sql_stats.calculate_delta()

            self.sqlservice.session.add(sql_stats)
            self.sqlservice.session.commit()

            self.logger.info("Stored event statistics log to database document '%s'", sql_stats.id)
            stats["flag_stored"] = True
            stats["db_id"] = sql_stats.id

        except Exception as exc:
            self.logger.error(str(exc))

        return stats

    # ---------------------------------------------------------------------------

    def _rrd_update_all(self, tstamp, value=0):
        """
        Update all RRD database files with given timestamp and the same value, ``0``
        by default. This method is usefull in case there were no messages in given
        time interval and the statistics are empty.

        :param datetime.datetime tstamp: Update timestamp.
        """
        utstamp = int(tstamp.timestamp())
        self.logger.info(
            "Updating all existing RRD DBs with default value '%d' and timestamp '%s':'%d'",
            value,
            str(tstamp),
            utstamp,
        )
        return self.stats_rrd.update_all(value, tst=utstamp)

    def _rrd_update_database(self, db_type, db_name, tstamp, value):
        """
        Update given RRD database with given timestamp and value.

        :param str db_type: Type part of the database identifier.
        :param str db_name: Name part of the database identifier.
        :param datetime.datetime tstamp: Update timestamp.
        :param int value: Update value.
        """
        db_id = f"{db_type}.{self.stats_rrd.clean(db_name)}"
        utstamp = int(tstamp.timestamp())
        self.logger.info(
            "Updating RRD DB '%s' with value '%d' and timestamp '%s':'%d'",
            db_id,
            value,
            str(tstamp),
            utstamp,
        )
        (rrddb, flag_new) = self.stats_rrd.update(db_id, value, tst=utstamp)
        return (rrddb, flag_new)
