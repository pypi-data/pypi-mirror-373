#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#
# This product includes GeoLite2 data created by MaxMind, available from
# http://www.maxmind.com.
# -------------------------------------------------------------------------------

"""
`IDEA <https://idea.cesnet.cz/en/index>`__ message enrichment plugin for the
:ref:`section-bin-mentat-enricher` daemon module performing lookup of all
``Source/IPx`` addresses within configured *geoip* service.

.. note::

    This product includes GeoLite2 data created by MaxMind, available from
    http://www.maxmind.com/.

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
import mentat.plugin.enricher
import mentat.services.geoip
from mentat.idea.internal import jpath_set


class GeoipEnricherPlugin(mentat.plugin.enricher.EnricherPlugin):
    """
    Enricher plugin performing lookup of all Source/IPx addresses within configured
    *geoip* service.
    """

    def __init__(self):
        self.geoip_service = None

    def setup(self, daemon, config_updates=None):
        """
        Setup plugin.
        """
        geoip_manager = mentat.services.geoip.GeoipServiceManager(daemon.config, config_updates)
        self.geoip_service = geoip_manager.service()
        daemon.logger.info(
            "Initialized '%s' enricher plugin: %s",
            self.__class__.__name__,
            pprint.pformat(self.geoip_service.status()),
        )

    def process(self, daemon, message_id, message):
        """
        Process and enrich given message.
        """
        daemon.logger.debug("GEOIP - processing message '%s'", message_id)

        sources = []
        sources += get_values(message, "Source.IP4")
        sources += get_values(message, "Source.IP6")

        resolved_asn_src = collections.defaultdict(int)
        resolved_country_src = collections.defaultdict(int)
        for src in sources:
            try:
                result = self.geoip_service.lookup_asn(src)
                if result is not None and "asn" in result and result["asn"]:
                    resolved_asn_src[result["asn"]] += 1

                result = self.geoip_service.lookup_country(src)
                if result is not None and "ctr_code" in result and result["ctr_code"]:
                    resolved_country_src[result["ctr_code"]] += 1
            # GeoIP database requires single IPv4/IPv6 address as argument, yet
            # IDEA messages may contain ranges and CIDRs. Deal with that by
            # ignoring the errors.
            except ValueError:
                pass

        changed = False
        resolved_asn_src = sorted(resolved_asn_src.keys())
        resolved_country_src = sorted(resolved_country_src.keys())
        if resolved_asn_src:
            jpath_set(message, "_Mentat.SourceResolvedASN", resolved_asn_src)
            daemon.logger.debug(
                "GEOIP - Enriched message '%s' with attribute '_Mentat.SourceResolvedASN' and values %s",
                message_id,
                pprint.pformat(resolved_asn_src),
            )
            changed = True
        if resolved_country_src:
            jpath_set(message, "_Mentat.SourceResolvedCountry", resolved_country_src)
            daemon.logger.debug(
                "GEOIP - Enriched message '%s' with attribute '_Mentat.SourceResolvedCountry' and values %s",
                message_id,
                pprint.pformat(resolved_country_src),
            )
            changed = True

        return (daemon.FLAG_CONTINUE, changed)
