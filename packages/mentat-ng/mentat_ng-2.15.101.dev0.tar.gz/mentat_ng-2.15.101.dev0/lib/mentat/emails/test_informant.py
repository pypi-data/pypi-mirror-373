#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.emails.informant` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import unittest

import mentat.emails.informant


class TestReportEmail(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`mentat.emails.informant.ReportEmail` class.
    """

    def test_basic(self):
        """
        Perform the basic operativity tests.
        """
        msg = mentat.emails.informant.ReportEmail(
            headers={
                "subject": "Test email",
                "from": "root",
                "to": "user",
                "cc": ["admin", "manager"],
                "bcc": "spy",
            },
            text_plain="TEXT PLAIN",
            text_html="<h1>TEXT HTML</h1>",
            data_events={"a": 1, "b": [datetime.datetime(2017, 1, 1, 12, 0, 0)]},
            data_reports={"a": 1, "b": [datetime.datetime(2017, 1, 1, 12, 0, 0)]},
        )
        # print(msg.as_string())
        self.assertTrue(msg.as_string())


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
