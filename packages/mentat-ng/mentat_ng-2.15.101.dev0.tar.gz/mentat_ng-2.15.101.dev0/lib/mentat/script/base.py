#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides base implementation of all Mentat scripts.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pyzenkit.baseapp
import pyzenkit.zenscript

import mentat.const


class MentatBaseScript(pyzenkit.zenscript.ZenScript):  # pylint: disable=locally-disabled,abstract-method
    """
    Base implementation of all Mentat scripts.
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

        super().__init__(**kwargs)
