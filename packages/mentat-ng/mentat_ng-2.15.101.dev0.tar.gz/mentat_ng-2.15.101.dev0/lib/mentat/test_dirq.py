#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing :py:mod:`mentat.dirq` module.
"""

import os
import shutil
import unittest

import mentat.dirq

#
# Global variables
#
DIRQ = "/tmp/dirq.tmpd"  # Name of the test directory input queue
DIRD = "/tmp/dirq.out.tmpd"  # Name of the test directory output queue


class TestDirectoryQueue(unittest.TestCase):
    """
    Unit test class for testing :py:class:`mentat.dirq.DirectoryQueue` module.
    """

    def setUp(self):
        try:
            qdir_name = DIRQ
            os.mkdir(qdir_name)
            ddir_name = DIRD
            os.mkdir(ddir_name)
        except FileExistsError:
            pass

    def tearDown(self):
        shutil.rmtree(DIRQ)
        shutil.rmtree(DIRD)

    def test_01_basic(self):
        """
        Perform the basic operativity tests.
        """
        dqh = mentat.dirq.DirectoryQueue(DIRQ, dir_next_queue=DIRD)

        # Check that all necessary subdirectories were created
        self.assertTrue(os.path.isdir(os.path.join(DIRQ, "incoming")))
        self.assertTrue(os.path.isdir(os.path.join(DIRQ, "pending")))
        self.assertTrue(os.path.isdir(os.path.join(DIRQ, "errors")))
        self.assertTrue(os.path.isdir(os.path.join(DIRQ, "tmp")))
        self.assertTrue(os.path.isdir(os.path.join(DIRD, "incoming")))
        self.assertTrue(os.path.isdir(os.path.join(DIRD, "pending")))
        self.assertTrue(os.path.isdir(os.path.join(DIRD, "errors")))
        self.assertTrue(os.path.isdir(os.path.join(DIRD, "tmp")))

        self.assertTrue(os.path.isdir(DIRD))

        msgid_01 = dqh.enqueue("TEST MESSAGE")
        self.assertTrue(msgid_01)
        self.assertEqual(dqh.count_incoming(), 1)
        self.assertEqual(dqh.count_pending(), 0)
        self.assertEqual(dqh.count_errors(), 0)
        self.assertEqual(dqh.count_done(), 0)
        (xid, xdata) = dqh.next()
        self.assertEqual(xid, msgid_01)
        self.assertEqual(xdata, "TEST MESSAGE")
        self.assertEqual(dqh.count_incoming(), 0)
        self.assertEqual(dqh.count_pending(), 1)
        self.assertEqual(dqh.count_errors(), 0)
        self.assertEqual(dqh.count_done(), 0)
        dqh.banish(msgid_01)
        self.assertEqual(dqh.count_incoming(), 0)
        self.assertEqual(dqh.count_pending(), 0)
        self.assertEqual(dqh.count_errors(), 1)
        self.assertEqual(dqh.count_done(), 0)
        msgid_02 = dqh.enqueue("TEST MESSAGE")
        msgid_03 = dqh.enqueue("TEST MESSAGE")
        self.assertEqual(dqh.count_incoming(), 2)
        self.assertEqual(dqh.count_pending(), 0)
        self.assertEqual(dqh.count_errors(), 1)
        self.assertEqual(dqh.count_done(), 0)
        (xid, xdata) = dqh.next()
        (xid, xdata) = dqh.next()
        self.assertEqual(dqh.count_incoming(), 0)
        self.assertEqual(dqh.count_pending(), 2)
        self.assertEqual(dqh.count_errors(), 1)
        self.assertEqual(dqh.count_done(), 0)
        dqh.commit(msgid_02)
        self.assertEqual(dqh.count_incoming(), 0)
        self.assertEqual(dqh.count_pending(), 1)
        self.assertEqual(dqh.count_errors(), 1)
        self.assertEqual(dqh.count_done(), 1)
        dqh.commit(msgid_03)
        self.assertEqual(dqh.count_incoming(), 0)
        self.assertEqual(dqh.count_pending(), 0)
        self.assertEqual(dqh.count_errors(), 1)
        self.assertEqual(dqh.count_done(), 2)
        msgid_04 = dqh.enqueue("TEST MESSAGE A")
        msgid_05 = dqh.enqueue("TEST MESSAGE B")
        msgid_06 = dqh.enqueue("TEST MESSAGE C")
        (xid, xdata) = dqh.next()
        (xid, xdata) = dqh.next()
        (xid, xdata) = dqh.next()
        dqh.update(msgid_04, "TEST MESSAGE D")
        dqh.update(msgid_05, "TEST MESSAGE E")
        dqh.update(msgid_06, "TEST MESSAGE F")
        self.assertEqual(dqh.reload(msgid_04), "TEST MESSAGE D")
        self.assertEqual(dqh.reload(msgid_05), "TEST MESSAGE E")
        self.assertEqual(dqh.reload(msgid_06), "TEST MESSAGE F")
        dqh.banish(msgid_04, {"error": "Something went really really wrong"})
        self.assertEqual(dqh.count_pending(), 2)
        self.assertEqual(dqh.count_errors(), 3)
        self.assertEqual(
            dqh._load_file(os.path.join(dqh.dir_errors, f"{msgid_04}.meta")),  # pylint: disable=protected-access
            '{\n    "error": "Something went really really wrong"\n}',
        )
        dqh.dispatch(msgid_05, "/tmp")
        self.assertEqual(dqh.count_pending(), 1)
        self.assertTrue(os.path.isfile(os.path.join("/tmp", msgid_05)))
        os.unlink(os.path.join("/tmp", msgid_05))
        dqh.duplicate(msgid_06, "/tmp")
        self.assertEqual(dqh.count_pending(), 1)
        self.assertTrue(os.path.isfile(os.path.join("/tmp", msgid_06)))
        os.unlink(os.path.join("/tmp", msgid_06))
        dqh.cancel(msgid_06)
        self.assertEqual(dqh.count_pending(), 0)
        self.assertEqual(dqh.count_errors(), 3)

    def test_02_paralel(self):
        """
        Perform paralel queue manager tests.
        """
        dq1 = mentat.dirq.DirectoryQueue(DIRQ)
        dq2 = mentat.dirq.DirectoryQueue(DIRQ)

        # msgid_01 = dq1.enqueue("TEST MESSAGE 1")
        # msgid_02 = dq2.enqueue("TEST MESSAGE 2")
        # msgid_03 = dq1.enqueue("TEST MESSAGE 3")
        # msgid_04 = dq2.enqueue("TEST MESSAGE 4")
        # msgid_05 = dq1.enqueue("TEST MESSAGE 5")
        # msgid_06 = dq2.enqueue("TEST MESSAGE 6")
        dq1.enqueue("TEST MESSAGE 1")
        dq2.enqueue("TEST MESSAGE 2")
        dq1.enqueue("TEST MESSAGE 3")
        dq2.enqueue("TEST MESSAGE 4")
        dq1.enqueue("TEST MESSAGE 5")
        dq2.enqueue("TEST MESSAGE 6")
        self.assertEqual(dq1.count_incoming(), 6)
        self.assertEqual(dq2.count_incoming(), 6)

        # (xid1, xdata1) = dq1.next()
        # (xid2, xdata2) = dq2.next()
        # (xid3, xdata3) = dq1.next()
        # (xid4, xdata4) = dq2.next()
        # (xid5, xdata5) = dq1.next()
        # (xid6, xdata6) = dq2.next()
        dq1.next()
        dq2.next()
        dq1.next()
        dq2.next()
        dq1.next()
        dq2.next()

        self.assertEqual(dq1.count_incoming(), 0)
        self.assertEqual(dq2.count_incoming(), 0)
        self.assertEqual(dq1.count_pending(), 6)
        self.assertEqual(dq2.count_pending(), 6)

        st1 = dq1.stats

        self.assertEqual(st1["cnt_dequeued"], 3)
        self.assertEqual(st1["cnt_skips"], 2)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
