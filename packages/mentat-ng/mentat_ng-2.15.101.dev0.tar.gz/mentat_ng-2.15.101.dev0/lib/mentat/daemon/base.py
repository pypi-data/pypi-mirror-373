#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides base implementation of all Mentat daemons.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.baseapp
import pyzenkit.zendaemon

import mentat.const

DEFAULT_EVENTS_SCHEDULED = [(mentat.const.DFLT_EVENT_START,)]
DEFAULT_EVENTS_SCHEDULED_AFTER = [
    (mentat.const.DFLT_INTERVAL_STATISTICS, mentat.const.DFLT_EVENT_LOG_STATISTICS),
    (mentat.const.DFLT_INTERVAL_RUNLOG, mentat.const.DFLT_EVENT_SAVE_RUNLOG),
]


class MentatBaseDaemon(pyzenkit.zendaemon.ZenDaemon):
    """
    This module provides base implementation of generic *pipe-like* message processing
    daemon.
    """

    def __init__(self, **kwargs):
        #
        # Configure required script paths.
        #
        kwargs.setdefault("path_cfg", mentat.const.PATH_CFG)
        kwargs.setdefault("path_var", mentat.const.PATH_VAR)
        kwargs.setdefault("path_log", mentat.const.PATH_LOG)
        kwargs.setdefault("path_run", mentat.const.PATH_RUN)
        kwargs.setdefault("path_tmp", mentat.const.PATH_TMP)

        #
        # Override default configurations.
        #
        kwargs.setdefault("default_config_dir", self.get_resource_path(mentat.const.PATH_CFG_CORE))
        kwargs.setdefault("default_stats_interval", mentat.const.DFLT_INTERVAL_STATISTICS)
        kwargs.setdefault("default_runlog_interval", mentat.const.DFLT_INTERVAL_RUNLOG)

        #
        # Schedule initial events.
        #
        kwargs.setdefault("schedule", DEFAULT_EVENTS_SCHEDULED)
        kwargs.setdefault("schedule_after", DEFAULT_EVENTS_SCHEDULED_AFTER)

        super().__init__(**kwargs)
