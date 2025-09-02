#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

import copy
import difflib
import json
import os
import unittest
from pprint import pformat
from unittest.mock import Mock

import idea.lite

import pyzenkit

import mentat.daemon.piper
import mentat.idea.internal

messages_raw = [
    {
        "ID": "message01",
        "Category": ["Attempt.Login"],
        "Target": [{"IP4": ["195.113.165.128/25"], "Port": [22]}],
        "Source": [{"IP4": ["188.14.166.39"]}],
        "Note": "SSH login attempt",
        "Node": [
            {
                "SW": ["Kippo"],
                "Name": "cz.uhk.apate.cowrie",
                "Type": ["Connection", "Honeypot"],
            }
        ],
        "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
        "Format": "IDEA0",
        "DetectTime": "2016-06-21T13:08:27Z",
    }
]


def _load_messages():
    result = []
    for msg in messages_raw:
        msgid = msg["ID"]
        msgc = copy.deepcopy(msg)
        result.append(
            {
                "id": msgid,
                "raw": msgc,
                "lite": idea.lite.Idea(msgc),
                "internal": mentat.idea.internal.Idea(msgc),
            }
        )
    return result


class DaemonComponentTestCase(unittest.TestCase):
    def setUp(self):
        #
        # Turn on more verbose output, which includes print-out of constructed
        # objects. This will really clutter your console, usable only for test
        # debugging.
        #
        self.verbose = False

        cdir_path = os.path.dirname(os.path.realpath(__file__))
        self.core_config = pyzenkit.jsonconf.config_load_dir(
            os.path.realpath(os.path.join(cdir_path, "../../../../conf/core"))
        )

        # Process all test messages into expected data structure.
        self.messages = _load_messages()

    def _verbose_print(self, label, data):
        """
        Helper method, print additional information in verbose mode.
        """
        if self.verbose:
            print(f"{label}\n{pformat(data)}\n")

    def _assert_result(self, result, expected_results):
        """
        Compare given result with expected results.
        """
        res = result["idea"]
        if isinstance(res, idea.base.IdeaBase):
            res = json.dumps(res, indent=4, sort_keys=True, default=res.json_default)
        else:
            res = json.dumps(res, indent=4, sort_keys=True)
        exp = expected_results[result["idea_id"]]
        exp = json.dumps(exp, indent=4, sort_keys=True)
        self.assertEqual(res, exp, list(difflib.context_diff(res.split("\n"), exp.split("\n"))))

    def _build_daemon_mock(self, config_list, core_config_list=None):
        """
        Helper method, build and return daemon mock object.
        """
        daemon = Mock(
            config=self.core_config,
            CORE_FILEQUEUE=mentat.daemon.piper.PiperDaemon.CORE_FILEQUEUE,
            CONFIG_QUEUE_IN_DIR=mentat.daemon.piper.PiperDaemon.CONFIG_QUEUE_IN_DIR,
            CONFIG_QUEUE_IN_WAIT=mentat.daemon.piper.PiperDaemon.CONFIG_QUEUE_IN_WAIT,
            CONFIG_QUEUE_OUT_DIR=mentat.daemon.piper.PiperDaemon.CONFIG_QUEUE_OUT_DIR,
            CONFIG_QUEUE_OUT_LIMIT=mentat.daemon.piper.PiperDaemon.CONFIG_QUEUE_OUT_LIMIT,
            CONFIG_QUEUE_OUT_WAIT=mentat.daemon.piper.PiperDaemon.CONFIG_QUEUE_OUT_WAIT,
            is_done=lambda: False,
        )
        daemon.attach_mock(
            Mock(
                # Define required configuration values in order they are required
                # from daemon instance (ussually in setup() method).
                side_effect=config_list
            ),
            "c",
        )
        if core_config_list:
            daemon.attach_mock(
                Mock(
                    # Define required configuration values in order they are required
                    # from daemon instance (ussually in setup() method).
                    side_effect=core_config_list
                ),
                "cc",
            )
        return daemon
