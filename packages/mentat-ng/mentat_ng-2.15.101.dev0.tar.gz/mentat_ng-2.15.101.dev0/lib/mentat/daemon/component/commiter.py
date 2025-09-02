#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component that is commiting all messages. It is intended to be used at the
end of the message processing chain and it will emit the 'message_commit' event
for any message it receives.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.zendaemon


class CommiterDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent commiting all messages.
    """

    EVENT_MSG_PROCESS = "message_process"
    EVENT_LOG_STATISTICS = "log_statistics"

    STATS_CNT_COMMITS = "cnt_commits"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "commiter")

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_MSG_PROCESS: self.EVENT_MSG_PROCESS,
                self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS,
            },
        )

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_MSG_PROCESS],
                "callback": self.cbk_event_message_process,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_LOG_STATISTICS],
                "callback": self.cbk_event_log_statistics,
                "prepend": False,
            },
        ]

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Schedule event for commiting given message.
        """
        daemon.logger.debug("Component '{}': Scheduling message commit for '{}'".format(self.cid, args["id"]))
        daemon.queue.schedule("message_commit", args)

        self.inc_statistic(self.STATS_CNT_COMMITS)
        return (daemon.FLAG_CONTINUE, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [self.STATS_CNT_COMMITS]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (daemon.FLAG_CONTINUE, args)
