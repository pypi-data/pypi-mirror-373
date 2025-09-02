#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component capable of filtering incoming messages with complex filtering
rules.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pprint
import sys

import pyzenkit.zendaemon
from ransack import Filter, Parser


class FilterDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent encapsulating ransack library.
    """

    EVENT_MSG_PROCESS = "message_process"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "filer")

        self.filter_rules_key = kwargs.get("filter_rules_key", "filter_rules")

        self.parser = Parser()
        self.filter = Filter()

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

    def setup(self, daemon):
        """
        Perform component setup.
        """
        self.filter_rules_cfg = daemon.c(self.filter_rules_key)
        daemon.dbgout(f"[STATUS] Component '{self.cid}': Loading filter rules {pprint.pformat(self.filter_rules_cfg)}")

        self.filter_rules = []
        for rule in self.filter_rules_cfg:
            try:
                flt = self.parser.parse(rule["rule"])
                nme = rule.get("name", rule["rule"])
                self.filter_rules.append({"rule": nme, "filter": flt})
                daemon.logger.debug(f"[STATUS] Component '{self.cid}': Loaded filter rule '{nme}'")
            except Exception:
                daemon.logger.debug(f"[STATUS] Component '{self.cid}': Unable to load filter rule '{rule}'")

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Print the message contents into the log.
        """
        daemon.logger.debug("Filtering message: '{}'".format(args["id"]))
        try:
            for rule in self.filter_rules:
                if self.filter.eval(rule["filter"], args["idea"]):
                    daemon.logger.debug("Message '{}' filtered out by filter '{}'".format(args["id"], rule["rule"]))
                    daemon.queue.schedule("message_cancel", args)
                    return (daemon.FLAG_STOP, args)
                daemon.logger.debug("Message '{}' passed by filter '{}'".format(args["id"], rule["rule"]))
            return (daemon.FLAG_CONTINUE, args)
        except Exception:
            daemon.logger.debug(
                "Message '{}' caused some trouble during processing: '{}'".format(args["id"], sys.exc_info()[1])
            )
            daemon.queue.schedule("message_banish", args)
            return (daemon.FLAG_STOP, args)
