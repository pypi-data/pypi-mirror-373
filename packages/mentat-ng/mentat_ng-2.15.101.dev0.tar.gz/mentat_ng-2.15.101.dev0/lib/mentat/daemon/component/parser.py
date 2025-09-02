#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component providing parsing and serializing functions of IDEA messages for
daemons. Is is implemented as an encapsulation of :py:mod:`mentat.idea.internal`
library.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import json
import traceback

import pyzenkit.zendaemon

import mentat.idea.internal


class ParserDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent encapsulating IDEA library.
    """

    EVENT_MSG_PROCESS = "message_process"
    EVENT_MSG_UPDATE = "message_update"
    EVENT_LOG_STATISTICS = "log_statistics"

    STATS_CNT_PARSED = "cnt_parsed"
    STATS_CNT_ENCODED = "cnt_encoded"
    STATS_CNT_ERRORS = "cnt_errors"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "parser")

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_MSG_PROCESS: self.EVENT_MSG_PROCESS,
                self.EVENT_MSG_UPDATE: self.EVENT_MSG_UPDATE,
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
                "event": self.event_map[self.EVENT_MSG_UPDATE],
                "callback": self.cbk_event_message_update,
                "prepend": True,
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
        Print the message contents into the log.
        """
        daemon.logger.debug("Component '{}': Parsing IDEA message from: '{}'".format(self.cid, args["id"]))
        try:
            msg_raw = json.loads(str(args["data"]).strip())
            args["idea"] = mentat.idea.internal.Idea(msg_raw)
            self.inc_statistic(self.STATS_CNT_PARSED)
            args["idea_id"] = args["idea"].get("ID", "__UNKNOWN__")
            daemon.logger.debug(
                "Component '{}': Parsed IDEA message '{}' from message file '{}'".format(
                    self.cid, args["idea_id"], args["id"]
                )
            )
            return (daemon.FLAG_CONTINUE, args)

        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to parse IDEA message '{}': '{}'".format(
                    self.cid, args["id"], traceback.format_exc()
                )
            )
            daemon.queue.schedule("message_banish", args)

            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, args)

    def cbk_event_message_update(self, daemon, args):
        """
        Print the message contents into the log.
        """
        daemon.logger.debug("Component '{}': Generating JSON from message: '{}'".format(self.cid, args["id"]))
        args["data"] = args["idea"].to_json()

        self.inc_statistic(self.STATS_CNT_ENCODED)
        return (daemon.FLAG_CONTINUE, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [self.STATS_CNT_PARSED, self.STATS_CNT_ENCODED, self.STATS_CNT_ERRORS]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (daemon.FLAG_CONTINUE, args)
