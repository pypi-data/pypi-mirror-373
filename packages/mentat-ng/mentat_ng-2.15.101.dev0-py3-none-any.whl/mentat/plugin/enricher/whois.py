#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
`IDEA <https://idea.cesnet.cz/en/index>`__ message enrichment plugin for the
:ref:`section-bin-mentat-enricher` daemon module performing lookup of all
``Source/IPx`` addresses within configured **whois** service.

.. todo::

    Documentation is still work in progress, please refer to the source code for
    details.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import collections
import pprint

from ransack import get_values

import mentat.const
import mentat.services.whois
from mentat.idea.internal import jpath_set


class WhoisEnricherPlugin:
    """
    Enricher plugin performing lookup of all Source/IPx addresses within configured
    whois service.
    """

    def __init__(self):
        self.whois_service = None

    def setup(self, daemon, config_updates=None):
        """
        Setup plugin.
        """
        whois_manager = mentat.services.whois.WhoisServiceManager(daemon.config, config_updates)
        self.whois_service = whois_manager.service()
        daemon.logger.info(
            "Initialized '%s' enricher plugin: %s",
            self.__class__.__name__,
            pprint.pformat(self.whois_service.status()),
        )

    def process(self, daemon, message_id, message):
        """
        Process and enrich given message.
        """
        daemon.logger.debug("WHOIS - processing message '%s'", message_id)

        changed = False
        for section, abuses in [
            ("Source", "ResolvedAbuses"),
            ("Target", "TargetAbuses"),
        ]:
            ips = []
            ips += get_values(message, f"{section}.IP4")
            ips += get_values(message, f"{section}.IP6")

            resolved_abuses = collections.defaultdict(int)
            for src in ips:
                result = self.whois_service.lookup_abuse(src, getall=True)
                if result is None:
                    continue

                for res in result:
                    resolved_abuses[res] += 1

            resolved_abuses = sorted(resolved_abuses.keys())
            if resolved_abuses:
                jpath_set(message, f"_Mentat.{abuses}", resolved_abuses)
                daemon.logger.debug(
                    f"WHOIS - Enriched message '%s' with attribute '_Mentat.{abuses}' and values %s",
                    message_id,
                    pprint.pformat(resolved_abuses),
                )
                changed = True

        return (daemon.FLAG_CONTINUE, changed)
