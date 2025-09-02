#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.detectors`.
"""

import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin
from mentat.datatype.sqldb import DetectorModel


class DetectorTestMixin:
    """
    Mixin class for detector specific tests.
    """

    def detector_get(self, detector_name, with_app_context=False):
        """
        Get given detector.
        """
        if not with_app_context:
            return hawat.db.db_session().query(DetectorModel).filter(DetectorModel.name == detector_name).one_or_none()
        with self.app.app_context():
            return hawat.db.db_session().query(DetectorModel).filter(DetectorModel.name == detector_name).one_or_none()

    def detector_save(self, detector_object, with_app_context=False):
        """
        Update given detector.
        """
        if not with_app_context:
            hawat.db.db_session().add(detector_object)
            hawat.db.db_session().commit()
        with self.app.app_context():
            hawat.db.db_session().add(detector_object)
            hawat.db.db_session().commit()

    def detector_id(self, detector_type, with_app_context=False):
        """
        Get ID of given detector.
        """
        if not with_app_context:
            fobj = self.detector_get(detector_type)
            return fobj.id
        with self.app.app_context():
            fobj = self.detector_get(detector_type)
            return fobj.id


class DetectorsListTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``detectors.list`` endpoint."""

    def _attempt_fail(self):
        self.assertGetURL(
            "/detectors/list",
            403,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/detectors/list",
            200,
            [
                b"View details of detector record &quot;DEMO_DETECTOR_A&quot;",
                b"View details of detector record &quot;DEMO_DETECTOR_B&quot;",
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


class DetectorsShowTestCase(DetectorTestMixin, TestRunnerMixin, HawatTestCase):
    """Base class for testing ``detectors.show`` and ``detectors.show_by_name`` endpoints."""

    def _attempt_fail(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/show",
            403,
        )
        self.assertGetURL(
            f"/detectors/{nname}/show_by_name",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/show",
            200,
            [f"{nname}".encode("utf8"), b"<strong>Detector created:</strong>"],
        )
        self.assertGetURL(
            f"/detectors/{nname}/show_by_name",
            200,
            [f"{nname}".encode("utf8"), b"<strong>Detector created:</strong>"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user 'user'.

        Only power user is able to view all available detectors.
        """
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user 'developer'.

        Only power user is able to view all available detectors.
        """
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user 'maintainer'.

        Only power user is able to view all available detectors.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user 'admin'.

        Only power user is able to view all available detectors.
        """
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)


class DetectorsCreateTestCase(DetectorTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``detectors.create`` endpoint."""

    detector_data_fixture = [
        ("name", "TEST_DETECTOR"),
        ("credibility", 0.24),
        ("description", "Test detector for unit testing purposes."),
    ]

    def _attempt_fail(self):
        self.assertGetURL("/detectors/create", 403)

    def _attempt_succeed(self):
        self.assertCreate(
            DetectorModel,
            "/detectors/create",
            self.detector_data_fixture,
            [b"was successfully created."],
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


class DetectorsUpdateTestCase(DetectorTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``detectors.update`` endpoint."""

    def _attempt_fail(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/update",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/update",
            200,
            [b"Update detector record details"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_05_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)


class DetectorsDeleteTestCase(DetectorTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``detectors.delete`` endpoint."""

    def _attempt_fail(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/delete",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.detector_id(nname, True)
        self.assertGetURL(
            f"/detectors/{nid}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/detectors/{nid}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully deleted."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_fail(hawat.test.fixtures.DEMO_DETECTOR_B)

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_A)
        self._attempt_succeed(hawat.test.fixtures.DEMO_DETECTOR_B)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
