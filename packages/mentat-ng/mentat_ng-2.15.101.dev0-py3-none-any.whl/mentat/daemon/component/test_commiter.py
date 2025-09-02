#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.commiter` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.daemon.component.commiter import CommiterDaemonComponent
from mentat.daemon.component.testsuite import DaemonComponentTestCase


class TestMentatDaemonCommiter(DaemonComponentTestCase):
    """
    Unit test class for testing the :py:mod:`mentat.daemon.component.commiter` module.
    """

    results = {
        "message01": {
            "Category": ["Attempt.Login"],
            "DetectTime": "2016-06-21T13:08:27Z",
            "Format": "IDEA0",
            "ID": "message01",
            "Node": [
                {
                    "Name": "cz.uhk.apate.cowrie",
                    "SW": ["Kippo"],
                    "Type": ["Connection", "Honeypot"],
                }
            ],
            "Note": "SSH login attempt",
            "Source": [{"IP4": ["188.14.166.39"]}],
            "Target": [{"IP4": ["195.113.165.128/25"], "Port": [22]}],
            "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
        }
    }

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.component = CommiterDaemonComponent()

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock([])

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.logger.assert_has_calls([])

    def test_02_process(self):
        """
        Perform processing test.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock([])

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.logger.assert_has_calls([])
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST02: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results)

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST02: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results)

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST02: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results)

        self._verbose_print("TEST02: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'commiter': Scheduling message commit for 'message01'"),
                call.debug("Component 'commiter': Scheduling message commit for 'message01'"),
                call.debug("Component 'commiter': Scheduling message commit for 'message01'"),
            ]
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
