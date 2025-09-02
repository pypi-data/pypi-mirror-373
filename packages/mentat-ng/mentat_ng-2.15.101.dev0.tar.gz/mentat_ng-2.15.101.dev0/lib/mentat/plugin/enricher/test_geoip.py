#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.plugin.enricher.geoip` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_GEOIP
from mentat.plugin.enricher.geoip import GeoipEnricherPlugin
from mentat.plugin.enricher.testsuite import MentatEnricherPluginTestCase

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatGeoipEnricherPlugin(MentatEnricherPluginTestCase):
    """
    Unit test class for testing the :py:class:`mentat.plugin.enricher.geoip.GeoipEnricherPlugin` class.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.plugin = GeoipEnricherPlugin()

    def test_01_setup(self):
        """
        Perform test of plugin setup.
        """
        self.maxDiff = None

        mapplication = self._build_application_mock([])

        self.plugin.setup(mapplication)
        asndb = mapplication.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["asndb"]
        citydb = mapplication.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["citydb"]
        countrydb = mapplication.config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP]["countrydb"]
        config = "{'asn': '%s',\n 'city': '%s',\n 'country': '%s'}" % (  # noqa: UP031
            asndb,
            citydb,
            countrydb,
        )
        self._verbose_print("TEST01: daemon mock calls after plugin 'setup'", mapplication.mock_calls)

        mapplication.assert_has_calls(
            [
                call.logger.info(
                    "Initialized '%s' enricher plugin: %s",
                    "GeoipEnricherPlugin",
                    config,
                )
            ]
        )

    def test_02_process_01(self):
        """
        Perform tests of message processing - message that should be enriched.
        """
        self.maxDiff = None

        mapplication = self._build_application_mock([])
        msg = {"Source": [{"IP4": "195.113.144.233"}]}

        self.plugin.setup(mapplication)

        result = self.plugin.process(mapplication, "msgid", msg)
        self._verbose_print("TEST02: daemon mock calls after plugin 'setup'", mapplication.mock_calls)
        self._verbose_print("TEST02: enriched message:", msg)
        self._verbose_print("TEST02: enrichement result:", result)

        mapplication.assert_has_calls(
            [
                call.logger.debug("GEOIP - processing message '%s'", "msgid"),
                call.logger.debug(
                    "GEOIP - Enriched message '%s' with attribute '_Mentat.SourceResolvedASN' and values %s",
                    "msgid",
                    "[2852]",
                ),
                call.logger.debug(
                    "GEOIP - Enriched message '%s' with attribute '_Mentat.SourceResolvedCountry' and values %s",
                    "msgid",
                    "['CZ']",
                ),
            ]
        )
        self.assertEqual(
            msg,
            {
                "Source": [{"IP4": "195.113.144.233"}],
                "_Mentat": {
                    "SourceResolvedASN": [2852],
                    "SourceResolvedCountry": ["CZ"],
                },
            },
        )
        self.assertEqual(result, (1, True))

    def test_03_process_02(self):
        """
        Perform tests of message processing - message that should not be enriched.
        """
        self.maxDiff = None

        mapplication = self._build_application_mock([])
        msg = {"Source": [{"IP4": "192.168.1.1"}]}

        self.plugin.setup(mapplication)

        result = self.plugin.process(mapplication, "msgid", msg)
        self._verbose_print("TEST02: daemon mock calls after plugin 'setup'", mapplication.mock_calls)
        self._verbose_print("TEST02: enriched message:", msg)
        self._verbose_print("TEST02: enrichement result:", result)

        mapplication.assert_has_calls([call.logger.debug("GEOIP - processing message '%s'", "msgid")])
        self.assertEqual(msg, {"Source": [{"IP4": "192.168.1.1"}]})
        self.assertEqual(result, (1, False))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
