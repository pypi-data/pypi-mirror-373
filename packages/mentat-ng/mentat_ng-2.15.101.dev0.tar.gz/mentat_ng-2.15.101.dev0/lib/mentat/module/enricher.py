#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of enriching
`IDEA <https://idea.cesnet.cz/en/index>`__ messages with additional data.

This daemon is implemented using the :py:mod:`pyzenkit.zendaemon` framework and
so it provides all of its core features. See the documentation for in-depth
details.

It is further based on :py:mod:`mentat.daemon.piper` module, which provides
*pipe-like* message processing features. See the documentation for in-depth
details.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-enricher.py --help

    # Run in debug mode and stay in foreground (enable output of debugging
    # information to terminal and do not daemonize).
    mentat-enricher.py --no-daemon --debug

    # Run with increased logging level.
    mentat-enricher.py --log-level debug
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mentat.const
import mentat.daemon.base
import mentat.daemon.component.commiter
import mentat.daemon.component.enricher
import mentat.daemon.component.parser
import mentat.daemon.piper
import mentat.plugin.app.sqlstorage


class MentatEnricherDaemon(mentat.daemon.piper.PiperDaemon):
    """
    Implementation of Mentat module (real-time daemon) capable of enriching
    `IDEA <https://idea.cesnet.cz/en/index>`__ messages with additional data.
    """

    def __init__(self):
        """
        Initialize enricher daemon object. This method overrides the base
        implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon.__init__` and
        it aims to even more simplify the daemon object creation by providing
        configuration values for parent contructor.
        """
        super().__init__(
            description="mentat-enricher.py - IDEA message enrichment daemon",
            #
            # Override default configurations.
            #
            default_reload_interval=mentat.const.DFLT_INTERVAL_RELOAD,
            #
            # Schedule initial events.
            #
            schedule_after=mentat.daemon.base.DEFAULT_EVENTS_SCHEDULED_AFTER
            + [(mentat.const.DFLT_INTERVAL_RELOAD, mentat.const.DFLT_EVENT_RELOAD)],
            #
            # Load additional application-level plugins.
            #
            plugins=[mentat.plugin.app.sqlstorage.SQLStoragePlugin()],
            #
            # Define required daemon components.
            #
            components=[
                mentat.daemon.component.parser.ParserDaemonComponent(),
                mentat.daemon.component.enricher.EnricherDaemonComponent(),
                mentat.daemon.component.commiter.CommiterDaemonComponent(),
            ],
        )

    def _init_argparser(self, **kwargs):
        """
        Initialize daemon command line argument parser. This method overrides the
        base implementation in :py:func:`mentat.daemon.piper.PiperDaemon._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this daemon object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for common script arguments.
        #
        arggroup_daemon = argparser.add_argument_group("custom daemon arguments")

        arggroup_daemon.add_argument(
            "--reload-interval",
            type=int,
            default=None,
            help="time interval for reloading enrichment plugins in seconds",
        )

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default daemon configurations. This method overrides the base
        implementation in :py:func:`mentat.daemon.piper.PiperDaemon._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (mentat.daemon.component.enricher.CONFIG_PLUGINS, None),
            (mentat.daemon.component.enricher.CONFIG_RELOAD_INTERVAL, 300),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)
