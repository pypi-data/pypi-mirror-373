#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of storing
`IDEA <https://idea.cesnet.cz/en/index>`__ messages into persistent storage.
Currently only `PostgreSQL <https://www.postgresql.org/>`__ SQL database is supported.

To view built-in help please execute the application with ``--help`` command line
option::

    mentat-storage.py --help

To view local documentation please use ``pydoc3``::

    pydoc3 mentat.module.storage

This daemon is implemented using the :py:mod:`pyzenkit.zendaemon` framework and
so it provides all of its core features. See the documentation for more in-depth
details. It is further based on :py:mod:`mentat.daemon.piper`, which provides
*pipe-like* message processing features. See the documentation for more in-depth
details.


License
^^^^^^^

Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
Use of this source is governed by the MIT license, see LICENSE file.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


from mentat.module.storage import MentatStorageDaemon

if __name__ == "__main__":
    MentatStorageDaemon().run()
