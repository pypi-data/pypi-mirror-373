#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.datatype.internal` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import unittest
from pprint import pprint

import ipranges

import mentat.datatype.internal

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatDatatypeInternal(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.datatype.internal` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    nr_records_raw = [
        {
            "source": "negistry",
            "netname": "MUNI-CUST-6TCZ",
            "network": "2001:718:805::/48",
            "_id": "rJraLUFYXe",
            "last": 4.25406320428021e37,
            "description": "Masaryk University, Brno",
            "type": "ipv6",
        },
        {
            "source": "negistry",
            "first": 4.254063204279606e37,
            "netname": "MUNI-6TCZ",
            "network": "2001:718:801::/48",
            "ip6_prefix": 48,
            "_id": "PO7U6jBOcE",
            "last": 4.254063204279727e37,
            "description": "Masaryk University, Brno",
            "ip6_addr": "2001:718:801::",
            "type": "ipv6",
        },
        {
            "source": "negistry",
            "first": 4.254063204279485e37,
            "netname": "MUNI-IC-6TCZ",
            "network": "2001:718:800:1::/64",
            "ip6_prefix": 64,
            "_id": "mbqWk8R4ie",
            "last": 4.254063204279485e37,
            "description": "Masaryk University, Brno",
            "ip6_addr": "2001:718:800:1::",
            "type": "ipv6",
        },
        {
            "source": "negistry",
            "first": 3283244544,
            "netname": "BAPS-T34CZ",
            "network": "195.178.86.0-195.178.87.255",
            "_id": "jpEayOwZ8m",
            "last": 3283245055,
            "description": "Brno Academic Computer Network, Brno",
            "ip4_end": "195.178.87.255",
            "ip4_start": "195.178.86.0",
            "type": "ipv4",
        },
        {
            "source": "negistry",
            "first": 2482700288,
            "netname": "MUNI-TCZ",
            "network": "147.251.0.0-147.251.255.255",
            "_id": "Hj3Tx0GG5T",
            "last": 2482765823,
            "description": "Masaryk University, Brno",
            "type": "ipv4",
        },
        {
            "source": "negistry",
            "first": 4.254063204279485e37,
            "netname": "MUNI-CUST-IC-6TCZ",
            "network": "2001:718:800:5::/64",
            "_id": "SIfqthXOFx",
            "last": 4.254063204279485e37,
            "description": "Masaryk University, Brno",
            "type": "ipv6",
        },
    ]

    nr_records_few_raw = [
        {
            "source": "negistry",
            "netname": "MUNI-CUST-6TCZ",
            "network": "2001:718:805::/48",
            "_id": "rJraLUFYXe",
            "last": 4.25406320428021e37,
            "description": "Masaryk University, Brno",
            "type": "ipv6",
        },
        {
            "source": "negistry",
            "first": 4.254063204279606e37,
            "netname": "MUNI-6TCZ",
            "network": "2001:718:801::/48",
            "ip6_prefix": 48,
            "_id": "PO7U6jBOcE",
            "last": 4.254063204279727e37,
            "description": "Masaryk University, Brno",
            "ip6_addr": "2001:718:801::",
            "type": "ipv6",
        },
        {
            "source": "negistry",
            "first": 4.254063204279485e37,
            "netname": "MUNI-IC-6TCZ",
            "network": "2001:718:800:1::/64",
            "ip6_prefix": 64,
            "_id": "mbqWk8R4ie",
            "last": 4.254063204279485e37,
            "description": "Masaryk University, Brno",
            "ip6_addr": "2001:718:800:1::",
            "type": "ipv6",
        },
    ]
    group_raw = {
        "_id": "abuse@muni.cz",
        "ts": 1493281523,
        "managers": [],
        "source": mentat.datatype.internal.NR_SOURCE_NEGISTRY,
        "subnet_cache": 0,
        "networks": nr_records_raw,
        "rep_mode": "summary",
        "rep_emails_info": ["abuse@muni.cz"],
        "rep_filters": [],
        "rep_mute": 0,
        "rep_redirect": 1,
    }

    group_empty_raw = {
        "_id": "abuse@cesnet.cz",
        "ts": 1493281523,
        "managers": [],
        "source": mentat.datatype.internal.NR_SOURCE_NEGISTRY,
        "subnet_cache": 0,
        "networks": [],
        "rep_mode": "summary",
        "rep_emails_info": ["abuse@muni.cz"],
        "rep_filters": [],
        "rep_mute": 0,
        "rep_redirect": 1,
    }

    user_raw = {
        "_id": "mach@cesnet.cz",
        "orggroups": ["cesnet:Employees", "cesnet:CERTS"],
        "groups": ["abuse@cesnet.cz"],
        "ts_last_login": 1505483119,
        "affiliations": ["member@cesnet.cz", "employee@cesnet.cz"],
        "organization": "CESNET, z. s. p. o.",
        "query": [
            {
                "detector": "au1/N6",
                "simple": 1,
                "dateto": "",
                "_id": "N6",
                "query": '( Alert/Analyzer/@analyzerid EQ "au1" AND Alert/Analyzer/@name EQ "N6" )',
                "ipor": "FALSE",
                "classification": "",
                "ipsrc": "",
                "datefrom": "",
                "ipdst": "",
            }
        ],
        "ts": 1388577600,
        "roles": ["admin", "user"],
        "email": "jan.mach@cesnet.cz",
        "name": "Jan Mach",
    }

    detector_raw = {
        "_id": "1",
        "ts": 1388577600,
        "source": "warden",
        "credibility": 0.73,
        "name": "Test detector",
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_01_conversions(self):
        """
        Perform tests of parsing network records.
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.datatype.internal.to_net4("192.168.1.0-192.168.1.255"),
            ipranges.IP4Range("192.168.1.0-192.168.1.255"),
        )
        with self.assertRaises(ValueError):
            mentat.datatype.internal.to_net4("192.168.1.1")

        self.assertEqual(
            mentat.datatype.internal.to_net6("2001:718:1:1::/64"),
            ipranges.IP6Net("2001:718:1:1::/64"),
        )
        with self.assertRaises(ValueError):
            mentat.datatype.internal.to_net6("2001:718:1:1::1")

        self.assertTrue(mentat.datatype.internal.gen_sid())
        self.assertTrue(mentat.datatype.internal.gen_sid())

        self.assertEqual(mentat.datatype.internal.t_net4("192.168.1.0"), ipranges.IP4("192.168.1.0"))
        self.assertEqual(
            mentat.datatype.internal.t_net4("192.168.1.0/28"),
            ipranges.IP4Net("192.168.1.0/28"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net4("192.168.1.0-192.168.1.255"),
            ipranges.IP4Range("192.168.1.0-192.168.1.255"),
        )
        with self.assertRaises(ValueError):
            mentat.datatype.internal.t_net4("192.168.300")

        self.assertEqual(
            mentat.datatype.internal.t_net6("2001:718:1:1::1"),
            ipranges.IP6("2001:718:1:1::1"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net6("2001:718:1:1::/64"),
            ipranges.IP6Net("2001:718:1:1::/64"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net6("2001:718:1:1::1-2001:718:1:1::100"),
            ipranges.IP6Range("2001:718:1:1::1-2001:718:1:1::100"),
        )
        with self.assertRaises(ValueError):
            mentat.datatype.internal.t_net6("2001:718:1:1:::")

        self.assertEqual(mentat.datatype.internal.t_net("192.168.1.0"), ipranges.IP4("192.168.1.0"))
        self.assertEqual(
            mentat.datatype.internal.t_net("192.168.1.0/28"),
            ipranges.IP4Net("192.168.1.0/28"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net("192.168.1.0-192.168.1.255"),
            ipranges.IP4Range("192.168.1.0-192.168.1.255"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net("2001:718:1:1::1"),
            ipranges.IP6("2001:718:1:1::1"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net("2001:718:1:1::/64"),
            ipranges.IP6Net("2001:718:1:1::/64"),
        )
        self.assertEqual(
            mentat.datatype.internal.t_net("2001:718:1:1::1-2001:718:1:1::100"),
            ipranges.IP6Range("2001:718:1:1::1-2001:718:1:1::100"),
        )
        with self.assertRaises(ValueError):
            mentat.datatype.internal.t_net("2001:718:1:1:::")

        self.assertEqual(
            mentat.datatype.internal.t_datetime(1497344152),
            datetime.datetime.fromtimestamp(1497344152),
        )
        self.assertEqual(
            mentat.datatype.internal.t_datetime("2017-06-13T10:55:52+02:00"),
            datetime.datetime.utcfromtimestamp(1497344152),
        )

        self.assertEqual(mentat.datatype.internal.t_network_record_type_ip4("ipv4"), "ipv4")
        self.assertEqual(mentat.datatype.internal.t_network_record_type_ip6("ipv6"), "ipv6")
        with self.assertRaises(ValueError):
            self.assertEqual(mentat.datatype.internal.t_network_record_type_ip4("ipv6"), "ipv4")
        with self.assertRaises(ValueError):
            self.assertEqual(mentat.datatype.internal.t_network_record_type_ip6("ipv4"), "ipv6")

    def test_02_network_record(self):
        """
        Perform tests of parsing network records.
        """
        self.maxDiff = None

        for r in self.nr_records_raw:
            nr = mentat.datatype.internal.t_network_record(r)
            if self.verbose:
                print("STR  '{}' => {}".format(r["network"], str(nr)))
                print("REPR '{}' => {}".format(r["network"], repr(nr)))
                print("FPR  '{}' => {}".format(r["network"], nr.fingerprint()))
                pprint(nr)

    def test_03_abuse_group(self):
        """
        Perform tests of parsing abuse groups.
        """
        self.maxDiff = None

        abg = mentat.datatype.internal.AbuseGroup(self.group_raw)
        self.assertEqual(abg["_id"], "abuse@muni.cz")
        self.assertEqual(abg["rep_mode"], "summary")
        if self.verbose:
            pprint(abg)
            for net in abg["networks"]:
                pprint(net)

    def test_04_user(self):
        """
        Perform tests of parsing user accounts.
        """
        self.maxDiff = None

        uac = mentat.datatype.internal.User(self.user_raw)
        self.assertEqual(uac["_id"], "mach@cesnet.cz")
        if self.verbose:
            pprint(uac)

    def test_05_detector(self):
        """
        Perform tests of parsing detectors.
        """
        self.maxDiff = None

        det = mentat.datatype.internal.Detector(self.detector_raw)
        self.assertEqual(det["_id"], "1")
        self.assertEqual(det["credibility"], 0.73)
        self.assertEqual(det["name"], "Test detector")
        self.assertEqual(det["source"], "warden")
        if self.verbose:
            pprint(det)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
