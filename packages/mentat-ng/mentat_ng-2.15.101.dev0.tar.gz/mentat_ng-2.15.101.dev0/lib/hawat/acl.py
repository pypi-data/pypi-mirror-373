#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains ACL features for Hawat.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


from functools import partial

import flask_principal

import hawat.const

MembershipNeed = partial(flask_principal.Need, "membership")  # pylint: disable=locally-disabled,invalid-name
MembershipNeed.__doc__ = """A need with the method preset to `"membership"`."""

ManagementNeed = partial(flask_principal.Need, "management")  # pylint: disable=locally-disabled,invalid-name
ManagementNeed.__doc__ = """A need with the method preset to `"management"`."""


ROLE_NAME_ADMIN = hawat.const.ROLE_ADMIN
ROLE_NAME_MAINTAINER = hawat.const.ROLE_MAINTAINER
ROLE_NAME_POWER = "power"
ROLE_NAME_DEVELOPER = hawat.const.ROLE_DEVELOPER
ROLE_NAME_USER = hawat.const.ROLE_USER
ROLE_NAME_ANY = "any"


PERMISSION_ADMIN = flask_principal.Permission(flask_principal.RoleNeed(ROLE_NAME_ADMIN))
"""
The :py:class:`flask_principal.Permission` permission for users with *admin* role
(ultimate power-user with unrestricted access to the whole system).
"""

PERMISSION_MAINTAINER = flask_principal.Permission(flask_principal.RoleNeed(ROLE_NAME_MAINTAINER))
"""
The :py:class:`flask_principal.Permission` permission for users with *maintainer* role
(power-users with slightly more restricted access to the system than *admin*).
"""

PERMISSION_POWER = flask_principal.Permission(
    flask_principal.RoleNeed(ROLE_NAME_ADMIN),
    flask_principal.RoleNeed(ROLE_NAME_MAINTAINER),
)
"""
The concatenated :py:class:`flask_principal.Permission` permission for any power-user role
(*admin* or *maintainer*).
"""

PERMISSION_DEVELOPER = flask_principal.Permission(flask_principal.RoleNeed(ROLE_NAME_DEVELOPER))
"""
The :py:class:`flask_principal.Permission` permission for users with *developer* role
(system developers with access to additional development and debugging data output).
"""

PERMISSION_USER = flask_principal.Permission(flask_principal.RoleNeed(ROLE_NAME_USER))
"""
The :py:class:`flask_principal.Permission` permission for regular users with *user* role.
"""

PERMISSION_ANY = flask_principal.Permission(
    flask_principal.RoleNeed(ROLE_NAME_ADMIN),
    flask_principal.RoleNeed(ROLE_NAME_MAINTAINER),
    flask_principal.RoleNeed(ROLE_NAME_DEVELOPER),
    flask_principal.RoleNeed(ROLE_NAME_USER),
)
"""
The concatenated :py:class:`flask_principal.Permission` permission for any user role
(*admin*, *maintainer*, *developer* or *user*).
"""

PERMISSIONS = {
    ROLE_NAME_ADMIN: PERMISSION_ADMIN,
    ROLE_NAME_MAINTAINER: PERMISSION_MAINTAINER,
    ROLE_NAME_POWER: PERMISSION_POWER,
    ROLE_NAME_DEVELOPER: PERMISSION_DEVELOPER,
    ROLE_NAME_USER: PERMISSION_USER,
    ROLE_NAME_ANY: PERMISSION_ANY,
}
"""
Map for accessing permission objects by name.
"""
