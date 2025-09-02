#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
`IDEA <https://idea.cesnet.cz/en/index>`__ message enrichment plugin for the
:ref:`section-bin-mentat-enricher` daemon module for logging the message into log
file, usefull mainly for development purposes or as an example for implementing
additional custom modules.

.. todo::

    Documentation is still work in progress, please refer to the source code for
    details.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pprint

import mentat.const
import mentat.plugin.enricher


class LoggerEnricherPlugin(mentat.plugin.enricher.EnricherPlugin):
    """
    Simple implementation of enricher plugin performing logging with 'info'
    severity to application log file.
    """

    def setup(self, daemon, config_updates=None):
        """
        Perform setup of enricher plugin.
        """
        daemon.logger.debug("Initialized '%s' enricher plugin", self.__class__.__name__)

    def process(self, daemon, message_id, message):
        """
        Process given message.
        """
        try:
            txt_msg = message.to_json(indent=4)
        except AttributeError:
            txt_msg = pprint.pformat(message, indent=4)

        daemon.logger.info("LOGGER - processing message '%s': %s", message_id, txt_msg)

        return (daemon.FLAG_CONTINUE, self.FLAG_UNCHANGED)
