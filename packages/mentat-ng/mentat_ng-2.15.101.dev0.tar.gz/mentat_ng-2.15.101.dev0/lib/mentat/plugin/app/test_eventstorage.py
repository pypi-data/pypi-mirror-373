#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.plugin.app.eventstorage` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest

from mentat.plugin.app.eventstorage import EventStoragePlugin
from mentat.plugin.app.testsuite import MentatAppPluginTestCase

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatPluginAppEventStorage(MentatAppPluginTestCase):
    """
    Unit test class for testing the :py:mod:`mentat.plugin.app.storage` module.
    """

    def setUp(self):
        # WARNING: Do not forget to call parent version of setUp() method !!!
        super().setUp()
        self.plugin = EventStoragePlugin()

    def test_01_setup(self):
        """
        ...
        """
        self.maxDiff = None

        mapplication = self._build_application_mock(self.core_config, None)

        self.plugin.configure(mapplication)
        self.plugin.setup(mapplication)
        self._verbose_print(
            "TEST04: Application mock calls after plugin 'setup'",
            mapplication.mock_calls,
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
