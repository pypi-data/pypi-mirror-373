#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.filters`.
"""

import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin
from mentat.datatype.sqldb import FilterModel


class FilterTestMixin:
    """
    Mixin class for filter specific tests.
    """

    @staticmethod
    def _fname(gname):
        return f"FLT_{gname}"

    def filter_get(self, filter_name, with_app_context=False):
        """
        Get given filter.
        """
        if not with_app_context:
            return hawat.db.db_session().query(FilterModel).filter(FilterModel.name == filter_name).one_or_none()
        with self.app.app_context():
            return hawat.db.db_session().query(FilterModel).filter(FilterModel.name == filter_name).one_or_none()

    def filter_save(self, filter_object, with_app_context=False):
        """
        Update given filter.
        """
        if not with_app_context:
            hawat.db.db_session().add(filter_object)
            hawat.db.db_session().commit()
        with self.app.app_context():
            hawat.db.db_session().add(filter_object)
            hawat.db.db_session().commit()

    def filter_id(self, filter_type, with_app_context=False):
        """
        Get ID of given filter.
        """
        if not with_app_context:
            fobj = self.filter_get(filter_type)
            return fobj.id
        with self.app.app_context():
            fobj = self.filter_get(filter_type)
            return fobj.id


class FiltersListTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``filters.list`` endpoint."""

    def _attempt_fail(self):
        self.assertGetURL("/filters/list", 403)

    def _attempt_succeed(self):
        self.assertGetURL(
            "/filters/list",
            200,
            [
                b"View details of reporting filter",
                b"FLT_DEMO_GROUP_A",
                b"FLT_DEMO_GROUP_B",
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


class FiltersShowTestCase(FilterTestMixin, TestRunnerMixin, HawatTestCase):
    """Base class for testing ``filters.show`` endpoint."""

    def _attempt_fail(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(f"/filters/{fid}/show", 403)

    def _attempt_succeed(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(
            f"/filters/{fid}/show",
            200,
            [f"{fname}".encode("utf8"), b"<strong>Filter created:</strong>"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user 'user'.

        Only power user is able to view all available filters.
        """
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user 'developer'.

        Only power user is able to view all available filters.
        """
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user 'maintainer'.

        Only power user is able to view all available filters.
        """
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user 'admin'.

        Only power user is able to view all available filters.
        """
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))


class FiltersCreateTestCase(FilterTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``filters.create`` endpoint."""

    filter_data_fixture = [
        ("name", "TEST_FILTER"),
        ("type", "advanced"),
        ("source_based", True),
        ("group", hawat.test.fixtures.DEMO_GROUP_A),
        ("description", "Test filter for unit testing purposes."),
        (
            "filter",
            '"Recon.Scanning" in Category and Target.IP4??[] in [191.168.1.1, 10.0.0.1]',
        ),
        ("enabled", True),
    ]

    def _attempt_fail(self):
        self.assertGetURL("/filters/create", 403)

    def _attempt_succeed(self):
        self.assertCreate(
            FilterModel,
            "/filters/create",
            self.filter_data_fixture,
            [
                b"Reporting filter <strong>TEST_FILTER</strong> for group ",
                b" was successfully created.",
            ],
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


class FiltersCreateForTestCase(FilterTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``filters.createfor`` endpoint."""

    filter_data_fixture = [
        ("name", "TEST_FILTER"),
        ("type", "advanced"),
        ("source_based", True),
        ("description", "Test filter for unit testing purposes."),
        (
            "filter",
            '"Recon.Scanning" in Category and Target.IP4??[] in [191.168.1.1, 10.0.0.1]',
        ),
        ("enabled", True),
    ]

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(f"/filters/createfor/{gid}", 403)

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertCreate(
            FilterModel,
            f"/filters/createfor/{gid}",
            self.filter_data_fixture,
            [
                b"Reporting filter <strong>TEST_FILTER</strong> for group ",
                b" was successfully created.",
            ],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_GROUP_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_GROUP_A)
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


class FiltersUpdateTestCase(FilterTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``filters.update`` endpoint."""

    def _attempt_fail(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(f"/filters/{fid}/update", 403)

    def _attempt_succeed(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(f"/filters/{fid}/update", 200, [b"Update reporting filter details"])

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_05_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))


class FiltersEnableDisableTestCase(FilterTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``filters.enable`` and ``filters.disable`` endpoint."""

    def _attempt_fail(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(f"/filters/{fid}/disable", 403)
        self.assertGetURL(f"/filters/{fid}/enable", 403)

    def _attempt_succeed(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(
            f"/filters/{fid}/disable",
            200,
            [b"Are you really sure you want to disable following item:"],
        )
        self.assertPostURL(
            f"/filters/{fid}/disable",
            {"submit": "Confirm"},
            200,
            [b"was successfully disabled."],
        )
        self.assertGetURL(
            f"/filters/{fid}/enable",
            200,
            [b"Are you really sure you want to enable following item:"],
        )
        self.assertPostURL(
            f"/filters/{fid}/enable",
            {"submit": "Confirm"},
            200,
            [b"was successfully enabled."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))


class FiltersDeleteTestCase(FilterTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``filters.delete`` endpoint."""

    def _attempt_fail(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(f"/filters/{fid}/delete", 403)

    def _attempt_succeed(self, fname):
        fid = self.filter_id(fname, True)
        self.assertGetURL(
            f"/filters/{fid}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/filters/{fid}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully and permanently deleted."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._fname(hawat.test.fixtures.DEMO_GROUP_B))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
