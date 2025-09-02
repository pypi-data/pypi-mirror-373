#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides base implementation of generic message fetching and processing
script. This script will take care of initializing :py:class:`mentat.plugin.app.storage.StoragePlugin`
and provides methods for fetching messages from database.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import os
import time

import mentat.const
import mentat.plugin.app.eventstorage
import mentat.plugin.app.sqlstorage
import mentat.script.base


class FetcherScript(mentat.script.base.MentatBaseScript):  # pylint: disable=locally-disabled,abstract-method
    """
    Base implementation of generic message fetching and processing script.
    """

    def __init__(self, **kwargs):
        """
        Initialize fetcher script. This method overrides the base implementation
        in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and it aims to even
        more simplify the script object creation.

        :param kwargs: Various additional parameters passed to object constructor.
        """
        self.eventservice = None

        # Manipulate the list of script plugins.
        plugins = kwargs.get(self.CONFIG_PLUGINS, [])

        # Force prepend the EventStoragePlugin.
        plugins.insert(0, mentat.plugin.app.eventstorage.EventStoragePlugin())
        # Force prepend the SQLStoragePlugin.
        plugins.insert(0, mentat.plugin.app.sqlstorage.SQLStoragePlugin())

        kwargs[self.CONFIG_PLUGINS] = plugins

        super().__init__(**kwargs)

    # ---------------------------------------------------------------------------

    @staticmethod
    def initialize_result(time_low, time_high, interval, result=None):
        """
        Initialize the result data structure.

        :param datetime.datetime time_low: Lower time interval boundary.
        :param datetime.datetime time_high: Upper time interval boundary.
        :param str interval: Time interval, one of the interval defined in :py:mod:`pyzenkit.zenscript`.
        :param dict result: Result data structure.
        :return: Result data structure.
        :rtype: dict
        """
        if result is None:
            result = {}

        result["ts_from_s"] = str(time_low)
        result["ts_to_s"] = str(time_high)
        result["ts_from"] = int(time_low.timestamp())
        result["ts_to"] = int(time_high.timestamp())
        result["ts_delta"] = result["ts_to"] - result["ts_from"]
        result["interval"] = interval
        result["_id"] = "{}_{}".format(result["ts_from"], result["ts_to"])

        return result

    def fetch_messages(self, time_low, time_high):
        """
        Fetch messages from database collection withing time interval defined by
        given upper and lower time boundary.

        :param datetime.datetime time_low: Lower time interval boundary.
        :param datetime.datetime time_high: Upper time interval boundary.
        :return: List of messages fetched from database.
        :rtype: list
        """

        self.logger.info(
            "Fetching messages from time interval '%s' -> '%s' (%i -> %i)",
            str(time_low),
            str(time_high),
            time_low.timestamp(),
            time_high.timestamp(),
        )

        count, result = self.eventservice.search_events({"st_from": time_low, "st_to": time_high})

        self.logger.info(
            "Fetched '%i' messages from time interval '%s' -> '%s' (%i -> %i)",
            len(result),
            str(time_low),
            str(time_high),
            time_low.timestamp(),
            time_high.timestamp(),
        )
        return result

    def fetch_all_messages(self):
        """
        Fetch all messages from database collection.

        :return: List of messages fetched from database.
        :rtype: list
        """
        self.logger.info("Fetching all messages")

        count, result = self.eventservice.search_events()

        self.logger.info("Fetched all '%i' messages", len(result))
        return result


class DemoFetcherScript(FetcherScript):
    """
    This is an internal implementation of :py:class:`FetcherScript` usable only
    for demonstration purposes.
    """

    def __init__(self, name=None, description=None):
        """
        Initialize demonstration fetcher script. This method overrides the base
        implementation in :py:func:`mentat.script.fetcher.FetcherScript.__init__` and
        t aims to even more simplify the script object creation.

        :param str name: Optional script name.
        :param str description: Optional script description.
        """
        if not name:
            name = "demo-fetcherscript.py"
        if not description:
            description = "demo-fetcherscript.py - Demonstration fetcher script"

        super().__init__(
            name=name,
            description=description,
            #
            # Configure required script paths.
            #
            path_bin="tmp",
            path_cfg="tmp",
            path_var="tmp",
            path_log="tmp",
            path_run="tmp",
            path_tmp="tmp",
            #
            # Override default configurations.
            #
            default_debug=True,
            default_config_dir=os.path.abspath(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../conf/core")
            ),
        )

    def get_default_command(self):
        """
        Return the name of a default script command.

        :return: Name of the default command.
        :rtype: str
        """
        return "demo"

    def cbk_command_demo(self):
        """
        Implementation of the 'demo' command (default command).
        """
        self.logger.warning("Fetcher demonstration run - begin")

        result = {}
        interval = "5_minutes"

        (time_low, time_high) = self.calculate_interval_thresholds(time_high=int(time.time()), interval=interval)

        result = self.initialize_result(time_low, time_high, interval)

        messages = self.fetch_messages(time_low, time_high)
        self.logger.info("Processed '%i' messages", len(messages))

        self.logger.warning("Fetcher demonstration run - end")
        return result


# -------------------------------------------------------------------------------

#
# Perform the demonstration.
#
if __name__ == "__main__":
    # Prepare demonstration environment.
    APP_NAME = "demo-fetcherscript.py"
    for directory in (
        DemoFetcherScript.get_resource_path("tmp"),
        DemoFetcherScript.get_resource_path(f"tmp/{APP_NAME}"),
    ):
        with contextlib.suppress(FileExistsError):
            os.mkdir(directory)

    DemoFetcherScript.json_save(
        DemoFetcherScript.get_resource_path(f"tmp/{APP_NAME}.conf"),
        {"test_a": 1, "test_b": 2, "test_c": 3},
    )

    #
    # Perform demonstation run.
    #
    DemoFetcherScript(APP_NAME).run()
