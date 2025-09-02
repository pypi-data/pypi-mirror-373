#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.base` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import os
import unittest
from unittest.mock import Mock, call

import mentat.reports.base

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatReportsBase(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.base` module.
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
        self.reporter = mentat.reports.base.BaseReporter(
            Mock(),
            "/var/tmp",
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../conf/templates/utest")),
        )

    def test_01_format_decimal(self):
        """
        Perform decimal formating tests.
        """
        self.maxDiff = None

        num = 1265358.56
        self.assertEqual(self.reporter.format_decimal(num), "1,265,358.56")
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_decimal(num), "1\xa0265\xa0358,56")

    def test_02_format_datetime(self):
        """
        Perform datetime formating tests.
        """
        self.maxDiff = None

        dtm = datetime.datetime(2018, 1, 1, 12, 0)
        self.assertRegex(
            self.reporter.format_datetime(dtm),
            r"Jan 1, 2018, 12:00:00[\u0020|\u202f]PM",
        )
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_datetime(dtm), "1. 1. 2018 12:00:00")

    def test_03_format_localdatetime(self):
        """
        Perform datetime formating tests in local timezone.
        """
        self.maxDiff = None

        dtm = datetime.datetime(2018, 1, 1, 12, 0)
        dtml = datetime.datetime(2018, 1, 1, 12, 0) + (
            datetime.datetime.fromtimestamp(dtm.timestamp()) - datetime.datetime.utcfromtimestamp(dtm.timestamp())
        )

        self.assertEqual(
            self.reporter.format_localdatetime(dtm),
            self.reporter.format_datetime(dtml),
        )
        self.reporter.set_locale("cs")
        self.assertEqual(
            self.reporter.format_localdatetime(dtm),
            self.reporter.format_datetime(dtml),
        )

    def test_04_format_tzdatetime(self):
        """
        Perform timezone aware datetime formating tests.
        """
        self.maxDiff = None

        dtm = datetime.datetime(2018, 1, 1, 12, 0)
        self.assertRegex(
            self.reporter.format_tzdatetime(dtm),
            r"Jan 1, 2018, 12:00:00[\u0020|\u202f]PM",
        )
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_tzdatetime(dtm), "1. 1. 2018 12:00:00")
        self.reporter.set_timezone("Europe/Prague")
        self.assertEqual(self.reporter.format_tzdatetime(dtm), "1. 1. 2018 13:00:00")
        self.reporter.set_timezone("America/Los_Angeles")
        self.assertEqual(self.reporter.format_tzdatetime(dtm), "1. 1. 2018 4:00:00")

    def test_05_format_rfctzdatetime(self):
        """
        Perform timezone aware datetime formating tests with enforced RFC 3339
        time format.
        """
        self.maxDiff = None

        dtm = datetime.datetime(2018, 1, 1, 12, 0)
        self.assertEqual(self.reporter.format_rfctzdatetime(dtm), "2018-01-01T12:00:00+0000")
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_rfctzdatetime(dtm), "2018-01-01T12:00:00+0000")
        self.reporter.set_timezone("Europe/Prague")
        self.assertEqual(self.reporter.format_rfctzdatetime(dtm), "2018-01-01T13:00:00+0100")
        self.reporter.set_timezone("America/Los_Angeles")
        self.assertEqual(self.reporter.format_rfctzdatetime(dtm), "2018-01-01T04:00:00-0800")

    def test_06_format_timedelta(self):
        """
        Perform timedelta formating tests.
        """
        self.maxDiff = None

        tdl = datetime.timedelta(days=2, seconds=12)
        self.assertEqual(self.reporter.format_timedelta(tdl), "2 days")
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.format_timedelta(tdl), "2 dny")

    def test_07_format_url(self):
        """
        Perform URL formating tests.
        """
        self.maxDiff = None

        self.assertEqual(self.reporter.format_url("https://domain.org/"), "https://domain.org/")
        self.assertEqual(
            self.reporter.format_url("https://domain.org/test", {"key1": "value1", "submit": "Search"}),
            "https://domain.org/test?key1=value1&submit=Search",
        )
        self.assertEqual(
            self.reporter.format_url("https://domain.org/test", {"key1": "test žščř", "submit": "Search"}),
            "https://domain.org/test?key1=test+%C5%BE%C5%A1%C4%8D%C5%99&submit=Search",
        )

    def test_08_translations(self):
        """
        Perform translations tests.
        """
        self.maxDiff = None

        self.assertEqual(self.reporter.translator.gettext("Locale:"), "Locale:")
        self.assertEqual(self.reporter.translator.gettext("Counter:"), "Counter:")
        self.assertEqual(self.reporter.translator.gettext("Time:"), "Time:")
        self.assertEqual(self.reporter.translator.gettext("Timezone:"), "Timezone:")
        self.assertEqual(self.reporter.translator.gettext("TZ time:"), "TZ time:")
        self.assertEqual(self.reporter.translator.gettext("Period:"), "Period:")
        self.reporter.set_locale("cs")
        self.assertEqual(self.reporter.translator.gettext("Locale:"), "Lokále:")
        self.assertEqual(self.reporter.translator.gettext("Counter:"), "Čítač:")
        self.assertEqual(self.reporter.translator.gettext("Time:"), "Čas:")
        self.assertEqual(self.reporter.translator.gettext("Timezone:"), "Zóna:")
        self.assertEqual(self.reporter.translator.gettext("TZ time:"), "Čas zóny:")
        self.assertEqual(self.reporter.translator.gettext("Period:"), "Perioda:")

    def test_09_rendering(self):
        """
        Perform rendering tests.
        """
        self.maxDiff = None

        template_txt = self.reporter.renderer.get_template("default.txt.j2")
        report_txt = template_txt.render(
            test_count=1265358.56,
            test_time=datetime.datetime(2018, 1, 1, 12, 0),
            test_period=datetime.timedelta(days=2, seconds=12),
        )
        self.reporter.logger.assert_has_calls([call.warning("Test log line from Jinja2 template.")])
        self.assertRegex(
            report_txt,
            "Locale: en\nCounter: 1,265,358.56\nTime: Jan 1, 2018, 12:00:00[\u0020|\u202f]PM\nTimezone: UTC\nTZ time: Jan 1, 2018, 12:00:00[\u0020|\u202f]PM\nPeriod: 2 days",
        )

        self.reporter.set_timezone("Europe/Prague")
        report_txt = template_txt.render(
            test_count=1265358.56,
            test_time=datetime.datetime(2018, 1, 1, 12, 0),
            test_period=datetime.timedelta(days=2, seconds=12),
        )
        self.assertRegex(
            report_txt,
            "Locale: en\nCounter: 1,265,358.56\nTime: Jan 1, 2018, 12:00:00[\u0020|\u202f]PM\nTimezone: Europe/Prague\nTZ time: Jan 1, 2018, 1:00:00[\u0020|\u202f]PM\nPeriod: 2 days",
        )

        self.reporter.set_timezone("America/Los_Angeles")
        report_txt = template_txt.render(
            test_count=1265358.56,
            test_time=datetime.datetime(2018, 1, 1, 12, 0),
            test_period=datetime.timedelta(days=2, seconds=12),
        )
        self.assertRegex(
            report_txt,
            "Locale: en\nCounter: 1,265,358.56\nTime: Jan 1, 2018, 12:00:00[\u0020|\u202f]PM\nTimezone: America/Los_Angeles\nTZ time: Jan 1, 2018, 4:00:00[\u0020|\u202f]AM\nPeriod: 2 days",
        )

        self.reporter.set_locale("cs")
        report_txt = template_txt.render(
            test_count=1265358.56,
            test_time=datetime.datetime(2018, 1, 1, 12, 0),
            test_period=datetime.timedelta(days=2, seconds=12),
        )
        self.assertRegex(
            report_txt,
            "Lokále: cs\nČítač: 1 265 358,56\nČas: 1. 1. 2018[\u0020|\u202f]12:00:00\nZóna: America/Los_Angeles\nČas zóny: 1. 1. 2018 4:00:00\nPerioda: 2 dny",  # noqa: RUF001
        )
        self.reporter.logger.assert_has_calls([call.warning("Test log line from Jinja2 template.")])


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
