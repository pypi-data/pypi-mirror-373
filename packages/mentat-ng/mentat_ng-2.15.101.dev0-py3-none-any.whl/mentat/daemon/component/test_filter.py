#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.daemon.component.filter` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from unittest.mock import call

from mentat.daemon.component.filter import FilterDaemonComponent
from mentat.daemon.component.testsuite import DaemonComponentTestCase


class TestMentatDaemonFilter(DaemonComponentTestCase):
    """
    Unit test class for testing the :py:mod:`mentat.daemon.component.filter` module.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()

        # Override settings for verbose output
        self.verbose = False

        self.component = FilterDaemonComponent()

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock(
            [
                # daemon.c(self.filter_rules_key)
                [
                    {"rule": 'Note == "SSH login attempts"'},
                    {"rule": 'Note == "SSH login attempt"'},
                ]
            ]
        )

        # Setup daemon component.
        self.component.setup(daemon)
        self._verbose_print("TEST01: Daemon mock calls after component setup", daemon.mock_calls)

        daemon.c.assert_has_calls([call("filter_rules")])
        daemon.logger.debug.assert_has_calls(
            [
                call("[STATUS] Component 'filer': Loaded filter rule 'Note == \"SSH login attempts\"'"),
                call("[STATUS] Component 'filer': Loaded filter rule 'Note == \"SSH login attempt\"'"),
            ]
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
