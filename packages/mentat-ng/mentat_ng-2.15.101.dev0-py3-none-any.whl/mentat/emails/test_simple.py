#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.emails.simple` module.
"""

__author__ = "Rajmund Hruška <rajmund.hruska@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)


import unittest

import mentat.emails.simple


class TestSimpleEmail(unittest.TestCase):
    """
    Unit test class for testing the :py:class:`mentat.emails.simple.SimpleEmail` class.
    """

    def test_basic(self):
        """
        Perform the basic operativity tests.
        """
        msg = mentat.emails.simple.SimpleEmail(
            headers={
                "subject": "Test email",
                "from": "root",
                "to": "user",
                "cc": ["admin", "manager"],
                "bcc": "spy",
            },
            text_plain="TEXT PLAIN",
        )
        self.assertTrue(msg.as_string())


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
