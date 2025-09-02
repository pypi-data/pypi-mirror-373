#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.users`.
"""

import unittest

import hawat.const
import hawat.test
import hawat.test.fixtures
from hawat.blueprints.users.test.utils import UsersTestCaseMixin
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin


class UsersListTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.list`` endpoint."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user ``user``.

        Only power user is able to list all available user accounts.
        """
        self._attempt_fail_list()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user ``developer``.

        Only power user is able to list all available user accounts.
        """
        self._attempt_fail_list()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user ``maintainer``.

        Only power user is able to list all available user accounts.
        """
        self._attempt_succeed_list()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user ``admin``.

        Only power user is able to list all available user accounts.
        """
        self._attempt_succeed_list()


class UsersShowOwnTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """
    Class for testing ``users.show`` endpoint: access to user`s own accounts.

    Each user must be able to access his own account.
    """

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed_show(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed_show(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed_show(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed_show(hawat.const.ROLE_ADMIN)


class UsersShowOtherTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.show`` endpoint: access to other user`s accounts."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user_developer(self):
        """
        Test access to 'developer' account as user 'user'.

        Regular user may view only his own account.
        """
        self._attempt_fail_show(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_02_as_user_maintainer(self):
        """
        Test access to 'maintainer' account as user 'user'.

        Regular user may view only his own account.
        """
        self._attempt_fail_show(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_03_as_user_admin(self):
        """
        Test access to 'admin' account as user 'user'.

        Regular user may view only his own account.
        """
        self._attempt_fail_show(hawat.const.ROLE_ADMIN)

    # --------------------------------------------------------------------------

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer_user(self):
        """
        Test access to 'user' account as user 'developer'.

        Developer should be able to access because he is a manager of group of
        which all other users are members.
        """
        self._attempt_succeed_show(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_05_as_developer_maintainer(self):
        """
        Test access to 'maintainer' account as user 'developer'.

        Developer should be able to access because he is a manager of group of
        which all other users are members.
        """
        self._attempt_succeed_show(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_06_as_developer_admin(self):
        """
        Test access to 'admin' account as user 'developer'.

        Developer should be able to access because he is a manager of group of
        which all other users are members.
        """
        self._attempt_succeed_show(hawat.const.ROLE_ADMIN)

    # --------------------------------------------------------------------------

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_07_as_maintainer_user(self):
        """
        Test access to 'user' account as user 'maintainer'.

        Maintainer should be allowed access, because he is a power user like admin.
        """
        self._attempt_succeed_show(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_08_as_maintainer_developer(self):
        """
        Test access to 'developer' account as user 'maintainer'.

        Maintainer should be allowed access, because he is a power user like admin.
        """
        self._attempt_succeed_show(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_09_as_maintainer_admin(self):
        """
        Test access to 'maintainer' account as user 'maintainer'.

        Maintainer should be allowed access, because he is a power user like admin.
        """
        self._attempt_succeed_show(hawat.const.ROLE_MAINTAINER)

    # --------------------------------------------------------------------------

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_10_as_admin_user(self):
        """Test access to 'user' account as user 'admin'."""
        self._attempt_succeed_show(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_11_as_admin_developer(self):
        """Test access to 'developer' account as user 'admin'."""
        self._attempt_succeed_show(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_12_as_admin_maintainer(self):
        """Test access to 'maintainer' account as user 'admin'."""
        self._attempt_succeed_show(hawat.const.ROLE_MAINTAINER)


class UsersCreateTestCase(UsersTestCaseMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``users.create`` endpoint."""

    user_data_fixture = [
        ("login", "test"),
        ("fullname", "Test User"),
        ("email", "test.user@domain.org"),
        ("organization", "TEST, org."),
        ("enabled", True),
    ]

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail_create()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail_create()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed_create(self.user_data_fixture)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed_create(self.user_data_fixture)


class UsersUpdateOwnTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.update`` endpoint: access to user`s own accounts."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed_update(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed_update(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed_update(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed_update(hawat.const.ROLE_ADMIN)


class UsersUpdateOtherTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.update`` endpoint: access to other user`s accounts."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user_developer(self):
        """Test access to 'developer' account as user 'user'."""
        self._attempt_fail_update(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_02_as_user_maintainer(self):
        """Test access to 'maintainer' account as user 'user'."""
        self._attempt_fail_update(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_03_as_user_admin(self):
        """Test access to 'admin' account as user 'user'."""
        self._attempt_fail_update(hawat.const.ROLE_ADMIN)

    # --------------------------------------------------------------------------

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer_user(self):
        """Test access to 'user' account as user 'developer'."""
        self._attempt_fail_update(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_05_as_developer_maintainer(self):
        """Test access to 'maintainer' account as user 'developer'."""
        self._attempt_fail_update(hawat.const.ROLE_MAINTAINER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_06_as_developer_admin(self):
        """Test access to 'admin' account as user 'developer'."""
        self._attempt_fail_update(hawat.const.ROLE_ADMIN)

    # --------------------------------------------------------------------------

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_07_as_maintainer_user(self):
        """Test access to 'user' account as user 'maintainer'."""
        self._attempt_fail_update(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_08_as_maintainer_developer(self):
        """Test access to 'developer' account as user 'maintainer'."""
        self._attempt_fail_update(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_09_as_maintainer_admin(self):
        """Test access to 'admin' account as user 'maintainer'."""
        self._attempt_fail_update(hawat.const.ROLE_ADMIN)

    # --------------------------------------------------------------------------

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_10_as_admin_user(self):
        """Test access to 'user' account as user 'admin'."""
        self._attempt_succeed_update(hawat.const.ROLE_USER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_11_as_admin_developer(self):
        """Test access to 'developer' account as user 'admin'."""
        self._attempt_succeed_update(hawat.const.ROLE_DEVELOPER)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_12_as_admin_maintainer(self):
        """Test access to 'maintainer' account as user 'admin'."""
        self._attempt_succeed_update(hawat.const.ROLE_MAINTAINER)


class UsersEnableDisableTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.enable`` and ``users.disable`` endpoint."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail_disable(uname)
            self._attempt_fail_enable(uname)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail_disable(uname)
            self._attempt_fail_enable(uname)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_succeed_disable(uname)
            self._attempt_succeed_enable(uname)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
        ):
            self._attempt_succeed_disable(uname)
            self._attempt_succeed_enable(uname)


class UsersAddRemRejMembershipTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.add_membership``, ``users.reject_membership`` and ``users.remove_membership`` endpoint."""

    def _attempt_fail(self, uname, gname):
        with self.app.app_context():
            uid = self.user_id(uname)
            gid = self.group_id(gname)
        self.assertGetURL(f"/users/{uid}/remove_membership/{gid}", 403)
        self.assertGetURL(f"/users/{uid}/reject_membership/{gid}", 403)
        self.assertGetURL(f"/users/{uid}/add_membership/{gid}", 403)

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
            f"/users/{uid}/remove_membership/{gid}",
            200,
            [b"Are you really sure you want to remove user"],
            print_response,
        )
        self.assertPostURL(
            f"/users/{uid}/remove_membership/{gid}",
            {"submit": "Confirm"},
            200,
            [b"was successfully removed as a member from group"],
            print_response,
        )

        #
        # Add user back to group.
        #
        self.assertGetURL(
            f"/users/{uid}/add_membership/{gid}",
            200,
            [b"Are you really sure you want to add user"],
            print_response,
        )
        self.assertPostURL(
            f"/users/{uid}/add_membership/{gid}",
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
            f"/users/{uid}/reject_membership/{gid}",
            200,
            [b"Are you really sure you want to reject membership request of user"],
            print_response,
        )
        self.assertPostURL(
            f"/users/{uid}/reject_membership/{gid}",
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


class UsersDeleteTestCase(UsersTestCaseMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``users.delete`` endpoint."""

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail_delete(uname)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail_delete(uname)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
            hawat.const.ROLE_ADMIN,
        ):
            self._attempt_fail_delete(uname)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        for uname in (
            hawat.const.ROLE_USER,
            hawat.const.ROLE_DEVELOPER,
            hawat.const.ROLE_MAINTAINER,
        ):
            self._attempt_succeed_delete(uname)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
