#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of inspecting
`IDEA <https://idea.cesnet.cz/en/index>`__ messages according to given set of
filtering rules and performing number of associated actions.

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
    mentat-inspector.py --help

    # Run in debug mode and stay in foreground (enable output of debugging
    # information to terminal and do not daemonize).
    mentat-inspector.py --no-daemon --debug

    # Run with increased logging level.
    mentat-inspector.py --log-level debug
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mentat.const
import mentat.daemon.component.commiter
import mentat.daemon.component.inspector
import mentat.daemon.component.mailer
import mentat.daemon.component.parser
import mentat.daemon.piper


class MentatInspectorDaemon(mentat.daemon.piper.PiperDaemon):
    """
    Implementation of Mentat module (real-time daemon) capable of inspecting
    `IDEA <https://idea.cesnet.cz/en/index>`__ messages according to given set of
    filtering rules and performing number of associated actions.
    """

    def __init__(self):
        """
        Initialize inspector daemon object. This method overrides the base
        implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon.__init__` and
        it aims to even more simplify the daemon object creation by providing
        configuration values for parent contructor.
        """
        super().__init__(
            description="mentat-inspector.py - IDEA message inspection daemon",
            #
            # Define required daemon components.
            #
            components=[
                mentat.daemon.component.parser.ParserDaemonComponent(),
                mentat.daemon.component.inspector.InspectorDaemonComponent(),
                mentat.daemon.component.mailer.MailerDaemonComponent(),
                mentat.daemon.component.commiter.CommiterDaemonComponent(),
            ],
        )
