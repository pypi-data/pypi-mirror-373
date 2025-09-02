#!/usr/bin/env python3
# pylint: disable=protected-access
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.aggregations` module.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import unittest
from datetime import datetime

from mentat.reports.aggregations import EventAggregator
from mentat.reports.data import AggregatedData
from mentat.reports.tests.fixtures import EVENTS_OBJ


class TestMentatReportingProperties(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.aggregations.EventAggregator` class.
    """

    def test_01_get_relevant_source_section(self):
        """
        Test :py:func:`mentat.reports.aggregations.EventAggregator._get_relevant_source_section` function.
        """
        result = EventAggregator._get_relevant_source_sections(EVENTS_OBJ[0], "10.0.2.1")
        self.assertEqual(len(result), 1)

        result = EventAggregator._get_relevant_source_sections(EVENTS_OBJ[1], "10.0.2.1")
        self.assertEqual(len(result), 2)

    def test_02_aggregate_data(self):
        """
        Test :py:func:`mentat.reports.aggregations.EventAggregator._aggregate_data` function.
        """
        result = AggregatedData()
        event = EVENTS_OBJ[0]
        EventAggregator._aggregate_data(result, event, event.get("Source"))
        EventAggregator._aggregate_data(result, event, event.get("Source"))
        result.finalize()

        self.assertEqual(result.first_time, datetime(2018, 1, 1, 12, 0))
        self.assertEqual(result.last_time, datetime(2018, 1, 1, 12, 0))
        self.assertEqual(result.event_count, 2)
        self.assertEqual(result.detector_data.keys(), {"org.example.kippo_honey"})

        detector_data = result.detector_data["org.example.kippo_honey"]
        self.assertEqual(detector_data.main_numeric_data.ConnCount, 2)
        self.assertEqual(detector_data.main_numeric_data.FlowCount, 30 * 2)
        self.assertEqual(detector_data.main_numeric_data.ByteCount, 4560 * 2)
        self.assertEqual(detector_data.main_numeric_data.ByteCountDropped, 100 * 2)
        self.assertEqual(detector_data.main_numeric_data.AvgPacketSize, 93)
        self.assertEqual(detector_data.main_list_data.Ref, {"https://cesnet.cz"})
        self.assertEqual(detector_data.main_list_data.UsernameAndPassword, {("sa", "")})

        self.assertEqual(detector_data.source_numeric_data.ClockSkew, -123)
        self.assertEqual(detector_data.source_numeric_data.InFlowCount, 30 * 2)
        self.assertEqual(detector_data.source_numeric_data.OutFlowCount, 30 * 2)
        self.assertEqual(detector_data.source_numeric_data.InByteCount, 4560 * 2)
        self.assertEqual(detector_data.source_numeric_data.InByteCount, 4560 * 2)
        self.assertEqual(detector_data.source_list_data.Proto, {"ssh", "telnet"})
        self.assertEqual(
            detector_data.source_list_data.ips,
            {"10.0.2.1", "2001:db8::ff00:42:0/112"},
        )

        self.assertEqual(detector_data.target_list_data.Proto, {"https", "http"})
        self.assertEqual(detector_data.target_list_data.Port, {"80", "443"})
        self.assertEqual(detector_data.target_list_data.Interface, {"45"})
        self.assertEqual(detector_data.target_list_data.Hostname, {"aaa.cesnet.cz", "bbb.cesnet.cz"})
        self.assertEqual(detector_data.target_list_data.Ref, {"https://ces.net"})
        self.assertEqual(detector_data.target_list_data.services, {("Apache", "2.4.53")})
        self.assertEqual(detector_data.target_list_data.X509ExpiredTime, {"2020-11-06T23:59:00Z"})

    def test_03_aggregate_source(self):
        """
        Test :py:func:`mentat.reports.aggregations.EventAggregator.aggregate_source` function.
        """
        events = {
            "10.0.0.1": EVENTS_OBJ[0:1],
            "10.0.2.1": EVENTS_OBJ[0:2],
        }
        result = EventAggregator.aggregate_source(events)

        self.assertEqual(len(result.keys()), 2)
        self.assertEqual(list(result["test-event-class"].keys()), ["10.0.0.1", "10.0.2.1"])
        self.assertEqual(list(result["recon-scanning"].keys()), ["10.0.2.1"])

        test_eventclass_ip1 = result["test-event-class"]["10.0.0.1"]
        self.assertEqual(test_eventclass_ip1.event_count, 1)
        self.assertEqual(test_eventclass_ip1.get_detector_count(), 1)
        # Check if finalize has been called by checking AvgPacketSize that is calculated at finalize().
        self.assertGreater(
            test_eventclass_ip1.detector_data["org.example.kippo_honey"].main_numeric_data.AvgPacketSize, 0
        )

    def test_04_aggregate_target(self):
        """
        Test :py:func:`mentat.reports.aggregations.EventAggregator.aggregate_target` function.
        """
        events = {
            "10.2.2.0/24": EVENTS_OBJ[0:1],
            "2001:ffff::ff00:42:0/112": EVENTS_OBJ[0:1],
        }
        result = EventAggregator.aggregate_target(events)

        self.assertEqual(len(result.keys()), 1)

        phishing = result["fraud-phishing-target"]
        self.assertEqual(phishing.event_count, 1)
        self.assertEqual(phishing.get_detector_count(), 1)
        self.assertEqual(
            phishing.detector_data["org.example.kippo_honey"].target_list_data.relevant_ips,
            {"10.2.2.0/24", "2001:ffff::ff00:42:0/112"},
        )
        # Check if finalize has been called by checking AvgPacketSize that is calculated at finalize().
        self.assertGreater(phishing.detector_data["org.example.kippo_honey"].main_numeric_data.AvgPacketSize, 0)
