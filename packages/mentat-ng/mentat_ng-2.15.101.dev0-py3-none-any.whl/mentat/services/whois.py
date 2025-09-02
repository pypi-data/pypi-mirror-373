#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Internal whois library.

Module contents
^^^^^^^^^^^^^^^

:py:class:`mentat.services.whois.WhoisModule`
    Generic whois lookup module.

:py:class:`mentat.services.whois.FileWhoisModule`
    Whois lookup module capable of loading data from JSON files.

:py:class:`mentat.services.whois.SqldbWhoisModule`
    Whois lookup module capable of loading data from SQL databases.

:py:class:`mentat.services.whois.WhoisService`
    Whois lookup service, container for multiple whois lookup modules.

:py:class:`mentat.services.whois.WhoisServiceManager`
    Whois lookup service manager, capable of understanding Mentat core configurations.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy
import json

import ipranges

import mentat.const
import mentat.datatype.internal
import mentat.services.sqlstorage
from mentat.const import CKEY_CORE_SERVICES, CKEY_CORE_SERVICES_WHOIS
from mentat.datatype.sqldb import GroupModel, NetworkModel

WHOIS_KEY_TYPE = "__whois_type__"
WHOIS_KEY_ABOUT_GENERIC = "__whois_about__"
WHOIS_KEY_ABOUT_NEGISTRY = "__negistry_about__"

WHOIS_TYPE_GENERIC = "whois"
WHOIS_TYPE_NEGISTRY = "negistry"


_MANAGER = None


class WhoisModule:
    """
    Base class for all whois lookup modules. This class provides general lookup
    algorithm. More modules may be build on top of this module simply by overriding
    the :py:func:`mentat.services.whois.WhoisModule.setup` method and focus on the task of
    obtaining list of :py:class:`mentat.datatype.internal.NetworkRecord` objects,
    which can be then simply passed to the parent implementation.
    """

    def __init__(self):
        self.networks_ip4 = []
        self.networks_ip6 = []

    def setup(self, networks):
        """
        Setup whois module internals. This method is intended to be subclassed
        and then called from subclass with a list of neworks that should be
        processed into internal database format. The subclasses should only take
        care of providing this list of network and use the service of this method
        for the rest.

        This method does full rewrite of all internal structures to enable easy
        refresh feature.

        :param list networks: List of :py:class:`mentat.datatype.internal.NetworkRecord` objects.
        :return: Self
        :rtype: mentat.services.whois.WhoisModule
        """
        self.networks_ip4 = []
        self.networks_ip6 = []

        for net in networks:
            self.add_network(net)

        self.networks_ip4 = sorted(
            sorted(self.networks_ip4, key=lambda x: x["last"], reverse=True),
            key=lambda x: x["first"],
        )
        self.networks_ip6 = sorted(
            sorted(self.networks_ip6, key=lambda x: x["last"], reverse=True),
            key=lambda x: x["first"],
        )

        return self

    def add_network(self, network):
        """
        Add given network into internal whois lookup table.

        :param list network: Instance of :py:class:`mentat.datatype.internal.NetworkRecord`.
        :return: Self
        :rtype: mentat.services.whois.WhoisModule
        """
        if network["type"] == mentat.datatype.internal.NR_TYPE_IPV4:
            self.networks_ip4.append(network)
        elif network["type"] == mentat.datatype.internal.NR_TYPE_IPV6:
            self.networks_ip6.append(network)
        else:
            raise TypeError("Invalid network record type")

        return self

    def status(self):
        """
        Determine and return the status of internal whois lookup table.

        :return: Dictionary containing various subkeys.
        :rtype: dict
        """
        return {
            "name": self.__class__.__name__,
            "count_ip4": len(self.networks_ip4),
            "count_ip6": len(self.networks_ip6),
        }

    @staticmethod
    def _lookup_ipaddr(ipaddr, networks):
        """
        Internal method for doing actual IP address lookup.
        """
        result = []
        for net in networks:
            if ipaddr.low() < net["first"]:
                break
            if ipaddr.high() > net["last"]:
                continue
            if ipaddr.low() >= net["first"] and ipaddr.high() <= net["last"]:
                result.append(net)
        return sorted(result, key=lambda net: net.get("rank", -1))

    @staticmethod
    def _lookup_email(email, networks):
        """
        Internal method for doing actual email address lookup.
        """
        result = []
        for net in networks:
            if email in net["abuse_group"]:
                result.append(net)
                continue
            for severity in (
                "emails_info",
                "emails_low",
                "emails_medium",
                "emails_high",
                "emails_critical",
            ):
                if severity in net and email in net[severity]:
                    result.append(net)
        return result

    def lookup(self, arg):
        """
        Search for relevant records for given IP or email address withing internal
        whois lookup table.
        """
        try:
            if not isinstance(arg, ipranges.Range):
                arg = mentat.datatype.internal.t_net(arg)

            if isinstance(arg, (ipranges.IP4Net, ipranges.IP4Range, ipranges.IP4)):
                return self._lookup_ipaddr(arg, self.networks_ip4)
            if isinstance(arg, (ipranges.IP6Net, ipranges.IP6Range, ipranges.IP6)):
                return self._lookup_ipaddr(arg, self.networks_ip6)
        except Exception:  # pylint: disable=locally-disabled,broad-except
            pass

        return self._lookup_email(str(arg), self.networks_ip4 + self.networks_ip6)

    def lookup_abuse(self, arg, getall=False):
        """
        Search for relevant records for given IP or email address withing internal
        whois lookup table.
        """
        result = self.lookup(arg)
        if result:
            if not getall:
                return [result[-1]["abuse_group"]]
            return [item["abuse_group"] for item in result]
        return []


class FileWhoisModule(WhoisModule):
    """
    This whois module is capable of loading network records from JSON files.
    """

    def __init__(self, whois_file):
        super().__init__()

        self.whois_file = whois_file

    def setup(self, **kwargs):
        """
        Perform full setup of internal whois lookup table by loading the data from
        external file.
        """
        # Open and load the file.
        with open(self.whois_file, "r", encoding="utf8") as flh:
            contents = "\n".join(line for line in flh if not line.lstrip().startswith(("#", "//")))
            whois_file_data = json.loads(contents)

        # Perform some amount of preprocessing.
        whois_file_type = WHOIS_TYPE_GENERIC

        # Generate list of network record objects.
        networks = []
        for network_data in whois_file_data:
            nwr = mentat.datatype.internal.t_network_record(network_data, source=whois_file_type)
            networks.append(nwr)

        # Let the parent implementation take care of loading internal lookup table.
        return super().setup(networks)


class SqldbWhoisModule(WhoisModule):
    """
    This whois module is capable of loading network records from SQL database.
    """

    def __init__(self, storage_manager=None):
        super().__init__()

        self.stmng = storage_manager

    def setup(self, **kwargs):
        """
        Perform full setup of internal whois lookup table by loading the data from
        SQL database.
        """
        # Obtain reference for storage manager, if necessary.
        if not self.stmng:
            self.stmng = mentat.services.sqlstorage.manager()

        # Get backend storage connection.
        storage = self.stmng.service()

        # Load network records from SQL database.
        # Only load those networks, that are from enabled groups.
        records = (
            storage.session.query(NetworkModel).join(GroupModel, NetworkModel.group).filter(GroupModel.enabled).all()
        )

        # Generate list of internal network record objects.
        networks = []
        for rec in records:
            netw = {
                "id": rec.id,
                "netnames": [rec.netname],
                "source": rec.source,
                "network": rec.network,
                "description": rec.description,
                "abuse_group": rec.group.name,
                "is_base": rec.is_base,
            }
            if rec.rank:
                netw["rank"] = rec.rank
            networks.append(mentat.datatype.internal.t_network_record(netw))

        storage.session.commit()

        # Let the parent implementation take care of loading internal lookup table.
        return super().setup(networks)


class WhoisService:
    """
    Implementation of more complex whois service capable of encapsulating multiple
    instances of :py:class:`mentat.services.whois.WhoisModule`.
    """

    def __init__(self, modules=None):
        self.whois_modules = []
        if modules:
            for mod in modules:
                self.add_module(mod)

    def add_module(self, module):
        """
        Add given module into internal registry.
        """
        self.whois_modules.append(module)

    def setup(self):
        """
        Perform setup of all whois modules in internal registry. This method will
        cause refreshing/reloading of all internal lookup tables.
        """
        for mod in self.whois_modules:
            mod.setup()

    def status(self):
        """
        Determine the status of all whois modules in internal registry.
        """
        return [mod.status() for mod in self.whois_modules]

    def lookup(self, arg):
        """
        Perform lookup of given IP address and return list of all relevant network
        records.
        """
        for mod in self.whois_modules:
            result = mod.lookup(arg)
            if result:
                return result
        return []

    def lookup_abuse(self, arg, getall=False):
        """
        Search for relevant records for given IP or email address withing internal
        whois lookup table.
        """
        result = self.lookup(arg)
        if result:
            if not getall:
                return [result[-1]["abuse_group"]]
            return [item["abuse_group"] for item in result]
        return []


class WhoisServiceManager:
    """
    Class representing a custom whois service manager capable of understanding and
    parsing Mentat system core configurations and enabling easy way of unified
    bootstrapping of :py:class:`mentat.services.whois.WhoisService` service.
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize WhoisServiceManager object with full core configuration tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._whoisconfig = {}

        self._service = None

        self._configure_whois(core_config, updates)

    def _configure_whois(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._whoisconfig = copy.deepcopy(core_config[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_WHOIS])

        if updates and CKEY_CORE_SERVICES in updates and CKEY_CORE_SERVICES_WHOIS in updates[CKEY_CORE_SERVICES]:
            self._whoisconfig.update(updates[CKEY_CORE_SERVICES][CKEY_CORE_SERVICES_WHOIS])

    def service(self):
        """
        Return handle to whois service according to internal configurations.

        :return: Reference to whois service object.
        :rtype: mentat.services.whois.WhoisService
        """
        if not self._service:
            self._service = WhoisService()

            for module in self._whoisconfig["modules"]:
                try:
                    # module_class = getattr(mentat.services.whois, module['name'])
                    module_class = globals()[module["name"]]
                    whois_module = module_class(**module["config"])
                    self._service.add_module(whois_module.setup())
                except Exception as exc:
                    if not module.get("optional", False):
                        raise exc

        return self._service


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`WhoisServiceManager` instance at module level and
    store the refence within module.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = WhoisServiceManager(core_config, updates)


def manager():
    """
    Obtain reference to :py:class:`WhoisServiceManager` instance stored at module
    level.
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`WhoisService` instance from module level manager.
    """
    return manager().service()
