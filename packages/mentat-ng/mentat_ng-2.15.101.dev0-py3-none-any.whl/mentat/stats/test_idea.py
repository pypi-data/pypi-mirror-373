#!/usr/bin/env python3
# pylint: disable=protected-access
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


import datetime
import unittest
from pprint import pprint

import pytz

import mentat.datatype.sqldb
import mentat.stats.idea


class TestMentatStatsIdea(unittest.TestCase):
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
            "TLP": "GREEN",
            "CreateTime": "2012-11-03T10:00:02Z",
            "DetectTime": "2012-11-03T10:00:07Z",
            "Category": ["Fraud.Phishing"],
            "Source": [
                {
                    "Type": ["Phishing"],
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                }
            ],
            "Target": [
                {
                    "IP4": ["192.168.1.2-192.168.1.5", "192.168.1.0/25"],
                    "IP6": ["2001:db8::ff01:42:0/112"],
                }
            ],
            "Node": [
                {
                    "Name": "org.example.kippo",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["Kippo"],
                }
            ],
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "TargetAbuses": ["abuse@cesnet.cz"],
                "EventSeverity": "low",
                "TargetSeverity": "low",
                "EventClass": "fraud-phishing",
                "TargetClass": "fraud-phishing-target",
            },
        },
        {
            "Format": "IDEA0",
            "ID": "msg02",
            "TLP": "CLEAR",
            "CreateTime": "2012-11-03T11:00:02Z",
            "DetectTime": "2012-11-03T11:00:07Z",
            "Category": ["Fraud.Phishing"],
            "Source": [
                {
                    "Type": ["Phishing"],
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                }
            ],
            "Node": [
                {
                    "Name": "org.example.kippo",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["Kippo"],
                }
            ],
            "_Mentat": {
                "ResolvedAbuses": ["abuse@cesnet.cz"],
                "EventSeverity": "medium",
                "TargetSeverity": "high",
            },
        },
        {
            "Format": "IDEA0",
            "ID": "msg03",
            "TLP": "AMBER",
            "CreateTime": "2012-11-03T12:00:02Z",
            "DetectTime": "2012-11-03T12:00:07Z",
            "Category": ["Fraud.Phishing"],
            "Source": [
                {
                    "Type": ["Phishing"],
                    "IP4": ["192.168.0.2-192.168.0.5", "192.168.0.0/25"],
                    "IP6": ["2001:db8::ff00:42:0/112"],
                }
            ],
            "Target": [
                {
                    "IP4": ["192.168.1.2-192.168.1.5", "192.168.1.0/25"],
                    "IP6": ["2001:db8::ff01:42:0/112"],
                }
            ],
            "Node": [
                {
                    "Name": "org.example.dionaea",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["Kippo"],
                }
            ],
            "_Mentat": {"ResolvedAbuses": ["abuse@cesnet.cz"], "TargetSeverity": "low"},
        },
        {
            "Format": "IDEA0",
            "ID": "msg04",
            "TLP": "AMBER",
            "CreateTime": "2012-11-03T15:00:02Z",
            "DetectTime": "2012-11-03T15:00:07Z",
            "Category": ["Spam"],
            "Source": [{"Type": ["Spam"], "IP4": ["192.168.0.100", "192.168.0.105"]}],
            "Node": [
                {
                    "Name": "org.example.dionaea",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["Dionaea"],
                }
            ],
        },
        {
            "Format": "IDEA0",
            "ID": "msg05",
            "CreateTime": "2012-11-03T18:00:02Z",
            "DetectTime": "2012-11-03T18:00:07Z",
            "Category": ["Exploit"],
            "Source": [{"Type": ["Exploit"], "IP4": ["192.168.0.109", "192.168.0.200"]}],
            "Target": [{"IP4": ["192.168.1.109", "192.168.1.200"]}],
            "Node": [
                {
                    "Name": "org.example.labrea",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["LaBrea"],
                }
            ],
            "_Mentat": {"TargetAbuses": ["abuse@cesnet.cz"], "EventSeverity": "medium"},
        },
        {
            "Format": "IDEA0",
            "ID": "msg06",
            "TLP": "GREEN",
            "CreateTime": "2012-11-03T18:00:02Z",
            "DetectTime": "2012-11-03T18:00:07Z",
            "Category": ["Exploit"],
            "Source": [{"Type": ["Exploit"], "IP4": ["192.172.0.109", "192.172.0.200"]}],
            "Node": [
                {
                    "Name": "org.example.labrea",
                    "Tags": ["Protocol", "Honeypot"],
                    "SW": ["LaBrea"],
                },
                {"SW": ["Beekeeper"], "Name": "cz.cesnet.holly"},
            ],
        },
    ]

    def test_01_counter_inc(self):
        """
        Test counter incrementation utility.
        """
        self.maxDiff = None

        test = {}

        self.assertEqual(mentat.stats.idea._counter_inc(test, "x", "a"), {"x": {"a": 1}})
        self.assertEqual(mentat.stats.idea._counter_inc(test, "x", "a"), {"x": {"a": 2}})
        self.assertEqual(mentat.stats.idea._counter_inc(test, "x", "a"), {"x": {"a": 3}})
        self.assertEqual(mentat.stats.idea._counter_inc(test, "x", "a", 5), {"x": {"a": 8}})

    def test_02_make_toplist(self):
        """
        Test toplist creation utility.
        """
        self.maxDiff = None

        test1 = {
            "detectors": {
                "org.example.holly": 1,
                "org.example.rimmer": 5,
                "org.example.kryten": 10,
                "org.example.queeg": 20,
                "org.example.dionaea": 5,
                "org.example.kippo": 3,
                "org.example.labrea": 2,
            }
        }

        self.assertEqual(
            mentat.stats.idea._make_toplist(test1, "detectors", 5),
            {
                "detectors": {
                    "org.example.holly": 1,
                    "org.example.rimmer": 5,
                    "org.example.kryten": 10,
                    "org.example.queeg": 20,
                    "org.example.dionaea": 5,
                    "org.example.kippo": 3,
                    "org.example.labrea": 2,
                }
            },
        )

        test2 = {
            "detectors": {
                "__REST__": 50,
                "org.example.rimmer": 5,
                "org.example.kryten": 10,
                "org.example.queeg": 20,
                "org.example.dionaea": 5,
                "org.example.kippo": 3,
                "org.example.labrea": 2,
            }
        }

        self.assertEqual(
            mentat.stats.idea._make_toplist(test2, "detectors", 5, True),
            {
                "detectors": {
                    "__REST__": 55,
                    "org.example.dionaea": 5,
                    "org.example.kryten": 10,
                    "org.example.queeg": 20,
                    "org.example.rimmer": 5,
                }
            },
        )

        test3 = {
            "detectors": {
                "__REST__": 50,
                "org.example.rimmer": 5,
                "org.example.kryten": 10,
                "org.example.queeg": 20,
            }
        }

        self.assertEqual(
            mentat.stats.idea._make_toplist(test3, "detectors", 5),
            {
                "detectors": {
                    "__REST__": 50,
                    "org.example.kryten": 10,
                    "org.example.queeg": 20,
                    "org.example.rimmer": 5,
                }
            },
        )

        test4 = {
            "ip4s": {
                "org.example.holly": 1,
                "org.example.rimmer": 5,
                "org.example.kryten": 10,
                "org.example.queeg": 20,
                "org.example.dionaea": 5,
                "org.example.kippo": 3,
                "org.example.labrea": 2,
            }
        }

        self.assertEqual(
            mentat.stats.idea._make_toplist(test4, "ip4s", 5),
            {
                "ip4s": {
                    "__REST__": 6,
                    "org.example.dionaea": 5,
                    "org.example.kryten": 10,
                    "org.example.queeg": 20,
                    "org.example.rimmer": 5,
                }
            },
        )

    def test_03_datetime_rounding(self):
        """Test datetime rounding"""
        self.maxDiff = None

        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_datetime_up(
                datetime.datetime(2022, 10, 11, 11, 32, 12), datetime.timedelta(hours=1)
            ),
            datetime.datetime(2022, 10, 11, 12, 0, 0),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_datetime_up(
                datetime.datetime(2022, 10, 11, 11, 32, 12),
                datetime.timedelta(minutes=5),
            ),
            datetime.datetime(2022, 10, 11, 11, 35, 0),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_datetime_up(
                datetime.datetime(2022, 10, 11, 11, 32, 12),
                datetime.timedelta(hours=1),
                timezone=pytz.timezone("Europe/Prague"),
            ),
            datetime.datetime(2022, 10, 11, 12, 0, 0),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_datetime_up(
                datetime.datetime(2022, 10, 11, 11, 32, 12),
                datetime.timedelta(days=1),
                timezone=pytz.timezone("Europe/Prague"),
            ),
            datetime.datetime(2022, 10, 11, 23, 0, 0),
        )

    def test_04_timedelta_rounding(self):
        """
        Test rounding of timedelta
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_timedelta_up(
                datetime.timedelta(seconds=42), datetime.timedelta(seconds=10)
            ),
            datetime.timedelta(seconds=50),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_timedelta_up(
                datetime.timedelta(microseconds=687231),
                datetime.timedelta(microseconds=500),
            ),
            datetime.timedelta(microseconds=687500),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._round_timedelta_up(
                datetime.timedelta(microseconds=687231), datetime.timedelta(seconds=2)
            ),
            datetime.timedelta(seconds=2),
        )

    def test_05_timeline_steps(self):
        """
        Test timeline step calculations.
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2018, 1, 1, 1, 11, 1),
                datetime.datetime(2018, 1, 11, 23, 59, 31),
                100,
            ),
            (
                datetime.datetime(2018, 1, 1, 3, 0, 0),
                datetime.timedelta(seconds=10800),
                88,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 22, 32),
                42,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 10),
                datetime.timedelta(seconds=10),
                34,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 18, 23),
                400,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.timedelta(microseconds=200000),
                390,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 18, 23),
                400,
                1,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.timedelta(seconds=1),
                78,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 18, 23),
                400,
                0.314159,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.timedelta(microseconds=500000),
                156,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                200,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.timedelta(microseconds=1),
                0,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                42,
                1,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.timedelta(seconds=1),
                0,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 0),
                datetime.datetime(2022, 10, 24, 15, 23, 40),
                200,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 0),
                datetime.timedelta(seconds=2),
                200,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 10, 24, 15, 17, 1),
                datetime.datetime(2022, 10, 24, 15, 23, 41),
                200,
            ),
            (
                datetime.datetime(2022, 10, 24, 15, 17, 3),
                datetime.timedelta(seconds=3),
                134,
            ),
        )
        self.assertEqual(
            mentat.stats.idea.TimelineCFG._calculate_timeline_steps(
                datetime.datetime(2022, 6, 2, 2, 17, 1),
                datetime.datetime(2022, 12, 9, 12, 28, 34),
                200,
                timezone=pytz.timezone("Canada/Newfoundland"),
            ),
            (datetime.datetime(2022, 6, 2, 3, 30, 0), datetime.timedelta(days=1), 192),
        )

    def test_06_test_timeline_cfg_to_dict(self):
        """
        Test timeline config calculations.
        """
        self.assertEqual(
            mentat.stats.idea.TimelineCFG(
                datetime.datetime(2018, 1, 1, 1, 11, 1),
                datetime.datetime(2018, 1, 11, 23, 59, 31),
                datetime.timedelta(hours=1),
            ).to_dict(),
            {
                "dt_from": datetime.datetime(2018, 1, 1, 1, 11, 1),
                "dt_to": datetime.datetime(2018, 1, 11, 23, 59, 31),
                "step": datetime.timedelta(hours=1),
                "count": 263,
                "first_step": datetime.datetime(2018, 1, 1, 1, 11, 1),
            },
        )

        self.assertEqual(
            mentat.stats.idea.TimelineCFG(
                datetime.datetime(2022, 10, 24, 15, 17, 5),
                datetime.datetime(2022, 10, 24, 15, 22, 32),
                datetime.timedelta(seconds=10),
                count=123,
                time_type=mentat.stats.idea.TimeBoundType.STORAGE_TIME,
            ).to_dict(),
            {
                "st_from": datetime.datetime(2022, 10, 24, 15, 17, 5),
                "st_to": datetime.datetime(2022, 10, 24, 15, 22, 32),
                "step": datetime.timedelta(seconds=10),
                "count": 123,
                "first_step": datetime.datetime(2022, 10, 24, 15, 17, 5),
            },
        )

        self.assertEqual(
            mentat.stats.idea.TimelineCFG(
                datetime.datetime(2018, 1, 1, 1, 11, 1),
                datetime.datetime(2018, 1, 11, 23, 59, 31),
                datetime.timedelta(hours=1),
                time_type=mentat.stats.idea.TimeBoundType.NONE,
            ).to_dict(),
            {
                "t_from": datetime.datetime(2018, 1, 1, 1, 11, 1),
                "t_to": datetime.datetime(2018, 1, 11, 23, 59, 31),
                "step": datetime.timedelta(hours=1),
                "count": 263,
                "first_step": datetime.datetime(2018, 1, 1, 1, 11, 1),
            },
        )

    def test_07_evaluate_events(self):
        """
        Perform the message evaluation tests.
        """
        self.maxDiff = None

        expected_results = {
            "abuses": {"__unknown__": 3, "abuse@cesnet.cz": 3},
            "analyzers": {"Beekeeper": 1, "Dionaea": 1, "Kippo": 3, "LaBrea": 1},
            "asns": {"__unknown__": 6},
            "categories": {"Exploit": 2, "Fraud.Phishing": 3, "Spam": 1},
            "category_sets": {"Exploit": 2, "Fraud.Phishing": 3, "Spam": 1},
            "classes": {"__unknown__": 5, "fraud-phishing": 1},
            "cnt_alerts": 6,
            "cnt_events": 6,
            "cnt_recurring": 0,
            "cnt_unique": 6,
            "countries": {"__unknown__": 6},
            "detectors": {
                "cz.cesnet.holly": 1,
                "org.example.dionaea": 2,
                "org.example.kippo": 2,
                "org.example.labrea": 1,
            },
            "detectorsws": {
                "cz.cesnet.holly/Beekeeper": 1,
                "org.example.dionaea/Dionaea": 1,
                "org.example.dionaea/Kippo": 1,
                "org.example.kippo/Kippo": 2,
                "org.example.labrea/LaBrea": 1,
            },
            "sources": {
                "192.168.0.0/25": 3,
                "192.168.0.100": 1,
                "192.168.0.105": 1,
                "192.168.0.109": 1,
                "192.168.0.2-192.168.0.5": 3,
                "192.168.0.200": 1,
                "192.172.0.109": 1,
                "192.172.0.200": 1,
                "2001:db8::ff00:42:0/112": 3,
            },
            "targets": {
                "192.168.1.2-192.168.1.5": 2,
                "192.168.1.0/25": 2,
                "2001:db8::ff01:42:0/112": 2,
                "192.168.1.109": 1,
                "192.168.1.200": 1,
                "__unknown__": 3,
            },
            "tlps": {"AMBER": 2, "CLEAR": 1, "GREEN": 2, "__unknown__": 1},
            "list_ids": ["msg01", "msg02", "msg03", "msg04", "msg05", "msg06"],
            "severities": {"__unknown__": 3, "medium": 2, "low": 1},
        }
        self.assertEqual(mentat.stats.idea.evaluate_events(self.ideas_raw), expected_results)

        # If is_target = True
        expected_results["abuses"] = {"__unknown__": 4, "abuse@cesnet.cz": 2}
        expected_results["classes"] = {"__unknown__": 5, "fraud-phishing-target": 1}
        expected_results["severities"] = {"__unknown__": 3, "low": 2, "high": 1}
        self.assertEqual(mentat.stats.idea.evaluate_events(self.ideas_raw, True), expected_results)

    def test_08_truncate_stats(self):
        """
        Perform the basic operativity tests.
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.stats.idea.truncate_stats(mentat.stats.idea.evaluate_events(self.ideas_raw), 3, True),
            {
                "abuses": {"__unknown__": 3, "abuse@cesnet.cz": 3},
                "analyzers": {"Beekeeper": 1, "Kippo": 3, "__REST__": 2},
                "asns": {"__unknown__": 6},
                "categories": {"Exploit": 2, "Fraud.Phishing": 3, "__REST__": 1},
                "category_sets": {"Exploit": 2, "Fraud.Phishing": 3, "__REST__": 1},
                "classes": {"__unknown__": 5, "fraud-phishing": 1},
                "cnt_alerts": 6,
                "cnt_events": 6,
                "cnt_recurring": 0,
                "cnt_unique": 6,
                "countries": {"__unknown__": 6},
                "detectors": {
                    "__REST__": 2,
                    "org.example.dionaea": 2,
                    "org.example.kippo": 2,
                },
                "detectorsws": {
                    "__REST__": 3,
                    "cz.cesnet.holly/Beekeeper": 1,
                    "org.example.kippo/Kippo": 2,
                },
                "sources": {
                    "192.168.0.0/25": 3,
                    "192.168.0.2-192.168.0.5": 3,
                    "__REST__": 9,
                },
                "targets": {"__unknown__": 3, "192.168.1.0/25": 2, "__REST__": 6},
                "tlps": {"AMBER": 2, "GREEN": 2, "__REST__": 2},
                "severities": {"__unknown__": 3, "medium": 2, "__REST__": 1},
            },
        )

        self.assertEqual(
            mentat.stats.idea.truncate_stats(mentat.stats.idea.evaluate_events(self.ideas_raw), 2),
            {
                "abuses": {"__unknown__": 3, "abuse@cesnet.cz": 3},
                "analyzers": {"Beekeeper": 1, "Dionaea": 1, "Kippo": 3, "LaBrea": 1},
                "asns": {"__unknown__": 6},
                "categories": {"Exploit": 2, "Fraud.Phishing": 3, "Spam": 1},
                "category_sets": {"Exploit": 2, "Fraud.Phishing": 3, "Spam": 1},
                "classes": {"__unknown__": 5, "fraud-phishing": 1},
                "cnt_alerts": 6,
                "cnt_events": 6,
                "cnt_recurring": 0,
                "cnt_unique": 6,
                "countries": {"__unknown__": 6},
                "detectors": {
                    "cz.cesnet.holly": 1,
                    "org.example.dionaea": 2,
                    "org.example.kippo": 2,
                    "org.example.labrea": 1,
                },
                "detectorsws": {
                    "cz.cesnet.holly/Beekeeper": 1,
                    "org.example.dionaea/Dionaea": 1,
                    "org.example.dionaea/Kippo": 1,
                    "org.example.kippo/Kippo": 2,
                    "org.example.labrea/LaBrea": 1,
                },
                "sources": {"192.168.0.0/25": 3, "__REST__": 12},
                "targets": {"__unknown__": 3, "__REST__": 8},
                "tlps": {"AMBER": 2, "CLEAR": 1, "GREEN": 2, "__unknown__": 1},
                "severities": {"__unknown__": 3, "low": 1, "medium": 2},
            },
        )

    def test_09_group_events(self):
        """
        Perform the basic operativity tests.
        """
        self.maxDiff = None

        self.assertEqual(
            mentat.stats.idea.group_events(self.ideas_raw),
            {
                "stats_external": [
                    self.ideas_raw[3],  # msg04
                    self.ideas_raw[4],  # msg05
                    self.ideas_raw[5],  # msg06
                ],
                "stats_internal": [
                    self.ideas_raw[0],  # msg01
                    self.ideas_raw[1],  # msg02
                    self.ideas_raw[2],  # msg03
                ],
                "stats_overall": [
                    self.ideas_raw[0],  # msg01
                    self.ideas_raw[1],  # msg02
                    self.ideas_raw[2],  # msg03
                    self.ideas_raw[3],  # msg04
                    self.ideas_raw[4],  # msg05
                    self.ideas_raw[5],  # msg06
                ],
            },
        )

    def test_10_evaluate_event_groups(self):
        """
        Perform the basic operativity tests.
        """
        result = mentat.stats.idea.evaluate_event_groups(self.ideas_raw)
        if self.verbose:
            print("*** result = mentat.stats.idea.evaluate_event_groups(self.ideas_raw) ***")
            pprint(result)
        self.assertTrue(result)

        result = mentat.stats.idea.truncate_evaluations(result, 3)
        if self.verbose:
            print("*** result = mentat.stats.idea.truncate_evaluations(result, 3) ***")
            pprint(result)
        self.assertTrue(result)

    def test_11_merge_stats(self):
        """
        Perform the statistics aggregation tests.
        """
        self.maxDiff = None

        sts1 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        sts2 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        sts3 = mentat.stats.idea.evaluate_events(self.ideas_raw)

        result = mentat.stats.idea._merge_stats(sts1)
        result = mentat.stats.idea._merge_stats(sts2, result)
        result = mentat.stats.idea._merge_stats(sts3, result)

        self.assertEqual(
            result,
            {
                "abuses": {"__unknown__": 9, "abuse@cesnet.cz": 9},
                "analyzers": {"Beekeeper": 3, "Dionaea": 3, "Kippo": 9, "LaBrea": 3},
                "asns": {"__unknown__": 18},
                "categories": {"Exploit": 6, "Fraud.Phishing": 9, "Spam": 3},
                "category_sets": {"Exploit": 6, "Fraud.Phishing": 9, "Spam": 3},
                "classes": {"__unknown__": 15, "fraud-phishing": 3},
                "cnt_alerts": 18,
                "cnt_events": 18,
                "countries": {"__unknown__": 18},
                "detectors": {
                    "cz.cesnet.holly": 3,
                    "org.example.dionaea": 6,
                    "org.example.kippo": 6,
                    "org.example.labrea": 3,
                },
                "detectorsws": {
                    "cz.cesnet.holly/Beekeeper": 3,
                    "org.example.dionaea/Dionaea": 3,
                    "org.example.dionaea/Kippo": 3,
                    "org.example.kippo/Kippo": 6,
                    "org.example.labrea/LaBrea": 3,
                },
                "sources": {
                    "192.168.0.0/25": 9,
                    "192.168.0.100": 3,
                    "192.168.0.105": 3,
                    "192.168.0.109": 3,
                    "192.168.0.2-192.168.0.5": 9,
                    "192.168.0.200": 3,
                    "192.172.0.109": 3,
                    "192.172.0.200": 3,
                    "2001:db8::ff00:42:0/112": 9,
                },
                "targets": {
                    "192.168.1.2-192.168.1.5": 6,
                    "192.168.1.0/25": 6,
                    "2001:db8::ff01:42:0/112": 6,
                    "192.168.1.109": 3,
                    "192.168.1.200": 3,
                    "__unknown__": 9,
                },
                "tlps": {"AMBER": 6, "CLEAR": 3, "GREEN": 6, "__unknown__": 3},
                "severities": {"__unknown__": 9, "medium": 6, "low": 3},
            },
        )

    def test_12_aggregate_stat_groups(self):
        """
        Perform the statistic group aggregation tests.
        """
        self.maxDiff = None

        timestamp = 1485993600

        stse1 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stse2 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stse3 = mentat.stats.idea.evaluate_events(self.ideas_raw)

        stso1 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stso2 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stso3 = mentat.stats.idea.evaluate_events(self.ideas_raw)

        stsi1 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stsi2 = mentat.stats.idea.evaluate_events(self.ideas_raw)
        stsi3 = mentat.stats.idea.evaluate_events(self.ideas_raw)

        sts1 = mentat.datatype.sqldb.EventStatisticsModel(
            interval="interval1",
            dt_from=datetime.datetime.fromtimestamp(timestamp),
            dt_to=datetime.datetime.fromtimestamp(timestamp + 300),
            count=stso1[mentat.stats.idea.ST_SKEY_CNT_ALERTS],
            stats_overall=stso1,
            stats_internal=stsi1,
            stats_external=stse1,
        )
        sts2 = mentat.datatype.sqldb.EventStatisticsModel(
            interval="interval2",
            dt_from=datetime.datetime.fromtimestamp(timestamp + 300),
            dt_to=datetime.datetime.fromtimestamp(timestamp + 600),
            count=stso2[mentat.stats.idea.ST_SKEY_CNT_ALERTS],
            stats_overall=stso2,
            stats_internal=stsi2,
            stats_external=stse2,
        )
        sts3 = mentat.datatype.sqldb.EventStatisticsModel(
            interval="interval3",
            dt_from=datetime.datetime.fromtimestamp(timestamp + 600),
            dt_to=datetime.datetime.fromtimestamp(timestamp + 900),
            count=stso3[mentat.stats.idea.ST_SKEY_CNT_ALERTS],
            stats_overall=stso3,
            stats_internal=stsi3,
            stats_external=stse3,
        )

        result = mentat.stats.idea.aggregate_stat_groups([sts1, sts2, sts3])

        self.assertTrue(result)
        self.assertEqual(result["dt_from"], datetime.datetime.fromtimestamp(timestamp))
        self.assertEqual(result["dt_to"], datetime.datetime.fromtimestamp(timestamp + 900))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
