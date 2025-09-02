#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.event_classes`.
"""

import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.fixtures import DEMO_EVENT_CLASS
from hawat.test.runner import TestRunnerMixin
from mentat.datatype.sqldb import EventClassModel, EventClassState


class EventClassTestMixin:
    """
    Mixin class for event class specific tests.
    """

    def event_class_get(self, event_class_name, with_app_context=False):
        """
        Get given event class.
        """
        if not with_app_context:
            return (
                hawat.db.db_session()
                .query(EventClassModel)
                .filter(EventClassModel.name == event_class_name)
                .one_or_none()
            )
        with self.app.app_context():
            return (
                hawat.db.db_session()
                .query(EventClassModel)
                .filter(EventClassModel.name == event_class_name)
                .one_or_none()
            )

    def event_class_save(self, event_class_object, with_app_context=False):
        """
        Update given event class.
        """
        if not with_app_context:
            hawat.db.db_session().add(event_class_object)
            hawat.db.db_session().commit()
        with self.app.app_context():
            hawat.db.db_session().add(event_class_object)
            hawat.db.db_session().commit()

    def event_class_id(self, event_class, with_app_context=False):
        """
        Get ID of given event class.
        """
        if not with_app_context:
            fobj = self.event_class_get(event_class)
            return fobj.id
        with self.app.app_context():
            fobj = self.event_class_get(event_class)
            return fobj.id


class EventClassListTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``event_classes.list`` endpoint."""

    def _attempt_fail(self):
        self.assertGetURL(
            "/event_classes/list",
            403,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/event_classes/list",
            200,
            [
                b"View details of event class",
                b"Event class management",
                b"Create event class",
                b"Creation time from",
                b"Clear",
                b"Severity",
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


class EventClassShowTestCase(EventClassTestMixin, TestRunnerMixin, HawatTestCase):
    """Base class for testing ``event_classes.show`` endpoint."""

    def _attempt_fail(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/show",
            403,
        )
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{DEMO_EVENT_CLASS}/show",
            403,
        )

    def _attempt_succeed(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/show",
            200,
            [
                f"{DEMO_EVENT_CLASS}".encode("utf8"),
                b"<strong>Event class created:</strong>",
                b"Filter playground",
                b"State:",
                b"Changelogs",
                b"Name:",
            ],
        )
        self.assertGetURL(
            f"/event_classes/{DEMO_EVENT_CLASS}/show",
            200,
            [
                f"{DEMO_EVENT_CLASS}".encode("utf8"),
                b"<strong>Event class created:</strong>",
                b"Filter playground",
                b"State:",
                b"Changelogs",
                b"Name:",
            ],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user 'user'.
        """
        self._attempt_fail()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user 'developer'.
        """
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user 'maintainer'.
        """
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user 'admin'.
        """
        self._attempt_succeed()


class EventClassCreateTestCase(EventClassTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``event_classes.create`` endpoint."""

    data_fixture = [
        ("name", "TEST_EVENT_CLASS"),
        ("source_based", True),
        ("label_en", "Test event class for unit testing purposes."),
        ("label_cz", "Testovací třída událostí."),
        ("reference", "https://csirt.cesnet.cz/cs/services/eventclass"),
        ("displayed_main", ["FlowCount"]),
        ("displayed_source", ["Hostname"]),
        ("displayed_target", ["Port"]),
        ("rule", 'Category IN ["Recon.Scanning"]'),
        ("severity", "medium"),
        ("subclassing", "Ref"),
        ("state", EventClassState.ENABLED),
    ]

    def _attempt_fail(self):
        self.assertGetURL(
            "/event_classes/create",
            403,
        )

    def _attempt_succeed(self):
        self.assertCreate(
            EventClassModel,
            "/event_classes/create",
            self.data_fixture,
            [b"Event class ", b"TEST_EVENT_CLASS", b"was successfully created."],
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


class EventClassUpdateTestCase(EventClassTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``event_classes.update`` endpoint."""

    def _attempt_fail(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/update",
            403,
        )

    def _attempt_succeed(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/update",
            200,
            [b"Update event class details", b"State:", b"Severity", b"Label"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail()

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_05_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed()

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed()


class EventClassDeleteTestCase(EventClassTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``event_classes.delete`` endpoint."""

    def _attempt_fail(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/delete",
            403,
        )

    def _attempt_succeed(self):
        ec_id = self.event_class_id(DEMO_EVENT_CLASS, True)
        self.assertGetURL(
            f"/event_classes/{ec_id}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/event_classes/{ec_id}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully and permanently deleted."],
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


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
