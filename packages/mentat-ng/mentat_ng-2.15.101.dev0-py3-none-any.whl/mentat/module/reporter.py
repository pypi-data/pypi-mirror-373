#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing periodical event reports to target groups.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------------------------------------------------------------------------

.. code-block:: shell

    # Display help message and exit.
    mentat-reporter.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-reporter.py --debug

    # Run with insanely increased logging level.
    mentat-reporter.py --log-level debug

    # Run in TEST DATA mode and MAIL TEST mode, force all reports to go to
    # 'admin@domain.org'. In test data mode only events tagged with 'Test'
    # category will be processed (useful for debugging). In mail test mode
    # all generated reports will be redirected to configured admin email (root
    # by default) instead of original contact, which is again useful for
    # debugging or testing.
    mentat-reporter.py --mail-test-mode --test-data --mail-to admin@domain.org

    # Force reporter to use different email report template and localization.
    mentat-reporter.py --template-id another --locale cs


Available script commands
--------------------------------------------------------------------------------

``report`` (*default*)
    Generate report containing overall Mentat system performance statistics
    within configured time interval thresholds.


Brief overview of reporting algorithm
--------------------------------------------------------------------------------

Reporting algorithm follows these steps:

#. For all groups found in database:

    #. For all event severities (``info``, ``low``, ``medium``, ``high``, ``critical``):

        #. Fetch reporting configuration settings.
        #. Fetch events with given severity, that appeared in database in given
           time window and belonging to that particular group.
        #. Filter events with configured reporting filters.
        #. Remove events from detectors with low credibility.
        #. Threshold already reported events.
        #. Fetch relapsed events.
        #. Generate *target*, *summary* and/or *extra* reports and store them to database.
        #. Send reports via email to target abuse contacts.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import datetime
import errno
import fcntl
import os
import time

import pydgets.widgets
import pyzenkit.utils

import mentat.const
import mentat.plugin.app.mailer
import mentat.reports.event
import mentat.reports.utils
import mentat.script.fetcher
from mentat.datatype.sqldb import GroupModel
from mentat.reports.data import ReportingProperties


class SimpleFlock:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Provides the simplest possible interface to flock-based file locking. Intended
    for use with the `with` syntax. It will create/truncate/delete the lock file
    as necessary.

    Resource: https://github.com/derpston/python-simpleflock
    """

    def __init__(self, path, timeout=None):
        self._path = path
        self._timeout = timeout
        self._fd = None

    def __enter__(self):
        self._fd = os.open(self._path, os.O_CREAT)
        start_lock_search = time.time()
        while True:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Lock acquired!
                return
            except OSError as ex:
                if ex.errno != errno.EAGAIN:  # Resource temporarily unavailable
                    raise
                if self._timeout is not None and time.time() > (start_lock_search + self._timeout):
                    # Exceeded the user-specified timeout.
                    raise

            # It would be nice to avoid an arbitrary sleep here, but spinning
            # without a delay is also undesirable.
            time.sleep(0.1)

    def __exit__(self, *args):
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)
        self._fd = None

        # Try to remove the lock file, but don't try too hard because it is
        # unnecessary. This is mostly to help the user see whether a lock
        # exists by examining the filesystem.
        with contextlib.suppress(Exception):
            os.unlink(self._path)


class MentatReporterScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing periodical statistical
    overview for message processing performance analysis.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CORECFG_REPORTER = "__core__reporter"
    CONFIG_REPORTS_DIR = "reports_dir"
    CONFIG_TEMPLATES_DIR = "templates_dir"
    CONFIG_TEMPLATE_VARS = "template_vars"
    CONFIG_DEFAULT_LOCALE = mentat.const.CKEY_CORE_REPORTER_DEFAULTLOCALE
    CONFIG_DEFAULT_TIMEZONE = mentat.const.CKEY_CORE_REPORTER_DEFAULTTIMEZONE
    CONFIG_FORCE_MODE = "force_mode"
    CONFIG_FORCE_TEMPLATE = "force_template"
    CONFIG_FORCE_LOCALE = "force_locale"
    CONFIG_FORCE_TIMEZONE = "force_timezone"
    CONFIG_TEST_DATA = "test_data"

    def __init__(self):
        """
        Initialize reporter script object. This method overrides the base
        implementation in :py:func:`mentat.script.fetcher.FetcherScript.__init__`
        and it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        # Declare private attributes.
        self.sqlservice = None
        self.mailerservice = None
        self.reporter = None

        super().__init__(
            description="mentat-reporter.py - Mentat system event reporting",
            #
            # Load additional application-level plugins.
            #
            plugins=[mentat.plugin.app.mailer.MailerPlugin()],
        )

    def _sub_stage_init(self, **kwargs):
        """
        **SUBCLASS HOOK**: Perform additional custom initialization actions.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from constructor.
        """
        # Override default 'interval' value.
        self.config[self.CONFIG_INTERVAL] = "10_minutes"

        # Override default 'adjust_thresholds' value.
        self.config[self.CONFIG_ADJUST_THRESHOLDS] = True

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
            "--force-mode",
            type=str,
            default=None,
            help="force a reporting mode setting",
        )
        arggroup_script.add_argument(
            "--force-template",
            type=str,
            default=None,
            help="force a template for generating reports",
        )
        arggroup_script.add_argument(
            "--force-locale",
            type=str,
            default=None,
            help="force a locale for generating reports",
        )
        arggroup_script.add_argument(
            "--force-timezone",
            type=str,
            default=None,
            help="force a timezone for generating reports",
        )
        arggroup_script.add_argument(
            "--test-data",
            action="store_true",
            default=None,
            help="use test data for reporting (flag)",
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
            (self.CONFIG_FORCE_MODE, None),
            (self.CONFIG_FORCE_TEMPLATE, None),
            (self.CONFIG_FORCE_LOCALE, None),
            (self.CONFIG_FORCE_TIMEZONE, None),
            (self.CONFIG_TEST_DATA, False),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _sub_stage_evaluate(self, analysis):
        """
        **SUBCLASS HOOK**: Perform additional evaluation actions in **evaluate** stage.

        Gets called from :py:func:`~BaseApp._stage_evaluate` and it is a **EVALUATE SUBSTAGE 01**.
        """
        if analysis.get(self.RLANKEY_COMMAND) == "report":
            if analysis["report"]["groups"]:
                self.logger.info(
                    "List of groups with any reports: %s",
                    ", ".join(analysis["report"]["groups"]),
                )
            if analysis["report"]["summary_ids"]:
                self.logger.info(
                    "List of generated summary reports: %s",
                    ", ".join(analysis["report"]["summary_ids"]),
                )
            if analysis["report"]["extra_ids"]:
                self.logger.info(
                    "List of generated extra reports: %s",
                    ", ".join(analysis["report"]["extra_ids"]),
                )
            if analysis["report"]["target_ids"]:
                self.logger.info(
                    "List of generated target reports: %s",
                    ", ".join(analysis["report"]["target_ids"]),
                )
            if analysis["report"]["mails_to"]:
                self.logger.info(
                    "List of report destinations: %s",
                    ", ".join(analysis["report"]["mails_to"]),
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
        return "report"

    def cbk_command_report(self):
        """
        Implementation of the **report** command (*default*).

        Calculate statistics for messages stored into database within configured
        time interval thresholds.
        """
        result = {"reports": {}}

        #
        # Use locking mechanism to ensure there is always only one reporter
        # instance running.
        #
        with SimpleFlock("/var/tmp/mentat-reporter.py", 5):
            groups_dict = {}
            settings_dict = {}
            for group in self._fetch_groups_enabled():
                groups_dict[group.name] = group
                settings_dict[group.name] = mentat.reports.utils.ReportingSettings(
                    group,
                    self.sqlservice,
                    force_mode=self.c(self.CONFIG_FORCE_MODE),
                    force_template=self.c(self.CONFIG_FORCE_TEMPLATE),
                    force_locale=self.c(self.CONFIG_FORCE_LOCALE),
                    force_timezone=self.c(self.CONFIG_FORCE_TIMEZONE),
                    default_locale=self.config[self.CORECFG_REPORTER][self.CONFIG_DEFAULT_LOCALE],
                    default_timezone=self.config[self.CORECFG_REPORTER][self.CONFIG_DEFAULT_TIMEZONE],
                )
            whoismodule = mentat.services.whois.SqldbWhoisModule()
            whoismodule.setup()

            # Instantinate the reporter object.
            reporter = mentat.reports.event.EventReporter(
                self.logger,
                pyzenkit.utils.get_resource_path_fr(self.config[self.CORECFG_REPORTER][self.CONFIG_REPORTS_DIR]),
                pyzenkit.utils.get_resource_path_fr(self.config[self.CORECFG_REPORTER][self.CONFIG_TEMPLATES_DIR]),
                self.config[mentat.const.CKEY_CORE_REPORTER][mentat.const.CKEY_CORE_REPORTER_FALLBACK],
                mentat.const.DFLT_REPORTING_LOCALE,
                mentat.const.DFLT_REPORTING_TIMEZONE,
                self.eventservice,
                self.sqlservice,
                self.mailerservice,
                groups_dict,
                settings_dict,
                whoismodule,
                self.c(self.CONFIG_REGULAR),
            )

            # Adjust time interval thresholds.
            time_h = self.calculate_upper_threshold(
                time_high=self.c(self.CONFIG_TIME_HIGH),
                interval=self.c(self.CONFIG_INTERVAL),
                adjust=self.c(self.CONFIG_REGULAR),
            )
            time_h = time_h.replace(microsecond=0)
            self.logger.info(
                "Upper event report calculation time interval threshold: %s (%s)",
                time_h.isoformat(),
                time_h.timestamp(),
            )
            if self.c(self.CONFIG_TEST_DATA):
                self.logger.info(
                    "Running in 'TESTDATA' mode: Reporting will be performed only for events tagged with 'Test' category."
                )

            # Perform reporting for all configured and enabled groups.
            for group in groups_dict.values():
                result["reports"][group.name] = self._report_for_group(
                    reporter, group, settings_dict[group.name], time_h
                )

            # Cleanup thresholding cache after the reporting.
            result["cleanup"] = reporter.cleanup(time_h)

        return result

    # ---------------------------------------------------------------------------

    def _report_for_group(self, reporter, group, reporting_settings, time_h):
        """
        Perform event reporting for given group.

        :param mentat.reports.event.EventReporter reporter: Event reporter.
        :param mentat.datatype.internal.GroupModel group: The group.
        :param mentat.reports.utils.ReportingSettings reporting_settings: Reporting settings.
        :param datetime.datetime time_h: Upper reporting time boundary.
        :return: Dictionary structure containing information about reporting result.
        :rtype: dict
        """
        result = {}

        # Perform reporting separatelly for each severity.
        for severity in mentat.const.EVENT_SEVERITIES:
            pstate_key = f"ts_last_{severity}_{group.name}"
            period = reporting_settings.timing_cfg[severity]["per"]
            time_l = self.pstate.get(pstate_key, None)

            # In case we have timestamp of last successful run, use it as lower
            # threshold.
            if time_l:
                time_l = datetime.datetime.fromtimestamp(time_l)

                # Check, that we are not running too soon.
                if self.c(self.CONFIG_REGULAR) and (time_l + period) > time_h:
                    self.logger.debug(
                        "%s: Skipping reporting for event severity '%s' and period '%s': At %s it is too soon, waiting until %s.",
                        group.name,
                        severity,
                        period,
                        time_h.isoformat(),
                        (time_l + period).isoformat(),
                    )
                    result[severity] = {"result": "skipped-too-soon"}
                    continue
            # Otherwise calculate lower threshold from configured reporting period.
            else:
                time_l = time_h - period

            reporting_properties = ReportingProperties(
                group,
                severity,
                time_l,
                time_h,
                self.config[self.CORECFG_REPORTER][self.CONFIG_TEMPLATE_VARS],
                self.c(self.CONFIG_TEST_DATA),
            )

            # Proceed to actual reporting.
            result[severity] = reporter.report(reporting_properties)

            # Evaluate reporting results.
            if result[severity]["result"] == "reported":
                for report_type in ["summary", "target"]:
                    if f"{report_type}_id" in result[severity]:
                        self.logger.info(
                            "%s: Generated %s report '%s' with severity '%s' and time interval %s -> %s (%s).",
                            group.name,
                            report_type,
                            result[severity][f"{report_type}_id"],
                            severity,
                            time_l.isoformat(),
                            time_h.isoformat(),
                            str(time_h - time_l),
                        )
            elif result[severity]["result"] == "skipped-no-events":
                self.logger.debug(
                    "%s: Skipped reporting for severity '%s' and time interval %s -> %s (%s): No events to report.",
                    group.name,
                    severity,
                    time_l.isoformat(),
                    time_h.isoformat(),
                    str(time_h - time_l),
                )

            # Update the timestamp of last successful reporting for particular
            # severity and group.
            self.pstate[pstate_key] = time_h.timestamp()

        return result

    # ---------------------------------------------------------------------------

    def _fetch_groups_from_events(self, time_h):
        """
        Fetch all group names from events database for a given time window.

        :return: Set of all group names as strings.
        :rtype: set
        """
        # Calculate lower threshold of considered events by using the longest period for reporting.
        period = datetime.timedelta(
            seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_PER]
        )
        time_l = time_h - period
        count, events = self.eventservice.search_events({"st_from": time_l, "st_to": time_h, "groups": ["__ANY__"]})
        # Uniquify the found groups.
        result = []
        for e in events:
            result.extend(e.get_source_groups())
            result.extend(e.get_target_groups())
        return set(result)

    # ---------------------------------------------------------------------------

    def _fetch_groups_enabled(self):
        """
        Fetch all group objects from main database with ``enabled`` attribute
        set to ``True``.

        :return: List of all enabled group objects as :py:class:`mentat.datatype.sqldb.GroupModel`.
        :rtype: list
        """
        groups = self.sqlservice.session.query(GroupModel).filter(GroupModel.enabled).order_by(GroupModel.name).all()
        self.sqlservice.session.commit()

        self.logger.debug("Found total of %d enabled group(s) in main database.", len(groups))
        return groups

    def _sub_runlog_analyze(self, runlog, analysis):
        """
        Analyze given runlog (hook for subclasses).

        Shadow reports are not included in this analysis.
        """
        command = runlog.get(self.RLANKEY_COMMAND, None)
        if command == "report":
            analysis[command] = {
                "report_count": 0,
                "summary_ids": [],
                "extra_ids": [],
                "target_ids": [],
                "mails_to": [],
                "groups": [],
            }
            tmphlp = analysis[command]

            for group, report_stats in runlog[command].get("reports", {}).items():
                for severity_stats in report_stats.values():
                    # If there is no 'Source' section, then it is an old runlog and
                    # stats for source reporting are fields in severity_stats.
                    source_stats = severity_stats.get("Source", severity_stats)
                    target_stats = severity_stats.get("Target", {})
                    for stats in [source_stats, target_stats]:
                        for counter in (
                            "evcount_all",
                            "evcount_new",
                            "evcount_rep",
                            "evcount_flt",
                            "evcount_flt_blk",
                            "evcount_thr",
                            "evcount_thr_blk",
                            "evcount_det_blk",
                            "evcount_rlp",
                        ):
                            tmphlp[counter] = tmphlp.get(counter, 0) + stats.get(counter, 0)

                    if source_stats.get("summary_id"):
                        # The format was changed from simple field to a list, so this
                        # is for compatibility reasons and can be removed later.
                        if isinstance(source_stats["summary_id"], list):
                            tmphlp["summary_ids"].extend(source_stats["summary_id"])
                        else:
                            tmphlp["summary_ids"].append(source_stats["summary_id"])
                        tmphlp["groups"].append(group)
                        tmphlp["report_count"] += 1
                    if source_stats.get("extra_id"):
                        tmphlp["extra_ids"].extend(source_stats["extra_id"])
                        tmphlp["groups"].append(group)
                        tmphlp["report_count"] += len(source_stats["extra_id"])
                    if target_stats.get("target_id"):
                        # The format was changed from simple field to a list, so this
                        # is for compatibility reasons and can be removed later.
                        if isinstance(target_stats["target_id"], list):
                            tmphlp["target_ids"].extend(target_stats["target_id"])
                        else:
                            tmphlp["target_ids"].append(target_stats["target_id"])
                        tmphlp["groups"].append(group)
                        tmphlp["report_count"] += len(target_stats["target_id"])
                    if severity_stats.get("mail_to"):
                        tmphlp["mails_to"].extend(severity_stats["mail_to"])

            tmphlp["mails_to"] = list(set(tmphlp["mails_to"]))
            tmphlp["groups"] = list(set(tmphlp["groups"]))

        return analysis

    def _sub_runlog_format_analysis(self, analysis):
        """
        Format runlog analysis (hook for subclasses).
        """
        if analysis.get(self.RLANKEY_COMMAND) == "report":
            tablew = pydgets.widgets.TableWidget()

            tcols = [
                {"label": "Statistics", "data_formating": "{:s}", "align": "<"},
                {"label": "Value", "data_formating": "{:s}", "align": ">"},
            ]
            tbody = [
                ["Processed [#]", "{:,d}".format(analysis["report"]["evcount_all"])],
                ["Reported [#]", "{:,d}".format(analysis["report"]["evcount_rep"])],
                ["New [#]", "{:,d}".format(analysis["report"]["evcount_new"])],
                ["Relapsed [#]", "{:,d}".format(analysis["report"]["evcount_rlp"])],
                ["Filtered [#]", "{:,d}".format(analysis["report"]["evcount_flt_blk"])],
                [
                    "Thresholded [#]",
                    "{:,d}".format(analysis["report"]["evcount_thr_blk"]),
                ],
                [
                    "Uncredible [#]",
                    "{:,d}".format(analysis["report"]["evcount_det_blk"]),
                ],
                ["Reports [#]", "{:,d}".format(analysis["report"]["report_count"])],
            ]
            self.p("")
            self.p("Reporting information:")
            self.p("\n".join(tablew.render(tbody, columns=tcols, enumerate=False, header=False)))

            if "groups" in analysis["report"] and analysis["report"]["groups"]:
                self.p("")
                self.p("Groups:")
                listw = pydgets.widgets.ListWidget()
                self.p("\n".join(listw.render(analysis["report"]["groups"])))

            if "summary_ids" in analysis["report"] and analysis["report"]["summary_ids"]:
                self.p("")
                self.p("Generated summary reports:")
                listw = pydgets.widgets.ListWidget()
                self.p("\n".join(listw.render(analysis["report"]["summary_ids"])))

            if "extra_ids" in analysis["report"] and analysis["report"]["extra_ids"]:
                self.p("")
                self.p("Generated extra reports:")
                listw = pydgets.widgets.ListWidget()
                self.p("\n".join(listw.render(analysis["report"]["extra_ids"])))

            if "target_ids" in analysis["report"] and analysis["report"]["target_ids"]:
                self.p("")
                self.p("Generated target reports:")
                listw = pydgets.widgets.ListWidget()
                self.p("\n".join(listw.render(analysis["report"]["target_ids"])))

            if "mails_to" in analysis["report"] and analysis["report"]["mails_to"]:
                self.p("")
                self.p("Email destinations:")
                listw = pydgets.widgets.ListWidget()
                self.p("\n".join(listw.render(analysis["report"]["mails_to"])))

    def _sub_runlogs_format_evaluation(self, evaluation):
        """
        Format runlog evaluations (hook for subclasses).
        """
        tablew = pydgets.widgets.TableWidget()

        table_columns = [
            {"label": "Date"},
            {"label": "Processed [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Reported [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "New [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Relapsed [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Filtered [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Uncredible [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Thresholded [#]", "data_formating": "{:,d}", "align": ">"},
            {"label": "Reports [#]", "data_formating": "{:,d}", "align": ">"},
        ]
        table_data = []
        for anl in evaluation[self.RLEVKEY_ANALYSES]:
            clrslt = anl.get("report", None)
            if clrslt:
                table_data.append(
                    [
                        anl["label"],
                        anl["report"].get("evcount_all", 0),
                        anl["report"].get("evcount_rep", 0),
                        anl["report"].get("evcount_new", 0),
                        anl["report"].get("evcount_rlp", 0),
                        anl["report"].get("evcount_flt_blk", 0),
                        anl["report"].get("evcount_det_blk", 0),
                        anl["report"].get("evcount_thr_blk", 0),
                        anl["report"].get("report_count", 0),
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
                        0,
                        0,
                        0,
                    ]
                )
        self.p("")
        self.p("Result overview for 'report' command:")
        self.p("\n".join(tablew.render(table_data, columns=table_columns)))
