#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.geoip` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import subprocess
import unittest

import mentat.services.geoip

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


def _strip_coords(result):
    """
    Helper method for removing highly volatile data from result to enable unit testing.
    """
    if not result or not isinstance(result, dict):
        return result
    if "city" in result and result["city"] and isinstance(result["city"], dict):
        if "latitude" in result["city"]:
            del result["city"]["latitude"]
        if "longitude" in result["city"]:
            del result["city"]["longitude"]
    if "latitude" in result:
        del result["latitude"]
    if "longitude" in result:
        del result["longitude"]
    return result


class TestMentatGeoip(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.geoip` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    geoip_test_list = [
        [
            "195.113.144.233",
            {
                "asn": {"asn": 2852, "ip": "195.113.144.233", "org": "CESNET z.s.p.o."},
                "city": {
                    "accuracy": 200,
                    "cnt_code": "EU",
                    "cnt_name": "Europe",
                    "ctr_code": "CZ",
                    "ctr_name": "Czechia",
                    "cty_name": "Olomouc",
                    "ip": "195.113.144.233",
                    "timezone": "Europe/Prague",
                },
                "country": {
                    "cnt_code": "EU",
                    "cnt_name": "Europe",
                    "ctr_code": "CZ",
                    "ctr_name": "Czechia",
                    "ip": "195.113.144.233",
                },
            },
        ]
        # [
        #    '2001:718:1:6::144:233', {
        #        'asn': {
        #            'asn': 2852,
        #            'ip': '2001:718:1:6::144:233',
        #            'org': 'CESNET z.s.p.o.'
        #        },
        #        'city': {
        #            'accuracy': 50,
        #            'cnt_code': 'EU',
        #            'cnt_name': 'Europe',
        #            'ctr_code': 'CZ',
        #            'ctr_name': 'Czechia',
        #            'cty_name': None,
        #            'ip': '2001:718:1:6::144:233',
        #            'timezone': 'Europe/Prague'
        #        },
        #        'country': {
        #            'cnt_code': 'EU',
        #            'cnt_name': 'Europe',
        #            'ctr_code': 'CZ',
        #            'ctr_name': 'Czechia',
        #            'ip': '2001:718:1:6::144:233'
        #        }
        #    }
        # ]
    ]

    def setUp(self):
        """
        Perform test case setup.
        """
        if not os.path.isfile("/var/tmp/GeoLite2-ASN.mmdb"):
            subprocess.call(["geoipupdate", "-d", "/var/tmp"])

    def disabledtest_01_lookup_asn(self):
        """
        Perform ASN lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(
            asndb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-ASN.mmdb"))
        )
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup_asn(test[0]), test[1]["asn"])

    def disabledtest_02_lookup_city(self):
        """
        Perform city lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(
            citydb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-City.mmdb"))
        )
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(_strip_coords(geoip.lookup_city(test[0])), test[1]["city"])

    def disabledtest_03_lookup_country(self):
        """
        Perform country lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(
            countrydb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-Country.mmdb"))
        )
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup_country(test[0]), test[1]["country"])

    def disabledtest_04_lookup(self):
        """
        Perform full lookup tests with manually configured geoip service.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(
            asndb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-ASN.mmdb")),
            citydb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-City.mmdb")),
            countrydb=os.path.abspath(os.path.join(os.path.dirname(__file__), "/var/tmp/GeoLite2-Country.mmdb")),
        )
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(_strip_coords(geoip.lookup(test[0])), test[1])

    def disabledtest_05_service_manager(self):
        """
        Perform full lookup tests with service obtained by manually configured service manager.
        """
        self.maxDiff = None

        manager = mentat.services.geoip.GeoipServiceManager(
            {
                "__core__services": {
                    "geoip": {
                        "asndb": "/var/tmp/GeoLite2-ASN.mmdb",
                        "citydb": "/var/tmp/GeoLite2-City.mmdb",
                        "countrydb": "/var/tmp/GeoLite2-Country.mmdb",
                    }
                }
            }
        )

        geoip = manager.service()
        for test in self.geoip_test_list:
            self.assertEqual(_strip_coords(geoip.lookup(test[0])), test[1])

    def disabledtest_06_module_service(self):
        """
        Perform full lookup tests with service obtained by module interface.
        """
        self.maxDiff = None

        mentat.services.geoip.init(
            {
                "__core__services": {
                    "geoip": {
                        "asndb": "/var/tmp/GeoLite2-ASN.mmdb",
                        "citydb": "/var/tmp/GeoLite2-City.mmdb",
                        "countrydb": "/var/tmp/GeoLite2-Country.mmdb",
                    }
                }
            }
        )

        geoip = mentat.services.geoip.service()
        for test in self.geoip_test_list:
            self.assertEqual(_strip_coords(geoip.lookup(test[0])), test[1])


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
