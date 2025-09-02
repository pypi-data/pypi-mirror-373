#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Daemon component capable of enriching IDEA messages with various additional data.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.

Component setup configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


This daemon component requires that following configurations are provided by
external daemon:

plugins
    List of dictionaries describing requested enrichment plugins. See below for
    plugin configuration description.

reload_interval
    Time interval for reloading enrichment plugins in seconds.


Plugin configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Each plugin configuration must be a Python dictionary with mandatory ``name``
attribute. This attribute should contain full name of the requested enrichment
plugin including the path, so that the Python interpreter is able to load all
necessary module and instantinate the plugin object. To be usable te plugin class
must implement interface defined by :py:class:`EnricherPlugin`.


.. code-block:: json

    {
        "name":  "mentat.plugin.enricher.geoip.GeoipEnricherPlugin"
    }


Current plugin list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :py:class:`mentat.plugin.enricher.geoip.GeoipEnricherPlugin`
* :py:class:`mentat.plugin.enricher.logger.LoggerEnricherPlugin`
* :py:class:`mentat.plugin.enricher.whois.WhoisEnricherPlugin`

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import importlib
import re
import sys
import traceback

import pyzenkit.zendaemon

PLUGIN_PTRN = re.compile(r"^(?:(.+)\.)?([\w]+)$")


CONFIG_PLUGINS = "plugins"
CONFIG_RELOAD_INTERVAL = "reload_interval"


class EnricherDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Daemon component capable of enriching IDEA messages with various extra data.
    """

    EVENT_MSG_PROCESS = "message_process"
    EVENT_LOG_STATISTICS = "log_statistics"
    EVENT_RELOAD = "reload"

    STATS_CNT_ENRICHED = "cnt_enriched"
    STATS_CNT_ERRORS = "cnt_errors"
    STATS_CNT_RELOADS = "cnt_reloads"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "enricher")

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_MSG_PROCESS: self.EVENT_MSG_PROCESS,
                self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS,
                self.EVENT_RELOAD: self.EVENT_RELOAD,
            },
        )

        # Initialize internal plugin list.
        self.plugins = []

    @staticmethod
    def _parse_plugin_name(name):
        """
        Parse module name and class name from given plugin name.
        """
        match = PLUGIN_PTRN.match(name)
        if match:
            return (match.group(1), match.group(2))
        raise TypeError(f"Invalid value for plugin name '{name}'")

    def _setup_plugin(self, daemon, plugin_conf):
        """
        Setup plugin according to given configuration.
        """
        full_name = plugin_conf.get("name")
        (module_name, class_name) = self._parse_plugin_name(full_name)
        daemon.logger.info(
            "[STATUS] Component '%s': Configuring enrichment plugin '%s'.'%s'",
            self.cid,
            module_name,
            class_name,
        )

        # Get reference to appropriate python module with requested plugin implementation.
        if module_name:
            if module_name not in sys.modules:
                module = importlib.import_module(module_name)
            else:
                module = sys.modules[module_name]
        else:
            module = sys.modules[__name__]

        plugin_class = getattr(module, class_name)
        plugin = plugin_class()

        plugin.setup(daemon, plugin_conf.get("config", None))
        return plugin

    def _setup_plugins(self, daemon):
        """
        Setup all plugins according to given configuration.
        """
        self.plugins = []

        plugin_list = daemon.c(CONFIG_PLUGINS)
        for plugin_conf in plugin_list:
            self.plugins.append(self._setup_plugin(daemon, plugin_conf))

    def _reload_plugins(self, daemon):
        """
        Reload all plugins according to given configuration.
        """
        plugin_list = daemon.c(CONFIG_PLUGINS)
        for plugin, plugin_conf in zip(self.plugins, plugin_list):
            daemon.logger.info(
                "Component '%s': Reloading enrichment plugin '%s'",
                self.cid,
                plugin_conf.get("name"),
            )
            plugin.setup(daemon, plugin_conf.get("config", None))

    def setup(self, daemon):
        """
        Perform component setup.
        """
        self._setup_plugins(daemon)

        daemon.logger.info(
            "[STATUS] Component '%s': Successfully set up all enrichment plugins",
            self.cid,
        )

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_MSG_PROCESS],
                "callback": self.cbk_event_message_process,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_LOG_STATISTICS],
                "callback": self.cbk_event_log_statistics,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_RELOAD],
                "callback": self.cbk_event_reload,
                "prepend": False,
            },
        ]

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Enrich message using all configured plugins.
        """
        daemon.logger.debug(
            "Component '%s': Enriching message '%s':'%s'",
            self.cid,
            args["id"],
            args["idea_id"],
        )
        try:
            changed = False
            result = daemon.FLAG_CONTINUE
            for plugin in self.plugins:
                (flag_cont, flag_changed) = plugin.process(daemon, args["idea_id"], args["idea"])
                if flag_cont == daemon.FLAG_STOP:
                    result = daemon.FLAG_STOP
                if flag_changed:
                    changed = True

            if changed:
                daemon.logger.info(
                    "Component '%s': Enriched message '%s':'%s'",
                    self.cid,
                    args["id"],
                    args["idea_id"],
                )
                daemon.queue.schedule(
                    "message_update",
                    {
                        "id": args["id"],
                        "idea_id": args["idea_id"],
                        "idea": args["idea"],
                    },
                )
                self.inc_statistic(self.STATS_CNT_ENRICHED)

            return (result, args)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '%s': Unable to enrich IDEA message '%s': '%s'",
                self.cid,
                args["id"],
                traceback.format_exc(),
            )
            daemon.queue.schedule("message_banish", args)

            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [self.STATS_CNT_ENRICHED, self.STATS_CNT_ERRORS]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        daemon.logger.info("Component '%s': *** Processing statistics ***%s", self.cid, stats_str)
        return (daemon.FLAG_CONTINUE, args)

    def cbk_event_reload(self, daemon, args):
        """
        Reload all enricher plugins.
        """
        self._reload_plugins(daemon)

        daemon.logger.info("Component '%s': Reloaded all message enrichment plugins", self.cid)
        self.inc_statistic(self.STATS_CNT_RELOADS)

        daemon.queue.schedule_after(daemon.c(CONFIG_RELOAD_INTERVAL), self.EVENT_RELOAD)
        return (daemon.FLAG_CONTINUE, args)
