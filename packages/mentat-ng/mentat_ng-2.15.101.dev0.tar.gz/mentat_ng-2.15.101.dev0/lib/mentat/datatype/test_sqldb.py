#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.datatype.sqldb` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import unittest

import sqlalchemy

from mentat.datatype.sqldb import (
    MODEL,
    DetectorModel,
    EventClassModel,
    EventClassState,
    EventReportModel,
    EventStatisticsModel,
    FilterModel,
    GroupModel,
    ItemChangeLogModel,
    NetworkModel,
    SettingsReportingModel,
    UserModel,
    jsondiff,
    usermodel_from_typeddict,
)
from mentat.services.sqlstorage import RetryingQuery

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatDatatypeSqldb(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.datatype.sqldb` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    def setUp(self):
        self.dbengine = sqlalchemy.create_engine("postgresql://mentat:mentat@localhost/mentat_utest", echo=self.verbose)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.dbengine)
        self.session = self.sessionmaker(query_cls=RetryingQuery)

        MODEL.metadata.drop_all(self.dbengine)
        MODEL.metadata.create_all(self.dbengine)

    def tearDown(self):
        self.session.close()
        self.session = None

    def test_01_user_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.UserModel`.
        """
        self.maxDiff = None

        user1 = UserModel(
            login="user1@cesnet.cz",
            fullname="First User",
            email="user1@cesnet.cz",
            organization="CESNET, z.s.p.o.",
        )
        user2 = UserModel(
            login="user2@cesnet.cz",
            fullname="Second User",
            email="user2@cesnet.cz",
            organization="CESNET, z.s.p.o.",
            roles=["admin"],
        )
        user3 = UserModel(
            login="USER3@CESNET.CZ",
            fullname="Third User",
            email="USER3@cesnet.cz",
            organization="CESNET, z.s.p.o.",
            roles=["user", "admin"],
            apikey="testapikey",
            locale="en",
            timezone="UTC",
        )

        # Add single user object to session
        self.session.add(user1)
        self.session.bulk_save_objects([user2, user3])
        self.session.commit()

        # Query for specific user and return exactly one object.
        result = self.session.query(UserModel).filter(UserModel.login == "user1@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user1@cesnet.cz', fullname='First User')>")
        self.assertEqual(result.__class__.__name__, "UserModel")
        self.assertTrue(result.to_dict())

        # Query for specific user and return first object.
        result = self.session.query(UserModel).filter(UserModel.login == "user2@cesnet.cz").first()
        self.assertEqual(repr(result), "<User(login='user2@cesnet.cz', fullname='Second User')>")
        self.assertTrue(result.to_dict())

        # Query for specific user and return all objects.
        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz").all()
        for res in result:
            self.assertEqual(repr(res), "<User(login='user3@cesnet.cz', fullname='Third User')>")
            self.assertTrue(res.to_dict())

        # Query for specific user and return all objects.
        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz")
        for res in result:
            self.assertEqual(repr(res), "<User(login='user3@cesnet.cz', fullname='Third User')>")
            self.assertTrue(res.to_dict())

        # Attempt to access each attribute in user object.
        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz").one()
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertFalse(result.logintime)
        self.assertEqual(result.login, "user3@cesnet.cz")
        self.assertEqual(result.fullname, "Third User")
        self.assertEqual(result.email, "user3@cesnet.cz")
        self.assertEqual(result.organization, "CESNET, z.s.p.o.")
        self.assertEqual(result.roles, ["user", "admin"])
        self.assertEqual(result.apikey, "testapikey")
        self.assertEqual(result.locale, "en")
        self.assertEqual(result.timezone, "UTC")

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.login = "user333@cesnet.cz"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz").first()
        self.assertEqual(result, None)
        result = self.session.query(UserModel).filter(UserModel.login == "user333@cesnet.cz").first()
        self.assertEqual(repr(result), "<User(login='user333@cesnet.cz', fullname='Third User')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(user1)
        self.session.commit()
        result = self.session.query(UserModel).filter(UserModel.login == "user1@cesnet.cz").first()
        self.assertEqual(result, None)

        user_from_dict = usermodel_from_typeddict(
            {
                "_id": "user@domain.org",
                "name": "Test User",
                "email": "user@domain.org",
                "organization": "Domain, org.",
                "roles": ["admin"],
            }
        )
        self.assertEqual(user_from_dict.login, "user@domain.org")
        self.assertEqual(user_from_dict.fullname, "Test User")
        self.assertEqual(user_from_dict.email, "user@domain.org")
        self.assertEqual(user_from_dict.organization, "Domain, org.")
        self.assertEqual(user_from_dict.roles, ["admin"])
        self.assertFalse(user_from_dict.enabled)

        user_from_dict = usermodel_from_typeddict(
            {
                "_id": "user@domain.org",
                "name": "Test User",
                "email": "user@domain.org",
                "organization": "Domain, org.",
                "roles": ["user", "admin"],
            }
        )
        self.assertEqual(user_from_dict.roles, ["user", "admin"])
        self.assertTrue(user_from_dict.enabled)

    def test_02_group_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.GroupModel`.
        """
        self.maxDiff = None

        group1 = GroupModel(
            name="abuse@cesnet.cz",
            source="manual",
            description="CESNET, z.s.p.o.",
            local_id="12345",
        )
        group2 = GroupModel(
            name="abuse@domain.org",
            source="manual",
            description="Domain Organization",
            parent=group1,
            local_id="67890",
        )

        self.session.add(group1)
        self.session.add_all([group2])
        self.session.commit()

        # Query for specific group and return exactly one object.
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result), "<Group(name='abuse@cesnet.cz')>")
        self.assertEqual(result.__class__.__name__, "GroupModel")
        self.assertEqual(result.parent_id, None)
        self.assertEqual(result.parent, None)
        self.assertEqual(repr(result.children), "[<Group(name='abuse@domain.org')>]")
        self.assertTrue(result.to_dict())

        # Query for specific group and return exactly one object.
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").first()
        self.assertEqual(repr(result), "<Group(name='abuse@domain.org')>")
        self.assertTrue(result.to_dict())

        # Attempt to access each attribute in user object.
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").one()
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertEqual(result.name, "abuse@domain.org")
        self.assertEqual(result.source, "manual")
        self.assertEqual(result.description, "Domain Organization")
        self.assertEqual(result.parent_id, 1)
        self.assertEqual(repr(result.parent), repr(group1))
        self.assertEqual(repr(result.children), "[]")
        self.assertEqual(result.local_id, "67890")

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.name = "abuse@another-domain.org"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").first()
        self.assertEqual(result, None)
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@another-domain.org").first()
        self.assertEqual(repr(result), "<Group(name='abuse@another-domain.org')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(group1)
        self.session.commit()
        result = self.session.query(UserModel).filter(UserModel.login == "abuse@cesnet.cz").first()
        self.assertEqual(result, None)

    def test_03_group_members_managers(self):  # pylint: disable=locally-disabled,too-many-statements
        """
        Perform tests of group members and managers.
        """
        self.maxDiff = None

        user1 = UserModel(
            login="user1@cesnet.cz",
            fullname="First User",
            email="user1@cesnet.cz",
            organization="CESNET, z.s.p.o.",
        )
        user2 = UserModel(
            login="user2@cesnet.cz",
            fullname="Second User",
            email="user2@cesnet.cz",
            organization="CESNET, z.s.p.o.",
            roles=["admin"],
        )
        user3 = UserModel(
            login="user3@cesnet.cz",
            fullname="Third User",
            email="user3@cesnet.cz",
            organization="CESNET, z.s.p.o.",
            roles=["user", "admin"],
            locale="en",
            timezone="UTC",
        )

        group1 = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")
        group2 = GroupModel(name="abuse@domain.org", source="manual", description="Domain Organization")

        # Test the membership relation from both directions.
        group1.members.append(user1)
        group1.members.append(user3)
        user2.memberships.append(group2)

        # Test the management relation from both directions.
        group1.managers.append(user2)
        user1.managements.append(group2)

        self.session.add_all([group1, group2])
        self.session.commit()

        # Verify from group perspective.
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result), "<Group(name='abuse@cesnet.cz')>")
        self.assertEqual(
            repr(result.members),
            "[<User(login='user1@cesnet.cz', fullname='First User')>, <User(login='user3@cesnet.cz', fullname='Third User')>]",
        )
        self.assertEqual(
            repr(result.managers),
            "[<User(login='user2@cesnet.cz', fullname='Second User')>]",
        )

        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").one()
        self.assertEqual(repr(result), "<Group(name='abuse@domain.org')>")
        self.assertEqual(
            repr(result.members),
            "[<User(login='user2@cesnet.cz', fullname='Second User')>]",
        )
        self.assertEqual(
            repr(result.managers),
            "[<User(login='user1@cesnet.cz', fullname='First User')>]",
        )

        # Verify from user perspective.
        result = self.session.query(UserModel).filter(UserModel.login == "user1@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user1@cesnet.cz', fullname='First User')>")
        self.assertEqual(repr(result.memberships), "[<Group(name='abuse@cesnet.cz')>]")
        self.assertEqual(repr(result.managements), "[<Group(name='abuse@domain.org')>]")

        result = self.session.query(UserModel).filter(UserModel.login == "user2@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user2@cesnet.cz', fullname='Second User')>")
        self.assertEqual(repr(result.memberships), "[<Group(name='abuse@domain.org')>]")
        self.assertEqual(repr(result.managements), "[<Group(name='abuse@cesnet.cz')>]")

        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user3@cesnet.cz', fullname='Third User')>")
        self.assertEqual(repr(result.memberships), "[<Group(name='abuse@cesnet.cz')>]")
        self.assertEqual(repr(result.managements), "[]")

        # Verify, that user deletion does not delete group.
        group_json_a = group1.to_json()
        self.session.delete(user1)
        self.session.commit()
        result = self.session.query(UserModel).filter(UserModel.login == "user1@cesnet.cz").first()
        self.assertEqual(result, None)
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result), "<Group(name='abuse@cesnet.cz')>")
        self.assertEqual(
            repr(result.members),
            "[<User(login='user3@cesnet.cz', fullname='Third User')>]",
        )
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").one()
        self.assertEqual(repr(result), "<Group(name='abuse@domain.org')>")
        self.assertEqual(repr(result.managers), "[]")
        group_json_b = group1.to_json()
        self.assertTrue(jsondiff(group_json_a, group_json_b))

        # Verify, that group deletion does not delete user.
        user_json_a = user2.to_json()
        self.session.delete(group1)
        self.session.commit()
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").first()
        self.assertEqual(result, None)
        result = self.session.query(UserModel).filter(UserModel.login == "user2@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user2@cesnet.cz', fullname='Second User')>")
        result = self.session.query(UserModel).filter(UserModel.login == "user3@cesnet.cz").one()
        self.assertEqual(repr(result), "<User(login='user3@cesnet.cz', fullname='Third User')>")
        user_json_b = user2.to_json()
        self.assertTrue(jsondiff(user_json_a, user_json_b))

    def test_04_network_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.NetworkModel`.
        """
        self.maxDiff = None

        group1 = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")

        network1 = NetworkModel(
            group=group1,
            netname="NET1",
            source="manual",
            network="192.168.0.0/24",
            description="Descr.",
            local_id="12345ABC",
        )
        self.assertIsNotNone(network1)
        network2 = NetworkModel(group=group1, netname="NET2", source="manual", network="10.0.0.0/8")
        self.assertIsNotNone(network2)
        network3 = NetworkModel(group=group1, netname="NET3", source="manual", network="::1/128")
        self.assertIsNotNone(network3)
        network4 = NetworkModel(group=group1, netname="NET4", source="manual", network="2001:ff::/64")
        self.assertIsNotNone(network4)

        self.session.add(group1)
        self.session.commit()

        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(len(result.networks), 4)
        for net in result.networks:
            self.assertTrue(net.netname in ["NET1", "NET2", "NET3", "NET4"])
            self.assertTrue(net.source == "manual")
            self.assertTrue(net.network in ["192.168.0.0/24", "10.0.0.0/8", "::1", "2001:ff::/64"])

        result = self.session.query(NetworkModel).filter(NetworkModel.netname == "NET1").one()
        self.assertEqual(repr(result), "<Network(netname='NET1',network='192.168.0.0/24')>")
        self.assertEqual(result.__class__.__name__, "NetworkModel")
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertEqual(result.netname, "NET1")
        self.assertEqual(result.source, "manual")
        self.assertEqual(result.network, "192.168.0.0/24")
        self.assertEqual(result.description, "Descr.")
        self.assertEqual(result.group_id, 1)
        self.assertEqual(result.local_id, "12345ABC")
        self.assertEqual(repr(result.group), "<Group(name='abuse@cesnet.cz')>")
        self.assertTrue(result.to_dict())

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.netname = "NET11"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(NetworkModel).filter(NetworkModel.netname == "NET1").first()
        self.assertEqual(result, None)
        result = self.session.query(NetworkModel).filter(NetworkModel.netname == "NET11").first()
        self.assertEqual(repr(result), "<Network(netname='NET11',network='192.168.0.0/24')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(network2)
        self.session.commit()
        result = self.session.query(NetworkModel).filter(NetworkModel.netname == "NET2").first()
        self.assertEqual(result, None)
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result), "<Group(name='abuse@cesnet.cz')>")

        # Attempt to delete parent object.
        self.session.delete(group1)
        self.session.commit()
        result = self.session.query(NetworkModel).count()
        self.assertEqual(result, 0)

    def test_05_filter_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.FilterModel`.
        """
        self.maxDiff = None

        group1 = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")

        filter1 = FilterModel(
            group=group1,
            name="FLT1",
            source_based=True,
            type="basic",
            filter="Source.IP4 == 127.0.0.1",
            description="DESC1",
        )
        self.assertIsNotNone(filter1)
        filter2 = FilterModel(
            group=group1,
            name="FLT2",
            source_based=True,
            type="advanced",
            filter="Source.IP4 == 127.0.0.2",
            description="DESC2",
        )
        self.assertIsNotNone(filter2)

        self.session.add(group1)
        self.session.commit()

        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(len(result.filters), 2)
        for flt in result.filters:
            self.assertTrue(flt.name in ["FLT1", "FLT2"])
            self.assertTrue(flt.type in ["basic", "advanced"])

        result = self.session.query(FilterModel).filter(FilterModel.name == "FLT1").one()
        self.assertEqual(repr(result), "<Filter(name='FLT1')>")
        self.assertEqual(result.__class__.__name__, "FilterModel")
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertEqual(result.name, "FLT1")
        self.assertEqual(result.type, "basic")
        self.assertEqual(result.filter, "Source.IP4 == 127.0.0.1")
        self.assertEqual(result.description, "DESC1")
        self.assertEqual(result.group_id, 1)
        self.assertEqual(repr(result.group), "<Group(name='abuse@cesnet.cz')>")
        self.assertTrue(result.to_dict())

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.name = "FLT11"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(FilterModel).filter(FilterModel.name == "FLT1").first()
        self.assertEqual(result, None)
        result = self.session.query(FilterModel).filter(FilterModel.name == "FLT11").one()
        self.assertEqual(repr(result), "<Filter(name='FLT11')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(filter2)
        self.session.commit()
        result = self.session.query(FilterModel).filter(FilterModel.name == "FLT2").first()
        self.assertEqual(result, None)
        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result), "<Group(name='abuse@cesnet.cz')>")

        # Attempt to delete parent object.
        self.session.delete(group1)
        self.session.commit()
        result = self.session.query(FilterModel).count()
        self.assertEqual(result, 0)

    def test_06_setrep_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.SettingsReportingModel`.
        """
        self.maxDiff = None

        group1 = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")

        settings1 = SettingsReportingModel(group=group1)  # pylint: disable=locally-disabled,unused-variable
        settings2 = SettingsReportingModel(emails_info=["abuse@domain"], redirect=True)  # pylint: disable=locally-disabled,unused-variable

        group2 = GroupModel(
            name="abuse@domain.org",
            source="manual",
            description="Domain Organization",
            settings_rep=settings2,
        )

        self.session.add(group1)
        self.session.add(group2)
        self.session.commit()

        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.assertEqual(repr(result.settings_rep), "<SettingsReporting(id='1',group_id='1')>")
        self.assertEqual(result.settings_rep.__class__.__name__, "SettingsReportingModel")
        self.assertTrue(result.settings_rep.to_dict())
        self.assertEqual(result.settings_rep.mode, None)

        result = self.session.query(GroupModel).filter(GroupModel.name == "abuse@domain.org").one()
        self.assertEqual(repr(result.settings_rep), "<SettingsReporting(id='2',group_id='2')>")
        self.assertEqual(result.settings_rep.mode, None)
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertEqual(result.settings_rep.mode, None)
        self.assertEqual(result.settings_rep.emails_info, ["abuse@domain"])
        self.assertEqual(result.settings_rep.redirect, True)
        self.assertEqual(result.settings_rep.locale, None)
        self.assertEqual(result.settings_rep.timezone, None)

        # Attempt to change something and make diff.
        settings_json_a = settings1.to_json()
        settings1.mode = "extra"
        self.session.commit()
        settings_json_b = settings1.to_json()
        self.assertTrue(jsondiff(settings_json_a, settings_json_b))

        # Attempt to delete parent object.
        self.session.delete(group1)
        self.session.commit()
        result = self.session.query(SettingsReportingModel).count()
        self.assertEqual(result, 1)
        self.session.delete(group2)
        self.session.commit()
        result = self.session.query(SettingsReportingModel).count()
        self.assertEqual(result, 0)

    def test_07_event_statistics_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.EventStatisticsModel`.
        """
        self.maxDiff = None

        dt_from = datetime.datetime(2017, 1, 1, 12, 0, 0)
        dt_to = datetime.datetime(2017, 1, 1, 12, 5, 0)
        delta = dt_to - dt_from
        interval = "{}_{}".format(dt_from.strftime("%FT%T"), dt_to.strftime("%FT%T"))

        stats1 = EventStatisticsModel(
            dt_from=dt_from,
            dt_to=dt_to,
            count=5555,
            stats_overall={
                "x": {"y": 5, "z": [0, 1, 2]},
                "a": None,
                "b": "test",
                "c": [{"u": 1, "v": 2}],
            },
            stats_internal={"i": ["uvw"]},
            stats_external={},
        )
        stats1.calculate_interval()
        stats1.calculate_delta()

        self.session.add(stats1)
        self.session.commit()

        result = self.session.query(EventStatisticsModel).filter(EventStatisticsModel.interval == interval).one()
        self.assertEqual(result.interval, interval)
        self.assertEqual(result.dt_from, dt_from)
        self.assertEqual(result.dt_to, dt_to)
        self.assertEqual(result.delta, delta.total_seconds())
        self.assertEqual(
            result.stats_overall,
            {
                "x": {"y": 5, "z": [0, 1, 2]},
                "a": None,
                "b": "test",
                "c": [{"u": 1, "v": 2}],
            },
        )
        self.assertEqual(result.stats_internal, {"i": ["uvw"]})
        self.assertEqual(result.stats_external, {})
        self.assertEqual(
            repr(result),
            "<EventStatistics(interval='2017-01-01T12:00:00_2017-01-01T12:05:00',delta='300')>",
        )
        self.assertEqual(result.__class__.__name__, "EventStatisticsModel")

    def test_08_event_report_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.EventReportModel`.
        """
        self.maxDiff = None

        group = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")

        dt_from = datetime.datetime(2017, 1, 1, 12, 0, 0)
        dt_to = datetime.datetime(2017, 1, 1, 12, 10, 0)
        delta = dt_to - dt_from

        report = EventReportModel(
            groups=[group],
            label="REPORTID",
            severity="low",
            type="summary",
            message="Report message",
            dt_from=dt_from,
            dt_to=dt_to,
            evcount_rep=1,
            evcount_all=2,
            evcount_new=3,
            evcount_flt=4,
            evcount_flt_blk=5,
            evcount_det=6,
            evcount_det_blk=7,
            evcount_thr=6,
            evcount_thr_blk=7,
            evcount_rlp=8,
            mail_to=["abuse@cesnet.cz"],
            mail_dt=dt_from,
            mail_res="Result",
            statistics={
                "x": {"y": 5, "z": [0, 1, 2]},
                "a": None,
                "b": "test",
                "c": [{"u": 1, "v": 2}],
            },
            filtering=[{"i": ["uvw"]}],
        )
        report.calculate_delta()

        self.session.add(group)
        self.session.commit()

        result = self.session.query(EventReportModel).filter(EventReportModel.label == "REPORTID").one()
        self.assertEqual(result.label, "REPORTID")
        self.assertEqual(result.dt_from, dt_from)
        self.assertEqual(result.dt_to, dt_to)
        self.assertEqual(result.delta, delta.total_seconds())
        self.assertEqual(
            result.statistics,
            {
                "x": {"y": 5, "z": [0, 1, 2]},
                "a": None,
                "b": "test",
                "c": [{"u": 1, "v": 2}],
            },
        )
        self.assertEqual(result.filtering, [{"i": ["uvw"]}])
        self.assertEqual(repr(result), "<EventReport(label='REPORTID')>")
        self.assertEqual(result.__class__.__name__, "EventReportModel")
        self.assertTrue(result.to_dict())

    def test_09_changelog_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.ItemChangeLogModel`.
        """
        self.maxDiff = None

        author = UserModel(
            login="user1@cesnet.cz",
            fullname="First User",
            email="user1@cesnet.cz",
            organization="CESNET, z.s.p.o.",
        )
        chlog1 = ItemChangeLogModel(
            model="modelname",
            model_id=1,
            endpoint="model.create",
            module="model",
            operation="create",
            before="Before",
            after="After",
        )
        chlog1.calculate_diff()
        chlog2 = ItemChangeLogModel(
            author=author,
            model="anothermodelname",
            model_id=2,
            endpoint="anothermodel.update",
            module="anothermodel",
            operation="update",
            before="Another before",
            after="Another after",
            diff="Another test difference",
        )
        chlog2.calculate_diff()

        self.session.add(chlog1)
        self.session.add(chlog2)
        self.session.commit()

        result = self.session.query(ItemChangeLogModel).filter(ItemChangeLogModel.operation == "create").first()
        self.assertEqual(result.author, None)
        self.assertEqual(result.model, "modelname")
        self.assertEqual(result.model_id, 1)
        self.assertEqual(result.endpoint, "model.create")
        self.assertEqual(result.module, "model")
        self.assertEqual(result.operation, "create")
        self.assertEqual(result.before, "Before")
        self.assertEqual(result.after, "After")
        self.assertTrue(result.diff)
        self.assertEqual(
            repr(result),
            "<ItemChangelog(author='None',operation='create',model='modelname#1')>",
        )
        self.assertEqual(result.__class__.__name__, "ItemChangeLogModel")

        result = self.session.query(ItemChangeLogModel).filter(ItemChangeLogModel.operation == "update").first()
        self.assertEqual(result.author, author)
        self.assertEqual(result.model, "anothermodelname")
        self.assertEqual(result.model_id, 2)
        self.assertEqual(result.endpoint, "anothermodel.update")
        self.assertEqual(result.module, "anothermodel")
        self.assertEqual(result.operation, "update")
        self.assertEqual(result.before, "Another before")
        self.assertEqual(result.after, "Another after")
        self.assertTrue(result.diff)
        self.assertEqual(
            repr(result),
            "<ItemChangelog(author='user1@cesnet.cz',operation='update',model='anothermodelname#2')>",
        )

        # Verify that when author account gets deleted the changelog will remain in database.
        self.session.delete(author)
        self.session.commit()
        result = self.session.query(ItemChangeLogModel).filter(ItemChangeLogModel.operation == "update").first()
        self.assertEqual(result.author, None)

    def test_10_detector_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.DetectorModel`.
        """
        self.maxDiff = None

        detector1 = DetectorModel(
            name="DETECTOR 1",
            source="manual",
            description="TEST DETECTOR 1",
            credibility=0.34,
        )
        detector2 = DetectorModel(
            name="DETECTOR 2",
            source="manual",
            description="TEST DETECTOR 2",
            credibility=0.79,
        )

        self.session.add(detector1)
        self.session.add_all([detector2])
        self.session.commit()

        # Query for a specific detector and return exactly one object.
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 1").one()
        self.assertEqual(repr(result), "<Detector(name='DETECTOR 1')>")
        self.assertEqual(result.__class__.__name__, "DetectorModel")
        self.assertTrue(result.to_dict())

        # Query for a specific detector and return exactly one object.
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 2").first()
        self.assertEqual(repr(result), "<Detector(name='DETECTOR 2')>")
        self.assertTrue(result.to_dict())

        # Attempt to access each attribute in the detector object.
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 2").one()
        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertEqual(result.name, "DETECTOR 2")
        self.assertEqual(result.source, "manual")
        self.assertEqual(result.description, "TEST DETECTOR 2")
        self.assertEqual(result.credibility, 0.79)

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.name = "DETECTOR 2 changed"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 2").first()
        self.assertEqual(result, None)
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 2 changed").first()
        self.assertEqual(repr(result), "<Detector(name='DETECTOR 2 changed')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(detector1)
        self.session.commit()
        result = self.session.query(DetectorModel).filter(DetectorModel.name == "DETECTOR 1").first()
        self.assertEqual(result, None)

    def test_11_event_class_model(self):
        """
        Perform initial minimal tests of :py:class:`mentat.datatype.sqldb.EventClassModel`.
        """
        event_class1 = EventClassModel(
            name="attempt-exploit",
            source_based=False,
            label_en="The machine attempted to exploit some well-known service.",
            label_cz="Stroj se pokoušel zneužít některou známou službu.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-exploit",
            displayed_main=["ConnCount", "protocols"],
            displayed_source=["Port"],
            displayed_target=["Port", "ips"],
            rule="Category in ['Attempt.Exploit']",
            severity="medium",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        event_class2 = EventClassModel(
            name="vulnerable-implementation",
            source_based=True,
            label_en="Vulnerable version of software was found.",
            label_cz="Byla nalezena zranitelná verze softvéru.",
            reference="",
            displayed_main=["Ref"],
            displayed_source=["Ref", "Hostname", "Proto", "Port", "services"],
            displayed_target=[],
            rule="Category in ['Vulnerable.Open'] and Ref like ['cvr:']",
            severity="medium",
            subclassing="Ref",
            state=EventClassState.ENABLED,
        )

        self.session.add(event_class1)
        self.session.add_all([event_class2])
        self.session.commit()

        # Query for a specific event class and return exactly one object.
        result = self.session.query(EventClassModel).filter(EventClassModel.name == "attempt-exploit").one()
        self.assertEqual(repr(result), "<EventClass(name='attempt-exploit')>")
        self.assertEqual(result.__class__.__name__, "EventClassModel")
        self.assertTrue(result.to_dict())
        self.assertEqual(len(result.get_inspection_rules()), 1)
        self.assertFalse(result.is_source_based())
        self.assertTrue(result.is_target_based())
        self.assertEqual(result.get_type(), "Target-based")

        # Check should_be_displayed method of the result.
        self.assertTrue(result.should_be_displayed("source", "Port"))
        self.assertFalse(result.should_be_displayed("source", "Proto"))
        self.assertFalse(result.should_be_displayed("source", "Hostname"))
        self.assertTrue(result.should_be_displayed("target", "ips"))
        self.assertTrue(result.should_be_displayed("target", "Port"))
        self.assertFalse(result.should_be_displayed("target", "Proto"))
        self.assertFalse(result.should_be_displayed("target", "Hostname"))
        self.assertTrue(result.should_be_displayed("main", "protocols"))
        self.assertTrue(result.should_be_displayed("main", "ConnCount"))
        self.assertFalse(result.should_be_displayed("main", "FlowCount"))
        self.assertFalse(result.should_be_displayed("main", "Ref"))

        # Attempt to access each attribute in the event class object.
        result = self.session.query(EventClassModel).filter(EventClassModel.name == "vulnerable-implementation").one()
        self.assertEqual(repr(result), "<EventClass(name='vulnerable-implementation')>")
        self.assertTrue(result.to_dict())
        self.assertEqual(len(result.get_inspection_rules()), 2)
        self.assertTrue(result.is_source_based())
        self.assertFalse(result.is_target_based())
        self.assertEqual(result.get_type(), "Source-based")

        self.assertTrue(result.id)
        self.assertTrue(result.createtime)
        self.assertTrue(result.last_update)
        self.assertEqual(result.state, EventClassState.ENABLED)
        self.assertEqual(result.name, "vulnerable-implementation")
        self.assertTrue(result.source_based)
        self.assertEqual(result.label_en, "Vulnerable version of software was found.")
        self.assertEqual(result.label_cz, "Byla nalezena zranitelná verze softvéru.")
        self.assertEqual(result.reference, "")
        self.assertEqual(result.rule, "Category in ['Vulnerable.Open'] and Ref like ['cvr:']")
        self.assertEqual(result.severity, "medium")
        self.assertEqual(result.subclassing, "Ref")

        # Attempt to change an object attribute and verify the change.
        result_json_a = result.to_json()
        result.name = "vulnerable-implementation changed"
        self.session.add(result)
        self.session.commit()
        result = self.session.query(EventClassModel).filter(EventClassModel.name == "vulnerable-implementation").first()
        self.assertEqual(result, None)
        result = (
            self.session.query(EventClassModel)
            .filter(EventClassModel.name == "vulnerable-implementation changed")
            .first()
        )
        self.assertEqual(repr(result), "<EventClass(name='vulnerable-implementation changed')>")
        result_json_b = result.to_json()
        self.assertTrue(jsondiff(result_json_a, result_json_b))

        # Attempt to delete an object and verify the change.
        self.session.delete(event_class1)
        self.session.commit()
        result = self.session.query(EventClassModel).filter(EventClassModel.name == "attempt-exploit").first()
        self.assertEqual(result, None)


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
