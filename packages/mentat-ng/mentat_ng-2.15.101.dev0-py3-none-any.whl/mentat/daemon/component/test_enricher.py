#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.enricher` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_GEOIP
from mentat.daemon.component.enricher import EnricherDaemonComponent
from mentat.daemon.component.testsuite import DaemonComponentTestCase

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatDaemonEnricher(DaemonComponentTestCase):
    """
    Unit test class for testing the :py:class:`mentat.daemon.component.enricher.EnricherDaemonComponent` class.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.component = EnricherDaemonComponent()

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(CONFIG_PLUGINS)
                [
                    # {
                    #    "name":  "mentat.plugin.enricher.whois.WhoisEnricherPlugin",
                    #    "whois_modules": [
                    #        {
                    #            "name": "FileWhoisModule",
                    #            "config": {
                    #                "whois_file": "/var/mentat/whois-negistry.json"
                    #            }
                    #        }
                    #    ]
                    # },
                    {"name": "mentat.plugin.enricher.geoip.GeoipEnricherPlugin"},
                    {"name": "mentat.plugin.enricher.logger.LoggerEnricherPlugin"},
                ],
                # daemon.c(mentat.const.CKEY_CORE_DATABASE)
                #'mentat'
                # daemon.c(mentat.const.CKEY_CORE_DATABASE)
                #'groups'
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        asndb = daemon.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["asndb"]
        citydb = daemon.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["citydb"]
        countrydb = daemon.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["countrydb"]
        config = "{'asn': '%s',\n 'city': '%s',\n 'country': '%s'}" % (  # noqa: UP031
            asndb,
            citydb,
            countrydb,
        )
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.c.assert_has_calls([call("plugins")])
        daemon.logger.assert_has_calls(
            [
                call.info(
                    "[STATUS] Component '%s': Configuring enrichment plugin '%s'.'%s'",
                    "enricher",
                    "mentat.plugin.enricher.geoip",
                    "GeoipEnricherPlugin",
                ),
                call.info(
                    "Initialized '%s' enricher plugin: %s",
                    "GeoipEnricherPlugin",
                    config,
                ),
                call.info(
                    "[STATUS] Component '%s': Configuring enrichment plugin '%s'.'%s'",
                    "enricher",
                    "mentat.plugin.enricher.logger",
                    "LoggerEnricherPlugin",
                ),
                call.debug("Initialized '%s' enricher plugin", "LoggerEnricherPlugin"),
                call.info(
                    "[STATUS] Component '%s': Successfully set up all enrichment plugins",
                    "enricher",
                ),
            ]
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
