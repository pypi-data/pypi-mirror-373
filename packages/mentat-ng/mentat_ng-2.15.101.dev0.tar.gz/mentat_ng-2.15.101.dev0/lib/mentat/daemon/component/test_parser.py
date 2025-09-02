#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.parser` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import Mock, call

import mentat.daemon.component.parser


class TestMentatDaemonParser(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.daemon.component.parser` module.
    """

    def setUp(self):
        self.obj = mentat.daemon.component.parser.ParserDaemonComponent()

    def test_01_basic(self):
        """Perform the basic operativity tests."""

        msg_raw = """{
           "Category" : [
              "Attempt.Login"
           ],
           "Target" : [
              {
                 "Proto" : [
                    "tcp",
                    "ssh"
                 ],
                 "IP4" : [
                    "195.113.165.128/25"
                 ],
                 "Port" : [
                    "22"
                 ],
                 "Anonymised" : true
              }
           ],
           "ID" : "4dd7cf5e-4a95-49f6-8f04-947de998012c",
           "WinStartTime" : "2016-06-21 11:55:02Z",
           "ConnCount" : 2,
           "Source" : [
              {
                 "IP4" : [
                    "188.14.166.39"
                 ]
              }
           ],
           "Note" : "SSH login attempt",
           "Node" : [
              {
                 "Type" : [
                    "Relay"
                 ],
                 "Name" : "cz.cesnet.mentat.warden_filer"
              },
              {
                 "SW" : [
                    "Kippo"
                 ],
                 "AggrWin" : "00:05:00",
                 "Name" : "cz.uhk.apate.cowrie",
                 "Type" : [
                    "Connection",
                    "Honeypot",
                    "Recon"
                 ]
              }
           ],
           "_Mentat" : {
              "StorageTime" : "2016-06-21T14:00:07Z"
           },
           "WinEndTime" : "2016-06-21 12:00:02Z",
           "Format" : "IDEA0",
           "DetectTime" : "2016-06-21 13:08:27Z"
        }"""

        daemon = Mock()
        self.obj.setup(daemon)

        result_a = self.obj.cbk_event_message_process(daemon, {"id": "msgid", "data": msg_raw})
        # pprint(result_a)
        # pprint(daemon.mock_calls)
        daemon.logger.debug.assert_has_calls(
            [
                call("Component 'parser': Parsing IDEA message from: 'msgid'"),
                call(
                    "Component 'parser': Parsed IDEA message '4dd7cf5e-4a95-49f6-8f04-947de998012c' from message file 'msgid'"
                ),
            ]
        )

        result_b = self.obj.cbk_event_message_update(daemon, result_a[1])
        self.assertEqual(result_b[0], daemon.FLAG_CONTINUE)
        # pprint(result_b)
        # pprint(daemon.mock_calls)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
