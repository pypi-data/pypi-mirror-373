#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.overview` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import unittest

import mentat.reports.overview

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------

REPORTS_DIR = "/var/tmp"


class TestMentatReportsOverview(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.overview` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    def setUp(self):
        """
        Perform test case setup.
        """
        self.reporter = mentat.reports.overview.OverviewReporter(
            None,
            "/var/tmp",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../conf/templates/informant")),
        )

    def test_01_format_section_key(self):
        """
        Perform section key formating tests.
        """
        self.maxDiff = None

        self.assertEqual(self.reporter.format_section_key("asns", 5555), "AS 5555")
        self.assertEqual(self.reporter.format_section_key("asns", "__unknown__"), "__unknown__")
        self.assertEqual(self.reporter.format_section_key("asns", "__REST__"), "__REST__")
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_section_key("asns", 5555), "AS 5555")
        self.assertEqual(self.reporter.format_section_key("asns", "__unknown__"), "__neznámé__")
        self.assertEqual(self.reporter.format_section_key("asns", "__REST__"), "__OSTATNÍ__")

    def test_02_save_to_json_file(self):
        """
        Test :py:func:`mentat.reports.everview.OverviewReporter._save_to_json_file` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = "utest-overview-report.json"
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_json_file(  # pylint: disable=locally-disabled,protected-access
                {"a": 1, "b": 2}, report_file
            ),
            report_path,
        )
        self.assertTrue(os.path.isfile(report_path))
        os.unlink(report_path)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
