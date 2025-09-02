#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Benchmarking module for the :py:mod:`mentat.services.eventstorage` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import timeit

import mentat.const
import mentat.idea.internal
import mentat.services.eventstorage

# -------------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------------

IDEA_INTO = mentat.idea.internal.Idea(
    {
        "Format": "IDEA0",
        "ID": "4390fc3f-c753-4a3e-bc83-1b44f24baf75",
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
            "Impact": "System provides SDDP service and can be misused for massive DDoS attack",
            "EventClass": "vulnerable-config-ssdp",
            "EventSeverity": "low",
            "InspectionErrors": [
                "Demonstration error - first",
                "Demonstration error - second",
            ],
        },
    }
)

STORAGE = mentat.services.eventstorage.EventStorageService(
    dbname="mentat_utest", user="mentat", password="mentat", host="localhost", port=5432
)


# -------------------------------------------------------------------------------
# BENCHMARK TESTS
# -------------------------------------------------------------------------------


def b001():
    IDEA_INTO["ID"] = mentat.const.random_str(10)
    STORAGE.insert_event(IDEA_INTO)


COUNTER = 0
THRESHOLD = 1


def b002():
    global COUNTER
    IDEA_INTO["ID"] = mentat.const.random_str(10)
    STORAGE.insert_event_bulkci(IDEA_INTO)
    COUNTER += 1
    if not COUNTER % THRESHOLD:
        STORAGE.commit_bulk()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    ITERATIONS = 100000
    DT_START = datetime.datetime.now()

    print(f"\n BENCHMARKING MENTAT.EVENTSTORAGE MODULE (v{mentat.__version__})")
    print(f" {DT_START!s}\n")

    print("=" * 84)
    print(" {:22s} | {:16s} | {:20s} | {:20s}".format("Name", "Iterations (#)", "Duration (s)", "Speed (#/s)"))
    print("=" * 84)
    FORMAT_PTRN = " {:22s} | {:16,d} | {:20.10f} | {:15,.3f}"

    # ---------------------------------------------------------------------------

    STORAGE.database_drop()
    STORAGE.database_create()

    RESULT = timeit.timeit("b001()", number=ITERATIONS, setup="from __main__ import b001")
    SPEED = ITERATIONS / RESULT
    print(FORMAT_PTRN.format("commit", ITERATIONS, RESULT, SPEED))

    # ---------------------------------------------------------------------------

    for thresh in (1, 10, 100, 250, 500, 750, 1000, 1250, 1500, 1750, 2000):
        COUNTER = 0
        THRESHOLD = thresh
        STORAGE.database_drop()
        STORAGE.database_create()

        RESULT = timeit.timeit("b002()", number=ITERATIONS, setup="from __main__ import b002")
        SPEED = ITERATIONS / RESULT
        print(FORMAT_PTRN.format(f"bulk commit ({THRESHOLD})", ITERATIONS, RESULT, SPEED))

    # ---------------------------------------------------------------------------

    print("=" * 84)
    DT_STOP = datetime.datetime.now()
    print(f" {DT_STOP!s}")
    print(f" Duration: {DT_STOP - DT_START!s}\n")

    STORAGE.database_drop()
    STORAGE.close()
