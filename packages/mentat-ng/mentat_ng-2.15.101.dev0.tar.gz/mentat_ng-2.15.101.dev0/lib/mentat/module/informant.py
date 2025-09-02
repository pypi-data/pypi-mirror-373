#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing periodical informational reports about
overall performance of Mentat system.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-informant.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-informant.py --debug

    # Run with increased logging level.
    mentat-informant.py --log-level debug


Available script commands
-------------------------

``report`` (*default*)
    Generate report containing overall Mentat system performance statistics
    within configured time interval thresholds.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mentat.const
import mentat.plugin.app.mailer
import mentat.reports.overview
import mentat.script.fetcher


class MentatInformantScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing periodical statistical
    overview for message processing performance analysis.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CORECFG_INFORMANT = "__core__informant"
    CONFIG_REPORTS_DIR = "reports_dir"
    CONFIG_TEMPLATES_DIR = "templates_dir"
    CONFIG_TEMPLATE_VARS = "template_vars"
    CONFIG_FORCE_TEMPLATE = "force_template"
    CONFIG_FORCE_LOCALE = "force_locale"
    CONFIG_FORCE_TIMEZONE = "force_timezone"

    def __init__(self):
        """
        Initialize statistician script object. This method overrides the base
        implementation in :py:func:`mentat.script.fetcher.FetcherScript.__init__`
        and it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        # Declare private attributes.
        self.sqlservice = None
        self.mailerservice = None

        super().__init__(
            description="mentat-informant.py - Mentat system overall performance statistics",
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
        self.config[self.CONFIG_INTERVAL] = "daily"

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
            (self.CONFIG_FORCE_TEMPLATE, "default"),
            (self.CONFIG_FORCE_LOCALE, "en"),
            (self.CONFIG_FORCE_TIMEZONE, "UTC"),
            (self.CONFIG_TEMPLATE_VARS, {}),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

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
        (time_l, time_h) = self.calculate_interval_thresholds(
            time_high=self.c(self.CONFIG_TIME_HIGH),
            interval=self.c(self.CONFIG_INTERVAL),
            adjust=self.c(self.CONFIG_REGULAR),
        )
        time_l = time_l.replace(microsecond=0)
        time_h = time_h.replace(microsecond=0)
        self.logger.info(
            "Lower summary report calculation time interval threshold: %s (%s)",
            time_l.isoformat(),
            time_l.timestamp(),
        )
        self.logger.info(
            "Upper summary report calculation time interval threshold: %s (%s)",
            time_h.isoformat(),
            time_h.timestamp(),
        )
        self.logger.info(
            "Using template '%s' to generate informational summary report.",
            self.c(self.CONFIG_FORCE_TEMPLATE),
        )

        reporter = mentat.reports.overview.OverviewReporter(
            self.logger,
            self.config[self.CORECFG_INFORMANT][self.CONFIG_REPORTS_DIR],
            self.config[self.CORECFG_INFORMANT][self.CONFIG_TEMPLATES_DIR],
            self.c(self.CONFIG_FORCE_LOCALE),
            self.c(self.CONFIG_FORCE_TIMEZONE),
        )

        return reporter.report(
            time_h,
            time_l,
            self.sqlservice.session,
            self.c(self.CONFIG_FORCE_TEMPLATE),
            self.mailerservice,
            self.c(self.CONFIG_TEMPLATE_VARS),
        )
