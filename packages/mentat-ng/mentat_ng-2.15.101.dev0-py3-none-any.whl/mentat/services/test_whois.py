#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.services.whois` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import unittest
from pprint import pprint

import mentat.datatype.internal
import mentat.datatype.sqldb
import mentat.services.whois
from mentat.datatype.internal import t_network_record

CONTENT_WHOIS_NEGISTRY = """
[
  {
    "primary_key": "78.128.128.0 - 78.128.255.255",
    "ip4_start": "78.128.128.0",
    "ip4_end": "78.128.255.255",
    "resolved_abuses": {
      "low": [
        "abuse@cesnet.cz"
      ]
    }
  }
]
"""

CONTENT_WHOIS_EXCEPTIONS = """
[
    {
        "primary_key": "78.128.214.67",
        "network": "78.128.214.67",
        "resolved_abuses": {
          "low": [
            "abuse@cuni.cz"
          ]
        },
        "type": "ipv4"
    }
]
"""

FILE_WHOIS_NEGISTRY = "/var/tmp/unittest-whois-negistry.json"
FILE_WHOIS_EXCEPTIONS = "/var/tmp/unittest-whois-exceptions.json"


# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatWhois(unittest.TestCase):
    """
    Unit test module for testing the :py:mod:`mentat.services.whois` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    networks_raw = [
        {
            "id": 1,
            "source": "negistry",
            "netnames": "MUNI-01",
            "network": "195.178.86.0-195.178.87.255",
            "type": "ipv4",
            "resolved_abuses": {"low": ["abuse@muni.cz"]},
        },
        {
            "id": 2,
            "source": "negistry",
            "netnames": "MUNI-02",
            "network": "147.251.0.0-147.251.255.255",
            "type": "ipv4",
            "resolved_abuses": {"low": ["abuse@muni.cz"]},
        },
        {
            "id": 3,
            "source": "negistry",
            "netnames": "MUNI-03",
            "network": "2001:718:800:5::/64",
            "type": "ipv6",
            "resolved_abuses": {"low": ["abuse@muni.cz"]},
        },
        {
            "id": 4,
            "source": "negistry",
            "netnames": "CESNET-01",
            "network": "195.179.86.0-195.179.87.255",
            "type": "ipv4",
            "resolved_abuses": {"low": ["abuse@cesnet.cz"]},
        },
        {
            "id": 5,
            "source": "negistry",
            "netnames": "CESNET-00",
            "network": "195.179.0.0-195.179.255.255",
            "type": "ipv4",
            "resolved_abuses": {"low": ["abuse@cesnet.cz"]},
        },
        {
            "id": 6,
            "source": "negistry",
            "netnames": "CESNET-02",
            "network": "147.252.0.0-147.252.255.255",
            "type": "ipv4",
            "resolved_abuses": {"low": ["abuse@cesnet.cz"]},
        },
        {
            "id": 7,
            "source": "negistry",
            "netnames": "CESNET-03",
            "network": "2001:718:1:6::/64",
            "type": "ipv6",
            "resolved_abuses": {"low": ["abuse@cesnet.cz"]},
        },
    ]

    def setUp(self):
        """
        Perform unit test case setup.
        """
        with open(FILE_WHOIS_NEGISTRY, "w", encoding="utf8") as fhnd:
            fhnd.write(CONTENT_WHOIS_NEGISTRY)
        with open(FILE_WHOIS_EXCEPTIONS, "w", encoding="utf8") as fhnd:
            fhnd.write(CONTENT_WHOIS_EXCEPTIONS)

    def tearDown(self):
        """
        Perform unit test case teardown.
        """
        os.unlink(FILE_WHOIS_NEGISTRY)
        os.unlink(FILE_WHOIS_EXCEPTIONS)

    def setup_db(self):
        """
        Setup database before each test.
        """
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
            obj.netname = net["netnames"]
            obj.network = net["network"]
            for grp in net["resolved_abuses"]["low"]:
                if grp not in groups:
                    groups[grp] = mentat.datatype.sqldb.GroupModel(name=grp, source="manual", description=grp)
                groups[grp].networks.append(obj)
        mentat.services.sqlstorage.service().session.add_all(groups.values())

        mentat.services.sqlstorage.service().session.commit()
        mentat.services.sqlstorage.service().session.flush()
        mentat.services.sqlstorage.close()

    def teardown_db(self):
        """
        Teardown database before each test.
        """
        mentat.services.sqlstorage.service().session.commit()
        mentat.services.sqlstorage.service().session.close()
        mentat.services.sqlstorage.service().database_drop()
        mentat.services.sqlstorage.close()

    def test_01_basic(self):
        """
        Perform basic operativity tests.
        """
        self.maxDiff = None

        networks = [t_network_record(net) for net in self.networks_raw]

        if self.verbose:
            pprint(networks)

        whois = mentat.services.whois.WhoisModule()
        whois.setup(networks)
        if self.verbose:
            pprint(whois)
            pprint(whois.networks_ip4)
            pprint(whois.networks_ip6)

        if self.verbose:
            pprint(whois.lookup("195.179.86.10"))
            pprint(whois.lookup("95.179.86.10"))
            pprint(whois.lookup("147.251.0.30"))
            pprint(whois.lookup("47.251.0.30"))

        self.assertEqual(whois.lookup_abuse("195.179.86.10"), ["abuse@cesnet.cz"])
        self.assertEqual(whois.lookup_abuse("95.179.86.10"), [])
        self.assertEqual(whois.lookup_abuse("147.251.0.30"), ["abuse@muni.cz"])
        self.assertEqual(whois.lookup_abuse("47.251.0.30"), [])

    def test_02_sql(self):
        """
        Perform basic operativity tests.
        """
        self.maxDiff = None

        self.setup_db()

        whois = mentat.services.whois.WhoisService([mentat.services.whois.SqldbWhoisModule().setup()])
        if self.verbose:
            for mod in whois.whois_modules:
                pprint(mod)
                pprint(mod.networks_ip4)
                pprint(mod.networks_ip6)

        if self.verbose:
            pprint(whois.lookup("195.179.86.10"))
            pprint(whois.lookup("2001:718:1:6::134:183"))

        self.assertEqual(whois.lookup_abuse("195.179.86.10"), ["abuse@cesnet.cz"])
        self.assertEqual(whois.lookup_abuse("2001:718:1:6::134:183"), ["abuse@cesnet.cz"])
        self.assertEqual(
            whois.lookup_abuse("195.179.86.10", getall=True),
            ["abuse@cesnet.cz", "abuse@cesnet.cz"],
        )
        self.assertEqual(
            whois.lookup_abuse("2001:718:1:6::134:183", getall=True),
            ["abuse@cesnet.cz"],
        )

        if self.verbose:
            pprint(whois.lookup("abuse@cesnet.cz"))

        self.teardown_db()

    def disabletest_03_file(self):
        """
        Perform basic operativity tests.
        """
        self.maxDiff = None

        whois = mentat.services.whois.WhoisService([mentat.services.whois.FileWhoisModule(FILE_WHOIS_NEGISTRY).setup()])
        if self.verbose:
            for mod in whois.whois_modules:
                pprint(mod)
                pprint(mod.networks_ip4)
                pprint(mod.networks_ip6)

        if self.verbose:
            pprint(whois.lookup("78.128.214.67"))

        self.assertEqual(whois.lookup_abuse("78.128.214.67"), ["abuse@cesnet.cz"])

    def disabletest_04_files(self):
        """
        Perform basic operativity tests.
        """
        self.maxDiff = None

        whois = mentat.services.whois.WhoisService(
            [
                mentat.services.whois.FileWhoisModule(FILE_WHOIS_EXCEPTIONS).setup(),
                mentat.services.whois.FileWhoisModule(FILE_WHOIS_NEGISTRY).setup(),
            ]
        )
        if self.verbose:
            for mod in whois.whois_modules:
                pprint(mod)
                pprint(mod.networks_ip4)
                pprint(mod.networks_ip6)

        if self.verbose:
            pprint(whois.lookup("78.128.214.67"))

        self.assertEqual(whois.lookup_abuse("78.128.214.67"), ["abuse@cuni.cz"])

        if self.verbose:
            pprint(whois.lookup("abuse@cuni.cz"))

    def test_05_service_manager(self):
        """
        Perform basic operativity tests.
        """
        self.maxDiff = None

        self.setup_db()

        manager = mentat.services.whois.WhoisServiceManager(
            {
                "__core__services": {
                    "whois": {
                        "modules": [
                            {
                                "name": "FileWhoisModule",
                                "config": {"whois_file": "/var/mentat/whois-exceptions.json"},
                                "optional": True,
                            },
                            {"name": "SqldbWhoisModule", "config": {}},
                        ]
                    }
                }
            }
        )

        whois = manager.service()
        if self.verbose:
            for mod in whois.whois_modules:
                pprint(mod)
                pprint(mod.networks_ip4)
                pprint(mod.networks_ip6)

        if self.verbose:
            pprint(whois.lookup("195.179.86.10"))
            pprint(whois.lookup("2001:718:1:6::134:183"))

        self.assertEqual(whois.lookup_abuse("195.179.86.10"), ["abuse@cesnet.cz"])
        self.assertEqual(whois.lookup_abuse("2001:718:1:6::134:183"), ["abuse@cesnet.cz"])

        if self.verbose:
            pprint(whois.lookup("abuse@cesnet.cz"))

        self.teardown_db()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
