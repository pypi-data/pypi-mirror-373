#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.inspector` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.daemon.component.inspector import InspectorDaemonComponent
from mentat.daemon.component.testsuite import DaemonComponentTestCase


class TestMentatDaemonInspector(DaemonComponentTestCase):
    """
    Unit test class for testing the :py:mod:`mentat.daemon.component.inspector` module.
    """

    results = {
        "tag": {
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
                "TestTag": {"ValueA1": "A2", "ValueA2": ["A4", "A5"]},
                "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
            }
        },
        "set": {
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
                "TestTag": {"ValueA1": 1466910407, "ValueA2": [1466514007, 1466517607]},
                "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
            }
        },
        "report": {
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
        },
        "drop": {
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
        },
        "dispatch": {
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
        },
        "duplicate": {
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
        },
        "log": {
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
        },
    }

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.component = InspectorDaemonComponent()

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempts"',
                        "actions": [
                            {
                                "action": "tag",
                                "args": {"path": "TestA.ValueA1", "value": "A1"},
                            }
                        ],
                    },
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "actions": [
                            {
                                "action": "tag",
                                "args": {
                                    "path": "TestB.ValueB1",
                                    "value": "B3",
                                    "overwrite": False,
                                },
                            }
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [
                    {
                        "action": "tag",
                        "args": {
                            "path": "TestB.ValueB2[*]",
                            "value": "B3",
                            "unique": True,
                        },
                    }
                ],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.c.assert_has_calls(
            [
                call("inspection_rules"),
                call("add_event_class_rules"),
                call("fallback_actions"),
            ]
        )
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'Note == \"SSH login attempts\"':'tag' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule 'Note == \"SSH login attempts\"' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'Note == \"SSH login attempt\"':'tag' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule 'Note == \"SSH login attempt\"' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Fallback action 'tag' successfully loaded"),
            ]
        )

    def test_02_tag(self):
        """
        Perform tests of 'tag' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [
                            {
                                "action": "tag",
                                "name": "action_01",
                                "args": {"path": "TestTag.ValueA1", "value": "A1"},
                            },
                            {
                                "action": "tag",
                                "name": "action_02",
                                "args": {"path": "TestTag.ValueA1", "value": "A2"},
                            },
                            {
                                "action": "tag",
                                "name": "action_03",
                                "args": {
                                    "path": "TestTag.ValueA1",
                                    "value": "A3",
                                    "overwrite": False,
                                },
                            },
                            {
                                "action": "tag",
                                "name": "action_04",
                                "args": {
                                    "path": "TestTag.ValueA2[*]",
                                    "value": "A4",
                                    "unique": True,
                                },
                            },
                            {
                                "action": "tag",
                                "name": "action_05",
                                "args": {
                                    "path": "TestTag.ValueA2[*]",
                                    "value": "A5",
                                    "unique": True,
                                },
                            },
                            {
                                "action": "tag",
                                "name": "action_06",
                                "args": {
                                    "path": "TestTag.ValueA2[*]",
                                    "value": "A5",
                                    "unique": True,
                                },
                            },
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST02: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_02' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_03' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_04' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_05' successfully loaded"
                ),
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_06' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
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
            self._assert_result(result[1], self.results["tag"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST02: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["tag"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST02: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["tag"])

        self._verbose_print("TEST02: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A1' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A2' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A3' key already exists, not overwriting (O:False U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A4' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' value already exists, not inserting (O:True U:True)"
                ),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A1' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A2' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A3' key already exists, not overwriting (O:False U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A4' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' value already exists, not inserting (O:True U:True)"
                ),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A1' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A2' key successfully set (O:True U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA1':'A3' key already exists, not overwriting (O:False U:False)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A4' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' key successfully set (O:True U:True)"
                ),
                call.debug(
                    "Component 'inspector': Tag - Message 'message01' path 'TestTag.ValueA2[*]':'A5' value already exists, not inserting (O:True U:True)"
                ),
            ]
        )

        # daemon.queue.schedule_after.assert_called_with(10, 'message_next')

    # def test_03_set(self):
    # """
    # Perform tests of 'set' action.
    # """
    # self.maxDiff = None

    ## Prepare mock object representing external daemon object.
    # daemon = self._build_daemon_mock([

    ## daemon.c(self.inspection_rules_key)
    # [
    # {
    #'rule': 'Note = "SSH login attempt"',
    #'name': 'rule_01',
    #'actions': [
    # {'action': 'set', 'name': 'action_01', 'args': {'path': 'TestTag.ValueA1',    'expression': '_Mentat.StorageTime + 3600'}},
    # {'action': 'set', 'name': 'action_02', 'args': {'path': 'TestTag.ValueA1',    'expression': '_Mentat.StorageTime + 400000'}},
    # {'action': 'set', 'name': 'action_03', 'args': {'path': 'TestTag.ValueA1',    'expression': '_Mentat.StorageTime + 800000', 'overwrite': False}},
    # {'action': 'set', 'name': 'action_04', 'args': {'path': 'TestTag.ValueA2[*]', 'expression': '_Mentat.StorageTime + 3600', 'unique': True}},
    # {'action': 'set', 'name': 'action_05', 'args': {'path': 'TestTag.ValueA2[*]', 'expression': '_Mentat.StorageTime + 7200', 'unique': True}},
    # {'action': 'set', 'name': 'action_06', 'args': {'path': 'TestTag.ValueA2[*]', 'expression': '_Mentat.StorageTime + 7200', 'unique': True}},
    # ]
    # },
    # ],

    ## daemon.c(self.fallback_actions_key)
    # []
    # ])

    ## Setup daemon component.
    # self.component.setup(daemon)
    # self._verbose_print("TEST03: Daemon mock calls after component setup", daemon.mock_calls)
    # daemon.logger.info.assert_has_calls([
    # call("Inspection rule action 'rule_01':'action_01' successfully loaded"),
    # call("Inspection rule action 'rule_01':'action_02' successfully loaded"),
    # call("Inspection rule action 'rule_01':'action_03' successfully loaded"),
    # call("Inspection rule action 'rule_01':'action_04' successfully loaded"),
    # call("Inspection rule action 'rule_01':'action_05' successfully loaded"),
    # call("Inspection rule action 'rule_01':'action_06' successfully loaded"),
    # call("Inspection rule 'rule_01' successfully loaded"),
    # ])
    ## Reset mock, so that further testing is more simple.
    # daemon.reset_mock()

    ## Attempt to process the message and analyze the result.
    # for tmsg in self.messages:
    # result = self.component.cbk_event_message_process(daemon, {'id': tmsg['id'], 'idea_id': tmsg['id'], 'idea': tmsg['raw']})
    # self._verbose_print("TEST03: Result after processing JSON raw message '{}'".format(tmsg['id']), result)
    # self._assert_result(result[1], self.results['set'])

    # result = self.component.cbk_event_message_process(daemon, {'id': tmsg['id'], 'idea_id': tmsg['id'], 'idea': tmsg['lite']})
    # self._verbose_print("TEST03: Result after processing idea.lite message '{}'".format(tmsg['id']), result)
    # self._assert_result(result[1], self.results['set'])

    # result = self.component.cbk_event_message_process(daemon, {'id': tmsg['id'], 'idea_id': tmsg['id'], 'idea': tmsg['internal']})
    # self._verbose_print("TEST03: Result after processing mentat.idea.internal message '{}'".format(tmsg['id']), result)
    # self._assert_result(result[1], self.results['set'])

    # self._verbose_print("TEST03: Daemon mock calls after message processing", daemon.mock_calls)

    # daemon.logger.assert_has_calls([
    # call.info("Inspecting message 'message01':'message01'"),
    # call.info("Message 'message01':'message01' matched inspection rule 'rule_01'"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 400000'=>1466910407 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 800000'=>1467310407 key already exists, not overwriting (O:False U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 value already exists, not inserting (O:True U:True)"),

    # call.info("Inspecting message 'message01':'message01'"),
    # call.info("Message 'message01':'message01' matched inspection rule 'rule_01'"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 400000'=>1466910407 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 800000'=>1467310407 key already exists, not overwriting (O:False U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 value already exists, not inserting (O:True U:True)"),

    # call.info("Inspecting message 'message01':'message01'"),
    # call.info("Message 'message01':'message01' matched inspection rule 'rule_01'"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 400000'=>1466910407 key successfully set (O:True U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA1':'_Mentat.StorageTime + 800000'=>1467310407 key already exists, not overwriting (O:False U:False)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 3600'=>1466514007 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 key successfully set (O:True U:True)"),
    # call.debug("Set - Message 'message01' path 'TestTag.ValueA2[*]':'_Mentat.StorageTime + 7200'=>1466517607 value already exists, not inserting (O:True U:True)")
    # ])

    def test_04_report(self):
        """
        Perform tests of 'report' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [
                            {
                                "action": "report",
                                "name": "action_01",
                                "args": {
                                    "to": "recipient@organization.com",
                                    "from": "sender@organization.com",
                                    "subject": "Inspection alert",
                                    "report_type": "inspection_alert",
                                },
                            }
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST04: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST04: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["report"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST04: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["report"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST04: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["report"])

        self._verbose_print("TEST04: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Report - Message 'message01' to 'recipient@organization.com' with subject 'Inspection alert'"
                ),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Report - Message 'message01' to 'recipient@organization.com' with subject 'Inspection alert'"
                ),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug(
                    "Component 'inspector': Report - Message 'message01' to 'recipient@organization.com' with subject 'Inspection alert'"
                ),
            ]
        )

    def test_05_drop(self):
        """
        Perform tests of 'drop' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [{"action": "drop", "name": "action_01"}],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST05: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST05: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["drop"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST05: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["drop"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST05: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["drop"])

        self._verbose_print("TEST05: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Drop - Message 'message01':'message01': 'Inspection rule matched'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Drop - Message 'message01':'message01': 'Inspection rule matched'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Drop - Message 'message01':'message01': 'Inspection rule matched'"),
            ]
        )

    def test_06_dispatch(self):
        """
        Perform tests of 'dispatch' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [
                            {
                                "action": "dispatch",
                                "name": "action_01",
                                "args": {"queue_tgt": "/var/tmp"},
                            }
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST06: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST06: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["dispatch"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST06: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["dispatch"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST06: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["dispatch"])

        self._verbose_print("TEST06: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Dispatch - Message 'message01' to target queue '/var/tmp'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Dispatch - Message 'message01' to target queue '/var/tmp'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Dispatch - Message 'message01' to target queue '/var/tmp'"),
            ]
        )

        daemon.queue.assert_has_calls(
            [
                call.schedule(
                    "message_dispatch",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
                call.schedule(
                    "message_dispatch",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
                call.schedule(
                    "message_dispatch",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
            ]
        )

    def test_06_duplicate(self):
        """
        Perform tests of 'duplicate' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [
                            {
                                "action": "duplicate",
                                "name": "action_01",
                                "args": {"queue_tgt": "/var/tmp"},
                            }
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST06: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST06: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["duplicate"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST06: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["duplicate"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST06: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["duplicate"])

        self._verbose_print("TEST06: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Duplicate - Message 'message01' to target queue '/var/tmp'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Duplicate - Message 'message01' to target queue '/var/tmp'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.debug("Component 'inspector': Duplicate - Message 'message01' to target queue '/var/tmp'"),
            ]
        )

        daemon.queue.assert_has_calls(
            [
                call.schedule(
                    "message_duplicate",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
                call.schedule(
                    "message_duplicate",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
                call.schedule(
                    "message_duplicate",
                    {
                        "queue_tgt": "/var/tmp",
                        "idea_id": "message01",
                        "id": "message01",
                    },
                ),
            ]
        )

    def test_07_log(self):
        """
        Perform tests of 'log' action.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.inspection_rules_key)
                [
                    {
                        "rule": 'Note == "SSH login attempt"',
                        "name": "rule_01",
                        "actions": [
                            {
                                "action": "log",
                                "name": "action_01",
                                "args": {"label": "TEST LABEL"},
                            }
                        ],
                    },
                ],
                # daemon.c(self.add_event_class_rules_key)
                False,
                # daemon.c(self.fallback_actions_key)
                [],
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST07: Daemon mock calls after component setup", daemon.mock_calls)
        daemon.logger.info.assert_has_calls(
            [
                call(
                    "[STATUS] Component 'inspector': Inspection rule action 'rule_01':'action_01' successfully loaded"
                ),
                call("[STATUS] Component 'inspector': Inspection rule 'rule_01' successfully loaded"),
            ]
        )
        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        # Attempt to process the message and analyze the result.
        for tmsg in self.messages:
            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["raw"]}
            )
            self._verbose_print(
                "TEST07: Result after processing JSON raw message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["log"])

            result = self.component.cbk_event_message_process(
                daemon, {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["lite"]}
            )
            self._verbose_print(
                "TEST07: Result after processing idea.lite message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["log"])

            result = self.component.cbk_event_message_process(
                daemon,
                {"id": tmsg["id"], "idea_id": tmsg["id"], "idea": tmsg["internal"]},
            )
            self._verbose_print(
                "TEST07: Result after processing mentat.idea.internal message '{}'".format(tmsg["id"]),
                result,
            )
            self._assert_result(result[1], self.results["log"])

        self._verbose_print("TEST07: Daemon mock calls after message processing", daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.warning("Component 'inspector': Log - Message 'message01':'message01': 'TEST LABEL'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.warning("Component 'inspector': Log - Message 'message01':'message01': 'TEST LABEL'"),
                call.debug("Component 'inspector': Inspecting message 'message01':'message01'"),
                call.info("Component 'inspector': Message 'message01':'message01' matched inspection rule 'rule_01'"),
                call.warning("Component 'inspector': Log - Message 'message01':'message01': 'TEST LABEL'"),
            ]
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
