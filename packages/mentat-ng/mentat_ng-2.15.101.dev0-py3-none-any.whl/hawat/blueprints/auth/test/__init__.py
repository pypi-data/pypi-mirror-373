#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.auth`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import unittest

from hawat.test import HawatTestCase
from hawat.test.runner import TestRunnerMixin


class AuthTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing :py:mod:`hawat.blueprints.auth` blueprint.
    """

    def test_01_login(self):
        """
        Test login directional page.
        """
        response = self.client.get(
            "/auth/login",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b"Following is a list of all available user login options. Please choose the one appropriate for you."
            in response.data
        )

    def test_02_register(self):
        """
        Test registration directional page.
        """
        response = self.client.get(
            "/auth/register",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b"Following is a list of all available user account registration options. Please choose the one most suitable for your needs."
            in response.data
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
