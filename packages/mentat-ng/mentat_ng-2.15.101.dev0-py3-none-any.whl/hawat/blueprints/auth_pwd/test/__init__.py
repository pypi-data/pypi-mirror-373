#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.auth_pwd`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import RegistrationHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin


class AuthPwdTestCase(TestRunnerMixin, RegistrationHawatTestCase):
    """
    Class for testing :py:mod:`hawat.blueprints.auth_pwd` blueprint.
    """

    def test_01_login_user(self):
        """
        Test login/logout with *auth_pwd* module - user 'user'.
        """
        with self.app.app_context():
            user = self.user_get(hawat.const.ROLE_USER)
            user.set_password("password")
            self.user_save(user)

        response = self.login_pwd(hawat.const.ROLE_USER, "password")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged in as" in response.data)

        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged out" in response.data)

    @full_test_only
    def test_02_login_developer(self):
        """
        Test login/logout with *auth_pwd* module - user 'developer'.
        """
        with self.app.app_context():
            user = self.user_get(hawat.const.ROLE_DEVELOPER)
            user.set_password("password")
            self.user_save(user)

        response = self.login_pwd(hawat.const.ROLE_DEVELOPER, "password")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged in as" in response.data)

        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged out" in response.data)

    @full_test_only
    def test_03_login_admin(self):
        """
        Test login/logout with *auth_pwd* module - user 'admin'.
        """
        with self.app.app_context():
            user = self.user_get(hawat.const.ROLE_ADMIN)
            user.set_password("password")
            self.user_save(user)

        response = self.login_pwd(hawat.const.ROLE_ADMIN, "password")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged in as" in response.data)

        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b"You have been successfully logged out" in response.data)

    def test_04_register(self):
        """
        Test registration with *auth_pwd* module - new user 'test'.
        """
        self.assertRegister(
            "/auth_pwd/register",
            [
                ("submit", "Register"),
                ("login", "test"),
                ("fullname", "Test User"),
                ("email", "test.user@domain.org"),
                ("organization", "TEST, org."),
                ("justification", "I really want in."),
                ("password", "password"),
                ("password2", "password"),
                ("memberships_wanted", "__NO_GROUP__"),
            ],
            {
                "txt": [
                    "Dear administrator,\n"
                    "\n"
                    'a new account "test" was just registered in Mentat. Please review the '
                    "following\n"
                    "request and activate or delete the account:\n"
                    "\n"
                    "    Login:           test\n"
                    "    Full name:       Test User\n"
                    "    E-mail:          test.user@domain.org\n"
                    "    Organization:    TEST, org.\n"
                    "\n"
                    "User has provided following justification to be given access to the system:\n"
                    "\n"
                    "    I really want in.\n"
                    "\n"
                    "Account details can be found here:\n"
                    "\n"
                    "  http://localhost/users/5/show\n"
                    "\n"
                    "Have a nice day\n"
                    "\n"
                    "-- Mentat",
                    "Dear user,\n"
                    "\n"
                    "this e-mail is a confirmation, that you have successfully registered your "
                    "new\n"
                    'user account "test" in Mentat.\n'
                    "\n"
                    "During the registration process you have provided following information:\n"
                    "\n"
                    "    Login:           test\n"
                    "    Full name:       Test User\n"
                    "    E-mail:          test.user@domain.org\n"
                    "    Organization:    TEST, org.\n"
                    "\n"
                    "You have provided following justification to be given access to the system:\n"
                    "\n"
                    "    I really want in.\n"
                    "\n"
                    "Administrator was informed about registration of a new account. You will\n"
                    "receive e-mail confirmation when your account will be activated.\n"
                    "\n"
                    "After successfull activation you will be able to login and start using the\n"
                    "system:\n"
                    "\n"
                    "\thttp://localhost/auth/login\n"
                    "\n"
                    "Have a nice day\n"
                    "\n"
                    "-- Mentat",
                ],
                "html": [None, None],
            },
        )

    def test_05_register_fail(self):
        """
        Test registration with *auth_pwd* module - existing user 'user'.
        """
        self.assertRegisterFail(
            "/auth_pwd/register",
            [
                ("submit", "Register"),
                ("login", "user"),
                ("fullname", "Demo User"),
                ("email", "demo.user@domain.org"),
                ("organization", "TEST, org."),
                ("justification", "I really want in."),
                ("password", "password"),
                ("password2", "password"),
            ],
        )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
