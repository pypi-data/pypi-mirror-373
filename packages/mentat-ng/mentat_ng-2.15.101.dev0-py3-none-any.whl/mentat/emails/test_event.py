#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.emails.event` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import json
import os
import unittest
import zipfile

import mentat.emails.event
import mentat.idea.internal

UTEST_JSON_RAW = "/var/tmp/utest-security-report-xxx.json"
UTEST_JSON_ZIP = "/var/tmp/utest-security-report-xxx.json.zip"


class TestReportEmail(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`mentat.emails.event.ReportEmail` class.
    """

    ideas_raw = [
        {
            "ID": "4dd7cf5e-4a95-49f6-8f04-947de998012c",
            "Format": "IDEA0",
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
            "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
        }
    ]
    ideas_obj = [mentat.idea.internal.Idea(x) for x in ideas_raw]

    def setUp(self):
        with open(UTEST_JSON_RAW, "w", encoding="utf8") as rawf:
            json.dump(
                self.ideas_obj,
                rawf,
                default=mentat.idea.internal.Idea.json_default,
                sort_keys=True,
                indent=4,
            )

        with zipfile.ZipFile(UTEST_JSON_ZIP, mode="w") as zipf:
            zipf.write(UTEST_JSON_RAW, compress_type=zipfile.ZIP_DEFLATED)

    def tearDown(self):
        os.unlink(UTEST_JSON_RAW)
        os.unlink(UTEST_JSON_ZIP)

    def test_01_guess_attachment(self):
        """
        Perform tests of guessing attachment mimetypes.
        """
        self.assertEqual(
            mentat.emails.event.ReportEmail.guess_attachment(UTEST_JSON_RAW),
            "application/json",
        )
        self.assertEqual(
            mentat.emails.event.ReportEmail.guess_attachment(UTEST_JSON_ZIP),
            "application/zip",
        )

    def test_02_create_report(self):
        """
        Perform the tests of generating basic report.
        """
        msg = mentat.emails.event.ReportEmail(
            headers={
                "subject": "Test email",
                "from": "root",
                "to": "user",
                "cc": ["admin", "manager"],
                "bcc": "spy",
                "report_type": "overridden-type",
                "return_path": "return@email.com",
                "report_id": "xxx",
            },
            text_plain="TEXT PLAIN",
            attachments=[UTEST_JSON_RAW, UTEST_JSON_ZIP],
        )
        self.assertTrue(msg)
        self.assertTrue(msg.as_string())
        # print(msg.as_string())


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
