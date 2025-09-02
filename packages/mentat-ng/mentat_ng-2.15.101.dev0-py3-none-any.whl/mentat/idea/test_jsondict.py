#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.idea.jsondict` module.
"""

import difflib
import json
import unittest

import idea.lite

import ipranges

import mentat.idea.internal
import mentat.idea.jsondict

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatIdeaJSON(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.idea.jsondict` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    idea_raw = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf75",
        "CreateTime": "2012-11-03T10:00:02Z",
        "DetectTime": "2012-11-03T10:00:07Z",
        "WinStartTime": "2012-11-03T05:00:00Z",
        "WinEndTime": "2012-11-03T10:00:00Z",
        "EventTime": "2012-11-03T07:36:00Z",
        "CeaseTime": "2012-11-03T09:55:22Z",
        "Category": ["Fraud.Phishing"],
        "Ref": ["cve:CVE-1234-5678"],
        "Confidence": 1.0,
        "Note": "Synthetic example",
        "ConnCount": 20,
        "Source": [
            {
                "Type": ["Phishing"],
                "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25"],
                "IP6": ["2001:db8::ff00:42:0/112"],
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
                "Spoofed": True,
            },
            {
                "Type": ["CasualIP"],
                "IP4": ["10.2.2.0/24"],
                "Port": [22, 25, 443],
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
                "Tags": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            }
        ],
        "_Mentat": {
            "StorageTime": "2017-04-05T10:21:39Z",
            "EventTemplate": "sserv-012",
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "Impact": "System provides SDDP service and can be misused for massive DDoS attack",
            "EventClass": "vulnerable-config-ssdp",
        },
    }

    def test_01_convert_timestamp(self):
        """
        Perfom isolated *Timestamp* conversion tests.
        """
        self.maxDiff = None

        tests = [
            [
                "ts_01",
                idea.lite.Timestamp("2012-11-03T10:00:02Z"),
                "2012-11-03T10:00:02Z",
            ]
        ]

        for tst in tests:
            res = mentat.idea.jsondict.Timestamp(tst[1])
            self.assertEqual([tst[0], res], [tst[0], tst[2]])

    def test_02_convert_net4(self):
        """
        Perfom isolated *Net4* conversion tests.
        """
        self.maxDiff = None

        tests = [
            ["ip_01", ipranges.IP4("192.168.0.1"), "192.168.0.1"],
            ["ip_02", ipranges.IP4Net("192.168.0.0/16"), "192.168.0.0/16"],
            [
                "ip_03",
                ipranges.IP4Range("192.168.0.1-192.168.0.250"),
                "192.168.0.1-192.168.0.250",
            ],
        ]

        for tst in tests:
            res = mentat.idea.jsondict.Net4(tst[1])
            self.assertEqual([tst[0], res], [tst[0], tst[2]])

    def test_03_convert_net6(self):
        """
        Perfom isolated *Net6* conversion tests.
        """
        self.maxDiff = None

        tests = [
            [
                "ip_01",
                ipranges.IP6("2001:db8:220:1:248:1893:25c8:1946"),
                "2001:db8:220:1:248:1893:25c8:1946",
            ],
            ["ip_02", ipranges.IP6Net("2001:db8:220:1::/64"), "2001:db8:220:1::/64"],
            [
                "ip_03",
                ipranges.IP6Range("2001:db8:220:1:248:1893:25c8:1946-2001:db8:230:1:248:1893:25c8:1946"),
                "2001:db8:220:1:248:1893:25c8:1946-2001:db8:230:1:248:1893:25c8:1946",
            ],
        ]

        for tst in tests:
            res = mentat.idea.jsondict.Net6(tst[1])
            self.assertEqual([tst[0], res], [tst[0], tst[2]])

    def test_04_conv_internal(self):
        """
        Perform basic parsing and conversion tests from ``menat.idea.internal.Idea`` class
        messages. For the purposes of comparison, the ``menat.idea.internal.Idea`` class
        is also tested here.
        """
        self.maxDiff = None

        #
        # Test conversions of raw JSON IDEA into 'mentat.idea.internal.Idea'.
        #
        idea_internal = mentat.idea.internal.Idea(self.idea_raw)
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
        orig = json.dumps(self.idea_raw, indent=4, sort_keys=True)
        new = json.dumps(idea_internal, indent=4, sort_keys=True, default=idea_internal.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        #
        # Test conversions of 'mentat.idea.internal.Idea' into 'mentat.idea.jsondict.Idea'.
        #
        idea_json = mentat.idea.jsondict.Idea(idea_internal)
        if self.verbose:
            print("'mentat.idea.jsondict.Idea' out of 'mentat.idea.internal.Idea':")
            print(json.dumps(idea_json, indent=4, sort_keys=True, default=idea_json.json_default))
        # Verify, that conversions really do occur.
        self.assertEqual(idea_json["CreateTime"], "2012-11-03T10:00:02Z")
        self.assertEqual(idea_json["Category"], ["Fraud.Phishing"])
        self.assertEqual(
            idea_json["Source"],
            [
                {
                    "AttachHand": ["att1"],
                    "Hostname": ["example.com"],
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                    "Netname": ["ripe:IANA-CBLK-RESERVED1"],
                    "Proto": ["tcp", "http"],
                    "Type": ["Phishing"],
                    "URL": ["http://example.com/cgi-bin/killemall"],
                }
            ],
        )

        #
        # Test conversions of 'mentat.idea.jsondict.Idea' based on 'mentat.idea.internal.Idea' back into 'mentat.idea.internal.Idea'.
        #
        idea_internal_out = mentat.idea.internal.Idea(idea_json)
        if self.verbose:
            print(
                "'mentat.idea.internal.Idea' out of 'mentat.idea.jsondict.Idea' based on 'mentat.idea.internal.Idea':"
            )
            print(
                json.dumps(
                    idea_internal_out,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_out.json_default,
                )
            )
        orig = json.dumps(idea_internal, indent=4, sort_keys=True, default=idea_internal.json_default)
        new = json.dumps(
            idea_internal_out,
            indent=4,
            sort_keys=True,
            default=idea_internal_out.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
