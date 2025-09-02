#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Database storage abstraction layer. The current implementation is based on the
awesome `SQLAlchemy <http://www.sqlalchemy.org/>`__ library.

.. warning::

    Current implementation is for optimalization purposes using some advanced
    schema features provided by the `PostgreSQL <https://www.postgresql.org/>`__
    database and thus no other engines are currently supported.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy

import sqlalchemy

from mentat.const import CKEY_CORE_DATABASE, CKEY_CORE_DATABASE_SQLSTORAGE
from mentat.datatype.sqldb import MODEL

_MANAGER = None


class RetryingQuery(sqlalchemy.orm.Query):
    """
    An override of SQLAlchemy's Query class, allowing for recovery from a lost DB
    connection.
    """

    def _execute_and_instances(self, querycontext):
        for _ in range(2):
            try:
                return super()._execute_and_instances(querycontext)
            except sqlalchemy.exc.OperationalError:
                self.session.close()
                continue
        return None


class StorageService:
    """
    Proxy object for working with persistent SQL storages. Maintains and provides
    access to database engine, session maker and session proxies.
    """

    def __init__(self, **enginecfg):
        """
        Open and cache connection to SQL storage. The connection arguments for
        database engine are passed directly to :py:func:`sqlalchemy.engine_from_config`
        method. The appropriate prefix is the empty string.

        :param enginecfg: Connection arguments.
        """
        self.dbengine = sqlalchemy.engine_from_config(enginecfg, prefix="")
        self.sessionmaker = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=self.dbengine))
        self._session = self.sessionmaker(query_cls=RetryingQuery)

    def __del__(self):
        self.close()

    def close(self):
        """
        Close current database connection.
        """
        self.session_close()
        self.dbengine = None

    @property
    def session(self):
        """ """
        if not self._session:
            self._session = self.sessionmaker(query_cls=RetryingQuery)
        return self._session

    def session_close(self):
        """ """
        if self._session:
            self.sessionmaker.remove()
            self._session = None

    def session_new(self):
        """
        Close existing session and create new fresh database session.
        """
        self.session_close()
        return self.session

    def database_create(self):
        """
        Create database SQL schema.
        """
        MODEL.metadata.create_all(self.dbengine)

    def database_drop(self):
        """
        Drop database SQL schema.
        """
        MODEL.metadata.drop_all(self.dbengine)


class StorageServiceManager:
    """
    Class representing a custom _StorageServiceManager_ capable of understanding
    and parsing Mentat system core configurations and enabling easy access to
    preconfigured database collections via indirrect handles (identifiers).
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize a _StorageServiceManager_ proxy object with full core configuration
        tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = {}
        self._storage = None
        self._configure_dbconfig(core_config, updates)

    def _configure_dbconfig(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = copy.deepcopy(core_config[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_SQLSTORAGE])

        if updates and CKEY_CORE_DATABASE in updates and CKEY_CORE_DATABASE_SQLSTORAGE in updates[CKEY_CORE_DATABASE]:
            self._dbconfig.update(updates[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_SQLSTORAGE])

    # ---------------------------------------------------------------------------

    def close(self):
        """
        Close internal storage connection.
        """
        if self._storage:
            self._storage.close()
            self._storage = None

    def service(self):
        """
        Return handle to storage connection service according to internal configurations.

        :return: Reference to storage service.
        :rtype: mentat.services.sqlstorage.StorageService
        """
        if not self._storage:
            self._storage = StorageService(**self._dbconfig)
        return self._storage


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`mentat.services.sqlstorage.StorageServiceManager`
    instance at module level and store the refence within module.

    :param dict core_config: Mentat core configuration structure.
    :param dict updates: Optional configuration updates (same structure as ``core_config``).
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = StorageServiceManager(core_config, updates)


def set_manager(new_manager):
    """
    Set manager from outside the module. This should be used only when you know
    exactly what you are doing.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = new_manager


def manager():
    """
    Obtain reference to :py:class:`mentat.services.sqlstorage.StorageServiceManager`
    instance stored at module level.

    :return: Storage service manager reference.
    :rtype: mentat.services.sqlstorage.StorageServiceManager
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`mentat.services.sqlstorage.StorageService`
    instance from module level manager.

    :return: Storage service reference.
    :rtype: mentat.services.sqlstorage.StorageServiceManager
    """
    return manager().service()


def close():
    """
    Close database connection on :py:class:`mentat.services.sqlstorage.StorageService`
    instance from module level manager.
    """
    return manager().close()
