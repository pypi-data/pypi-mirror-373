#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component providing message sampling functions based on configurable keys.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pprint
import sys

import pyzenkit.zendaemon
from ransack import get_values


class SamplerDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent providing message sampling functions.
    """

    EVENT_MSG_PROCESS = "message_process"
    EVENT_LOG_STATISTICS = "log_statistics"

    CONFIG_SAMPLING_KEYS = "sampling_keys"
    CONFIG_SAMPLING_LIMIT = "sampling_limit"
    CONFIG_SAMPLING_POLICY = "sampling_policy"

    STATS_CNT_SAMPLED = "cnt_sampled"
    STATS_CNT_STOPPED = "cnt_stopped"
    STATS_CNT_ERRORS = "cnt_errors"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "sampler")

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

    def setup(self, daemon):
        """
        Perform component setup.
        """
        self.sampling_keys = daemon.c(self.CONFIG_SAMPLING_KEYS)
        daemon.dbgout(f"[STATUS] Using sampling keys: {pprint.pformat(self.sampling_keys)}")
        self.sampling_limit = daemon.c(self.CONFIG_SAMPLING_LIMIT)
        daemon.dbgout(f"[STATUS] Using sampling limit: {self.sampling_limit}")
        self.sampling_policy = daemon.c(self.CONFIG_SAMPLING_POLICY)
        daemon.dbgout(f"[STATUS] Using sampling policy: {self.sampling_policy}")

        self.sampling_cache = {}

        if self.sampling_policy == "simple":
            self.cbk_sample = self.cbk_sample_simple
        elif self.sampling_policy == "keyed":
            self.cbk_sample = self.cbk_sample_keyed
        else:
            raise Exception(f"Unknown sampling policy '{self.sampling_policy}'")

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Print the message contents into the log.
        """
        daemon.logger.debug("Sampling message: '{}'".format(args["id"]))
        try:
            cbk = self.cbk_sample
            if cbk(daemon, args):
                daemon.logger.debug("Message '{}' passed by sampling".format(args["id"]))
                self.inc_statistic(self.STATS_CNT_SAMPLED)
                return (daemon.FLAG_CONTINUE, args)

            daemon.logger.debug("Message '{}' stopped by sampling".format(args["id"]))
            self.inc_statistic(self.STATS_CNT_STOPPED)
            daemon.queue.schedule("message_cancel", args)
            return (daemon.FLAG_STOP, args)

        except Exception:
            daemon.logger.debug(
                "Message '{}' caused some trouble during sampling: '{}'".format(args["id"], sys.exc_info()[1])
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            daemon.queue.schedule("message_banish", args)
            return (daemon.FLAG_STOP, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [
            self.STATS_CNT_SAMPLED,
            self.STATS_CNT_STOPPED,
            self.STATS_CNT_ERRORS,
        ]:
            if k in stats:
                stats_str = "{}\n\t{:15s} {:12,d} (+{:8,d}, {:8,.2f} #/s)".format(
                    stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"]
                )

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (pyzenkit.zendaemon.ZenDaemon.FLAG_CONTINUE, args)

    def cbk_sample_simple(self, daemon, args):
        """
        Simple sampling algorithm.
        """
        key = "___simple___"

        self.sampling_cache[key] = self.sampling_cache.get(key, 0) + 1
        daemon.logger.debug(
            "Simple sampling cache for message '{}' ['{}']: {}".format(args["id"], key, self.sampling_cache[key])
        )

        return bool((self.sampling_cache[key] % self.sampling_limit) == 1)

    def cbk_sample_keyed(self, daemon, args):
        """
        Sampling algorithm - keyed counting.
        """
        key = ""
        daemon.logger.debug("Calculating sampling cache key")
        for k in self.sampling_keys:
            values = get_values(args["idea"], k)
            daemon.logger.debug(f"Path: '{k}', vals: '{pprint.pformat(values)}'")
            joined = "+".join(values)
            key = key + "|" + joined

        self.sampling_cache[key] = self.sampling_cache.get(key, 0) + 1
        daemon.logger.debug(
            "Keyed sampling cache for message '{}' ['{}']: {}".format(args["id"], key, self.sampling_cache[key])
        )

        return bool((self.sampling_cache[key] % self.sampling_limit) == 1)
