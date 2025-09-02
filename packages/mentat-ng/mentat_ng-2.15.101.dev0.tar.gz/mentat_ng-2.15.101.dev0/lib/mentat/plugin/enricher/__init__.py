#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains base class for all :ref:`section-bin-mentat-enricher` daemon
plugins for enriching incoming `IDEA <https://idea.cesnet.cz/en/index>`__ messages
with additional data.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


class EnricherPlugin:
    """
    Base class for all :ref:`section-bin-mentat-enricher` daemon plugins.
    """

    FLAG_CHANGED = True
    FLAG_UNCHANGED = False

    def setup(self, daemon, config_updates=None):
        """
        Perform setup of enricher plugin.
        """
        raise NotImplementedError("The setup() method needs implementation")

    def process(self, daemon, message_id, message):
        """
        Process given message.
        """
        raise NotImplementedError("The process() method needs implementation")
