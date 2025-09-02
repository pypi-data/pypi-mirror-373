#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.passivednsrr` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import pprint
import unittest

import mentat.services.pdnsr

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatPassiveDNS(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.passivednsrr` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    pdnsr_test_list = [
        # [
        #    '195.113.144.233', {
        #    }
        # ],
        ["195.113.144.238", {}],
    ]

    def distest_01_lookup_ip(self):
        """
        Perform IP lookup tests.
        """
        self.maxDiff = None

        pdnsr = mentat.services.pdnsr.PDNSRService(
            base_url="https://passivedns.cesnet.cz/",
            base_api_url="https://passivedns.cesnet.cz/api/v1/",
            api_key="place_your_pdnsr_api_key_here",
        )
        pdnsr.setup()

        for test in self.pdnsr_test_list:
            pprint.pprint(pdnsr.lookup_ip(test[0]))
            # self.assertEqual(pdnsr.lookup_ip(test[0]), test[1])

    def distest_02_service_manager(self):
        """
        Perform full lookup tests with service obtained by manually configured service manager.
        """
        self.maxDiff = None

        manager = mentat.services.pdnsr.PDNSRServiceManager(
            {
                "__core__services": {
                    "passivedns": {
                        "base_url": "https://passivedns.cesnet.cz/",
                        "base_api_url": "https://passivedns.cesnet.cz/api/v1/",
                        "api_key": "place_your_pdnsr_api_key_here",
                    }
                }
            }
        )

        pdnsr = manager.service()
        for test in self.pdnsr_test_list:
            pprint.pprint(pdnsr.lookup_ip(test[0]))
            # self.assertEqual(pdnsr.lookup(test[0]), test[1])

    def distest_03_module_service(self):
        """
        Perform full lookup tests with service obtained by module interface.
        """
        self.maxDiff = None

        mentat.services.pdnsr.init(
            {
                "__core__services": {
                    "passivedns": {
                        "base_url": "https://passivedns.cesnet.cz/",
                        "base_api_url": "https://passivedns.cesnet.cz/api/v1/",
                        "api_key": "place_your_pdnsr_api_key_here",
                    }
                }
            }
        )

        pdnsr = mentat.services.pdnsr.service()
        for test in self.pdnsr_test_list:
            pprint.pprint(pdnsr.lookup_ip(test[0]))
            # self.assertEqual(pdnsr.lookup(test[0]), test[1])


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
