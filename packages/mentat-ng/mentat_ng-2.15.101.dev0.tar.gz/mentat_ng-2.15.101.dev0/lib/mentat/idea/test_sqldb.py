#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.idea.sqldb` module.
"""

import difflib
import json
import unittest
from pprint import pprint

import ipranges

import mentat.idea.internal
import mentat.idea.sqldb

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatIdeaJSON(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.idea.sqldb` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    idea_raw_1 = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf75",
        "TLP": "Amber",
        "CreateTime": "2012-11-03T10:00:02Z",
        "DetectTime": "2012-11-03T10:00:07Z",
        "WinStartTime": "2012-11-03T05:00:00Z",
        "WinEndTime": "2012-11-03T10:00:00Z",
        "EventTime": "2012-11-03T07:36:00Z",
        "CeaseTime": "2012-11-03T09:55:22Z",
        "Category": ["Fraud.Phishing", "Test"],
        "Ref": ["cve:CVE-1234-5678"],
        "Confidence": 1.0,
        "Description": "Synthetic example",
        "Note": "Synthetic example note",
        "ConnCount": 20,
        "Source": [
            {
                "Type": ["Phishing"],
                "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25", "192.168.1.1"],
                "IP6": ["2001:db8::ff00:42:0/112", "2001:db8::ff00:42:50"],
                "Hostname": ["example.com"],
                "URL": ["http://example.com/cgi-bin/killemall"],
                "Proto": ["tcp", "http"],
                "AttachHand": ["att1"],
                "Netname": ["ripe:IANA-CBLK-RESERVED1"],
            }
        ],
        "Target": [
            {
                "Type": ["Backscatter", "OriginSpam"],
                "Email": ["innocent@example.com"],
                "IP6": ["2001:ffff::ff00:42:0/112"],
                "Port": [22, 25, 443],
                "Proto": ["tcp", "http"],
                "Spoofed": True,
            },
            {
                "Type": ["CasualIP"],
                "IP4": ["10.2.2.0/24"],
                "Port": [22, 25, 443],
                "Proto": ["tcp", "HTTP"],
                "Anonymised": True,
            },
        ],
        "Attach": [
            {
                "Handle": "att1",
                "FileName": ["killemall"],
                "Type": ["Malware"],
                "ContentType": "application/octet-stream",
                "Hash": ["sha1:0c4a38c3569f0cc632e74f4c"],
                "Size": 46,
                "Ref": ["Trojan-Spy:W32/FinSpy.A"],
                "ContentEncoding": "base64",
                "Content": "TVpqdXN0a2lkZGluZwo=",
            }
        ],
        "Node": [
            {
                "Name": "org.example.kippo_honey",
                "Realm": "cesnet.cz",
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            }
        ],
        "_Mentat": {
            "StorageTime": "2017-04-05T10:21:39Z",
            "EventTemplate": "sserv-012",
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "TargetAbuses": ["abuse@sanet.sk"],
            "Impact": "System provides SDDP service and can be misused for massive DDoS attack",
            "EventClass": "vulnerable-config-ssdp",
            "TargetClass": "vulnerable-config-ssdp-target",
            "EventSeverity": "low",
            "TargetSeverity": "medium",
            "InspectionErrors": [
                "Demonstration error - first",
                "Demonstration error - second",
            ],
            "ShadowReporting": True,
            "ShadowReportingTarget": True,
        },
    }

    idea_raw_2 = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf76",
        "DetectTime": "2012-11-03T10:00:07Z",
        "Category": ["Fraud.Phishing", "Test"],
        "Node": [
            {
                "Name": "org.example.kippo_honey",
                "Realm": "cesnet.cz",
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            },
            {
                "Name": "org.example.kippo_honey2",
                "Realm": "cesnet.cz",
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            },
        ],
    }

    idea_raw_3 = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf76",
        "DetectTime": "2012-11-03T10:00:07Z",
        "Category": ["Fraud.Phishing", "Test"],
        "Node": [
            {
                "Name": "org.example.kippo_honey",
                "Realm": "cesnet.cz",
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            },
            {"Type": ["External"]},
        ],
    }

    idea_raw_4 = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf77",
        "DetectTime": "2012-11-03T10:00:07Z",
        "Category": ["Fraud.Phishing", "Test"],
        "Node": [
            {
                "Realm": "cesnet.cz",
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            },
            {"Type": ["External"]},
        ],
    }

    def test_01_conv_internal(self):
        """
        Perform basic parsing and conversion tests from ``menat.idea.internal.Idea`` class
        messages. For the purposes of comparison, the ``menat.idea.internal.Idea`` class
        is also tested here.
        """
        self.maxDiff = None

        #
        # Test conversions of raw JSON IDEA into 'mentat.idea.internal.Idea'.
        #
        idea_internal = mentat.idea.internal.Idea(self.idea_raw_1)
        if self.verbose:
            print("'mentat.idea.internal.Idea' out of raw JSON IDEA:")
            print(
                json.dumps(
                    idea_internal,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal.json_default,
                )
            )
        orig = json.dumps(self.idea_raw_1, indent=4, sort_keys=True)
        new = json.dumps(idea_internal, indent=4, sort_keys=True, default=idea_internal.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        #
        # Test conversions of 'mentat.idea.internal.Idea' into 'mentat.idea.sqldb.Idea'.
        #
        idea_sqldb = mentat.idea.sqldb.Idea(idea_internal)
        if self.verbose:
            print("'mentat.idea.sqldb.Idea' out of 'mentat.idea.internal.Idea':")
            pprint(idea_sqldb.get_record())

        # Verify, that conversions really do occur.
        self.assertTrue(idea_sqldb.jsonb)
        self.assertEqual(idea_sqldb.ident, "4390fc3f-c753-4a3e-bc83-1b44f24baf75")
        self.assertEqual(idea_sqldb.detecttime.isoformat(), "2012-11-03T10:00:07")
        self.assertEqual(
            idea_sqldb.source_ip,
            [
                ipranges.IP4("192.168.1.1"),
                ipranges.IP4Range("192.168.0.0-192.168.0.127"),
                ipranges.IP6Range("2001:db8::ff00:42:0-2001:db8::ff00:42:ffff"),
            ],
        )
        self.assertEqual(
            idea_sqldb.target_ip,
            [
                ipranges.IP4Range("10.2.2.0-10.2.2.255"),
                ipranges.IP6Net("2001:ffff::ff00:42:0/112"),
            ],
        )
        self.assertEqual(idea_sqldb.source_ip_aggr_ip4, ipranges.IP4Range("192.168.0.0-192.168.1.1"))
        self.assertEqual(
            idea_sqldb.source_ip_aggr_ip6,
            ipranges.IP6Range("2001:db8::ff00:42:0-2001:db8::ff00:42:ffff"),
        )
        self.assertEqual(idea_sqldb.target_ip_aggr_ip4, ipranges.IP4Range("10.2.2.0-10.2.2.255"))
        self.assertEqual(
            idea_sqldb.target_ip_aggr_ip6,
            ipranges.IP6Range("2001:ffff::ff00:42:0-2001:ffff::ff00:42:ffff"),
        )

        self.assertEqual(idea_sqldb.source_port, [])
        self.assertEqual(idea_sqldb.target_port, [22, 25, 443])
        self.assertEqual(idea_sqldb.source_type, ["Phishing"])
        self.assertEqual(idea_sqldb.target_type, ["Backscatter", "CasualIP", "OriginSpam"])
        self.assertEqual(idea_sqldb.protocol, ["http", "tcp"])
        self.assertEqual(idea_sqldb.category, ["Fraud.Phishing", "Test"])
        self.assertEqual(idea_sqldb.description, "Synthetic example")
        self.assertEqual(idea_sqldb.node_name, ["org.example.kippo_honey"])
        self.assertEqual(idea_sqldb.node_type, ["Honeypot", "Protocol"])
        self.assertEqual(idea_sqldb.resolvedabuses, ["abuse@cesnet.cz"])
        self.assertEqual(idea_sqldb.targetabuses, ["abuse@sanet.sk"])
        self.assertEqual(idea_sqldb.storagetime.isoformat(), "2017-04-05T10:21:39")
        self.assertEqual(idea_sqldb.eventclass, "vulnerable-config-ssdp")
        self.assertEqual(idea_sqldb.targetclass, "vulnerable-config-ssdp-target")
        self.assertEqual(idea_sqldb.eventseverity, "low")
        self.assertEqual(idea_sqldb.targetseverity, "medium")
        self.assertEqual(
            idea_sqldb.inspectionerrors,
            ["Demonstration error - first", "Demonstration error - second"],
        )
        self.assertEqual(idea_sqldb.tlp, "AMBER")
        self.assertEqual(idea_sqldb.shadow_reporting, True)
        self.assertEqual(idea_sqldb.shadow_reporting_target, True)

    def test_02_missing_node_names(self):
        """
        Perform test of presence of node names in the event.
        """
        # Only one node
        idea_internal = mentat.idea.internal.Idea(self.idea_raw_1)
        idea_sqldb = mentat.idea.sqldb.Idea(idea_internal)
        self.assertEqual(idea_sqldb.node_name, ["org.example.kippo_honey"])

        # Two nodes with two names
        idea_internal = mentat.idea.internal.Idea(self.idea_raw_2)
        idea_sqldb = mentat.idea.sqldb.Idea(idea_internal)
        self.assertEqual(
            idea_sqldb.node_name,
            ["org.example.kippo_honey", "org.example.kippo_honey2"],
        )

        # Two nodes but only one of them has a name
        idea_internal = mentat.idea.internal.Idea(self.idea_raw_3)
        idea_sqldb = mentat.idea.sqldb.Idea(idea_internal)
        self.assertEqual(idea_sqldb.node_name, ["org.example.kippo_honey"])

        # Two nodes but there is no name
        idea_internal = mentat.idea.internal.Idea(self.idea_raw_4)
        with self.assertRaisesRegex(KeyError, "Missing Node name"):
            idea_sqldb = mentat.idea.sqldb.Idea(idea_internal)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
