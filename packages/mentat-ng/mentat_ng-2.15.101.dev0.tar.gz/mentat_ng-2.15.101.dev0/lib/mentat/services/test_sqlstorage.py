#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Unit test module for testing the :py:mod:`mentat.services.sqlstorage` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest

import mentat.services.sqlstorage

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatStorage(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.sqlstorage` module.
    """

    def test_01_basic(self):
        """
        Perform the basic storage connection and operativity tests.
        """
        storage = mentat.services.sqlstorage.StorageService(
            url="postgresql://mentat:mentat@localhost/mentat_utest", echo=False
        )
        storage.database_create()
        storage.database_drop()
        storage.close()

    def test_02_service_manager(self):
        """
        Perform the tests of storage service manager.
        """
        manager = mentat.services.sqlstorage.StorageServiceManager(
            {
                "__core__database": {
                    "sqlstorage": {
                        "url": "postgresql://mentat:mentat@localhost/mentat_utest",
                        "echo": False,
                    }
                }
            },
            {"__core__database": {"sqlstorage": {"echo": False}}},
        )
        storage = manager.service()
        storage.database_create()
        storage.database_drop()

        manager.close()

    def test_03_module_service(self):
        """
        Perform the tests of module service.
        """
        mentat.services.sqlstorage.init(
            {
                "__core__database": {
                    "sqlstorage": {
                        "url": "postgresql://mentat:mentat@localhost/mentat_utest",
                        "echo": False,
                    }
                }
            },
            {"__core__database": {"sqlstorage": {"echo": False}}},
        )

        manager = mentat.services.sqlstorage.manager()
        storage = manager.service()
        storage.database_create()
        storage.database_drop()
        storage.close()


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
