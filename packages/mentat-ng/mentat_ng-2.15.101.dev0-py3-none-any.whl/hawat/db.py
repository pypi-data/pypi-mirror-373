#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains database layer for *Hawat* application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask_sqlalchemy
from flask_sqlalchemy.model import Model
from sqlalchemy.orm import declarative_base

_DB = None
MODEL = declarative_base(cls=Model)


def db_setup(**kwargs):
    """
    Opens a new database connection if there is none yet for the
    current application context.

    :return: Database storage handler.
    :rtype: flask_sqlalchemy.SQLAlchemy
    """
    if not kwargs:
        kwargs = {"model_class": MODEL}

    global _DB  # pylint: disable=locally-disabled,global-statement
    if not _DB:
        _DB = flask_sqlalchemy.SQLAlchemy(**kwargs)

    return _DB


def db_get():
    """
    Convenience method.
    """
    return _DB


def db_session():
    """
    Convenience method.
    """
    return db_get().session


def db_query(dbmodel):
    """
    Convenience method.
    """
    return db_session().query(dbmodel)
