#!python
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of enriching
`IDEA <https://idea.cesnet.cz/en/index>`__ messages with additional data.

.. warning::

    **BUG WARNING:** The dynamic plugin loading feature is currently broken, all
    enricher plugins must be preloaded inside code of this module. Bugfix is under
    development.

To view built-in help please execute the application with ``--help`` command line
option::

    mentat-enricher.py --help

To view local documentation please use ``pydoc3``::

    pydoc3 mentat.module.enricher

This daemon is implemented using the :py:mod:`pyzenkit.zendaemon` framework and
so it provides all of its core features. See the documentation for more in-depth
details. It is further based on :py:mod:`mentat.daemon.piper`, which provides
*pipe-like* message processing features. See the documentation for more in-depth
details.


License
^^^^^^^

Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
Use of this source is governed by the MIT license.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


# *******************************************************************************
# BUG WARNING: The dynamic plugin loading feature is currently broken, all enricher
# plugins must be preloaded here. Bugfix is under development.
# *******************************************************************************

import mentat.module.enricher
import mentat.plugin.enricher.geoip
import mentat.plugin.enricher.logger
import mentat.plugin.enricher.whois

# *******************************************************************************


if __name__ == "__main__":
    mentat.module.enricher.MentatEnricherDaemon().run()
