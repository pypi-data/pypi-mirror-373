#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Base library for web interface unit test database fixtures.
"""

import hawat.const
from mentat.datatype.sqldb import EventClassState

DEMO_GROUP_A = "DEMO_GROUP_A"
DEMO_GROUP_B = "DEMO_GROUP_B"

DEMO_DETECTOR_A = "DEMO_DETECTOR_A"
DEMO_DETECTOR_B = "DEMO_DETECTOR_B"

DEMO_EVENT_CLASS = "DEMO_EVENT_CLASS"


def get_fixtures_db(app):
    """
    Get general database object fixtures.
    """
    fixture_list = []

    user_model = app.get_model(hawat.const.MODEL_USER)
    group_model = app.get_model(hawat.const.MODEL_GROUP)
    detector_model = app.get_model(hawat.const.MODEL_DETECTOR)
    event_class_model = app.get_model(hawat.const.MODEL_EVENT_CLASS)

    def _gen_user(user_name):
        user = user_model(
            login=user_name,
            fullname=f"Demo {user_name[0].upper() + user_name[1:]}",
            email=f"{user_name}@bogus-domain.org",
            roles=list({hawat.const.ROLE_USER, user_name}),
            enabled=True,
            apikey=f"apikey-{user_name}",
        )
        fixture_list.append(user)
        return user

    account_user = _gen_user(hawat.const.ROLE_USER)
    account_developer = _gen_user(hawat.const.ROLE_DEVELOPER)
    account_maintainer = _gen_user(hawat.const.ROLE_MAINTAINER)
    account_admin = _gen_user(hawat.const.ROLE_ADMIN)

    def _gen_event_class(ec_name):
        event_class = event_class_model(
            name=ec_name,
            label_en="English label",
            label_cz="Czech label",
            reference="cesnet.cz",
            displayed_main=["ConnCount"],
            displayed_source=["Port"],
            displayed_target=["Proto"],
            rule='Category in ["Malware.Virus"]',
            severity="medium",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        fixture_list.append(event_class)

    _gen_event_class(DEMO_EVENT_CLASS)

    def _gen_detector(det_name, descr, cred=1.0):
        detector = detector_model(
            name=det_name,
            source="manual",
            credibility=cred,
            description=descr,
        )
        fixture_list.append(detector)

    _gen_detector(DEMO_DETECTOR_A, "DEMO_DETECTOR_A")
    _gen_detector(DEMO_DETECTOR_B, "DEMO_DETECTOR_B")

    def _gen_group(group_name, group_descr):
        group = group_model(
            name=group_name,
            description=group_descr,
            enabled=True,
        )
        fixture_list.append(group)
        return group

    group_a = _gen_group(DEMO_GROUP_A, "Demo Group A")
    group_b = _gen_group(DEMO_GROUP_B, "Demo Group B")
    assert group_b  # Deliberately empty group

    group_a.members.append(account_user)
    group_a.members.append(account_developer)
    group_a.members.append(account_maintainer)
    group_a.members.append(account_admin)

    group_a.managers.append(account_developer)
    group_a.managers.append(account_maintainer)

    return fixture_list
