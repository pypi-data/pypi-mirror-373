#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.groups`.
"""

import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin


class GroupsListTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``groups.list`` endpoint."""

    def _attempt_fail(self):
        self.assertGetURL(
            "/groups/list",
            403,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/groups/list",
            200,
            [
                b"View details of group &quot;DEMO_GROUP_A&quot;",
                b"View details of group &quot;DEMO_GROUP_B&quot;",
            ],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user ``user``."""
        self._attempt_fail()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user ``developer``."""
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user ``maintainer``."""
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user ``admin``."""
        self._attempt_succeed()


class GroupsShowTestCase(TestRunnerMixin, HawatTestCase):
    """Base class for testing ``groups.show`` and ``groups.show_by_name`` endpoints."""

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/show",
            403,
        )
        self.assertGetURL(
            f"/groups/{gname}/show_by_name",
            403,
        )

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/show",
            200,
            [f"{gname}".encode("utf8"), b"<strong>Group created:</strong>"],
        )
        self.assertGetURL(
            f"/groups/{gname}/show_by_name",
            200,
            [f"{gname}".encode("utf8"), b"<strong>Group created:</strong>"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user 'user'.

        Only power user is able to view all available groups.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user 'developer'.

        Only power user is able to view all available groups.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user 'maintainer'.

        Only power user is able to view all available groups.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user 'admin'.

        Only power user is able to view all available groups.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)


class GroupsCreateTestCase(TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``groups.create`` endpoint."""

    group_data_fixture = [
        ("name", "TEST_GROUP"),
        ("description", "Test group for unit testing purposes."),
        ("enabled", True),
    ]

    def _attempt_fail(self):
        self.assertGetURL(
            "/groups/create",
            403,
        )

    def _attempt_succeed(self):
        self.assertCreate(
            self.group_model(),
            "/groups/create",
            self.group_data_fixture,
            [b"Group <strong>TEST_GROUP</strong> was successfully created."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed()


class GroupsUpdateTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``groups.update`` endpoint."""

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/update",
            403,
        )

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/update",
            200,
            [b"Update group details"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_05_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)


class GroupsEnableDisableTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``groups.enable`` and ``groups.disable`` endpoint."""

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/disable",
            403,
        )
        self.assertGetURL(
            f"/groups/{gid}/enable",
            403,
        )

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/disable",
            200,
            [b"Are you really sure you want to disable following item:"],
        )
        self.assertPostURL(
            f"/groups/{gid}/disable",
            {"submit": "Confirm"},
            200,
            [b"was successfully disabled."],
        )
        self.assertGetURL(
            f"/groups/{gid}/enable",
            200,
            [b"Are you really sure you want to enable following item:"],
        )
        self.assertPostURL(
            f"/groups/{gid}/enable",
            {"submit": "Confirm"},
            200,
            [b"was successfully enabled."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)


class GroupsAddRemRejMemberTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``groups.add_member``, ``groups.reject_member`` and ``groups.remove_member`` endpoint."""

    def _attempt_fail(self, uname, gname):
        with self.app.app_context():
            uid = self.user_id(uname)
            gid = self.group_id(gname)
        self.assertGetURL(
            f"/groups/{gid}/remove_member/{uid}",
            403,
        )
        self.assertGetURL(
            f"/groups/{gid}/reject_member/{uid}",
            403,
        )
        self.assertGetURL(
            f"/groups/{gid}/add_member/{uid}",
            403,
        )

    def _attempt_succeed(self, uname, gname, print_response=False):
        # Additional test preparations.
        with self.app.app_context():
            uid = self.user_id(uname)
            gid = self.group_id(gname)
            self.user_enabled(uname, False)

        #
        # First check the removal of existing membership.
        #
        self.assertGetURL(
            f"/groups/{gid}/remove_member/{uid}",
            200,
            [b"Are you really sure you want to remove user"],
            print_response,
        )
        self.assertPostURL(
            f"/groups/{gid}/remove_member/{uid}",
            {"submit": "Confirm"},
            200,
            [b"was successfully removed as a member from group"],
            print_response,
        )

        #
        # Add user back to group.
        #
        self.assertGetURL(
            f"/groups/{gid}/add_member/{uid}",
            200,
            [b"Are you really sure you want to add user"],
            print_response,
        )
        self.assertPostURL(
            f"/groups/{gid}/add_member/{uid}",
            {"submit": "Confirm"},
            200,
            [b"was successfully added as a member to group"],
            print_response,
        )
        self.app.mailer.assert_has_calls(
            [
                unittest.mock.call.send(
                    {
                        "subject": "[Mentat] Account activation - user",
                        "to": ["user@bogus-domain.org"],
                    },
                    'Dear user,\n\nthis e-mail is a confirmation, that your account "user" '
                    "in Mentat system was\njust activated. You may now login and start using "
                    "the system:\n\n\thttp://localhost/\n\nHave a nice day\n\n-- Mentat System",
                )
            ]
        )

        # Additional test preparations.
        with self.app.app_context():
            uobj = self.user_get(uname)
            gobj = self.group_get(gname)
            uid = uobj.id
            gid = gobj.id
            uobj.enabled = False
            uobj.memberships.remove(gobj)
            uobj.memberships_wanted.append(gobj)
            self.user_save(uobj)

        #
        # Check membership request rejection feature.
        #
        self.assertGetURL(
            f"/groups/{gid}/reject_member/{uid}",
            200,
            [b"Are you really sure you want to reject membership request of user"],
            print_response,
        )
        self.assertPostURL(
            f"/groups/{gid}/reject_member/{uid}",
            {"submit": "Confirm"},
            200,
            [b"was successfully rejected."],
            print_response,
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail(uname, hawat.test.fixtures.DEMO_GROUP_A)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_succeed(uname, hawat.test.fixtures.DEMO_GROUP_A)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_succeed(uname, hawat.test.fixtures.DEMO_GROUP_A)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
        ):
            self._attempt_succeed(uname, hawat.test.fixtures.DEMO_GROUP_A)


class GroupsDeleteTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``groups.delete`` endpoint."""

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/delete",
            403,
        )

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/groups/{gid}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/groups/{gid}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully and permanently deleted."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_B)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
