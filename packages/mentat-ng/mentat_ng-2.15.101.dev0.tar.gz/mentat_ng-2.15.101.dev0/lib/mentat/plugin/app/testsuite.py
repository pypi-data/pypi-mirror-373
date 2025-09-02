#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Base test suite for testing Mentat application plugins.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import unittest
from pprint import pformat
from unittest.mock import Mock

import pyzenkit.jsonconf


class MentatAppPluginTestCase(unittest.TestCase):
    """
    Base test suite for testing Mentat application plugins.
    """

    def setUp(self):
        #
        # Turn on more verbose output, which includes print-out of constructed
        # objects. This will really clutter your console, usable only for test
        # debugging.
        #
        self.verbose = False

        cdir_path = os.path.dirname(os.path.realpath(__file__))
        self.core_config = pyzenkit.jsonconf.json_load(
            os.path.realpath(os.path.join(cdir_path, "../../../../conf/core/database.json.conf"))
        )

    def _verbose_print(self, label, data):
        """
        Helper method, print additional information in verbose mode.
        """
        if self.verbose:
            print(f"{label}\n{pformat(data)}")

    @staticmethod
    def _build_application_mock(config, config_list, core_config_list=None):
        """
        Helper method, build and return daemon mock object.
        """
        daemon = Mock(config=config)
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
