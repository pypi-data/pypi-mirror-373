#!/usr/bin/env python3
# pylint: disable=protected-access
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.data` module.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime
import unittest

from mentat.datatype.sqldb import GroupModel
from mentat.reports.data import ReportingProperties


class TestMentatReportingProperties(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.data.ReportingProperties` data class.
    """

    DATE_LOW = datetime.datetime(2024, 1, 1, 10, 0, 0)
    DATE_HIGH = datetime.datetime(2024, 1, 1, 14, 0, 0)

    def setUp(self):
        """
        Perform test case setup.
        """
        self.reporting1 = ReportingProperties(
            GroupModel(name="DEMO_GROUP"),
            "medium",
            self.DATE_LOW,
            self.DATE_HIGH,
            has_test_data=False,
            is_shadow=False,
            is_target=False,
        )
        self.reporting_target = ReportingProperties(
            GroupModel(name="DEMO_GROUP"),
            "low",
            self.DATE_LOW,
            self.DATE_HIGH,
            has_test_data=False,
            is_shadow=False,
            is_target=True,
        )
        self.reporting_shadow = ReportingProperties(
            GroupModel(name="DEMO_GROUP"),
            "low",
            self.DATE_LOW,
            self.DATE_HIGH,
            has_test_data=False,
            is_shadow=True,
            is_target=False,
        )
        self.reporting_shadow_target = ReportingProperties(
            GroupModel(name="DEMO_GROUP"),
            "info",
            self.DATE_LOW,
            self.DATE_HIGH,
            has_test_data=False,
            is_shadow=True,
            is_target=True,
        )

    def test_01_basic_methods(self):
        """
        Test basic methods of the ReportingProperties class.
        """
        self.assertEqual(self.reporting1.get_current_section(), "Source")
        self.assertEqual(self.reporting_target.get_current_section(), "Target")
        self.assertEqual(self.reporting_shadow.get_current_section(), "ShadowSource")
        self.assertEqual(self.reporting_shadow_target.get_current_section(), "ShadowTarget")

        self.assertEqual(self.reporting1._get_reporting_window_size(), "4:00:00")

        self.assertEqual(
            self.reporting1.to_log_text(),
            "source severity 'medium' and time interval 2024-01-01T10:00:00 -> 2024-01-01T14:00:00 (4:00:00). (normal reporting)",
        )
        self.assertEqual(
            self.reporting_target.to_log_text(),
            "target severity 'low' and time interval 2024-01-01T10:00:00 -> 2024-01-01T14:00:00 (4:00:00). (normal reporting)",
        )
        self.assertEqual(
            self.reporting_shadow.to_log_text(),
            "source severity 'low' and time interval 2024-01-01T10:00:00 -> 2024-01-01T14:00:00 (4:00:00). (shadow reporting)",
        )
        self.assertEqual(
            self.reporting_shadow_target.to_log_text(),
            "target severity 'info' and time interval 2024-01-01T10:00:00 -> 2024-01-01T14:00:00 (4:00:00). (shadow reporting)",
        )

    def test_02_ReportingProperties_get_event_search_parameters(self):
        """
        Test get_event_search_parameters of the ReportingProperties class.
        """
        self.assertEqual(
            self.reporting1.get_event_search_parameters(),
            {
                "categories": ["Test"],
                "groups": ["DEMO_GROUP"],
                "not_categories": True,
                "severities": ["medium"],
                "shadow_reporting": False,
                "st_from": self.DATE_LOW,
                "st_to": self.DATE_HIGH,
            },
        )
        self.assertEqual(
            self.reporting_target.get_event_search_parameters(),
            {
                "categories": ["Test"],
                "target_groups": ["DEMO_GROUP"],
                "not_categories": True,
                "target_severities": ["low"],
                "shadow_reporting_target": False,
                "st_from": self.DATE_LOW,
                "st_to": self.DATE_HIGH,
            },
        )
        self.assertEqual(
            self.reporting_shadow.get_event_search_parameters(),
            {
                "groups": ["DEMO_GROUP"],
                "severities": ["low"],
                "shadow_reporting": True,
                "st_from": self.DATE_LOW,
                "st_to": self.DATE_HIGH,
            },
        )
        self.assertEqual(
            self.reporting_shadow_target.get_event_search_parameters(),
            {
                "target_groups": ["DEMO_GROUP"],
                "target_severities": ["info"],
                "shadow_reporting_target": True,
                "st_from": self.DATE_LOW,
                "st_to": self.DATE_HIGH,
            },
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
