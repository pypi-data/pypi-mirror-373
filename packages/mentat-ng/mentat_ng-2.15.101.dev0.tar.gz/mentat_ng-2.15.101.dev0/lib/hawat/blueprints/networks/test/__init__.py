#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit tests for :py:mod:`hawat.blueprints.networks`.
"""

import json
import unittest

import hawat.const
import hawat.db
import hawat.test
import hawat.test.fixtures
from hawat.test import HawatTestCase, ItemCreateHawatTestCase, full_test_only
from hawat.test.runner import TestRunnerMixin
from mentat.datatype.sqldb import GroupModel, NetworkModel, SettingsReportingModel


class NetworkTestMixin:
    """
    Mixin class for network specific tests.
    """

    @staticmethod
    def _nname(gname):
        return f"NET_{gname}"

    def network_get(self, network_name, with_app_context=False):
        """
        Get given network.
        """
        if not with_app_context:
            return hawat.db.db_session().query(NetworkModel).filter(NetworkModel.netname == network_name).one_or_none()
        with self.app.app_context():
            return hawat.db.db_session().query(NetworkModel).filter(NetworkModel.netname == network_name).one_or_none()

    def network_save(self, network_object, with_app_context=False):
        """
        Update given network.
        """
        if not with_app_context:
            hawat.db.db_session().add(network_object)
            hawat.db.db_session().commit()
        with self.app.app_context():
            hawat.db.db_session().add(network_object)
            hawat.db.db_session().commit()

    def network_id(self, network_type, with_app_context=False):
        """
        Get ID of given network.
        """
        if not with_app_context:
            fobj = self.network_get(network_type)
            return fobj.id
        with self.app.app_context():
            fobj = self.network_get(network_type)
            return fobj.id


class NetworksListTestCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``networks.list`` endpoint."""

    def _attempt_fail(self):
        self.assertGetURL(
            "/networks/list",
            403,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/networks/list",
            200,
            [
                b"View details of network record &quot;NET_DEMO_GROUP_A&quot;",
                b"View details of network record &quot;NET_DEMO_GROUP_B&quot;",
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


class NetworksShowTestCase(NetworkTestMixin, TestRunnerMixin, HawatTestCase):
    """Base class for testing ``networks.show`` endpoint."""

    def _attempt_fail(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/show",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/show",
            200,
            [f"{nname}".encode("utf8"), b"<strong>Network created:</strong>"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """
        Test access as user 'user'.

        Only power user is able to view all available networks.
        """
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """
        Test access as user 'developer'.

        Only power user is able to view all available networks.
        """
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """
        Test access as user 'maintainer'.

        Only power user is able to view all available networks.
        """
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """
        Test access as user 'admin'.

        Only power user is able to view all available networks.
        """
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))


class NetworksCreateTestCase(NetworkTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``networks.create`` endpoint."""

    network_data_fixture = [
        ("group", hawat.test.fixtures.DEMO_GROUP_A),
        ("netname", "TEST_NETWORK"),
        ("network", "191.168.1.0/24"),
        ("description", "Test network for unit testing purposes."),
    ]

    def _attempt_fail(self):
        self.assertGetURL(
            "/networks/create",
            403,
        )

    def _attempt_succeed(self):
        self.assertCreate(
            NetworkModel,
            "/networks/create",
            self.network_data_fixture,
            [
                b"Network record <strong>TEST_NETWORK</strong> for group ",
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


class NetworksCreateForTestCase(NetworkTestMixin, TestRunnerMixin, ItemCreateHawatTestCase):
    """Class for testing ``networks.createfor`` endpoint."""

    network_data_fixture = [
        ("netname", "TEST_NETWORK"),
        ("network", "191.168.1.0/24"),
        ("description", "Test network for unit testing purposes."),
    ]

    def _attempt_fail(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertGetURL(
            f"/networks/createfor/{gid}",
            403,
        )

    def _attempt_succeed(self, gname):
        gid = self.group_id(gname, with_app_ctx=True)
        self.assertCreate(
            NetworkModel,
            f"/networks/createfor/{gid}",
            self.network_data_fixture,
            [
                b"Network record <strong>TEST_NETWORK</strong> for group ",
                b" was successfully created.",
            ],
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


class NetworksUpdateTestCase(NetworkTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``networks.update`` endpoint."""

    def _attempt_fail(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/update",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/update",
            200,
            [b"Update network record details"],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_04_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_05_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))


class NetworksDeleteTestCase(NetworkTestMixin, TestRunnerMixin, HawatTestCase):
    """Class for testing ``networks.delete`` endpoint."""

    def _attempt_fail(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/delete",
            403,
        )

    def _attempt_succeed(self, nname):
        nid = self.network_id(nname, True)
        self.assertGetURL(
            f"/networks/{nid}/delete",
            200,
            [b"Are you really sure you want to permanently remove following item:"],
        )
        self.assertPostURL(
            f"/networks/{nid}/delete",
            {"submit": "Confirm"},
            200,
            [b"was successfully and permanently deleted."],
        )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_USER)
    def test_01_as_user(self):
        """Test access as user 'user'."""
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_DEVELOPER)
    def test_02_as_developer(self):
        """Test access as user 'developer'."""
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_fail(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_MAINTAINER)
    def test_03_as_maintainer(self):
        """Test access as user 'maintainer'."""
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))

    @full_test_only
    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_04_as_admin(self):
        """Test access as user 'admin'."""
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_A))
        self._attempt_succeed(self._nname(hawat.test.fixtures.DEMO_GROUP_B))


class NetworksAPIViewCase(TestRunnerMixin, HawatTestCase):
    """Class for testing ``api.networks.get`` endpoint."""

    def _attempt_fail_unauthorized(self):
        self.assertGetURL(
            "/api/networks/get",
            401,
            [b"Unauthorized"],
        )

    def _attempt_fail(self):
        self.assertGetURL(
            "/api/networks/get",
            403,
        )

    def _attempt_succeed(self):
        self.assertGetURL(
            "/api/networks/get",
            200,
            [b"data"],
        )

    def get_fixtures_db(self, app):
        """
        Setup database object fixtures.
        """
        out = []
        group = GroupModel(
            name="Fallback group",
            source="manual",
            description="fallback group",
        )
        group.settings_rep = SettingsReportingModel(emails_medium=["abuse@medium"])
        NetworkModel(
            is_base=True,
            group=group,
            netname="base network",
            source="manual",
            network="195.13.41.0/24",
        )
        NetworkModel(
            group=group,
            rank=1234,
            source="negistry",
            netname="full network",
            description="network with all data",
            local_id="AF1294",
            network="9.10.11.0/24",
        )
        out.append(group)

        group2 = GroupModel(
            name="Group 2",
            source="manual",
            description="group with multiple abuse contacts",
        )
        group2.settings_rep = SettingsReportingModel(
            emails_info=["abuse@info"],
            emails_low=["abuse@low"],
            emails_medium=["abuse@medium"],
            emails_high=["abuse@high"],
            emails_critical=["abuse@critical"],
        )
        NetworkModel(
            group=group2,
            netname="network 2",
            source="manual",
            network="200.132.141.0/24",
        )
        NetworkModel(
            group=group2,
            netname="IP6 CIDR net",
            source="manual",
            network="2001::/48",
        )
        NetworkModel(
            group=group2,
            netname="IP6 range",
            source="manual",
            network="2003::-2004::",
        )
        out.append(group2)

        out.extend(super().get_fixtures_db(app))
        return out

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

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_05_fallback_networks(self):
        """Test export of fallback networks."""
        response = self.client.get("/api/networks/get")
        networks = json.loads(response.data.decode())["data"]
        resolved_abuses = [net["resolved_abuses"] for net in networks]
        self.assertTrue(any("fallback" in contacts for contacts in resolved_abuses))

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_06_multiple_resolved_abuses(self):
        """Test export of networks with multiple resolved abuses."""
        response = self.client.get("/api/networks/get")
        networks = json.loads(response.data.decode())["data"]
        resolved_abuses = [net["resolved_abuses"] for net in networks]
        self.assertTrue(any(len(contacts) == 5 for contacts in resolved_abuses))
        for contacts in resolved_abuses:
            if len(contacts) == 5:
                self.assertEqual(
                    contacts,
                    {
                        "info": ["abuse@info"],
                        "low": ["abuse@low"],
                        "medium": ["abuse@medium"],
                        "high": ["abuse@high"],
                        "critical": ["abuse@critical"],
                    },
                )

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_07_IP6_networks(self):
        """Test export of IPv6 networks."""
        response = self.client.get("/api/networks/get")
        networks = json.loads(response.data.decode())["data"]
        netname_cidr = "IP6 CIDR net"
        netname_range = "IP6 range"
        self.assertTrue(any(net["netname"] == netname_cidr for net in networks))
        for net in networks:
            if net["netname"] == netname_cidr:
                self.assertEqual(net["ip6_addr"], "2001::")
                self.assertEqual(net["ip6_prefix"], 48)
        self.assertTrue(any(net["netname"] == netname_range for net in networks))
        for net in networks:
            if net["netname"] == netname_range:
                self.assertEqual(net["ip6_start"], "2003::")
                self.assertEqual(net["ip6_end"], "2004::")

    @hawat.test.do_as_user_decorator(hawat.const.ROLE_ADMIN)
    def test_08_export(self):
        """Test export of network with all data."""
        response = self.client.get("/api/networks/get")
        networks = json.loads(response.data.decode())["data"]
        netname = "full network"
        self.assertTrue(any(net["netname"] == netname for net in networks))
        for net in networks:
            if net["netname"] == netname:
                self.assertEqual(net["rank"], 1234)
                self.assertEqual(net["source"], "negistry")
                self.assertEqual(net["descr"], "network with all data")
                self.assertEqual(net["client_id"], "AF1294")
                self.assertEqual(net["resolved_abuses"], {"medium": ["abuse@medium"]})
                self.assertEqual(net["ip4_start"], "9.10.11.0")
                self.assertEqual(net["ip4_end"], "9.10.11.255")

    def test_09_as_anonymous(self):
        """Test access as anonymous user."""
        self._attempt_fail_unauthorized()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
