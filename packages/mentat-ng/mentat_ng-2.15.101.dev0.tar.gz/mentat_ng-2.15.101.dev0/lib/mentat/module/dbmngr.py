#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing database management functions and features.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-dbmngr.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-dbmngr.py --debug

    # Run with increased logging level.
    mentat-dbmngr.py --log-level debug

    # Perform initial database schema creation (both IDEA event and metadata dbs).
    mentat-dbmngr.py --command init

    # Reinitialize metadata database (drop and create, data destructive!).
    mentat-dbmngr.py --command reinit-main

    # Rebuild all IDEA event database indices.
    mentat-dbmngr.py --command reindex-event

    # Insert/remove demonstration data (accounts, groups, filters, networks and event classes).
    mentat-dbmngr.py --command fixtures-add
    mentat-dbmngr.py --command fixtures-remove

    # Insert event classes into database.
    mentat-dbmngr.py --command event-classes-add

    # Add new user account to the database. Usefull for creating initial account
    # after fresh installation. Note the use of double quotes to pass values
    # containing spaces (name, organization) and the use of commas to pass multiple
    # roles:
    mentat-dbmngr.py --command user-add login=admin "fullname=Clark Kent" email=kent@dailyplanet.com "organization=Daily Planet, inc." roles=user,admin


Available script commands
-------------------------

``init`` (*default*)
    Perform necessary database initializations including creating all required
    indices.

``fixtures-add``
    Populate database with demonstration objects - fixtures (user accounts and groups).

``fixtures-remove``
    Remove demonstration objects from database - fixtures (user accounts and groups).

``event-classes-add``
    Populate database with event classes.

``reinit-main``
    Reinitialize main database (drop whole database and recreate).

``reindex-event``
    Rebuild event database indices (drop all indices and recreate).

``user-add``
    Add new user account into the database.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.zenscript

import mentat.script.fetcher
from mentat.datatype.sqldb import UserModel
from mentat.fixtures import MentatFixtures


class MentatDbmngrScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing database management functions
    and features.
    """

    # List of configuration keys.
    CONFIG_ADDITIONAL_ARGS = "additional_args"

    def __init__(self):
        """
        Initialize dbmngr script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent constructor.
        """
        self.eventservice = None
        self.sqlservice = None

        super().__init__(description="mentat-dbmngr.py - Mentat database management script")

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser. This method overrides the
        base implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this script object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for custom script arguments.
        #
        arggroup_script = argparser.add_argument_group("custom script arguments")
        arggroup_script.add_argument("additional_args", nargs="*", help="optional additional arguments")

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default script configurations. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = ((self.CONFIG_ADDITIONAL_ARGS, []),) + cfgs
        return super()._init_config(cfgs, **kwargs)

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "init"

    def cbk_command_init(self):
        """
        Implementation of the **init** command.

        Perform necessary database initializations including creating all
        required indices.
        """
        self.logger.info("Initializing main database.")
        self.sqlservice.database_create()
        self.logger.info("Initializing event database.")
        self.eventservice.database_create()
        self.logger.info("Initializing event database indices.")
        self.eventservice.index_create()

        return self.RESULT_SUCCESS

    def cbk_command_fixtures_add(self):
        """
        Implementation of the **fixtures-add** command.

        Populate database with demonstration objects - fixtures (user accounts
        and groups).
        """
        self.logger.info("Populating main database with demonstration objects.")

        MentatFixtures(self.eventservice, self.sqlservice, self.logger).import_to_db()

        return self.RESULT_SUCCESS

    def cbk_command_event_classes_add(self):
        """
        Implementation of the **event-classes-add** command.

        Populate database with event classes from fixtures.py.
        """
        self.logger.info("Populating main database with event classes.")

        MentatFixtures(self.eventservice, self.sqlservice, self.logger).import_event_classes_to_db()

        return self.RESULT_SUCCESS

    def cbk_command_fixtures_remove(self):
        """
        Implementation of the **fixtures-remove** command.

        Remove demonstration objects from database - fixtures (user accounts
        and groups).
        """
        self.logger.info("Removing demonstration objects from main database.")

        MentatFixtures(self.eventservice, self.sqlservice, self.logger).remove_from_db()

        return self.RESULT_SUCCESS

    def cbk_command_reinit_main(self):
        """
        Implementation of the **reinit-main** command.

        Reinitialize main database (drop and create).
        """
        self.logger.info("Dropping main database.")
        self.sqlservice.database_drop()
        self.logger.info("Initializing main database.")
        self.sqlservice.database_create()

        return self.RESULT_SUCCESS

    def cbk_command_reindex_event(self):
        """
        Implementation of the **reindex-event** command.

        Drop existing indices in **event** database and recreate them according
        to current configuration.
        """
        self.logger.info("Dropping current indices in event database.")
        self.eventservice.index_drop()
        self.logger.info("Initializing event database indices.")
        self.eventservice.index_create()

        return self.RESULT_SUCCESS

    def cbk_command_user_add(self):
        """
        Implementation of the **user-add** command.

        Add new user account into the database.
        """
        self.logger.info("Creating new user account.")

        account_user = UserModel(enabled=True)

        for attr in self.c(self.CONFIG_ADDITIONAL_ARGS):
            key, value = attr.split("=", 2)
            if not key or not value:
                raise pyzenkit.zenscript.ZenScriptException(f"Invalid user account attribute: {attr!s}")

            if key == "login":
                account_user.login = value
            elif key == "fullname":
                account_user.fullname = value
            elif key == "email":
                account_user.email = value
            elif key == "organization":
                account_user.organization = value
            elif key == "roles":
                account_user.roles = value.split(",")

        for attrname in ("login", "fullname", "email", "organization", "roles"):
            if not getattr(account_user, attrname, None):
                raise pyzenkit.zenscript.ZenScriptException(
                    f'Please provide user`s {attrname} as "{attrname}=value" command line argument'
                )

        try:
            self.sqlservice.session.add(account_user)
            self.sqlservice.session.commit()
            self.logger.info("Added user account to database: '%s'", str(account_user))
            return self.RESULT_SUCCESS

        except Exception as exc:
            self.sqlservice.session.rollback()
            self.logger.info(
                "Unable to add user account to database: '%s' (%s)",
                str(account_user),
                str(exc),
            )
            return self.RESULT_FAILURE
