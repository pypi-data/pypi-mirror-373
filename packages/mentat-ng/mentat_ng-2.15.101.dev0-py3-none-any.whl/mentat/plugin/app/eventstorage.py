#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat application plugin provides functions for accessing event database. It
is usable both in script and daemon modules.

The biggest advantage when using this plugin is that it automatically retrieves
correct database configurations from application configuration tree and opens the
connection to database storage.

This application plugin is implemented using the :py:mod:`pyzenkit.baseapp`
framework and it is based on :py:class:`pyzenkit.baseapp.ZenAppPlugin`. See the
documentation for in-depth details.


Example usage
^^^^^^^^^^^^^

Using the plugin like in following way::

    mentat.plugin.app.eventstorage.EventStoragePlugin()

That will yield following results:

* The application object will have a ``eventservice`` attribute containing reference to
  event storage service represented by :py:class:`mentat.services.eventstorage.EventStorageService`.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.baseapp

import mentat.services.eventstorage


class EventStoragePlugin(pyzenkit.baseapp.ZenAppPlugin):
    """
    Implementation of Mentat application plugin providing functions for accessing
    SQL database. It is usable both in script and daemon modules.
    """

    def __init__(self, settings=None):
        """
        Initialize internal plugin configuration.
        """
        if settings is None:
            settings = {}
        self.settings = settings

    # ---------------------------------------------------------------------------

    def configure(self, app):
        """
        Configure application. This method will be called from :py:func:`pyzenkit.baseapp.BaseApp._configure_plugins`
        and it further updates current application configurations.

        This method is part of the **setup** stage of application`s life cycle.

        :param app: Reference to the parent application.
        """

    def setup(self, app):
        """
        Configure application. This method will be called from :py:func:`pyzenkit.baseapp.BaseApp._stage_setup_plugins`
        and it further updates current application configurations.

        This method is part of the **setup** stage of application`s life cycle.

        :param app: Reference to the parent application.
        """
        esm = mentat.services.eventstorage.EventStorageServiceManager(app.config)
        app.eventservice = esm.service()
        app.logger.debug("[STATUS] Set up event storage service.")
