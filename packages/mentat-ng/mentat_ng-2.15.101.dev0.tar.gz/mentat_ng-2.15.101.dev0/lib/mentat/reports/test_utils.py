#!/usr/bin/env python3
# pylint: disable=protected-access
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.utils` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import pprint
import unittest
from unittest.mock import Mock

from ransack import Parser, get_values

import mentat.const
import mentat.idea.internal
import mentat.reports.utils
import mentat.services.eventstorage
import mentat.services.sqlstorage
from mentat.datatype.sqldb import (
    FilterModel,
    GroupModel,
    NetworkModel,
    SettingsReportingModel,
)
from mentat.reports.data import ReportingProperties

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------

REPORTS_DIR = "/var/tmp"


class TestMentatReportsUtils(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.utils` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    ideas_raw = [
        {
            "Format": "IDEA0",
            "ID": "msg01",
            "DetectTime": "2018-01-01T12:00:00Z",
            "Category": ["Fraud.Phishing"],
            "Description": "Synthetic example 01",
            "Source": [
                {
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25", "10.0.0.1"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                }
            ],
            "Target": [{"IP4": ["10.2.2.0/24"], "IP6": ["2001:ffff::ff00:42:0/112"]}],
            "Node": [{"Name": "org.example.kippo_honey", "SW": ["Kippo"]}],
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "EventClass": "class01",
                "EventSeverity": "low",
            },
        },
        {
            "Format": "IDEA0",
            "ID": "msg02",
            "DetectTime": "2018-01-01T13:00:00Z",
            "Category": ["Recon.Scanning"],
            "Description": "Synthetic example 02",
            "Source": [
                {
                    "IP4": ["192.168.1.2-192.168.1.5", "192.169.0.0/25", "10.0.0.1"],
                    "IP6": ["2002:db8::ff00:42:0/112"],
                }
            ],
            "Target": [{"IP4": ["11.2.2.0/24"], "IP6": ["2004:ffff::ff00:42:0/112"]}],
            "Node": [{"Name": "org.example.dionaea", "SW": ["Dionaea"]}],
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "EventClass": "class02",
                "EventSeverity": "low",
            },
        },
    ]

    ideas_obj = list(map(mentat.idea.internal.Idea, ideas_raw))

    def setUp(self):
        """
        Perform test case setup.
        """
        self.sqlstorage = mentat.services.sqlstorage.StorageService(
            url="postgresql://mentat:mentat@localhost/mentat_utest", echo=False
        )
        self.sqlstorage.database_drop()
        self.sqlstorage.database_create()

        self.eventstorage = mentat.services.eventstorage.EventStorageService(
            dbname="mentat_utest",
            user="mentat",
            password="mentat",
            host="localhost",
            port=5432,
        )
        self.eventstorage.database_drop()
        self.eventstorage.database_create()
        for event in self.ideas_obj:
            event["_Mentat"]["StorageTime"] = datetime.datetime.utcnow()
            self.eventstorage.insert_event(event)

        group = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")

        FilterModel(
            group=group,
            name="FLT1",
            source_based=True,
            type="basic",
            filter='Node.Name contains "org.example.kippo_honey"',
            description="DESC1",
            enabled=True,
        )
        FilterModel(
            group=group,
            name="FLT2",
            source_based=True,
            type="basic",
            filter='"Recon.Scanning" in Category',
            description="DESC2",
            enabled=True,
        )
        global_filter = FilterModel(
            name="FLT_GLOBAL",
            source_based=True,
            type="advanced",
            filter='"Anomaly.Traffic" in Category',
            description="DESC3",
            enabled=True,
        )

        NetworkModel(group=group, netname="UNET1", source="manual", network="10.0.0.0/8")

        SettingsReportingModel(group=group)

        self.sqlstorage.session.add(group)
        self.sqlstorage.session.add(global_filter)
        self.sqlstorage.session.commit()

        self.stcache = mentat.reports.utils.StorageThresholdingCache(Mock(), self.eventstorage)
        self.ntcache = mentat.reports.utils.NoThresholdingCache()

    def tearDown(self):
        self.sqlstorage.session.close()
        self.sqlstorage.database_drop()
        self.eventstorage.database_drop()

    def test_01_generate_cache_keys(self):
        """
        Test :py:func:`mentat.reports.utils.ThresholdingCache._generate_cache_keys` function.
        """
        self.maxDiff = None

        for ip in get_values(self.ideas_raw[0], "Source.IP4") + get_values(self.ideas_raw[0], "Source.IP6"):
            key = self.stcache._generate_cache_key(self.ideas_raw[0], ip, False)  # pylint: disable=locally-disabled,protected-access
            self.assertEqual(self.stcache.get_source_from_cache_key(key), ip)
        self.assertEqual(
            self.stcache._generate_cache_key(
                {  # pylint: disable=locally-disabled,protected-access
                    "Category": ["Test", "Value"],
                    "Source": [{"IP4": ["195.113.144.194"]}],
                },
                "195.113.144.194",
                False,
            ),
            "Test/Value+++195.113.144.194",
        )
        self.assertEqual(
            self.stcache._generate_cache_key(
                {
                    "Source": [{"IP4": ["191.113.144.194"]}],
                    "_Mentat": {"EventClass": "anomaly-traffic"},
                },
                "191.113.144.194",
                False,
            ),
            "anomaly-traffic+++191.113.144.194",
        )
        self.assertEqual(
            self.stcache._generate_cache_key(
                {  # pylint: disable=locally-disabled,protected-access
                    "Source": [{"IP4": ["195.113.144.104"]}],
                    "_Mentat": {
                        "EventClass": "vulnerable-implementation",
                        "EventSubclass": ["cvr:73"],
                    },
                },
                "195.113.144.104",
                False,
            ),
            "vulnerable-implementation/cvr:73+++195.113.144.104",
        )
        self.assertEqual(
            self.stcache._generate_cache_key(
                {  # pylint: disable=locally-disabled,protected-access
                    "Source": [{"IP4": ["195.13.144.104"]}],
                    "_Mentat": {
                        "EventClass": "vulnerable-implementation",
                        "EventSubclass": ["cvr:73"],
                        "TargetClass": "anomaly-traffic-target",
                    },
                },
                "195.13.144.104",
                True,
            ),
            "anomaly-traffic-target+++195.13.144.104",
        )
        self.assertEqual(
            self.stcache._generate_cache_key(
                {  # pylint: disable=locally-disabled,protected-access
                    "Source": [{"IP4": ["195.119.144.104"]}],
                    "_Mentat": {
                        "TargetClass": "anomaly-traffic-target",
                        "TargetSubclass": ["123"],
                    },
                },
                "195.119.144.104",
                True,
            ),
            "anomaly-traffic-target/123+++195.119.144.104",
        )

    def test_02_no_thr_cache(self):
        """
        Test :py:func:`mentat.reports.utils.NoThresholdingCache` class.
        """
        self.maxDiff = None

        ttltime = datetime.datetime.utcnow()
        relapsetime = ttltime - datetime.timedelta(seconds=600)
        thresholdtime = relapsetime - datetime.timedelta(seconds=600)

        self.assertFalse(self.ntcache.event_is_thresholded(self.ideas_obj[0], "192.168.1.1", ttltime, False))
        self.ntcache.set_threshold(self.ideas_obj[0], "192.168.1.1", thresholdtime, relapsetime, ttltime, False)
        self.assertFalse(self.ntcache.event_is_thresholded(self.ideas_obj[0], "192.168.1.1", ttltime, False))
        self.ntcache.threshold_event(
            ReportingProperties(
                GroupModel(name="TEST"),
                "low",
                datetime.datetime.utcnow(),
                datetime.datetime.utcnow(),
                is_target=False,
            ),
            self.ideas_obj[0],
            "192.168.1.1",
        )
        self.assertFalse(self.ntcache.event_is_thresholded(self.ideas_obj[0], "192.168.1.1", ttltime, False))

    def test_03_storage_thr_cache(self):
        """
        Test :py:func:`mentat.reports.utils.StorageThresholdingCache` class.
        """
        self.maxDiff = None

        ttltime = datetime.datetime.utcnow()
        reltime = ttltime - datetime.timedelta(seconds=300)
        thrtime = reltime - datetime.timedelta(seconds=300)

        self.assertFalse(
            self.stcache.event_is_thresholded(self.ideas_obj[0], "192.168.0.2-192.168.0.5", ttltime, False)
        )
        self.stcache.set_threshold(
            self.ideas_obj[0],
            "192.168.0.2-192.168.0.5",
            thrtime,
            reltime,
            ttltime,
            False,
        )
        self.assertTrue(
            self.stcache.event_is_thresholded(
                self.ideas_obj[0],
                "192.168.0.2-192.168.0.5",
                ttltime - datetime.timedelta(seconds=50),
                False,
            )
        )
        self.assertFalse(
            self.stcache.event_is_thresholded(
                self.ideas_obj[0],
                "192.168.0.0/25",
                ttltime - datetime.timedelta(seconds=50),
                False,
            )
        )
        self.stcache.set_threshold(self.ideas_obj[0], "192.168.0.0/25", thrtime, reltime, ttltime, False)
        self.assertTrue(
            self.stcache.event_is_thresholded(
                self.ideas_obj[0],
                "192.168.0.0/25",
                ttltime - datetime.timedelta(seconds=50),
                False,
            )
        )

        self.stcache.threshold_event(
            ReportingProperties(
                GroupModel(name="test@domain.org"),
                "low",
                ttltime - datetime.timedelta(seconds=100),
                ttltime - datetime.timedelta(seconds=50),
                is_target=False,
            ),
            self.ideas_obj[0],
            "192.168.0.2-192.168.0.5",
        )
        self.stcache.threshold_event(
            ReportingProperties(
                GroupModel(name="test@domain.org"),
                "low",
                ttltime - datetime.timedelta(seconds=100),
                ttltime - datetime.timedelta(seconds=50),
                is_target=False,
            ),
            self.ideas_obj[0],
            "192.168.0.0/25",
        )

        self.assertEqual(self.stcache.eventservice.thresholds_count(), 2)
        self.assertEqual(self.stcache.eventservice.thresholded_events_count(), 2)

        self.assertEqual(
            self.stcache.cleanup(ttltime + datetime.timedelta(seconds=50)),
            {"thresholds": 2, "events": 2},
        )

    def test_04_reporting_settings(self):
        """
        Test :py:class:`mentat.reports.utils.ReportingSettings` class.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.sqlstorage.session.commit()

        reporting_settings = mentat.reports.utils.ReportingSettings(abuse_group, self.sqlstorage)
        self.assertEqual(reporting_settings.group_name, "abuse@cesnet.cz")
        self.assertEqual(len(reporting_settings.filters), 3)
        self.assertEqual(
            str(reporting_settings.filters),
            "[<Filter(name='FLT_GLOBAL')>, <Filter(name='FLT1')>, <Filter(name='FLT2')>]",
        )
        self.assertEqual(
            str(reporting_settings.networks),
            "[<Network(netname='UNET1',network='10.0.0.0/8')>]",
        )
        self.assertEqual(reporting_settings.mode, "extra")
        self.assertEqual(reporting_settings.redirect, False)
        self.assertEqual(reporting_settings.template, "default")
        self.assertEqual(reporting_settings.locale, "en")
        self.assertEqual(reporting_settings.timezone, "UTC")
        self.assertEqual(reporting_settings.timing, "default")
        self.assertEqual(
            reporting_settings.timing_cfg,
            {
                "critical": {
                    "per": datetime.timedelta(0, 600),
                    "rel": datetime.timedelta(0),
                    "rel_target": datetime.timedelta(0),
                    "thr": datetime.timedelta(0, 7200),
                    "thr_target": datetime.timedelta(0),
                },
                "high": {
                    "per": datetime.timedelta(0, 600),
                    "rel": datetime.timedelta(0, 43200),
                    "rel_target": datetime.timedelta(0),
                    "thr": datetime.timedelta(1),
                    "thr_target": datetime.timedelta(0),
                },
                "info": {
                    "per": datetime.timedelta(1),
                    "rel": datetime.timedelta(7),
                    "rel_target": datetime.timedelta(0),
                    "thr": datetime.timedelta(28),
                    "thr_target": datetime.timedelta(0),
                },
                "low": {
                    "per": datetime.timedelta(1),
                    "rel": datetime.timedelta(2),
                    "rel_target": datetime.timedelta(0),
                    "thr": datetime.timedelta(6),
                    "thr_target": datetime.timedelta(0),
                },
                "medium": {
                    "per": datetime.timedelta(0, 7200),
                    "rel": datetime.timedelta(2),
                    "rel_target": datetime.timedelta(0),
                    "thr": datetime.timedelta(6),
                    "thr_target": datetime.timedelta(0),
                },
            },
        )
        if self.verbose:
            pprint.pprint(reporting_settings)

        reporting_settings = mentat.reports.utils.ReportingSettings(
            abuse_group,
            self.sqlstorage,
            force_mode="both",
            force_template="another",
            force_locale="cs",
            force_timezone="America/Los_Angeles",
        )
        self.assertEqual(reporting_settings.mode, "both")
        self.assertEqual(reporting_settings.template, "another")
        self.assertEqual(reporting_settings.locale, "cs")
        self.assertEqual(reporting_settings.timezone, "America/Los_Angeles")
        if self.verbose:
            pprint.pprint(reporting_settings)

        filter_parser = Parser()

        reporting_settings.setup_filters(filter_parser, False)

        network_list = reporting_settings.setup_networks()
        self.assertEqual([str(x["nrobj"]) for x in network_list], ["10.0.0.0/8"])

    def test_get_recipients(self):
        """
        Test :py:func:`mentat.reports.utils.get_recipients` function.
        """
        self.maxDiff = None

        # Settings for first group
        settings1 = SettingsReportingModel(
            emails_info=["info1@example.com"],
            emails_low=["low1@example.com"],
            emails_medium=["medium1@example.com"],
            emails_high=["high1@example.com"],
            emails_critical=["critical1@example.com"],
        )

        # Settings for second group (different emails)
        settings2 = SettingsReportingModel(
            emails_info=["info2@example.com"],
            emails_low=["low2@example.com"],
            emails_medium=["medium2@example.com"],
            emails_high=["high2@example.com"],
            emails_critical=["critical2@example.com"],
        )

        group1 = GroupModel(name="Group1", settings_rep=settings1)
        group2 = GroupModel(name="Group2", settings_rep=settings2)

        # Test severity 'medium'
        to, cc = mentat.reports.utils.get_recipients([group1, group2], "medium")
        self.assertEqual(to, ["medium1@example.com"])
        self.assertEqual(
            cc,
            ["low1@example.com", "info1@example.com", "medium2@example.com", "low2@example.com", "info2@example.com"],
        )

        # Test severity 'critical'
        to, cc = mentat.reports.utils.get_recipients([group1, group2], "critical")
        self.assertEqual(to, ["critical1@example.com"])
        self.assertEqual(
            cc,
            [
                "high1@example.com",
                "medium1@example.com",
                "low1@example.com",
                "info1@example.com",
                "critical2@example.com",
                "high2@example.com",
                "medium2@example.com",
                "low2@example.com",
                "info2@example.com",
            ],
        )

        # Test severity 'high' with missing high emails (fallback to lower)
        settings1.emails_high = []
        settings2.emails_high = []
        to, cc = mentat.reports.utils.get_recipients([group1, group2], "high")
        self.assertEqual(to, ["medium1@example.com"])
        self.assertEqual(
            cc,
            ["low1@example.com", "info1@example.com", "medium2@example.com", "low2@example.com", "info2@example.com"],
        )

        # Test severity 'low' with no low or lower emails
        settings1.emails_low = []
        settings2.emails_low = []
        settings1.emails_info = []
        settings2.emails_info = []
        to, cc = mentat.reports.utils.get_recipients([group1, group2], "low")
        self.assertEqual(to, [])
        self.assertEqual(cc, [])

        # Test severity 'info' with emails only in group1
        settings1.emails_info = ["info1_1@example.com", "info1_2@example.com"]
        to, cc = mentat.reports.utils.get_recipients([group1, group2], "info")
        self.assertEqual(to, ["info1_1@example.com", "info1_2@example.com"])
        self.assertEqual(cc, [])


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
