#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.filer` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import shutil
import unittest
from unittest.mock import call

from mentat.daemon.component.filer import FilerDaemonComponent
from mentat.daemon.component.testsuite import DaemonComponentTestCase

#
# Global variables
#
DIRQ = "/tmp/filer.tmpd"  # Name of the test directory queue
DIRD = "/tmp/filer.out.tmpd"  # Name of the output test directory queue


class TestMentatDaemonFiler(DaemonComponentTestCase):
    """
    Unit test class for testing the :py:mod:`mentat.daemon.component.filer` module.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.component = FilerDaemonComponent()

        try:
            qdir_name = DIRQ
            os.mkdir(qdir_name)
        except FileExistsError:
            pass
        try:
            qdir_name = DIRD
            os.mkdir(qdir_name)
        except FileExistsError:
            pass

    def tearDown(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        shutil.rmtree(DIRQ)
        shutil.rmtree(DIRD)

    def _get_daemon_mock(self):
        return self._build_daemon_mock(
            [
                None,
                None,
                3,
            ],
            # daemon.cc(daemon.CORE_FILEQUEUE)
            [
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
                {
                    "dir_next_queue": DIRD,
                    "dir_queue": DIRQ,
                    "queue_out_limit": 100,
                    "queue_out_wait": 3,
                    "queue_perms": 0o775,
                },
            ],
        )

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._get_daemon_mock()

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.dbgout.assert_has_calls(
            [
                call("[STATUS] Component 'filer': Event 'queue_check' mapped to 'queue_check'"),
                call("[STATUS] Component 'filer': Event 'message_enqueue' mapped to 'message_enqueue'"),
                call("[STATUS] Component 'filer': Event 'message_next' mapped to 'message_next'"),
                call("[STATUS] Component 'filer': Event 'message_update' mapped to 'message_update'"),
                call("[STATUS] Component 'filer': Event 'message_commit' mapped to 'message_commit'"),
                call("[STATUS] Component 'filer': Event 'message_banish' mapped to 'message_banish'"),
                call("[STATUS] Component 'filer': Event 'message_cancel' mapped to 'message_cancel'"),
                call("[STATUS] Component 'filer': Event 'message_dispatch' mapped to 'message_dispatch'"),
                call("[STATUS] Component 'filer': Event 'message_duplicate' mapped to 'message_duplicate'"),
            ]
        )
        daemon.logger.debug.assert_has_calls([])
        daemon.logger.info.assert_has_calls(
            [
                call("[STATUS] Component 'filer': Using directory '/tmp/filer.tmpd' as input message queue"),
                call("[STATUS] Component 'filer': Using '3' as wait time for empty input message queue"),
                call("[STATUS] Component 'filer': Using directory '/tmp/filer.out.tmpd' as output message queue"),
                call("[STATUS] Component 'filer': Using '100' as output message queue limit"),
                call("[STATUS] Component 'filer': Using '3' as wait time for full output message queue"),
            ]
        )

    def test_02_enqueue(self):
        """
        Perform the test of 'cbk_event_message_enqueue'.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._get_daemon_mock()

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST02: Daemon mock calls after component setup", daemon.mock_calls)

        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        (flag1, args1) = self.component.cbk_event_message_enqueue(daemon, {"data": '{"test1": 1, "test2": 2}'})
        self._verbose_print("TEST02: Daemon mock calls after first message enqueue", daemon.mock_calls)
        (flag2, args2) = self.component.cbk_event_message_enqueue(daemon, {"data": ""})
        self._verbose_print("TEST02: Daemon mock calls after second message enqueue", daemon.mock_calls)

        daemon.logger.debug.assert_has_calls(
            [
                call("Component 'filer': Adding new message into the queue"),
                call("Component 'filer': Adding new message into the queue"),
            ]
        )
        daemon.logger.info.assert_has_calls(
            [
                call("Component 'filer': Added new message into the queue as '{}'".format(args1["id"])),
                call("Component 'filer': Added new message into the queue as '{}'".format(args2["id"])),
            ]
        )

    def test_03_next(self):
        """
        Perform the test of 'cbk_event_message_next'.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._get_daemon_mock()

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST03: Daemon mock calls after component setup", daemon.mock_calls)

        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        msg01 = {"data": '{"test1": 1, "test2": 2}'}
        msg02 = {"data": ""}

        (flag1, args1) = self.component.cbk_event_message_enqueue(daemon, msg01)
        (flag2, args2) = self.component.cbk_event_message_enqueue(daemon, msg02)
        self._verbose_print(
            "TEST03: Daemon mock calls after all message enqueue calls",
            daemon.mock_calls,
        )

        (flag3, args3) = self.component.cbk_event_message_next(daemon)
        self._verbose_print("TEST03: Daemon mock calls after first message next call", daemon.mock_calls)
        (flag4, args4) = self.component.cbk_event_message_next(daemon)
        self._verbose_print(
            "TEST03: Daemon mock calls after second message next call",
            daemon.mock_calls,
        )
        (flag5, args5) = self.component.cbk_event_message_next(daemon)
        self._verbose_print("TEST03: Daemon mock calls after all message next calls", daemon.mock_calls)

        daemon.logger.debug.assert_has_calls(
            [
                call("Component 'filer': Adding new message into the queue"),
                call("Component 'filer': Adding new message into the queue"),
                call("Component 'filer': Fetching a next message from queue"),
                call("Component 'filer': Fetching a next message from queue"),
                call("Component 'filer': Fetched message '{}'".format(args1["id"])),
                call("Component 'filer': Fetching a next message from queue"),
            ],
            any_order=True,
        )
        daemon.logger.info.assert_has_calls(
            [
                call("Component 'filer': Added new message into the queue as '{}'".format(args1["id"])),
                call("Component 'filer': Added new message into the queue as '{}'".format(args2["id"])),
                call("Component 'filer': Scheduling next queue check after '3' seconds"),
            ]
        )
        daemon.queue.schedule.assert_has_calls(
            [
                call("message_banish", {"id": args2["id"]}),
                call("message_process", {"id": args1["id"], "data": msg01["data"]}),
                call("message_next"),
            ],
            any_order=True,
        )

    def test_04_update(self):
        """
        Perform the test of 'cbk_event_message_update'.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._get_daemon_mock()

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST04: Daemon mock calls after component setup", daemon.mock_calls)

        # Reset mock, so that further testing is more simple.
        daemon.reset_mock()

        msg01 = {"data": '{"test1": 1, "test2": 2}'}

        (flag1, args1) = self.component.cbk_event_message_enqueue(daemon, msg01)
        self._verbose_print(
            "TEST04: Daemon mock calls after all message enqueue calls",
            daemon.mock_calls,
        )

        (flag2, args2) = self.component.cbk_event_message_next(daemon)
        self._verbose_print("TEST04: Daemon mock calls after first message next call", daemon.mock_calls)

        (flag3, args3) = self.component.cbk_event_message_update(daemon, args1)
        self._verbose_print("TEST04: Daemon mock calls after message update call", daemon.mock_calls)

        (flag3, args3) = self.component.cbk_event_message_update(daemon, {"id": "bogus", "data": {}})
        self._verbose_print(
            "TEST04: Daemon mock calls after invalid message update call",
            daemon.mock_calls,
        )

        daemon.logger.debug.assert_has_calls(
            [
                call("Component 'filer': Adding new message into the queue"),
                call("Component 'filer': Fetching a next message from queue"),
                call("Component 'filer': Fetched message '{}'".format(args1["id"])),
                call("Component 'filer': Updating message '{}'".format(args1["id"])),
                call("Component 'filer': Updating message 'bogus'"),
            ]
        )
        daemon.logger.info.assert_has_calls(
            [call("Component 'filer': Added new message into the queue as '{}'".format(args1["id"]))]
        )
        daemon.logger.error.assert_has_calls(
            [
                call(
                    "Component 'filer': Unable to update message 'bogus': [Errno 2] No such file or directory: '/tmp/filer.tmpd/pending/bogus'"
                )
            ]
        )
        daemon.queue.schedule.assert_has_calls(
            [
                call(
                    "message_process",
                    {"id": args1["id"], "data": '{"test1": 1, "test2": 2}'},
                ),
                call("message_next"),
            ]
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
