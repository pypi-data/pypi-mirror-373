#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.plugin.enricher.logger` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.plugin.enricher.logger import LoggerEnricherPlugin
from mentat.plugin.enricher.testsuite import MentatEnricherPluginTestCase

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatLoggerEnricherPlugin(MentatEnricherPluginTestCase):
    """
    Unit test class for testing the :py:class:`mentat.plugin.enricher.logger.LoggerEnricherPlugin` class.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.plugin = LoggerEnricherPlugin()

    def test_01_setup(self):
        """
        Perform test of plugin setup.
        """
        self.maxDiff = None

        mapplication = self._build_application_mock([])

        self.plugin.setup(mapplication)
        self._verbose_print("TEST01: daemon mock calls after plugin 'setup'", mapplication.mock_calls)

        mapplication.assert_has_calls([call.logger.debug("Initialized '%s' enricher plugin", "LoggerEnricherPlugin")])

    def test_02_process_01(self):
        """
        Perform tests of message processing - message that should be enriched.
        """
        self.maxDiff = None

        mapplication = self._build_application_mock([])
        msg = {"Source": [{"IP4": "195.113.144.233"}]}

        self.plugin.setup(mapplication)
        mapplication.assert_has_calls([call.logger.debug("Initialized '%s' enricher plugin", "LoggerEnricherPlugin")])
        mapplication.reset_mock()

        result = self.plugin.process(mapplication, "msgid", msg)
        self._verbose_print("TEST02: daemon mock calls after plugin 'setup'", mapplication.mock_calls)
        self._verbose_print("TEST02: enriched message:", msg)
        self._verbose_print("TEST02: enrichement result:", result)

        mapplication.assert_has_calls(
            [
                call.logger.info(
                    "LOGGER - processing message '%s': %s",
                    "msgid",
                    "{'Source': [{'IP4': '195.113.144.233'}]}",
                )
            ]
        )
        self.assertEqual(msg, {"Source": [{"IP4": "195.113.144.233"}]})
        self.assertEqual(result, (1, False))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
