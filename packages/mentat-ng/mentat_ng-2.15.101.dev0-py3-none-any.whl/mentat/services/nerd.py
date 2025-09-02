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
Implementation of internal **NERD** service connector.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy

import requests

from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_NERD

_MANAGER = None


class NerdConfigException(ValueError):
    pass


class NerdRuntimeException(RuntimeError):
    pass


class NerdService:
    """
    Implementation of internal **NERD** access service.
    """

    def __init__(self, base_url, base_api_url, api_key):
        """
        Initialize geolocation service with paths to desired database files.
        """
        self.base_url = base_url
        self.base_api_url = base_api_url
        self.api_key = api_key

        # Check presence and validity of config.
        if not self.base_url:
            raise NerdConfigException("NERD service is used but base URL is not configured")
        if not (self.base_url.startswith("https://") or self.base_url.startswith("http://")):
            raise NerdConfigException("Invalid NERD service base URL")
        if not self.base_api_url:
            raise NerdConfigException("NERD service is used but base API URL is not configured")
        if not (self.base_api_url.startswith("https://") or self.base_api_url.startswith("http://")):
            raise NerdConfigException("Invalid NERD service base API URL")
        if not self.api_key:
            raise NerdConfigException("NERD service is used but api_key is not configured")

        # Ensure both base_url and base_api_url end with slash.
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        if not self.base_api_url.endswith("/"):
            self.base_api_url += "/"

    def setup(self):
        """
        Additional internal setup currently not necessary.
        """

    def status(self):
        """
        Display status of the service.
        """
        return {
            "base_url": self.base_url,
            "base_api_url": self.base_api_url,
        }

    def get_url_lookup_ip(self, ipaddr):
        """
        Get URL for looking up given IP address in NERD service.
        """
        return f"{self.base_url}ip/{ipaddr!s}"

    def get_api_url_lookup_ip(self, ipaddr):
        """
        Get URL for looking up given IP address in NERD service.
        """
        return f"{self.base_api_url}ip/{ipaddr!s}"

    def lookup_ip(self, ipaddr):
        """
        Lookup given IP address in NERD service.
        """
        # Prepare request to NERD API
        url = self.get_api_url_lookup_ip(ipaddr)
        headers = {"Authorization": self.api_key}

        # Send request
        try:
            resp = requests.get(url, headers=headers, timeout=300)
        except Exception as exc:
            raise NerdRuntimeException(f"Can't get data from NERD service: {exc!s}") from exc

        if resp.status_code == requests.codes.not_found:
            return None
        resp.raise_for_status()

        # Parse response
        try:
            return resp.json()
        except Exception as exc:
            raise NerdRuntimeException(f"Invalid data received from NERD service: {exc!s}") from exc


class NerdServiceManager:
    """
    Class representing a custom NerdServiceManager capable of understanding and
    parsing Mentat system core configurations and enabling easy way of unified
    bootstrapping of :py:class:`mentat.services.nerd.NerdService` service.
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize NerdServiceManager object with full core configuration tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._nerdconfig = {}

        self._service = None

        self._configure_nerd(core_config, updates)

    def _configure_nerd(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._nerdconfig = copy.deepcopy(core_config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_NERD])

        if updates and CKEY_CORE_SERVICES in updates and CKEY_CORE_SERVICES_NERD in updates[CKEY_CORE_SERVICES]:
            self._nerdconfig.update(updates[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_NERD])

    def service(self):
        """
        Return handle to NERD service according to internal configurations.

        :return: Reference to NERD service object.
        :rtype: mentat.services.nerd.NerdService
        """
        if not self._service:
            self._service = NerdService(**self._nerdconfig)
            self._service.setup()
        return self._service


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`NerdServiceManager` instance at module level and
    store the refence within module.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = NerdServiceManager(core_config, updates)


def manager():
    """
    Obtain reference to :py:class:`NerdServiceManager` instance stored at module
    level.
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`NerdService` instance from module level manager.
    """
    return manager().service()
