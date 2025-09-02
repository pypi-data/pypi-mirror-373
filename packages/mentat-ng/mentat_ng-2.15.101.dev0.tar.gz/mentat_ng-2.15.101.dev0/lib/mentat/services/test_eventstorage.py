#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.eventstorage` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import difflib
import json
import pprint
import unittest

import mentat.idea.internal
import mentat.services.eventstorage
import mentat.stats.idea

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class MockUserObject:
    """
    Used for testing TLP-based authorization.
    """

    def __init__(self, group_names: list[str]) -> None:
        self.group_names = group_names

    def get_all_group_names(self) -> list[str]:
        return self.group_names


class TestMentatStorage(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.sqlstorage` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    IDEA_RAW_1 = {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf75",
        "TLP": "AMBER",
        "CreateTime": "2012-11-03T10:00:02Z",
        "DetectTime": "2012-11-03T10:00:07Z",
        "WinStartTime": "2012-11-03T05:00:00Z",
        "WinEndTime": "2012-11-03T10:00:00Z",
        "EventTime": "2012-11-03T07:36:00Z",
        "CeaseTime": "2012-11-03T09:55:22Z",
        "Category": ["Fraud.Phishing", "Test"],
        "Ref": ["cve:CVE-1234-5678"],
        "Confidence": 1.0,
        "Description": "Synthetic example",
        "Note": "Synthetic example note",
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
                "IP6": ["2001:ffff::ff00:42:0/112"],
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
                "Type": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
            }
        ],
        "_Mentat": {
            "StorageTime": "2017-04-05T10:21:39Z",
            "EventTemplate": "sserv-012",
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "TargetAbuses": ["abuse@muni.cz"],
            "Impact": "System provides SDDP service and can be misused for massive DDoS attack",
            "EventClass": "vulnerable-config-ssdp",
            "TargetClass": "vulnerable-config-ssdp-target",
            "EventSeverity": "low",
            "TargetSeverity": "medium",
            "InspectionErrors": [
                "Demonstration error - first",
                "Demonstration error - second",
            ],
            "ShadowReporting": True,
            "ShadowReportingTarget": True,
        },
    }

    #
    # This second IDEA message verifies, that is it possible to store messages
    # containing null characters.
    #
    IDEA_RAW_2 = {
        "Attach": [
            {
                "data": "root:zlxx.\u0000\nenable\u0000:system\u0000\nshell\u0000:sh\u0000",
                "datalen": 38,
            }
        ],
        "Category": ["Attempt.Login", "Test"],
        "ConnCount": 1,
        "DetectTime": "2018-04-30T08:54:28.550680Z",
        "Format": "IDEA0",
        "ID": "b434c36f-f0e6-4afb-afab-95863486e76f",
        "TLP": "GREEN",
        "Node": [
            {
                "Name": "cz.cesnet.hugo.haas_telnetd",
                "SW": ["telnetd"],
                "Type": ["Honeypot", "Connection"],
            }
        ],
        "Note": "telnetd event",
        "Source": [{"IP4": ["212.111.222.111"], "Port": [3246], "Proto": ["tcp"]}],
        "Target": [{"Anonymised": True, "IP4": ["192.0.0.0"], "Port": [23], "Proto": ["tcp"]}],
        "_Mentat": {
            "StorageTime": "2017-04-05T10:21:39Z",
            "EventClass": "attempt-login-telnet",
            "EventSeverity": "medium",
            "TargetClass": "attempt-login-telnet-target",
            "TargetSeverity": "low",
            "SourceResolvedASN": [12338],
            "SourceResolvedCountry": ["ES"],
            "ShadowReportingTarget": True,
        },
    }

    PGDB_CONFIG = {
        "dbname": "mentat_utest",
        "user": "mentat",
        "password": "mentat",
        "host": "localhost",
        "port": 5432,
    }

    MUNI_USER = MockUserObject(["abuse@muni.cz"])
    CESNET_USER = MockUserObject(["abuse@cesnet.cz"])
    RANDOM_USER = MockUserObject(["abuse@random.cz"])

    def _get_clean_storage(self):
        storage = mentat.services.eventstorage.EventStorageService(**self.PGDB_CONFIG)
        storage.database_drop()
        storage.database_create()
        return storage

    def test_01_service(self):  # pylint: disable=locally-disabled
        """
        Perform the basic tests of storage service.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()
        storage.database_drop()
        storage.close()

    def test_02_service_manager(self):
        """
        Perform the basic tests of storage service manager.
        """
        self.maxDiff = None

        manager = mentat.services.eventstorage.EventStorageServiceManager(
            {
                "__core__database": {
                    "eventstorage": {
                        "dbname": "mentat_utest",
                        "user": "mentatttt",
                        "password": "mentat",
                        "host": "localhost",
                        "port": 5432,
                    }
                }
            },
            {"__core__database": {"eventstorage": {"user": "mentat"}}},
        )
        storage = manager.service()
        storage.database_drop()
        storage.database_create()
        storage.database_drop()
        storage.close()
        manager.close()

    def test_03_module_service(self):
        """
        Perform the basic tests of module service.
        """
        self.maxDiff = None

        mentat.services.eventstorage.init(
            {
                "__core__database": {
                    "eventstorage": {
                        "dbname": "mentat_utest",
                        "user": "mentatttt",
                        "password": "mentat",
                        "host": "localhost",
                        "port": 5432,
                    }
                }
            },
            {"__core__database": {"eventstorage": {"user": "mentat"}}},
        )

        manager = mentat.services.eventstorage.manager()
        storage = manager.service()
        storage.database_drop()
        storage.database_create()
        storage.database_drop()
        storage.close()
        manager.close()

    def test_04_crd(self):
        """
        Perform the basic event create,read,delete tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)
        idea_from = storage.fetch_event(idea_into["ID"])

        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new = json.dumps(idea_from, indent=4, sort_keys=True, default=idea_from.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        idea_from = storage.fetch_event(idea_into["ID"])
        self.assertTrue(idea_from)
        storage.delete_event(idea_into["ID"])
        idea_from = storage.fetch_event(idea_into["ID"])
        self.assertEqual(idea_from, None)

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_2)
        storage.insert_event(idea_into)
        idea_from = storage.fetch_event(idea_into["ID"])
        self.assertTrue(idea_from)

        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new = json.dumps(idea_from, indent=4, sort_keys=True, default=idea_from.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        idea_from = storage.fetch_event(idea_into["ID"])
        self.assertTrue(idea_from)
        storage.delete_event(idea_into["ID"])
        idea_from = storage.fetch_event(idea_into["ID"])
        self.assertEqual(idea_from, None)

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)
        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_2)
        storage.insert_event(idea_into)
        count = storage.count_events()
        self.assertEqual(count, 2)
        count = storage.delete_events()
        self.assertEqual(count, 2)
        count = storage.count_events()
        self.assertEqual(count, 0)

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        idea_into["ID"] = "a1"
        storage.insert_event_bulkci(idea_into)
        idea_into["ID"] = "b2"
        storage.insert_event_bulkci(idea_into)
        idea_into["ID"] = "c3"
        storage.insert_event_bulkci(idea_into)
        idea_into["ID"] = "d4"
        storage.insert_event_bulkci(idea_into)
        try:
            idea_into["ID"] = "a1"
            storage.insert_event_bulkci(idea_into)
        except Exception:
            pass

        storage.commit_bulk()
        self.assertEqual(storage.savepoint, None)
        self.assertEqual(storage.count_events(), 4)

        storage.database_drop()
        storage.close()

    def test_05_build_query(self):
        """
        Perform various query building tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        tests = [
            (
                {"parameters": {}},
                b"SELECT * FROM events INNER JOIN events_json USING(id)",
            ),
            (
                {"parameters": {"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"detecttime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "st_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "st_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"storagetime\" >= '2012-11-03T10:00:07'::timestamp AND \"storagetime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "st_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "st_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    },
                    "qtype": "delete",
                },
                b"DELETE FROM events WHERE \"storagetime\" >= '2012-11-03T10:00:07'::timestamp AND \"storagetime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "st_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "st_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    },
                    "qtype": "count",
                },
                b"SELECT count(id) FROM events WHERE \"storagetime\" >= '2012-11-03T10:00:07'::timestamp AND \"storagetime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {"parameters": {"source_addrs": ["192.168.1.0/24"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE (\"source_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"source_ip\"))",
            ),
            (
                {"parameters": {"source_addrs": ["2001::/54"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE (\"source_ip_aggr_ip6\" && '2001::/54' AND '2001::/54' && ANY(\"source_ip\"))",
            ),
            (
                {"parameters": {"source_addrs": ["192.168.1.0/24", "2001::/54"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE ((\"source_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"source_ip\")) OR (\"source_ip_aggr_ip6\" && '2001::/54' AND '2001::/54' && ANY(\"source_ip\")))",
            ),
            (
                {"parameters": {"target_addrs": ["192.168.1.0/24"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE (\"target_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"target_ip\"))",
            ),
            (
                {"parameters": {"target_addrs": ["2001::/54"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE (\"target_ip_aggr_ip6\" && '2001::/54' AND '2001::/54' && ANY(\"target_ip\"))",
            ),
            (
                {"parameters": {"target_addrs": ["192.168.1.0/24", "2001::/54"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE ((\"target_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"target_ip\")) OR (\"target_ip_aggr_ip6\" && '2001::/54' AND '2001::/54' && ANY(\"target_ip\")))",
            ),
            (
                {"parameters": {"host_addrs": ["192.168.1.0/24"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE ((\"source_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"source_ip\")) OR (\"target_ip_aggr_ip4\" && '192.168.1.0/24' AND '192.168.1.0/24' && ANY(\"target_ip\")))",
            ),
            (
                {"parameters": {"source_ports": [22, 443]}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "source_port" && ARRAY[22,443]',
            ),
            (
                {"parameters": {"target_ports": [22, 443]}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "target_port" && ARRAY[22,443]',
            ),
            (
                {"parameters": {"host_ports": [22, 443], "source_ports": [22, 443]}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE ("source_port" && ARRAY[22,443] OR "target_port" && ARRAY[22,443])',
            ),
            (
                {"parameters": {"source_types": ["Test", "Tag"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"source_type\" && ARRAY['Test','Tag']",
            ),
            (
                {"parameters": {"target_types": ["Test", "Tag"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"target_type\" && ARRAY['Test','Tag']",
            ),
            (
                {
                    "parameters": {
                        "host_types": ["Test", "Tag"],
                        "target_types": ["Test", "Tag"],
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE (\"source_type\" && ARRAY['Test','Tag'] OR \"target_type\" && ARRAY['Test','Tag'])",
            ),
            (
                {"parameters": {"protocols": ["tcp", "ssh"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"protocol\" && ARRAY['tcp','ssh']",
            ),
            (
                {"parameters": {"protocols": ["tcp", "ssh"], "not_protocols": True}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"protocol\" && ARRAY['tcp','ssh'])",
            ),
            (
                {"parameters": {"protocols": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"protocol\" = '{}'",
            ),
            (
                {"parameters": {"protocols": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"protocol\" != '{}'",
            ),
            (
                {"parameters": {"categories": ["Test", "Category"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"category\" && ARRAY['Test','Category']",
            ),
            (
                {
                    "parameters": {
                        "categories": ["Test", "Category"],
                        "not_categories": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"category\" && ARRAY['Test','Category'])",
            ),
            (
                {"parameters": {"categories": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"category\" = '{}'",
            ),
            (
                {"parameters": {"categories": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"category\" != '{}'",
            ),
            (
                {"parameters": {"classes": ["test", "vulnerable-config-ssdp"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"eventclass\" = ANY(ARRAY['test','vulnerable-config-ssdp'])",
            ),
            (
                {
                    "parameters": {
                        "classes": ["test", "vulnerable-config-ssdp"],
                        "not_classes": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"eventclass\" = ANY(ARRAY['test','vulnerable-config-ssdp']))",
            ),
            (
                {"parameters": {"classes": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"eventclass\",'') = ''",
            ),
            (
                {"parameters": {"classes": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"eventclass\",'') != ''",
            ),
            (
                {"parameters": {"target_classes": ["test", "vulnerable-config-ssdp-target"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"targetclass\" = ANY(ARRAY['test','vulnerable-config-ssdp-target'])",
            ),
            (
                {
                    "parameters": {
                        "target_classes": ["test", "vulnerable-config-ssdp-target"],
                        "not_target_classes": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"targetclass\" = ANY(ARRAY['test','vulnerable-config-ssdp-target']))",
            ),
            (
                {"parameters": {"target_classes": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"targetclass\",'') = ''",
            ),
            (
                {"parameters": {"target_classes": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"targetclass\",'') != ''",
            ),
            (
                {"parameters": {"severities": ["test", "low"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"eventseverity\" = ANY(ARRAY['test','low'])",
            ),
            (
                {"parameters": {"severities": ["test", "low"], "not_severities": True}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"eventseverity\" = ANY(ARRAY['test','low']))",
            ),
            (
                {"parameters": {"severities": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"eventseverity\",'') = ''",
            ),
            (
                {"parameters": {"severities": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"eventseverity\",'') != ''",
            ),
            (
                {"parameters": {"target_severities": ["test", "low"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"targetseverity\" = ANY(ARRAY['test','low'])",
            ),
            (
                {
                    "parameters": {
                        "target_severities": ["test", "low"],
                        "not_target_severities": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"targetseverity\" = ANY(ARRAY['test','low']))",
            ),
            (
                {"parameters": {"target_severities": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"targetseverity\",'') = ''",
            ),
            (
                {"parameters": {"target_severities": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"targetseverity\",'') != ''",
            ),
            (
                {"parameters": {"detectors": ["cz.cesnet.kippo", "cz.cesnet.dionaea"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_name\" && ARRAY['cz.cesnet.kippo','cz.cesnet.dionaea']",
            ),
            (
                {
                    "parameters": {
                        "detectors": ["cz.cesnet.kippo", "cz.cesnet.dionaea"],
                        "not_detectors": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"node_name\" && ARRAY['cz.cesnet.kippo','cz.cesnet.dionaea'])",
            ),
            (
                {"parameters": {"detectors": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_name\" = '{}'",
            ),
            (
                {"parameters": {"detectors": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_name\" != '{}'",
            ),
            (
                {"parameters": {"detector_types": ["Test", "Tag"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_type\" && ARRAY['Test','Tag']",
            ),
            (
                {
                    "parameters": {
                        "detector_types": ["Test", "Tag"],
                        "not_detector_types": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"node_type\" && ARRAY['Test','Tag'])",
            ),
            (
                {"parameters": {"detector_types": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_type\" = '{}'",
            ),
            (
                {"parameters": {"detector_types": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"node_type\" != '{}'",
            ),
            (
                {"parameters": {"groups": ["abuse@cesnet.cz", "abuse@nic.cz"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"resolvedabuses\" && ARRAY['abuse@cesnet.cz','abuse@nic.cz']",
            ),
            (
                {
                    "parameters": {
                        "groups": ["abuse@cesnet.cz", "abuse@nic.cz"],
                        "not_groups": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"resolvedabuses\" && ARRAY['abuse@cesnet.cz','abuse@nic.cz'])",
            ),
            (
                {"parameters": {"groups": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"resolvedabuses\" = '{}'",
            ),
            (
                {"parameters": {"groups": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"resolvedabuses\" != '{}'",
            ),
            (
                {"parameters": {"target_groups": ["abuse@cesnet.cz", "abuse@nic.cz"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"targetabuses\" && ARRAY['abuse@cesnet.cz','abuse@nic.cz']",
            ),
            (
                {
                    "parameters": {
                        "target_groups": ["abuse@cesnet.cz", "abuse@nic.cz"],
                        "not_target_groups": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"targetabuses\" && ARRAY['abuse@cesnet.cz','abuse@nic.cz'])",
            ),
            (
                {"parameters": {"target_groups": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"targetabuses\" = '{}'",
            ),
            (
                {"parameters": {"target_groups": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"targetabuses\" != '{}'",
            ),
            (
                {"parameters": {"description": "Test description"}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"description\" ILIKE '%' || 'Test description' || '%' ESCAPE '&'",
            ),
            (
                {"parameters": {"limit": 50}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) LIMIT 50",
            ),
            (
                {"parameters": {"limit": 50, "page": 11}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) LIMIT 50 OFFSET 500",
            ),
            (
                {
                    "parameters": {
                        "groups": ["abuse@cesnet.cz", "abuse@nic.cz"],
                        "limit": 50,
                        "page": 11,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"resolvedabuses\" && ARRAY['abuse@cesnet.cz','abuse@nic.cz'] LIMIT 50 OFFSET 500",
            ),
            (
                {"parameters": {"tlps": ["CLEAR", "GREEN"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"tlp\" = ANY(ARRAY['CLEAR','GREEN'])",
            ),
            (
                {
                    "parameters": {
                        "tlps": ["AMBER", "RED"],
                        "not_tlps": True,
                    }
                },
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE NOT (\"tlp\" = ANY(ARRAY['AMBER','RED']))",
            ),
            (
                {"parameters": {"tlps": ["__EMPTY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"tlp\", '') = ''",
            ),
            (
                {"parameters": {"tlps": ["__ANY__"]}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE COALESCE(\"tlp\", '') != ''",
            ),
            (
                {"parameters": {"shadow_reporting": "True"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting" IS TRUE',
            ),
            (
                {"parameters": {"shadow_reporting": True}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting" IS TRUE',
            ),
            (
                {"parameters": {"shadow_reporting": "False"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting" IS FALSE',
            ),
            (
                {"parameters": {"shadow_reporting": False}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting" IS FALSE',
            ),
            (
                {"parameters": {"shadow_reporting_target": "True"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting_target" IS TRUE',
            ),
            (
                {"parameters": {"shadow_reporting_target": True}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting_target" IS TRUE',
            ),
            (
                {"parameters": {"shadow_reporting_target": "False"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting_target" IS FALSE',
            ),
            (
                {"parameters": {"shadow_reporting_target": False}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) WHERE "shadow_reporting_target" IS FALSE',
            ),
            (
                {"parameters": {"sortby": "detecttime.desc"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) ORDER BY "detecttime" DESC',
            ),
            (
                {"parameters": {"sortby": "detecttime.asc"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) ORDER BY "detecttime" ASC',
            ),
            (
                {"parameters": {"sortby": "storagetime.desc"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) ORDER BY "storagetime" DESC',
            ),
            (
                {"parameters": {"sortby": "storagetime.asc"}},
                b'SELECT * FROM events INNER JOIN events_json USING(id) ORDER BY "storagetime" ASC',
            ),
        ]

        for test in tests:
            query, params = mentat.services.eventstorage.build_query(**test[0])
            self.assertEqual(
                str(storage.mogrify(query, params)).replace(", ", ","),
                str(test[1]).replace(", ", ","),
            )

        storage.database_drop()
        storage.close()

    def test_06_build_query_aggr(self):
        """
        Perform various query building tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        tests = [
            ({"parameters": {}, "qtype": "aggregate"}, b"SELECT COUNT(*) FROM events"),
            (
                {
                    "parameters": {"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)},
                    "qtype": "aggregate",
                },
                b"SELECT COUNT(*) FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    },
                    "qtype": "aggregate",
                },
                b"SELECT COUNT(*) FROM events WHERE \"detecttime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                    },
                    "qtype": "aggregate",
                },
                b"SELECT COUNT(*) FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" <= '2012-11-03T10:00:07'::timestamp",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "aggr_set": "eventclass",
                    },
                    "qtype": "aggregate",
                },
                b"SELECT COALESCE(\"eventclass\", '__unknown__') AS set,COUNT(*) FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" <= '2012-11-03T10:00:07'::timestamp GROUP BY set",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "aggr_set": "category",
                    },
                    "qtype": "aggregate",
                },
                b'SELECT unnest("category") AS set,COUNT(*) FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" <= \'2012-11-03T10:00:07\'::timestamp GROUP BY set',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "aggr_set": "eventclass",
                        "limit": 10,
                    },
                    "qtype": "aggregate",
                },
                b"SELECT COALESCE(\"eventclass\", '__unknown__') AS set,COUNT(*) FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" <= '2012-11-03T10:00:07'::timestamp GROUP BY set",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "aggr_set": "category",
                        "limit": 10,
                    },
                    "qtype": "aggregate",
                },
                b'SELECT unnest("category") AS set,COUNT(*) FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" <= \'2012-11-03T10:00:07\'::timestamp GROUP BY set',
            ),
            (
                {
                    "parameters": {
                        "timeline_cfg": mentat.stats.idea.TimelineCFG(
                            datetime.datetime(2012, 11, 3, 10, 0, 7),
                            datetime.datetime(2012, 12, 3, 10, 0, 7),
                            datetime.timedelta(days=1),
                            first_step=datetime.datetime(2012, 11, 4),
                        ),
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 12, 3, 10, 0, 7),
                    },
                    "qtype": "timeline",
                },
                b"WITH timeline AS (SELECT * FROM (SELECT '2012-11-03T10:00:07'::timestamp AS bucket UNION SELECT generate_series('2012-11-04T00:00:00'::timestamp, '2012-12-03T10:00:07'::timestamp - INTERVAL '1 microsecond', '1 days 0.000000 seconds'::interval) AS bucket) AS t ORDER BY bucket), raw AS (SELECT GREATEST('2012-11-03T10:00:07'::timestamp, '2012-11-04T00:00:00'::timestamp + '1 days 0.000000 seconds'::interval * (width_bucket(\"detecttime\", (SELECT array_agg(bucket) FROM generate_series('2012-11-04T00:00:00'::timestamp, '2012-12-03T10:00:07'::timestamp - INTERVAL '1 microsecond', '1 days 0.000000 seconds'::interval) AS bucket)) - 1)) AS bucket, COUNT(*) AS count FROM \"events\" WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp GROUP BY bucket) (SELECT timeline.bucket, COALESCE(count, 0) AS count FROM \"timeline\" LEFT JOIN \"raw\" ON timeline.bucket = raw.bucket ORDER BY bucket ASC) UNION ALL SELECT NULL, SUM(count)::bigint FROM \"raw\"",
            ),
            (
                {
                    "parameters": {
                        "timeline_cfg": mentat.stats.idea.TimelineCFG(
                            datetime.datetime(2012, 11, 3, 10, 0, 7),
                            datetime.datetime(2012, 12, 3, 10, 0, 7),
                            datetime.timedelta(days=1),
                            first_step=datetime.datetime(2012, 11, 4),
                        ),
                        "aggr_set": "eventclass",
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 12, 3, 10, 0, 7),
                    },
                    "qtype": "timeline",
                },
                b'WITH timeline AS (SELECT * FROM (SELECT \'2012-11-03T10:00:07\'::timestamp AS bucket UNION SELECT generate_series(\'2012-11-04T00:00:00\'::timestamp, \'2012-12-03T10:00:07\'::timestamp - INTERVAL \'1 microsecond\', \'1 days 0.000000 seconds\'::interval) AS bucket) AS t ORDER BY bucket), total_events AS (SELECT COUNT(*) AS total FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-12-03T10:00:07\'::timestamp), raw AS (SELECT GREATEST(\'2012-11-03T10:00:07\'::timestamp, \'2012-11-04T00:00:00\'::timestamp + \'1 days 0.000000 seconds\'::interval * (width_bucket("detecttime", (SELECT array_agg(bucket) FROM generate_series(\'2012-11-04T00:00:00\'::timestamp, \'2012-12-03T10:00:07\'::timestamp - INTERVAL \'1 microsecond\', \'1 days 0.000000 seconds\'::interval) AS bucket)) - 1)) AS bucket, COALESCE("eventclass", \'__unknown__\') AS set, COUNT(*) AS count FROM "events" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-12-03T10:00:07\'::timestamp GROUP BY bucket, set), sums AS (SELECT raw.set::text AS set, SUM(raw.count)::bigint AS sum FROM raw GROUP BY raw.set ORDER BY sum DESC) (SELECT timeline.bucket, "sums".set, COALESCE(count, 0) AS count FROM ("timeline" FULL JOIN "sums" ON TRUE) LEFT JOIN "raw" ON "timeline".bucket = "raw".bucket AND "sums".set IS NOT DISTINCT FROM "raw".set ORDER BY bucket ASC, "sums".sum DESC) UNION ALL SELECT NULL, "sums".set, "sums".sum FROM "sums" UNION ALL SELECT NULL, NULL, total FROM "total_events" UNION ALL SELECT NULL, NULL, total FROM total_events',
            ),
            (
                {
                    "parameters": {
                        "timeline_cfg": mentat.stats.idea.TimelineCFG(
                            datetime.datetime(2012, 11, 3, 10, 0, 7),
                            datetime.datetime(2012, 12, 3, 10, 0, 7),
                            datetime.timedelta(days=1),
                            first_step=datetime.datetime(2012, 11, 4),
                        ),
                        "aggr_set": "category",
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 12, 3, 10, 0, 7),
                    },
                    "qtype": "timeline",
                },
                b'WITH timeline AS (SELECT * FROM (SELECT \'2012-11-03T10:00:07\'::timestamp AS bucket UNION SELECT generate_series(\'2012-11-04T00:00:00\'::timestamp, \'2012-12-03T10:00:07\'::timestamp - INTERVAL \'1 microsecond\', \'1 days 0.000000 seconds\'::interval) AS bucket) AS t ORDER BY bucket), total AS (SELECT COALESCE(SUM(CARDINALITY("category")), 0) AS total FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-12-03T10:00:07\'::timestamp), total_events AS (SELECT COUNT(*) AS total FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-12-03T10:00:07\'::timestamp), raw AS (SELECT GREATEST(\'2012-11-03T10:00:07\'::timestamp, \'2012-11-04T00:00:00\'::timestamp + \'1 days 0.000000 seconds\'::interval * (width_bucket("detecttime", (SELECT array_agg(bucket) FROM generate_series(\'2012-11-04T00:00:00\'::timestamp, \'2012-12-03T10:00:07\'::timestamp - INTERVAL \'1 microsecond\', \'1 days 0.000000 seconds\'::interval) AS bucket)) - 1)) AS bucket, unnest("category") AS set, COUNT(*) AS count FROM "events" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-12-03T10:00:07\'::timestamp GROUP BY bucket, set), sums AS (SELECT raw.set::text AS set, SUM(raw.count)::bigint AS sum FROM raw GROUP BY raw.set ORDER BY sum DESC) (SELECT timeline.bucket, "sums".set, COALESCE(count, 0) AS count FROM ("timeline" FULL JOIN "sums" ON TRUE) LEFT JOIN "raw" ON "timeline".bucket = "raw".bucket AND "sums".set IS NOT DISTINCT FROM "raw".set ORDER BY bucket ASC, "sums".sum DESC) UNION ALL SELECT NULL, "sums".set, "sums".sum FROM "sums" UNION ALL SELECT NULL, NULL, total FROM "total" UNION ALL SELECT NULL, NULL, total FROM total_events',
            ),
            (
                {
                    "parameters": {
                        "timeline_cfg": mentat.stats.idea.TimelineCFG(
                            datetime.datetime(2012, 11, 3, 10, 0, 7),
                            datetime.datetime(2012, 12, 3, 10, 0, 7),
                            datetime.timedelta(days=1),
                            first_step=datetime.datetime(2012, 11, 4),
                        ),
                        "aggr_set": "target_port",
                        "limit": 42,
                        "include_residuals": True,
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 12, 3, 10, 0, 7),
                    },
                    "qtype": "timeline",
                    "dbtoplist": True,
                },
                b"WITH timeline AS (SELECT * FROM (SELECT '2012-11-03T10:00:07'::timestamp AS bucket UNION SELECT generate_series('2012-11-04T00:00:00'::timestamp, '2012-12-03T10:00:07'::timestamp - INTERVAL '1 microsecond', '1 days 0.000000 seconds'::interval) AS bucket) AS t ORDER BY bucket), total AS (SELECT COALESCE(SUM(CARDINALITY(\"target_port\")), 0) AS total FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp), total_events AS (SELECT COUNT(*) AS total FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp), toplist AS (SELECT unnest(\"target_port\") AS set, COUNT(*) AS sum FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp GROUP BY set ORDER BY sum DESC LIMIT 42), toplist_with_rest AS (SELECT set::text, sum FROM toplist UNION (SELECT '__REST__' as set, total - SUM(sum)::bigint as sum FROM \"total\", toplist GROUP BY total HAVING total - SUM(sum)::bigint > 0) ORDER BY sum DESC), raw AS (SELECT GREATEST('2012-11-03T10:00:07'::timestamp, '2012-11-04T00:00:00'::timestamp + '1 days 0.000000 seconds'::interval * (width_bucket(\"detecttime\", (SELECT array_agg(bucket) FROM generate_series('2012-11-04T00:00:00'::timestamp, '2012-12-03T10:00:07'::timestamp - INTERVAL '1 microsecond', '1 days 0.000000 seconds'::interval) AS bucket)) - 1)) AS bucket, set, COUNT(*) AS count FROM (SELECT \"detecttime\", unnest(\"target_port\") AS set FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp) top_events INNER JOIN toplist USING (set) GROUP BY bucket, set), raw_with_rest AS (SELECT bucket, set::text, count FROM raw UNION ALL SELECT bucket, '__REST__' AS set, raw_totals.count - raw_sums.count AS count FROM (SELECT GREATEST('2012-11-03T10:00:07'::timestamp, '2012-11-04T00:00:00'::timestamp + '1 days 0.000000 seconds'::interval * (width_bucket(\"detecttime\", (SELECT array_agg(bucket) FROM generate_series('2012-11-04T00:00:00'::timestamp, '2012-12-03T10:00:07'::timestamp - INTERVAL '1 microsecond', '1 days 0.000000 seconds'::interval) AS bucket)) - 1)) AS bucket, SUM(CARDINALITY(\"target_port\")) AS count FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" < '2012-12-03T10:00:07'::timestamp GROUP BY bucket) raw_totals FULL JOIN (SELECT bucket, SUM(count)::bigint AS count FROM raw GROUP BY bucket) raw_sums USING (bucket)) (SELECT timeline.bucket, \"toplist_with_rest\".set, COALESCE(count, 0) AS count FROM (\"timeline\" FULL JOIN \"toplist_with_rest\" ON TRUE) LEFT JOIN \"raw_with_rest\" ON \"timeline\".bucket = \"raw_with_rest\".bucket AND \"toplist_with_rest\".set IS NOT DISTINCT FROM \"raw_with_rest\".set ORDER BY bucket ASC, \"toplist_with_rest\".sum DESC) UNION ALL SELECT NULL, \"toplist_with_rest\".set, \"toplist_with_rest\".sum FROM \"toplist_with_rest\" UNION ALL SELECT NULL, NULL, total FROM \"total\" UNION ALL SELECT NULL, NULL, total FROM total_events",
            ),
            (
                {
                    "parameters": {"col_agg": "category", "row_agg": "protocol", "include_residuals": True},
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("protocol") AS "row_category" CROSS JOIN LATERAL unnest("category") AS "col_category" GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "category",
                        "row_agg": "protocol",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("protocol") AS "row_category" CROSS JOIN LATERAL unnest("category") AS "col_category" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "category",
                        "row_agg": "node_type",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("node_type") AS "row_category" CROSS JOIN LATERAL unnest("category") AS "col_category" WHERE "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "eventclass",
                        "row_agg": "eventseverity",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT COALESCE("eventseverity",\'__unknown__\') AS "row_category",COALESCE("eventclass",\'__unknown__\') AS "col_category",COUNT(*) AS observed FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "source_type",
                        "row_agg": "target_type",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("target_type") AS "row_category" CROSS JOIN LATERAL unnest("source_type") AS "col_category" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "event_class",
                        "row_agg": "protocol",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category",COALESCE("event_class",\'__unknown__\') AS "col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("protocol") AS "row_category" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "tlp",
                        "row_agg": "tlp",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT COALESCE("tlp",\'__unknown__\') AS "row_category",COALESCE("tlp",\'__unknown__\') AS "col_category",COUNT(*) AS observed FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "col_agg": "protocol",
                        "row_agg": "protocol",
                        "include_residuals": True,
                    },
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("protocol") AS "row_category" CROSS JOIN LATERAL unnest("protocol") AS "col_category" WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" < \'2012-11-03T10:00:07\'::timestamp GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category),row_totals AS (SELECT row_category,SUM(observed) AS row_total FROM pivot GROUP BY row_category),column_totals AS (SELECT col_category,SUM(observed) AS col_total FROM pivot GROUP BY col_category),total AS (SELECT SUM(observed) AS total FROM pivot),expected AS (SELECT p.row_category,p.col_category,p.observed,(rt.row_total * ct.col_total)::NUMERIC / t.total AS expected,rt.row_total,ct.col_total,t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t),residuals AS (SELECT row_category,col_category,observed,expected,CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)SELECT row_category,col_category,observed,"standardized_residual" FROM "residuals" AS "res" ORDER BY row_category,col_category',
            ),
            (
                {
                    "parameters": {"col_agg": "category", "row_agg": "protocol", "include_residuals": False},
                    "qtype": "pivot",
                },
                b'WITH observed_counts AS (SELECT "row_category","col_category",COUNT(*) AS observed FROM events CROSS JOIN LATERAL unnest("protocol") AS "row_category" CROSS JOIN LATERAL unnest("category") AS "col_category" GROUP BY row_category,col_category),distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts),distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts),all_pairs AS (SELECT dr.row_category,dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc),pivot AS (SELECT ap.row_category,ap.col_category,COALESCE(oc.observed,0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category)SELECT row_category,col_category,observed,NULL FROM "pivot" AS "res" ORDER BY row_category,col_category',
            ),
        ]

        for test in tests:
            query, params = mentat.services.eventstorage.build_query(**test[0])
            self.assertEqual(
                str(storage.mogrify(query, params)).replace(", ", ","),
                str(test[1]).replace(", ", ","),
            )

        storage.database_drop()
        storage.close()

    def test_07_search_events(self):
        """
        Perform various event search tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)

        orig = json.dumps([idea_into], indent=4, sort_keys=True, default=idea_into.json_default)

        # ---

        ideas_count, ideas_from = storage.search_events({"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"dt_to": datetime.datetime(2012, 11, 3, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"st_from": datetime.datetime(2017, 4, 5, 10, 10, 0)})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"st_to": datetime.datetime(2017, 4, 5, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_addrs": ["10.2.2.55"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_addrs": ["10.0.0.0/8"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"host_addrs": ["10.0.0.0/8"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_addrs": ["10.25.2.55"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"source_addrs": ["2001:db8::ff00:42:0/112"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"source_addrs": ["2001:db8::0/64"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"host_addrs": ["2001:db8::0/64"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"source_addrs": ["2001:ffff::ffff:42:0/112"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_ports": [22, 888]})
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"host_ports": [22, 888]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_ports": [888, 999]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_types": ["Test", "Backscatter"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_types": ["Test", "Tag"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"source_types": ["Test", "Phishing"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"host_types": ["Test", "Phishing"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"source_types": ["Test", "Tag"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"protocols": ["tcp", "ipv6"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"protocols": ["udp", "ipv8"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"protocols": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"protocols": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"categories": ["Fraud.Phishing"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"categories": ["Test.Heartbeat"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"categories": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"categories": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"classes": ["test", "vulnerable-config-ssdp"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"classes": ["test", "class"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"classes": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"classes": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_classes": ["test", "vulnerable-config-ssdp-target"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_classes": ["test", "class"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_classes": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_classes": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"severities": ["test", "low"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"severities": ["test", "high"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"severities": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"severities": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_severities": ["medium"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_severities": ["high"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_severities": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_severities": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"detectors": ["org.example.kippo_honey"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"detectors": ["org.another.kippo_honey"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"detectors": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"detectors": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"detector_types": ["Honeypot"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"detector_types": ["Test", "Tag"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"detector_types": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"detector_types": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"groups": ["abuse@cesnet.cz"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"groups": ["abuse@nic.cz"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"groups": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"groups": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_groups": ["abuse@muni.cz"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_groups": ["abuse@nic.cz"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"target_groups": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"target_groups": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"description": "Synthetic example"})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"description": "Bogus description"})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"tlps": ["RED"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"tlps": ["AMBER"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"tlps": ["__ANY__"]})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"tlps": ["__EMPTY__"]})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"shadow_reporting": True})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"shadow_reporting": "False"})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events({"shadow_reporting_target": "True"})
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        # ---

        ideas_count, ideas_from = storage.search_events({"shadow_reporting_target": False})
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # storage.database_drop()
        storage.close()

    def test_08_search_with_authorization(self):
        """
        Perform various event search and SQL generation test when
        TLP-based authorization is enabled.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        # Test SQL generation (build_query).
        tests = [
            (
                {"parameters": {"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)}},
                b"SELECT * FROM events INNER JOIN events_json USING(id) WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND (\"tlp\" IS NULL OR \"tlp\" NOT IN ('AMBER-STRICT','AMBER','RED') OR \"resolvedabuses\" && ARRAY['abuse@cesnet.cz'] OR \"targetabuses\" && ARRAY['abuse@cesnet.cz'])",
            ),
            (
                {
                    "parameters": {
                        "dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "dt_to": datetime.datetime(2012, 11, 3, 10, 0, 7),
                        "aggr_set": "category",
                    },
                    "qtype": "aggregate",
                },
                b"SELECT unnest(\"category\") AS set,COUNT(*) FROM events WHERE \"detecttime\" >= '2012-11-03T10:00:07'::timestamp AND \"detecttime\" <= '2012-11-03T10:00:07'::timestamp AND (\"tlp\" IS NULL OR \"tlp\" NOT IN ('AMBER-STRICT','AMBER','RED') OR \"resolvedabuses\" && ARRAY['abuse@cesnet.cz'] OR \"targetabuses\" && ARRAY['abuse@cesnet.cz']) GROUP BY set",
            ),
        ]

        for test in tests:
            query, params = mentat.services.eventstorage.build_query(**test[0], user=self.CESNET_USER)
            self.assertEqual(
                str(storage.mogrify(query, params)).replace(", ", ","),
                str(test[1]).replace(", ", ","),
            )

        # Test event searching.
        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)
        orig = json.dumps([idea_into], indent=4, sort_keys=True, default=idea_into.json_default)

        ideas_count, ideas_from = storage.search_events(user=self.CESNET_USER)
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        ideas_count, ideas_from = storage.search_events(user=self.MUNI_USER)
        self.assertEqual(ideas_count, 1)
        new = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        ideas_count, ideas_from = storage.search_events(user=self.RANDOM_USER)
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        storage.database_drop()
        storage.close()

    def test_09_count_events(self):
        """
        Perform various event count tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)

        # ---

        ideas_count = storage.count_events({"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)})
        self.assertEqual(ideas_count, 1)

        # ---

        ideas_count = storage.count_events({"dt_to": datetime.datetime(2012, 11, 3, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)

        # ---

        ideas_count = storage.count_events({"st_from": datetime.datetime(2017, 4, 5, 10, 10, 0)})
        self.assertEqual(ideas_count, 1)

        # ---

        ideas_count = storage.count_events({"st_to": datetime.datetime(2017, 4, 5, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)

    def test_10_delete_events(self):
        """
        Perform various event delete tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events({"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)})
        self.assertEqual(ideas_count, 1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events({"dt_to": datetime.datetime(2012, 11, 3, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)

        # ---

        ideas_count = storage.delete_events({"st_from": datetime.datetime(2017, 4, 5, 10, 10, 0)})
        self.assertEqual(ideas_count, 1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events({"st_to": datetime.datetime(2017, 4, 5, 10, 0, 0)})
        self.assertEqual(ideas_count, 0)

    def test_11_distinct_values(self):
        """
        Perform various distinct values tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)

        ideas_count, ideas_from = storage.search_events()
        self.assertEqual(ideas_count, 1)
        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new = json.dumps(ideas_from[0], indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(
            orig,
            new,
            "\n".join(difflib.context_diff(orig.split("\n"), new.split("\n"))),
        )

        self.assertEqual(storage.distinct_values("category"), ["Fraud.Phishing", "Test"])

        self.assertEqual(storage.distinct_values("eventclass"), ["vulnerable-config-ssdp"])

        self.assertEqual(storage.distinct_values("eventseverity"), ["low"])

    def test_12_thresholding_cache(self):
        """
        Perform various thresholding cache tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        ttltime = datetime.datetime.utcnow()
        reltime = ttltime - datetime.timedelta(seconds=300)
        thrtime = reltime - datetime.timedelta(seconds=300)
        label = "label"

        storage.threshold_set("ident1", thrtime, reltime, ttltime, label)
        storage.threshold_set("ident2", thrtime, reltime, ttltime, label)
        storage.threshold_set("ident3", thrtime, reltime, ttltime, label)
        self.assertEqual(storage.thresholds_count(), 3)

        storage.threshold_save(
            "msgid1",
            "ident3",
            "test@domain.org",
            "low",
            reltime + datetime.timedelta(seconds=5),
            False,
            False,
        )
        storage.threshold_save(
            "msgid2",
            "ident3",
            "test@domain.org",
            "low",
            reltime + datetime.timedelta(seconds=6),
            False,
            False,
        )
        storage.threshold_save(
            "msgid3",
            "ident2",
            "test@domain.com",
            "low",
            reltime + datetime.timedelta(seconds=2),
            True,
            False,
        )
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertTrue(storage.threshold_check("ident1", ttltime))
        self.assertTrue(storage.threshold_check("ident1", ttltime - datetime.timedelta(seconds=300)))
        self.assertFalse(storage.threshold_check("ident1", ttltime + datetime.timedelta(seconds=300)))

        self.assertEqual(storage.thresholds_clean(ttltime), 0)
        self.assertEqual(storage.thresholded_events_clean(), 0)
        self.assertEqual(storage.thresholds_count(), 3)
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertEqual(storage.thresholds_clean(ttltime - datetime.timedelta(seconds=300)), 0)
        self.assertEqual(storage.thresholded_events_clean(), 0)
        self.assertEqual(storage.thresholds_count(), 3)
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertEqual(storage.thresholds_clean(ttltime + datetime.timedelta(seconds=300)), 3)
        self.assertEqual(storage.thresholds_count(), 0)
        self.assertEqual(storage.thresholded_events_count(), 3)
        self.assertEqual(storage.thresholded_events_clean(), 3)
        self.assertEqual(storage.thresholds_count(), 0)
        self.assertEqual(storage.thresholded_events_count(), 0)

    def test_13_relapse(self):
        """
        Perform various relapse tests.
        """
        self.maxDiff = None
        storage = self._get_clean_storage()

        def _threshold_save(eventid, keyid, createtime, target):
            storage.threshold_save(
                eventid=eventid,
                keyid=keyid,
                group_name="test@domain.org",
                severity="low",
                createtime=createtime,
                is_target=target,
                is_shadow=False,
            )

        for target in True, False:
            ttltime = datetime.datetime.utcnow()
            reltime = ttltime - datetime.timedelta(seconds=300)
            thrtime = reltime - datetime.timedelta(seconds=300)
            label = "label"

            idea1 = mentat.idea.internal.Idea(self.IDEA_RAW_1)
            idea2 = mentat.idea.internal.Idea(self.IDEA_RAW_2)

            # Test event recorded during thresholding period but before relapse period
            storage.insert_event(idea1)
            storage.threshold_set("ident1", thrtime, reltime, ttltime, label)
            _threshold_save(idea1["ID"], "ident1", reltime - datetime.timedelta(seconds=200), target)

            relapses = storage.search_relapsed_events("test@domain.org", "low", ttltime, target, False)
            self.assertEqual(len(relapses), 0)
            count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds=300))
            self.assertEqual(count, 1)
            count = storage.thresholded_events_clean()
            self.assertEqual(count, 1)
            count = storage.delete_events()
            self.assertEqual(count, 1)

            # Test events recorded during thresholding period before and during relapse period
            storage.insert_event(idea1)
            storage.insert_event(idea2)
            storage.threshold_set("ident1", thrtime, reltime, ttltime, label)
            _threshold_save(idea1["ID"], "ident1", reltime - datetime.timedelta(seconds=200), target)
            _threshold_save(idea2["ID"], "ident1", reltime + datetime.timedelta(seconds=200), target)

            relapses = storage.search_relapsed_events(
                "test@domain.org", "low", ttltime + datetime.timedelta(seconds=300), target, False
            )
            self.assertEqual(len(relapses), 2)
            count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds=300))
            self.assertEqual(count, 1)
            count = storage.thresholded_events_clean()
            self.assertEqual(count, 2)
            count = storage.delete_events()
            self.assertEqual(count, 2)

            # Test that target-based events do not interfere with source-based events and vice versa
            storage.insert_event(idea1)
            storage.insert_event(idea2)
            storage.threshold_set("ident1", thrtime, reltime, ttltime, label)
            storage.threshold_set("ident2", thrtime, reltime, ttltime, label)
            _threshold_save(idea1["ID"], "ident1", reltime + datetime.timedelta(seconds=200), target)
            _threshold_save(
                idea2["ID"],
                "ident2",
                reltime + datetime.timedelta(seconds=200),
                not target,
            )

            relapses = storage.search_relapsed_events(
                "test@domain.org", "low", ttltime + datetime.timedelta(seconds=300), target, False
            )
            self.assertEqual(len(relapses), 1)
            count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds=300))
            self.assertEqual(count, 2)
            count = storage.thresholded_events_clean()
            self.assertEqual(count, 2)
            count = storage.delete_events()
            self.assertEqual(count, 2)

            # Test events with different keyid combinations where one event is created during the relapse period
            # and the other is created before the relapse period. Ensure only the event created during the
            # relapse period is included in the results, and events with different keyid combinations do not
            # interfere with one another.
            storage.insert_event(idea1)
            storage.insert_event(idea2)
            storage.threshold_set("ident1", thrtime, reltime, ttltime, label)
            storage.threshold_set("ident2", thrtime, reltime, ttltime, label)
            _threshold_save(idea1["ID"], "ident1", reltime + datetime.timedelta(seconds=200), target)
            _threshold_save(idea2["ID"], "ident2", reltime - datetime.timedelta(seconds=200), target)

            relapses = storage.search_relapsed_events(
                "test@domain.org",
                "low",
                ttltime + datetime.timedelta(seconds=300),
                target,
                False,
            )
            self.assertEqual(len(relapses), 1)
            count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds=300))
            self.assertEqual(count, 2)
            count = storage.thresholded_events_clean()
            self.assertEqual(count, 2)
            count = storage.delete_events()
            self.assertEqual(count, 2)

            # Test that events are not reported as relapsed when the relapse period is set to 0.
            storage.insert_event(idea1)
            storage.threshold_set("ident1", ttltime, ttltime, ttltime, label)
            _threshold_save(idea1["ID"], "ident1", ttltime, target)

            relapses = storage.search_relapsed_events("test@domain.org", "low", ttltime, target, False)
            self.assertEqual(len(relapses), 0)
            count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds=1))
            self.assertEqual(count, 1)
            count = storage.thresholded_events_clean()
            self.assertEqual(count, 1)
            count = storage.delete_events()
            self.assertEqual(count, 1)

    def test_14_search_event_ghosts(self):
        """
        Perform various event search tests.
        """
        self.maxDiff = None

        storage = self._get_clean_storage()

        idea_into = mentat.idea.internal.Idea(self.IDEA_RAW_1)
        storage.insert_event(idea_into)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {"dt_from": datetime.datetime(2012, 11, 3, 10, 0, 7)},
            qtype=mentat.services.eventstorage.QTYPE_SELECT_GHOST,
        )
        if self.verbose:
            pprint.pprint(ideas_from)
        self.assertEqual(ideas_count, 1)
        self.assertEqual(idea_into["ID"], ideas_from[0]["ID"])
        self.assertEqual(idea_into["DetectTime"], ideas_from[0]["DetectTime"])
        self.assertEqual(list(idea_into["Category"]), list(ideas_from[0]["Category"]))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
