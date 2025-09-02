#!/usr/bin/env python3
# pylint: disable=protected-access
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Module for common data used in multiple test files.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from mentat.idea.internal import Idea

EVENTS_RAW = [
    {
        "Format": "IDEA0",
        "ID": "msg01",
        "DetectTime": "2018-01-01T12:00:00Z",
        "Category": ["Fraud.Phishing"],
        "Description": "Synthetic example 01",
        "ConnCount": 1,
        "FlowCount": 30,
        "PacketCount": 50,
        "ByteCount": 4560,
        "ByteCountDropped": 100,
        "AvgPacketSize": 93,
        "Ref": ["https://cesnet.cz"],
        "Credentials": [{"Password": "", "Username": "sa"}],
        "Source": [
            {
                "ClockSkew": -123,
                "InFlowCount": 30,
                "OutFlowCount": 30,
                "InByteCount": 4560,
                "OutByteCount": 4560,
                "IP4": ["10.0.2.1"],
                "Proto": ["ssh"],
            },
            {
                "IP6": ["2001:db8::ff00:42:0/112"],
                "Proto": ["telnet"],
            },
        ],
        "Target": [
            {
                "IP4": ["10.2.2.0/24"],
                "IP6": ["2001:ffff::ff00:42:0/112"],
                "Proto": ["https", "http"],
                "Port": [80, 443],
                "Interface": [45],
                "Hostname": ["aaa.cesnet.cz", "bbb.cesnet.cz"],
                "Ref": ["https://ces.net"],
                "ServiceName": "Apache",
                "ServiceVersion": "2.4.53",
                "X509ExpiredTime": "2020-11-06T23:59:00Z",
            }
        ],
        "Node": [{"Name": "org.example.kippo_honey", "SW": ["Kippo"]}],
        "_Mentat": {
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "EventClass": "test-event-class",
            "EventSeverity": "low",
            "TargetClass": "fraud-phishing-target",
            "TargetSeverity": "medium",
            "TargetAbuses": ["abuse@cesnet.cz"],
        },
    },
    {
        "Format": "IDEA0",
        "ID": "msg02",
        "DetectTime": "2018-01-01T13:00:00Z",
        "Category": ["Recon.Scanning"],
        "Description": "Synthetic example 02",
        "ConnCount": 42,
        "Source": [
            {
                "IP4": [
                    "10.0.1.2-10.0.1.5",
                    "10.0.0.0/25",
                    "10.0.2.1",
                ],
                "Port": [22],
            },
            {
                "IP4": [
                    "10.0.2.1",
                ],
                "Port": [23],
            },
        ],
        "Target": [{"IP4": ["11.2.2.0/24"], "IP6": ["2004:ffff::ff00:42:0/112"]}],
        "Node": [{"Name": "org.example.dionaea", "SW": ["Dionaea"]}],
        "Note": "Test note containing ; CSV delimiter.",
        "_Mentat": {
            "ResolvedAbuses": ["abuse@cesnet.cz"],
            "EventClass": "recon-scanning",
            "EventSeverity": "low",
            "TargetClass": "recon-scanning-target",
            "TargetSeverity": "low",
            "TargetAbuses": ["abuse@cesnet.cz"],
        },
    },
]

EVENTS_OBJ = list(map(Idea, EVENTS_RAW))
