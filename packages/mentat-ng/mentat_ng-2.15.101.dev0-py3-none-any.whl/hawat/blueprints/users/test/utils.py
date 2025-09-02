#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test utilities for :py:mod:`hawat.blueprints.users`.
"""


class UsersTestCaseMixin:
    """Mixin class with unit test framework for testing user account management endpoints."""

    def _attempt_fail_list(self):
        """Check access to ``users.list`` endpoint and fail."""
        self.assertGetURL(
            "/users/list",
            403,
        )

    def _attempt_succeed_list(self, content_checks=None):
        """Check access to ``users.list`` endpoint and succeed."""
        if content_checks is None:
            content_checks = [
                b"Show details of user account &quot;user&quot;",
                b"Show details of user account &quot;developer&quot;",
                b"Show details of user account &quot;maintainer&quot;",
                b"Show details of user account &quot;admin&quot;",
            ]
        self.assertGetURL(
            "/users/list",
            200,
            content_checks,
        )

    def _attempt_fail_show(self, uname):
        """Check access to ``users.show`` endpoint and fail."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/show",
            403,
        )

    def _attempt_succeed_show(self, uname):
        """Check access to ``users.show`` endpoint and succeed."""
        with self.app.app_context():
            uobj = self.user_get(uname)
            uid = uobj.id
            ufname = uobj.fullname
        self.assertGetURL(
            f"/users/{uid}/show",
            200,
            [
                f"{ufname} ({uname})".encode("utf8"),
                b"<strong>Account created:</strong>",
            ],
        )

    def _attempt_fail_create(self):
        """Check access to ``users.create`` endpoint and fail."""
        self.assertGetURL(
            "/users/create",
            403,
        )

    def _attempt_succeed_create(self, data):
        """Check access to ``users.create`` endpoint and succeed."""
        self.assertCreate(
            self.user_model(),
            "/users/create",
            data,
            [f"User account <strong>{data[0][1]}</strong> was successfully created.".encode("utf8")],
        )
        self._attempt_succeed_show(data[0][1])
        self._attempt_succeed_list([f"Show details of user account &quot;{data[0][1]}&quot;".encode("utf8")])

    def _attempt_fail_update(self, uname):
        """Check access to ``users.update`` endpoint and fail."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/update",
            403,
        )

    def _attempt_succeed_update(self, uname):
        """Check access to ``users.update`` endpoint and succeed."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/update",
            200,
            [b"Update user account details"],
        )

    def _attempt_fail_enable(self, uname):
        """Check access to ``users.enable`` endpoint and fail."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/enable",
            403,
        )

    def _attempt_succeed_enable(self, uname):
        """Check access to ``users.enable`` endpoint and succeed."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/enable",
            200,
            [b"Are you really sure you want to enable following item:"],
        )
        self.assertPostURL(
            f"/users/{uid}/enable",
            {"submit": "Confirm"},
            200,
            [b"was successfully enabled."],
        )

    def _attempt_fail_disable(self, uname):
        """Check access to ``users.disable`` endpoint and fail."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/disable",
            403,
        )

    def _attempt_succeed_disable(self, uname):
        """Check access to ``users.disable`` endpoint and succeed."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/disable",
            200,
            [b"Are you really sure you want to disable following item:"],
        )
        self.assertPostURL(
            f"/users/{uid}/disable",
            {"submit": "Confirm"},
            200,
            [b"was successfully disabled."],
        )

    def _attempt_fail_delete(self, uname):
        """Check access to ``users.delete`` endpoint and fail."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/delete",
            403,
        )

    def _attempt_succeed_delete(self, uname):
        """Check access to ``users.delete`` endpoint and succeed."""
        uid = self.user_id(uname, with_app_ctx=True)
        self.assertGetURL(
            f"/users/{uid}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/users/{uid}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully and permanently deleted."],
        )
