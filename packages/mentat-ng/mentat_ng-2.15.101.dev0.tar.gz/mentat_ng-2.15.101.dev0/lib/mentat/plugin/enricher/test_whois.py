#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.plugin.enricher.whois` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

import mentat.services.sqlstorage
from mentat.plugin.enricher.testsuite import MentatEnricherPluginTestCase
from mentat.plugin.enricher.whois import WhoisEnricherPlugin

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatWhoisEnricherPlugin(MentatEnricherPluginTestCase):
    """
    Unit test class for testing the :py:class:`mentat.plugin.enricher.whois.WhoisEnricherPlugin` class.
    """

    networks_raw = [
        {
            "id": 1,
            "source": "negistry",
            "netname": "MUNI-01",
            "network": "195.178.86.0-195.178.87.255",
            "type": "ipv4",
            "resolved_abuses": ["abuse@muni.cz"],
        },
        {
            "id": 2,
            "source": "negistry",
            "netname": "MUNI-02",
            "network": "147.251.0.0-147.251.255.255",
            "type": "ipv4",
            "resolved_abuses": ["abuse@muni.cz"],
        },
        {
            "id": 3,
            "source": "negistry",
            "netname": "MUNI-03",
            "network": "2001:718:800:5::/64",
            "type": "ipv6",
            "resolved_abuses": ["abuse@muni.cz"],
        },
        {
            "id": 4,
            "source": "negistry",
            "netname": "CESNET-01",
            "network": "195.179.86.0-195.179.87.255",
            "type": "ipv4",
            "resolved_abuses": ["abuse@cesnet.cz"],
        },
        {
            "id": 5,
            "source": "negistry",
            "netname": "CESNET-00",
            "network": "195.179.0.0-195.179.255.255",
            "type": "ipv4",
            "resolved_abuses": ["abuse@cesnet.cz"],
        },
        {
            "id": 6,
            "source": "negistry",
            "netname": "CESNET-02",
            "network": "147.252.0.0-147.252.255.255",
            "type": "ipv4",
            "resolved_abuses": ["abuse@cesnet.cz"],
        },
        {
            "id": 7,
            "source": "negistry",
            "netname": "CESNET-03",
            "network": "2001:718:1:6::/64",
            "type": "ipv6",
            "resolved_abuses": ["abuse@cesnet.cz"],
        },
    ]

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.plugin = WhoisEnricherPlugin()

        mentat.services.sqlstorage.init(
            {
                "__core__database": {
                    "sqlstorage": {
                        "url": "postgresql://mentat:mentat@localhost/mentat_utest",
                        "echo": False,
                    }
                }
            }
        )
        mentat.services.sqlstorage.service().database_drop()
        mentat.services.sqlstorage.service().database_create()

        groups = {}
        for net in self.networks_raw:
            obj = mentat.datatype.sqldb.NetworkModel()
            obj.source = net["source"]
            obj.netname = net["netname"]
            obj.network = net["network"]
            for grp in net["resolved_abuses"]:
                if grp not in groups:
                    groups[grp] = mentat.datatype.sqldb.GroupModel(name=grp, source="manual", description=grp)
                groups[grp].networks.append(obj)
        mentat.services.sqlstorage.service().session.add_all(groups.values())

        mentat.services.sqlstorage.service().session.commit()
        mentat.services.sqlstorage.service().session.flush()
        mentat.services.sqlstorage.close()

    def tearDown(self):
        # WARNING: Do not forget to call parent version of tearDown() method !!!
        super().tearDown()

        mentat.services.sqlstorage.service().session.commit()
        mentat.services.sqlstorage.service().session.close()
        mentat.services.sqlstorage.service().database_drop()
        mentat.services.sqlstorage.close()

    def test_01_setup(self):
        """
        Perform test of plugin setup.
        """
        self.maxDiff = None

        mentat.services.sqlstorage.init(
            {
                "__core__database": {
                    "sqlstorage": {
                        "url": "postgresql://mentat:mentat@localhost/mentat_utest",
                        "echo": False,
                    }
                }
            }
        )

        mapplication = self._build_application_mock([])

        self.plugin.setup(mapplication)
        self._verbose_print("TEST01: daemon mock calls after plugin 'setup'", mapplication.mock_calls)

        # mapplication.assert_has_calls([
        #    call.logger.info("Initialized '%s' enricher plugin: %s", 'WhoisEnricherPlugin', "[{'count_ip4': 331, 'count_ip6': 0, 'name': 'FileWhoisModule'},\n {'count_ip4': 5, 'count_ip6': 2, 'name': 'SqldbWhoisModule'}]")
        # ])

    def test_02_process_01(self):
        """
        Perform tests of message processing - message that should be enriched.
        """
        self.maxDiff = None

        mentat.services.sqlstorage.init(
            {
                "__core__database": {
                    "sqlstorage": {
                        "url": "postgresql://mentat:mentat@localhost/mentat_utest",
                        "echo": False,
                    }
                }
            }
        )

        mapplication = self._build_application_mock([])
        msg = {
            "Source": [{"IP4": "195.179.86.50"}],
            "Target": [{"IP4": "195.179.86.9"}],
        }

        self.plugin.setup(mapplication)
        # mapplication.assert_has_calls([
        #    call.logger.info("Initialized '%s' enricher plugin: %s", 'WhoisEnricherPlugin', "[{'count_ip4': 331, 'count_ip6': 0, 'name': 'FileWhoisModule'},\n {'count_ip4': 5, 'count_ip6': 2, 'name': 'SqldbWhoisModule'}]")
        # ])
        mapplication.reset_mock()

        result = self.plugin.process(mapplication, "msgid", msg)
        self._verbose_print("TEST02: daemon mock calls after plugin 'setup'", mapplication.mock_calls)
        self._verbose_print("TEST02: enriched message:", msg)
        self._verbose_print("TEST02: enrichement result:", result)

        mapplication.assert_has_calls(
            [
                call.logger.debug("WHOIS - processing message '%s'", "msgid"),
                call.logger.debug(
                    "WHOIS - Enriched message '%s' with attribute '_Mentat.ResolvedAbuses' and values %s",
                    "msgid",
                    "['abuse@cesnet.cz']",
                ),
            ]
        )
        self.assertEqual(
            msg,
            {
                "Source": [{"IP4": "195.179.86.50"}],
                "Target": [{"IP4": "195.179.86.9"}],
                "_Mentat": {
                    "ResolvedAbuses": ["abuse@cesnet.cz"],
                    "TargetAbuses": ["abuse@cesnet.cz"],
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
        msg = {
            "Source": [{"IP4": "192.168.1.1"}],
            "Target": [
                {"IP4": "192.168.1.2"},
            ],
        }

        self.plugin.setup(mapplication)
        # mapplication.assert_has_calls([
        #    call.logger.info("Initialized '%s' enricher plugin: %s", 'WhoisEnricherPlugin', "[{'count_ip4': 331, 'count_ip6': 0, 'name': 'FileWhoisModule'},\n {'count_ip4': 5, 'count_ip6': 2, 'name': 'SqldbWhoisModule'}]")
        # ])
        mapplication.reset_mock()

        result = self.plugin.process(mapplication, "msgid", msg)
        self._verbose_print("TEST02: daemon mock calls after plugin 'setup'", mapplication.mock_calls)
        self._verbose_print("TEST02: enriched message:", msg)
        self._verbose_print("TEST02: enrichement result:", result)

        mapplication.assert_has_calls([call.logger.debug("WHOIS - processing message '%s'", "msgid")])
        self.assertEqual(
            msg,
            {"Source": [{"IP4": "192.168.1.1"}], "Target": [{"IP4": "192.168.1.2"}]},
        )
        self.assertEqual(result, (1, False))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
