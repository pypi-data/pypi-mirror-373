#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

import datetime

import mentat.datatype.sqldb
import mentat.stats.idea

ideas_raw = [
    {
        "Format": "IDEA0",
        "ID": "msg01",
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
        "Node": [
            {
                "Name": "org.example.kippo",
                "Tags": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
            }
        ],
        "_Mentat": {"ResolvedAbuses": ["abuse@cesnet.cz"]},
    },
    {
        "Format": "IDEA0",
        "ID": "msg02",
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
        "_Mentat": {"ResolvedAbuses": ["abuse@cesnet.cz"]},
    },
    {
        "Format": "IDEA0",
        "ID": "msg03",
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
        "Node": [
            {
                "Name": "org.example.dionaea",
                "Tags": ["Protocol", "Honeypot"],
                "SW": ["Kippo"],
            }
        ],
        "_Mentat": {"ResolvedAbuses": ["abuse@cesnet.cz"]},
    },
    {
        "Format": "IDEA0",
        "ID": "msg04",
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
        "Node": [
            {
                "Name": "org.example.labrea",
                "Tags": ["Protocol", "Honeypot"],
                "SW": ["LaBrea"],
            }
        ],
        "_Mentat": {"ResolvedAbuses": ["abuse@cesnet.cz"]},
    },
    {
        "Format": "IDEA0",
        "ID": "msg06",
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

timestamp = 1485993600

stse1 = mentat.stats.idea.evaluate_events(ideas_raw)
stse2 = mentat.stats.idea.evaluate_events(ideas_raw)
stse3 = mentat.stats.idea.evaluate_events(ideas_raw)

stso1 = mentat.stats.idea.evaluate_events(ideas_raw)
stso2 = mentat.stats.idea.evaluate_events(ideas_raw)
stso3 = mentat.stats.idea.evaluate_events(ideas_raw)

stsi1 = mentat.stats.idea.evaluate_events(ideas_raw)
stsi2 = mentat.stats.idea.evaluate_events(ideas_raw)
stsi3 = mentat.stats.idea.evaluate_events(ideas_raw)

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

for _ in range(100000):
    result = mentat.stats.idea.aggregate_stat_groups([sts1, sts2, sts3])
