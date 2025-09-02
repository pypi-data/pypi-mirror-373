#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component capable of simple printing of incoming messages to log file with
the ``info`` severity.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.zendaemon


class PrinterDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent printing messages to log file.
    """

    EVENT_MSG_PROCESS = "message_process"

    STATS_CNT_PRINTED = "cnt_printed"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Permit changing of default event mapping
        self.event_map = kwargs.get("event_map", {self.EVENT_MSG_PROCESS: self.EVENT_MSG_PROCESS})

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_MSG_PROCESS],
                "callback": self.cbk_event_message_process,
                "prepend": False,
            }
        ]

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Print the message contents into the log.
        """
        daemon.logger.info("Printing message: '{}': '{}'".format(args["id"], str(args["idea"]).strip()))
        daemon.queue.schedule("message_commit", args["id"])
        self.inc_statistic(self.STATS_CNT_PRINTED)
        return (daemon.FLAG_CONTINUE, None)
