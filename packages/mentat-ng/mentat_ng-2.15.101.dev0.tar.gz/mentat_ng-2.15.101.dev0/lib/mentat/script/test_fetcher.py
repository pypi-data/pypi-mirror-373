#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.script.fetcher` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import os
import shutil
import unittest
from pprint import pprint

import mentat.idea.internal
import mentat.script.fetcher

#
# Global variables.
#
SCR_NAME = "test-fetcherscript.py"
CFG_FILE_NAME = mentat.script.fetcher.DemoFetcherScript.get_resource_path(f"tmp/{SCR_NAME}.conf")
CFG_DIR_NAME = mentat.script.fetcher.DemoFetcherScript.get_resource_path(f"tmp/{SCR_NAME}")


class TestMentatFetcherScript(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`mentat.script.fetcher.FetcherScript` class.
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
            "EventTemplate": "sserv-012",
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "Impact": "System provides SDDP service and can be misused for massive DDoS attack",
            "EventClass": "vulnerable-config-ssdp",
        },
    }

    def setUp(self):
        for directory in (
            mentat.script.fetcher.DemoFetcherScript.get_resource_path("tmp"),
            CFG_DIR_NAME,
        ):
            with contextlib.suppress(FileExistsError):
                os.mkdir(directory)

        mentat.script.fetcher.DemoFetcherScript.json_save(CFG_FILE_NAME, {"test_a": 1, "test_b": 2, "test_c": 3})

        self.script = mentat.script.fetcher.DemoFetcherScript(
            name=SCR_NAME,
            description="test-fetcherscript.py - Test fetcher script",
        )
        self.script.plugin()

    def tearDown(self):
        os.remove(CFG_FILE_NAME)
        shutil.rmtree(CFG_DIR_NAME)

    def test_01_time_calculations(self):
        """
        Perform the basic operativity tests.
        """
        tst = 1498477101.2179916
        if self.verbose:
            pprint(self.script.calculate_interval_thresholds(tst, "5_minutes"))
            pprint(self.script.calculate_interval_thresholds(tst, "10_minutes"))
            pprint(self.script.calculate_interval_thresholds(tst, "15_minutes"))
            pprint(self.script.calculate_interval_thresholds(tst, "20_minutes"))
            pprint(self.script.calculate_interval_thresholds(tst, "30_minutes"))

            pprint(self.script.calculate_interval_thresholds(tst, "5_minutes", True))
            pprint(self.script.calculate_interval_thresholds(tst, "10_minutes", True))
            pprint(self.script.calculate_interval_thresholds(tst, "15_minutes", True))
            pprint(self.script.calculate_interval_thresholds(tst, "20_minutes", True))
            pprint(self.script.calculate_interval_thresholds(tst, "30_minutes", True))

    # def test_02_fetching(self):
    # """
    # Perform the basic operativity tests.
    # """
    # self.script.eventservice.database_create()
    # self.script.eventservice.index_create()

    # This currently writes into production database, FIX it.
    # idea_internal = mentat.idea.internal.Idea(self.idea_raw)
    # idea_internal['_Mentat']['StorageTime'] = time.time()
    # self.script.eventservice.insert_event(idea_internal)

    # (time_high, time_low) = self.script.calculate_interval_thresholds(time.time(), '5_minutes')
    # pprint((time_high, time_low))
    # pprint(self.script.fetch_messages(time_high, time_low))
    # pprint(self.script.fetch_all_messages())


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
