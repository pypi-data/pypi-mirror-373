# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.dnsr` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest

import mentat.services.dnsr

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatDns(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.dnsr` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    rdns_test_list = [
        ["195.113.144.233", [{"type": "PTR", "value": "ns.ces.net"}]],
        ["195.113.144.230", [{"type": "PTR", "value": "www.cesnet.cz"}]],
    ]

    dns_test_list = [
        [
            "ns.ces.net",
            [
                {"type": "A", "value": "195.113.144.233"},
                {"type": "AAAA", "value": "2001:718:1:101::3"},
            ],
        ],
        [
            "www.cesnet.cz",
            [
                {"type": "A", "value": "195.113.144.230"},
                {"type": "AAAA", "value": "2001:718:1:101::4"},
            ],
        ],
    ]

    def distest_01_lookup_ip(self):
        """
        Perform lookup tests by IP address.
        """
        self.maxDiff = None

        dns = mentat.services.dnsr.DnsService(timeout=1, lifetime=3)
        dns.setup()

        for test in self.rdns_test_list:
            self.assertEqual(dns.lookup_ip(test[0]), test[1])

    def distest_02_lookup_hostname(self):
        """
        Perform lookup tests by hostname.
        """
        self.maxDiff = None

        dns = mentat.services.dnsr.DnsService(timeout=1, lifetime=3)
        dns.setup()

        for test in self.dns_test_list:
            self.assertEqual(dns.lookup_hostname(test[0]), test[1])

    def distest_03_lookup(self):
        """
        Perform lookup tests by hostname.
        """
        self.maxDiff = None

        dns = mentat.services.dnsr.DnsService(timeout=1, lifetime=3)
        dns.setup()

        for test in self.rdns_test_list:
            self.assertEqual(dns.lookup(test[0]), test[1])
        for test in self.dns_test_list:
            self.assertEqual(dns.lookup(test[0]), test[1])

    def distest_04_service_manager(self):
        """
        Perform full lookup tests with service obtained by manually configured service manager.
        """
        self.maxDiff = None

        manager = mentat.services.dnsr.DnsServiceManager({"__core__services": {"dns": {"timeout": 1, "lifetime": 3}}})

        dns = manager.service()
        for test in self.rdns_test_list:
            self.assertEqual(dns.lookup_ip(test[0]), test[1])

    def distest_05_module_service(self):
        """
        Perform full lookup tests with service obtained by module interface.
        """
        self.maxDiff = None

        mentat.services.dnsr.init({"__core__services": {"dns": {"timeout": 1, "lifetime": 3}}})

        dns = mentat.services.dnsr.service()
        for test in self.rdns_test_list:
            self.assertEqual(dns.lookup_ip(test[0]), test[1])


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
