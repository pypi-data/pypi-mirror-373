#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing third-party IDEA library for sanity.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import difflib
import json
import unittest

from idea import lite, valid

RAW_IDEA = {
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
            "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.10/25"],
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
}


class TestIDEA(unittest.TestCase):
    """
    Test third-party IDEA library for sanity.
    """

    def test_basic(self):
        """
        Perform the basic operativity tests.
        """
        idea = lite.Idea(RAW_IDEA)
        orig = json.dumps(RAW_IDEA, indent=4, sort_keys=True)
        new = json.dumps(idea, indent=4, sort_keys=True, default=idea.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))

        idea = valid.Idea(RAW_IDEA)
        orig = json.dumps(RAW_IDEA, indent=4, sort_keys=True)
        new = json.dumps(idea, indent=4, sort_keys=True, default=idea.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
