#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.cross_table`.
"""

import unittest

import hawat.const
import hawat.test
from hawat.test import HawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin


class SearchTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing ``cross_table.search`` endpoint.
    """

    def _attempt_fail_redirect(self):
        self.assertGetURL(
            "/cross_table/search",
            302,
            [b"Redirecting...", b"login?next="],
            follow_redirects=False,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/cross_table/search",
            200,
            [b"Calculate event cross table"],
        )

    def test_01_as_anonymous(self):
        """Test access as anonymous user."""
        self._attempt_fail_redirect()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_02_as_user(self):
        """Test access as user ``user``."""
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_03_as_developer(self):
        """Test access as user ``developer``."""
        self._attempt_succeed()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_04_as_maintainer(self):
        """Test access as user ``maintainer``."""
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_05_as_admin(self):
        """Test access as user ``admin``."""
        self._attempt_succeed()


class APISearchTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing ``cross_table.apisearch`` endpoint.
    """

    def _attempt_fail_unauthorized(self):
        self.assertGetURL(
            "/api/cross_table/search",
            401,
            [b"Unauthorized"],
        )

    def test_01_as_anonymous(self):
        """Test access as anonymous user."""
        self._attempt_fail_unauthorized()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
