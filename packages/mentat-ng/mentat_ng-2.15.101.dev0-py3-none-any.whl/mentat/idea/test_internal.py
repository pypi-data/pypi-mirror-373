#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.idea.internal` module.
"""

import difflib
import json
import unittest

import idea.lite

import ipranges

import mentat.idea.internal
from mentat.idea.internal import (
    JPATH_RC_VALUE_DUPLICATE,
    JPATH_RC_VALUE_EXISTS,
    JPATH_RC_VALUE_SET,
    jpath_parse,
    jpath_set,
)

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatIdeaInternal(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.idea.internal` module.
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
        "TLP": "Green",
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
        "ConnCount": 20,
        "Source": [
            {
                "Type": ["Phishing"],
                "IP4": [
                    "192.168.0.2-192.168.0.5",
                    "192.168.0.0/25",
                    "192.168.1.1",
                    "192.168.1.2",
                    "192.168.1.4",
                ],
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
                "Proto": ["tcp", "http"],
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
            "EventSubclass": ["cvr-42"],
            "TargetSubclass": ["cvr-42"],
            "EventSeverity": "low",
            "TargetSeverity": "medium",
            "ShadowReporting": True,
        },
    }

    idea_raw_2 = {
        "ID": "4dd7cf5e-4a95-49f6-8f04-947de998012c",
        "Format": "IDEA0",
        "TLP": "AMBER",
        "DetectTime": "2016-06-21T13:08:27Z",
        "WinStartTime": "2016-06-21T11:55:02Z",
        "WinEndTime": "2016-06-21T12:00:02Z",
        "ConnCount": 2,
        "Category": ["Attempt.Login"],
        "Description": "SSH login attempt",
        "Source": [{"IP4": ["188.14.166.39"]}],
        "Target": [
            {
                "Proto": ["tcp", "ssh"],
                "IP4": ["195.113.165.128/25"],
                "Port": [22],
                "Anonymised": True,
            }
        ],
        "Node": [
            {"Type": ["Relay"], "Name": "cz.cesnet.mentat.warden_filer"},
            {
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
                "Name": "cz.uhk.apate.cowrie",
                "Type": ["Connection", "Honeypot", "Recon"],
            },
        ],
        "_Mentat": {
            "StorageTime": "2016-06-21T14:00:07Z",
            "ShadowReportingTarget": True,
        },
    }

    def test_jpath_parse(self):
        """
        Perform the basic JPath parsing tests.

        Make sure all possible JPath forms parse correctly.
        """
        self.maxDiff = None

        self.assertEqual(jpath_parse("Test"), [{"m": "Test", "n": "Test", "p": "Test"}])
        self.assertEqual(
            jpath_parse("Test.Path"),
            [{"m": "Test", "n": "Test", "p": "Test"}, {"m": "Path", "n": "Path", "p": "Test.Path"}],
        )
        self.assertEqual(
            jpath_parse("Long.Test.Path"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"m": "Test", "n": "Test", "p": "Long.Test"},
                {"m": "Path", "n": "Path", "p": "Long.Test.Path"},
            ],
        )

        self.assertEqual(
            jpath_parse("Long[1].Test.Path"),
            [
                {"i": 0, "m": "Long[1]", "n": "Long", "p": "Long[1]"},
                {"m": "Test", "n": "Test", "p": "Long[1].Test"},
                {"m": "Path", "n": "Path", "p": "Long[1].Test.Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[2].Path"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": 1, "m": "Test[2]", "n": "Test", "p": "Long.Test[2]"},
                {"m": "Path", "n": "Path", "p": "Long.Test[2].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test.Path[3]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"m": "Test", "n": "Test", "p": "Long.Test"},
                {"i": 2, "m": "Path[3]", "n": "Path", "p": "Long.Test.Path[3]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[1].Test[1].Path"),
            [
                {"i": 0, "m": "Long[1]", "n": "Long", "p": "Long[1]"},
                {"i": 0, "m": "Test[1]", "n": "Test", "p": "Long[1].Test[1]"},
                {"m": "Path", "n": "Path", "p": "Long[1].Test[1].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[2].Path[2]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": 1, "m": "Test[2]", "n": "Test", "p": "Long.Test[2]"},
                {"i": 1, "m": "Path[2]", "n": "Path", "p": "Long.Test[2].Path[2]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[3].Test.Path[3]"),
            [
                {"i": 2, "m": "Long[3]", "n": "Long", "p": "Long[3]"},
                {"m": "Test", "n": "Test", "p": "Long[3].Test"},
                {"i": 2, "m": "Path[3]", "n": "Path", "p": "Long[3].Test.Path[3]"},
            ],
        )

        self.assertEqual(
            jpath_parse("Long[#].Test.Path"),
            [
                {"i": -1, "m": "Long[#]", "n": "Long", "p": "Long[#]"},
                {"m": "Test", "n": "Test", "p": "Long[#].Test"},
                {"m": "Path", "n": "Path", "p": "Long[#].Test.Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[#].Path"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": -1, "m": "Test[#]", "n": "Test", "p": "Long.Test[#]"},
                {"m": "Path", "n": "Path", "p": "Long.Test[#].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test.Path[#]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"m": "Test", "n": "Test", "p": "Long.Test"},
                {"i": -1, "m": "Path[#]", "n": "Path", "p": "Long.Test.Path[#]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[#].Test[#].Path"),
            [
                {"i": -1, "m": "Long[#]", "n": "Long", "p": "Long[#]"},
                {"i": -1, "m": "Test[#]", "n": "Test", "p": "Long[#].Test[#]"},
                {"m": "Path", "n": "Path", "p": "Long[#].Test[#].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[#].Path[#]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": -1, "m": "Test[#]", "n": "Test", "p": "Long.Test[#]"},
                {"i": -1, "m": "Path[#]", "n": "Path", "p": "Long.Test[#].Path[#]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[#].Test.Path[#]"),
            [
                {"i": -1, "m": "Long[#]", "n": "Long", "p": "Long[#]"},
                {"m": "Test", "n": "Test", "p": "Long[#].Test"},
                {"i": -1, "m": "Path[#]", "n": "Path", "p": "Long[#].Test.Path[#]"},
            ],
        )

        self.assertEqual(
            jpath_parse("Long[*].Test.Path"),
            [
                {"i": "*", "m": "Long[*]", "n": "Long", "p": "Long[*]"},
                {"m": "Test", "n": "Test", "p": "Long[*].Test"},
                {"m": "Path", "n": "Path", "p": "Long[*].Test.Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[*].Path"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": "*", "m": "Test[*]", "n": "Test", "p": "Long.Test[*]"},
                {"m": "Path", "n": "Path", "p": "Long.Test[*].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test.Path[*]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"m": "Test", "n": "Test", "p": "Long.Test"},
                {"i": "*", "m": "Path[*]", "n": "Path", "p": "Long.Test.Path[*]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[*].Test[*].Path"),
            [
                {"i": "*", "m": "Long[*]", "n": "Long", "p": "Long[*]"},
                {"i": "*", "m": "Test[*]", "n": "Test", "p": "Long[*].Test[*]"},
                {"m": "Path", "n": "Path", "p": "Long[*].Test[*].Path"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long.Test[*].Path[*]"),
            [
                {"m": "Long", "n": "Long", "p": "Long"},
                {"i": "*", "m": "Test[*]", "n": "Test", "p": "Long.Test[*]"},
                {"i": "*", "m": "Path[*]", "n": "Path", "p": "Long.Test[*].Path[*]"},
            ],
        )
        self.assertEqual(
            jpath_parse("Long[*].Test.Path[*]"),
            [
                {"i": "*", "m": "Long[*]", "n": "Long", "p": "Long[*]"},
                {"m": "Test", "n": "Test", "p": "Long[*].Test"},
                {"i": "*", "m": "Path[*]", "n": "Path", "p": "Long[*].Test.Path[*]"},
            ],
        )

        self.assertEqual(jpath_parse("Test"), [{"m": "Test", "n": "Test", "p": "Test"}])
        self.assertEqual(jpath_parse("test"), [{"m": "test", "n": "test", "p": "test"}])
        self.assertEqual(jpath_parse("TEST"), [{"m": "TEST", "n": "TEST", "p": "TEST"}])
        self.assertEqual(jpath_parse("_test"), [{"m": "_test", "n": "_test", "p": "_test"}])

        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test/Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test|Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test-Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test-.Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test[]Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "TestValue[]")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test[1]Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test[].Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test.Value[]")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test[-1].Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test.[1].Value")
        self.assertRaisesRegex(ValueError, "Invalid JPath chunk", jpath_parse, "Test.Value.[1]")

    def test_jpath_set(self):
        """
        Perform the basic JPath value setting tests.
        """
        self.maxDiff = None

        msg = {}
        self.assertEqual(jpath_set(msg, "TestA.ValueA1", "A1"), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestA": {"ValueA1": "A1"}})
        self.assertEqual(jpath_set(msg, "TestA.ValueA2", "A2"), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestA": {"ValueA1": "A1", "ValueA2": "A2"}})
        self.assertEqual(jpath_set(msg, "TestB[1].ValueB1", "B1"), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestA": {"ValueA1": "A1", "ValueA2": "A2"}, "TestB": [{"ValueB1": "B1"}]})
        self.assertEqual(jpath_set(msg, "TestB[#].ValueB2", "B2"), JPATH_RC_VALUE_SET)
        self.assertEqual(
            msg, {"TestA": {"ValueA1": "A1", "ValueA2": "A2"}, "TestB": [{"ValueB1": "B1", "ValueB2": "B2"}]}
        )
        self.assertEqual(jpath_set(msg, "TestB[*].ValueB3", "B3"), JPATH_RC_VALUE_SET)
        self.assertEqual(
            msg,
            {
                "TestA": {"ValueA1": "A1", "ValueA2": "A2"},
                "TestB": [{"ValueB1": "B1", "ValueB2": "B2"}, {"ValueB3": "B3"}],
            },
        )
        self.assertEqual(jpath_set(msg, "TestB[#].ValueB4", "B4"), JPATH_RC_VALUE_SET)
        self.assertEqual(
            msg,
            {
                "TestA": {"ValueA1": "A1", "ValueA2": "A2"},
                "TestB": [{"ValueB1": "B1", "ValueB2": "B2"}, {"ValueB3": "B3", "ValueB4": "B4"}],
            },
        )
        self.assertEqual(jpath_set(msg, "TestB[#]", "DROP"), JPATH_RC_VALUE_SET)
        self.assertEqual(
            msg, {"TestA": {"ValueA1": "A1", "ValueA2": "A2"}, "TestB": [{"ValueB1": "B1", "ValueB2": "B2"}, "DROP"]}
        )

        # This will fail, because "TestA" node is not a list
        self.assertRaisesRegex(
            ValueError, "Expected list-like object under structure key", jpath_set, msg, "TestA[#].ValueC1", "C1"
        )

        # This will fail, because "TestA.ValueA1" node is not a dict
        self.assertRaisesRegex(
            ValueError, "Expected dict-like object under structure key", jpath_set, msg, "TestA.ValueA1.ValueC1", "C1"
        )

        # This will fail, because we try to attach a node to scalar "TestB[#]"
        self.assertRaisesRegex(
            ValueError,
            "Expected dict-like structure to attach node",
            jpath_set,
            msg,
            "TestB[#].ValueB5",
            "RAISE EXCEPTION",
        )

    def test_jpath_set_unique(self):
        """
        Perform JPath value setting tests with unique flag.
        """
        self.maxDiff = None

        msg = {}
        self.assertEqual(jpath_set(msg, "TestC[#].ListVals1[*]", "LV1", unique=True), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestC": [{"ListVals1": ["LV1"]}]})
        self.assertEqual(jpath_set(msg, "TestC[#].ListVals1[*]", "LV2", unique=True), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestC": [{"ListVals1": ["LV1", "LV2"]}]})
        self.assertEqual(jpath_set(msg, "TestC[#].ListVals1[*]", "LV1", unique=True), JPATH_RC_VALUE_DUPLICATE)
        self.assertEqual(msg, {"TestC": [{"ListVals1": ["LV1", "LV2"]}]})

    def test_jpath_set_overwrite(self):
        """
        Perform JPath value setting tests with overwrite flag.
        """
        self.maxDiff = None

        msg = {}

        #
        # Overwriting in lists.
        #
        self.assertEqual(jpath_set(msg, "TestD[#].ListVals1[*]", "LV1", overwrite=False), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1"]}]})
        self.assertEqual(jpath_set(msg, "TestD[#].ListVals1[*]", "LV2", overwrite=False), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1", "LV2"]}]})
        self.assertEqual(jpath_set(msg, "TestD[#].ListVals1[2]", "LV3", overwrite=False), JPATH_RC_VALUE_EXISTS)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1", "LV2"]}]})
        self.assertEqual(jpath_set(msg, "TestD[#].ListVals1[3]", "LV3", overwrite=False), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1", "LV2", "LV3"]}]})

        #
        # Overwriting in dicts.
        #
        self.assertEqual(jpath_set(msg, "TestD[#].DictVal", "DV1", overwrite=False), JPATH_RC_VALUE_SET)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1", "LV2", "LV3"], "DictVal": "DV1"}]})
        self.assertEqual(jpath_set(msg, "TestD[#].DictVal", "DV2", overwrite=False), JPATH_RC_VALUE_EXISTS)
        self.assertEqual(msg, {"TestD": [{"ListVals1": ["LV1", "LV2", "LV3"], "DictVal": "DV1"}]})

    def test_01_idea_raw(self):
        """
        Perform basic parsing and conversion tests from raw JSON.
        """
        self.maxDiff = None

        idea_internal_1 = mentat.idea.internal.Idea(self.idea_raw_1)
        if self.verbose:
            print("IDEA raw 1 as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_1,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_1.json_default,
                )
            )
        self.assertEqual(
            json.dumps(
                idea_internal_1,
                indent=4,
                sort_keys=True,
                default=idea_internal_1.json_default,
            ),
            idea_internal_1.to_json(indent=4),
        )
        orig = json.dumps(self.idea_raw_1, indent=4, sort_keys=True)
        new = json.dumps(
            idea_internal_1,
            indent=4,
            sort_keys=True,
            default=idea_internal_1.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        idea_internal_2 = mentat.idea.internal.Idea(self.idea_raw_2)
        if self.verbose:
            print("IDEA raw 2 as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_2,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_2.json_default,
                )
            )
        self.assertEqual(
            json.dumps(
                idea_internal_2,
                indent=4,
                sort_keys=True,
                default=idea_internal_2.json_default,
            ),
            idea_internal_2.to_json(indent=4),
        )
        orig = json.dumps(self.idea_raw_2, indent=4, sort_keys=True)
        new = json.dumps(
            idea_internal_2,
            indent=4,
            sort_keys=True,
            default=idea_internal_2.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

    def test_02_idea_lite(self):
        """
        Perform basic parsing and conversion tests from ``idea.lite.Idea``. For
        the purposes of comparison, the ``idea.lite.Idea`` class is also tested here.
        """
        self.maxDiff = None

        idea_lite_1 = idea.lite.Idea(self.idea_raw_1)
        if self.verbose:
            print("IDEA raw 1 as 'idea.lite.Idea' object:")
            print(
                json.dumps(
                    idea_lite_1,
                    indent=4,
                    sort_keys=True,
                    default=idea_lite_1.json_default,
                )
            )
        orig = json.dumps(self.idea_raw_1, indent=4, sort_keys=True)
        new = json.dumps(idea_lite_1, indent=4, sort_keys=True, default=idea_lite_1.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        idea_internal_1 = mentat.idea.internal.Idea(idea_lite_1)
        if self.verbose:
            print("IDEA object 'idea.lite.Idea' as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_1,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_1.json_default,
                )
            )
        orig = json.dumps(self.idea_raw_1, indent=4, sort_keys=True)
        new = json.dumps(
            idea_internal_1,
            indent=4,
            sort_keys=True,
            default=idea_internal_1.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        idea_lite_2 = idea.lite.Idea(self.idea_raw_2)
        if self.verbose:
            print("IDEA raw 2 as 'idea.lite.Idea' object:")
            print(
                json.dumps(
                    idea_lite_2,
                    indent=4,
                    sort_keys=True,
                    default=idea_lite_2.json_default,
                )
            )
        orig = json.dumps(self.idea_raw_2, indent=4, sort_keys=True)
        new = json.dumps(idea_lite_2, indent=4, sort_keys=True, default=idea_lite_2.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        idea_internal_2 = mentat.idea.internal.Idea(idea_lite_2)
        if self.verbose:
            print("IDEA object 'idea.lite.Idea' as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_2,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_2.json_default,
                )
            )
        orig = json.dumps(self.idea_raw_2, indent=4, sort_keys=True)
        new = json.dumps(
            idea_internal_2,
            indent=4,
            sort_keys=True,
            default=idea_internal_2.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

    def test_03_accessors(self):
        """
        Perform tests of message convenience accessors.
        """
        self.maxDiff = None

        idea_internal_1 = mentat.idea.internal.Idea(self.idea_raw_1)
        if self.verbose:
            print("IDEA raw 1 as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_1,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_1.json_default,
                )
            )

        self.assertEqual(idea_internal_1.get_id(), "4390fc3f-c753-4a3e-bc83-1b44f24baf75")
        self.assertEqual(idea_internal_1.get_tlp(), "GREEN")
        self.assertEqual(idea_internal_1.get_detect_time().isoformat(), "2012-11-03T10:00:07")
        self.assertEqual(idea_internal_1.get_storage_time().isoformat(), "2017-04-05T10:21:39")
        self.assertEqual(idea_internal_1.get_source_groups(), ["abuse@cesnet.cz"])
        self.assertEqual(idea_internal_1.get_target_groups(), ["abuse@sanet.sk"])
        self.assertEqual(set(idea_internal_1.get_all_groups()), {"abuse@cesnet.cz", "abuse@sanet.sk"})
        self.assertEqual(idea_internal_1.get_categories(), ["Fraud.Phishing", "Test"])
        self.assertEqual(idea_internal_1.get_description(), "Synthetic example")
        self.assertEqual(idea_internal_1.get_class(), "vulnerable-config-ssdp")
        self.assertEqual(idea_internal_1.get_subclass(), "cvr-42")
        self.assertEqual(idea_internal_1.get_whole_class(), "vulnerable-config-ssdp/cvr-42")
        self.assertEqual(idea_internal_1.get_target_class(), "vulnerable-config-ssdp-target")
        self.assertEqual(idea_internal_1.get_target_subclass(), "cvr-42")
        self.assertEqual(
            idea_internal_1.get_whole_target_class(),
            "vulnerable-config-ssdp-target/cvr-42",
        )
        self.assertEqual(idea_internal_1.get_severity(), "low")
        self.assertEqual(idea_internal_1.get_target_severity(), "medium")
        self.assertEqual(idea_internal_1.get_detectors(), ["org.example.kippo_honey"])
        self.assertEqual(idea_internal_1.get_last_detector_name(), "org.example.kippo_honey")
        self.assertEqual(
            idea_internal_1.get_addresses("Source"),
            [
                ipranges.IP4("192.168.1.4"),
                ipranges.IP4Range("192.168.1.1-192.168.1.2"),
                ipranges.IP4Range("192.168.0.0-192.168.0.127"),
                ipranges.IP6Range("2001:db8::ff00:42:0-2001:db8::ff00:42:ffff"),
            ],
        )
        self.assertEqual(
            idea_internal_1.get_addresses("Target"),
            [
                ipranges.IP4Range("10.2.2.0-10.2.2.255"),
                ipranges.IP6Range("2001:ffff::ff00:42:0-2001:ffff::ff00:42:ffff"),
            ],
        )
        self.assertEqual(idea_internal_1.get_ports("Source"), [])
        self.assertEqual(idea_internal_1.get_ports("Target"), [22, 25, 443])
        self.assertEqual(idea_internal_1.get_protocols("Source"), ["http", "tcp"])
        self.assertEqual(idea_internal_1.get_protocols("Target"), ["http", "tcp"])
        self.assertEqual(idea_internal_1.get_types("Source"), ["Phishing"])
        self.assertEqual(
            idea_internal_1.get_types("Target"),
            ["Backscatter", "CasualIP", "OriginSpam"],
        )
        self.assertEqual(idea_internal_1.get_types("Node"), ["Honeypot", "Protocol"])
        self.assertTrue(idea_internal_1.is_shadow())
        self.assertFalse(idea_internal_1.is_shadow_target())

        idea_internal_2 = mentat.idea.internal.Idea(self.idea_raw_2)
        self.assertEqual(idea_internal_2.get_tlp(), "AMBER")
        self.assertTrue(idea_internal_2.has_restricted_access())
        self.assertFalse(idea_internal_2.is_shadow())
        self.assertTrue(idea_internal_2.is_shadow_target())

    def test_04_to_and_from_string(self):
        """
        Perform tests of message conversions to and from JSON string representation.
        """
        self.maxDiff = None

        idea_internal_1 = mentat.idea.internal.Idea(self.idea_raw_1)
        if self.verbose:
            print("IDEA raw 1 as 'mentat.idea.internal.Idea' object:")
            print(
                json.dumps(
                    idea_internal_1,
                    indent=4,
                    sort_keys=True,
                    default=idea_internal_1.json_default,
                )
            )
        idea_internal_2 = mentat.idea.internal.Idea.from_json(idea_internal_1.to_json())
        orig = json.dumps(
            idea_internal_1,
            indent=4,
            sort_keys=True,
            default=idea_internal_1.json_default,
        )
        new = json.dumps(
            idea_internal_2,
            indent=4,
            sort_keys=True,
            default=idea_internal_2.json_default,
        )
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

    def test_05_get_ranges(self):
        """
        Perform tests of get_ranges function.
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges([], ipranges.IP4Range, ipranges.IP4),
            [],
        )
        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges([], ipranges.IP6Range, ipranges.IP4),
            [],
        )
        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges(
                [
                    ipranges.IP4("192.168.0.2"),
                    ipranges.IP4("192.168.0.3"),
                    ipranges.IP4("192.168.0.4"),
                    ipranges.IP4("192.168.0.5"),
                ],
                ipranges.IP4Range,
                ipranges.IP4,
            ),
            [ipranges.IP4Range((ipranges.IP4("192.168.0.2"), ipranges.IP4("192.168.0.5")))],
        )
        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges(
                [
                    ipranges.IP4("192.168.0.3"),
                    ipranges.IP4("192.168.0.5"),
                    ipranges.IP4("192.168.1.19"),
                    ipranges.IP4("192.168.1.20"),
                ],
                ipranges.IP4Range,
                ipranges.IP4,
            ),
            [
                ipranges.IP4Range((ipranges.IP4("192.168.1.19"), ipranges.IP4("192.168.1.20"))),
                ipranges.IP4("192.168.0.5"),
                ipranges.IP4("192.168.0.3"),
            ],
        )
        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges(
                [
                    ipranges.IP4("192.168.0.2"),
                    ipranges.IP4("192.168.0.5"),
                    ipranges.IP4("192.168.0.7"),
                ],
                ipranges.IP4Range,
                ipranges.IP4,
            ),
            [
                ipranges.IP4("192.168.0.7"),
                ipranges.IP4("192.168.0.5"),
                ipranges.IP4("192.168.0.2"),
            ],
        )

        self.assertEqual(
            mentat.idea.internal.Idea.get_ranges(
                [
                    ipranges.IP6("2001:db8::ff00:42:50"),
                    ipranges.IP6("2001:0db8::ff00:42:51"),
                    ipranges.IP6("2001:db8::ff00:42:0052"),
                    ipranges.IP6("2001:0db8::ff00:0042:0053"),
                ],
                ipranges.IP6Range,
                ipranges.IP6,
            ),
            [
                ipranges.IP6Range(
                    (
                        ipranges.IP6("2001:db8::ff00:42:50"),
                        ipranges.IP6("2001:db8::ff00:42:53"),
                    )
                )
            ],
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
