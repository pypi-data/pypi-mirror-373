# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Implementation of internal **DNS** service library.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy

import dns.exception
import dns.resolver

import ipranges

from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_DNS

_MANAGER = None


class DnsService:
    """
    Implementation of internal **DNS** database service.
    """

    def __init__(self, timeout=1, lifetime=3):
        """
        Initialize geolocation service with paths to desired database files.
        """
        self.resolver = None
        self.timeout = timeout
        self.lifetime = lifetime

    def setup(self):
        """
        Setup internal DNS service resolver.
        """
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = self.timeout
        self.resolver.lifetime = self.lifetime

    def status(self):
        """
        Display status of internal geolocation readers.
        """
        return {"timeout": self.timeout, "lifetime": self.lifetime}

    def lookup_ip(self, ipaddr):
        """
        Lookup given IP address in DNS.
        """
        result = []
        revipaddr = dns.reversename.from_address(ipaddr)  # create .in-addr.arpa address
        try:
            answer = self.resolver.query(revipaddr, "PTR")
            for res in answer.rrset:
                res = str(res)
                if res[-1] == ".":
                    res = res[:-1]  # trim trailing '.'
                result.append({"type": "PTR", "value": res})
        except dns.exception.Timeout as exc:
            raise RuntimeError(f"DNS query for {ipaddr} timed out") from exc
        except dns.exception.DNSException:
            pass
        return result

    def lookup_hostname(self, hname):
        """
        Lookup given hostname in DNS.
        """
        result = []
        try:
            for qtype in ("A", "AAAA"):
                answer = self.resolver.query(hname, qtype)
                for res in answer.rrset:
                    res = str(res)
                    result.append({"type": qtype, "value": res})
        except dns.exception.Timeout as exc:
            raise RuntimeError(f"DNS query for {hname} timed out") from exc
        except dns.exception.DNSException:
            pass
        return result

    def lookup(self, thing):
        """
        Lookup given object in DNS.
        """
        for tconv in ipranges.IP4, ipranges.IP6:
            try:
                tconv(thing)
                return self.lookup_ip(thing)
            except ValueError:
                pass
        return self.lookup_hostname(thing)


class DnsServiceManager:
    """
    Class representing a custom DnsServiceManager capable of understanding and
    parsing Mentat system core configurations and enabling easy way of unified
    bootstrapping of :py:class:`mentat.services.dns.DnsService` service.
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize DnsServiceManager object with full core configuration tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dnsconfig = {}

        self._service = None

        self._configure_dns(core_config, updates)

    def _configure_dns(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dnsconfig = copy.deepcopy(core_config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_DNS])

        if updates and CKEY_CORE_SERVICES in updates and CKEY_CORE_SERVICES_DNS in updates[CKEY_CORE_SERVICES]:
            self._dnsconfig.update(updates[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_DNS])

    def service(self):
        """
        Return handle to DNS service according to internal configurations.

        :return: Reference to DNS service object.
        :rtype: mentat.services.dnsr.DnsService
        """
        if not self._service:
            self._service = DnsService(**self._dnsconfig)
            self._service.setup()
        return self._service


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`DnsServiceManager` instance at module level and
    store the refence within module.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = DnsServiceManager(core_config, updates)


def manager():
    """
    Obtain reference to :py:class:`DnsServiceManager` instance stored at module
    level.
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`DnsService` instance from module level manager.
    """
    return manager().service()
