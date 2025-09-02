#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#
# This product includes GeoLite2 data created by MaxMind, available from
# http://www.maxmind.com.
# -------------------------------------------------------------------------------


"""
Implementation of internal **geoip2** database library.


Prerequisites
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This library is dependent on `geoip2 <https://geoip2.readthedocs.io/en/latest/>`__
(available through `PyPI <https://pypi.python.org/pypi/geoip2/>`__) and requires
GeoLite2 Free `downloadable databases <http://dev.maxmind.com/geoip/geoip2/geolite2/>`__:

* `GeoLite2-ASN.mmdb <http://geolite.maxmind.com/download/geoip/database/GeoLite2-ASN.tar.gz>`__
* `GeoLite2-City.mmdb <http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz>`__
* `GeoLite2-Country.mmdb <http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz>`__

.. note::

    This product includes GeoLite2 data created by MaxMind, available from
    http://www.maxmind.com/.

.. warning::

    Work in progress and alpha code.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy

import geoip2.database

from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_GEOIP

_MANAGER = None


class GeoipService:
    """
    Implementation of internal **geoip2** database service.
    """

    def __init__(self, asndb=None, citydb=None, countrydb=None):
        """
        Initialize geolocation service with paths to desired database files.
        """
        self.fn_asndb = asndb
        self.fn_citydb = citydb
        self.fn_countrydb = countrydb

        self.asndb = None
        self.citydb = None
        self.countrydb = None

    def __del__(self):
        """
        Close internal geolocation database readers.
        """
        if self.asndb:
            self.asndb.close()
            self.asndb = None
        if self.citydb:
            self.citydb.close()
            self.citydb = None
        if self.countrydb:
            self.countrydb.close()
            self.countrydb = None

    def setup(self):
        """
        Setup internal geolocation database readers.
        """
        if self.fn_asndb:
            self.asndb = geoip2.database.Reader(self.fn_asndb)
        else:
            self.asndb = None

        if self.fn_citydb:
            self.citydb = geoip2.database.Reader(self.fn_citydb)
        else:
            self.citydb = None

        if self.fn_countrydb:
            self.countrydb = geoip2.database.Reader(self.fn_countrydb)
        else:
            self.countrydb = None

    def status(self):
        """
        Display status of internal geolocation readers.
        """
        return {
            "asn": self.fn_asndb,
            "city": self.fn_citydb,
            "country": self.fn_countrydb,
        }

    def lookup(self, ipaddr):
        """
        Lookup given IP address in all databases.
        """
        result = {}
        if self.asndb:
            result["asn"] = self.lookup_asn(ipaddr)
            if not result["asn"]:
                del result["asn"]
        if self.citydb:
            result["city"] = self.lookup_city(ipaddr)
            if not result["city"]:
                del result["city"]
        if self.countrydb:
            result["country"] = self.lookup_country(ipaddr)
            if not result["country"]:
                del result["country"]
        return result or None

    def lookup_asn(self, ipaddr):
        """
        Lookup given IP address in ASN database.
        """
        try:
            response = self.asndb.asn(str(ipaddr))
            return {
                "ip": response.ip_address,
                "asn": response.autonomous_system_number,
                "org": response.autonomous_system_organization,
            }

        except geoip2.errors.AddressNotFoundError:
            return None

    def lookup_city(self, ipaddr):
        """
        Lookup given IP address in city database.
        """
        try:
            response = self.citydb.city(str(ipaddr))
            return {
                "ip": response.traits.ip_address,
                "cty_name": response.city.name,
                "ctr_code": response.country.iso_code,
                "ctr_name": response.country.name,
                "cnt_code": response.continent.code,
                "cnt_name": response.continent.name,
                "longitude": response.location.longitude,
                "latitude": response.location.latitude,
                "timezone": response.location.time_zone,
                "accuracy": response.location.accuracy_radius,
            }
        except geoip2.errors.AddressNotFoundError:
            return None

    def lookup_country(self, ipaddr):
        """
        Lookup given IP address in Country database.
        """
        try:
            response = self.countrydb.country(str(ipaddr))
            return {
                "ip": response.traits.ip_address,
                "ctr_code": response.country.iso_code,
                "ctr_name": response.country.name,
                "cnt_code": response.continent.code,
                "cnt_name": response.continent.name,
            }

        except geoip2.errors.AddressNotFoundError:
            return None


class GeoipServiceManager:
    """
    Class representing a custom GeoipServiceManager capable of understanding and
    parsing Mentat system core configurations and enabling easy way of unified
    bootstrapping of :py:class:`mentat.services.geoip.GeoipService` service.
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize GeoipServiceManager object with full core configuration tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._geoconfig = {}

        self._service = None

        self._configure_geoip(core_config, updates)

    def _configure_geoip(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._geoconfig = copy.deepcopy(core_config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP])

        if updates and CKEY_CORE_SERVICES in updates and CKEY_CORE_SERVICES_GEOIP in updates[CKEY_CORE_SERVICES]:
            self._geoconfig.update(updates[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_GEOIP])

    def service(self):
        """
        Return handle to geoip service according to internal configurations.

        :return: Reference to geoip service object.
        :rtype: mentat.services.geoip.GeoipService
        """
        if not self._service:
            self._service = GeoipService(**self._geoconfig)
            self._service.setup()
        return self._service


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`GeoipServiceManager` instance at module level and
    store the refence within module.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = GeoipServiceManager(core_config, updates)


def manager():
    """
    Obtain reference to :py:class:`GeoipServiceManager` instance stored at module
    level.
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`GeoipService` instance from module level manager.
    """
    return manager().service()
