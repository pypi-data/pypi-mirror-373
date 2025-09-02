#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of storing
`IDEA <https://idea.cesnet.cz/en/index>`__ messages into persistent storage.
Currently only `PostgreSQL <https://www.postgresql.org/>`__ database is supported.

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
    mentat-storage.py --help

    # Run in debug mode and stay in foreground (enable output of debugging
    # information to terminal and do not daemonize).
    mentat-storage.py --no-daemon --debug

    # Run with increased logging level.
    mentat-storage.py --log-level debug
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mentat.const
import mentat.daemon.component.commiter
import mentat.daemon.component.parser
import mentat.daemon.component.storage
import mentat.daemon.piper


class MentatStorageDaemon(mentat.daemon.piper.PiperDaemon):
    """
    Implementation of Mentat module (real-time daemon) capable of storing
    `IDEA <https://idea.cesnet.cz/en/index>`__ messages into persistent storage.
    Currently only `PostgreSQL <https://www.postgresql.org/>`__ database is supported.
    """

    def __init__(self):
        """
        Initialize storage daemon object. This method overrides the base
        implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon.__init__` and
        it aims to even more simplify the daemon object creation by providing
        configuration values for parent contructor.
        """
        super().__init__(
            description="mentat-storage.py - IDEA message storing daemon",
            #
            # Override default configurations.
            #
            default_commit_bulk=True,
            default_commit_bulk_interval=5,
            default_commit_bulk_threshold=500,
            #
            # Define required daemon components.
            #
            components=[
                mentat.daemon.component.parser.ParserDaemonComponent(),
                mentat.daemon.component.storage.StorageDaemonComponent(),
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
            "--commit-bulk",
            action="store_true",
            default=None,
            help="run in bulk commit mode (flag)",
        )
        arggroup_daemon.add_argument(
            "--commit-bulk-interval",
            type=int,
            default=None,
            help="time interval for enforcing commit of currently uncommitted events in seconds",
        )
        arggroup_daemon.add_argument(
            "--commit-bulk-threshold",
            type=int,
            default=None,
            help="event count threshold for performing commit of currently uncommitted events in seconds",
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
            (mentat.daemon.component.storage.CONFIG_COMMIT_BULK, False),
            (mentat.daemon.component.storage.CONFIG_COMMIT_BULKINTV, 5),
            (mentat.daemon.component.storage.CONFIG_COMMIT_BULKTHR, 500),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)
