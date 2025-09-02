#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.devtools`.
"""

import unittest

import hawat.const
import hawat.db
import hawat.test
from hawat.test import HawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin


class ConfigTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing ``devtools.config`` endpoint.

    This endpoint is for developers only.
    """

    def _attempt_fail_redirect(self):
        self.assertGetURL(
            "/devtools/config",
            302,
            [b"Redirecting...", b"login?next="],
            follow_redirects=False,
        )

    def _attempt_fail(self):
        self.assertGetURL("/devtools/config", 403)

    def _attempt_succeed(self):
        self.assertGetURL(
            "/devtools/config",
            200,
            [
                b"System configuration",
                b"Enabled modules",
                b"Endpoint permissions",
                b"Timezone settings",
                b"Configuration",
            ],
        )

    def test_01_as_anonymous(self):
        """Test access as anonymous user."""
        self._attempt_fail_redirect()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_02_as_user(self):
        """Test access as user ``user``."""
        self._attempt_fail()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_03_as_developer(self):
        """Test access as user ``developer``."""
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_04_as_maintainer(self):
        """Test access as user ``maintainer``."""
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_05_as_admin(self):
        """Test access as user ``admin``."""
        self._attempt_succeed()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
