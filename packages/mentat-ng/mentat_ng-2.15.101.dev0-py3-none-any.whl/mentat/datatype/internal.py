#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Internal datatype library.


Library contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


* :py:class:`NetworkRecordIP4`
* :py:class:`NetworkRecordIP6`
* :py:class:`AbuseGroup`


.. todo::

    Documentation needs to be finished.

.. warning::

    Still should be considered as work in progress and alpha code.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import pprint
import random
import re
import string
import time

import ipranges
import typedcols

import mentat.const

NR_TYPE_IPV4 = "ipv4"
NR_TYPE_IPV6 = "ipv6"

NR_SOURCE_MANUAL = "manual"
NR_SOURCE_NEGISTRY = "negistry"
NR_SOURCE_WHOIS = "whois"

AG_REPORTING_MODE_SUMMARY = "summary"
AG_REPORTING_MODE_EXTRA = "extra"
AG_REPORTING_MODE_BOTH = "both"

RE_TIMESTAMP = re.compile(
    r"^([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?([Zz]|(?:[+-][0-9]{2}:[0-9]{2}))$"
)


# -------------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------------


def list_factory(name, item_type):
    """
    Default implementation of list factory.
    """
    return typedcols.typed_list(name, item_type)


def list_types(flavour, cb_list_factory=None):
    """
    Generate list type flavours from given scalar flavour definitions.

    :param dict flavour: Type flavour definitions
    :param list_factory: List factory callable
    :type list_factory: callable or None
    :return: list flavour
    :rtype: dict
    """
    if cb_list_factory is None:
        cb_list_factory = list_factory
    lists = {}
    for tpe in (
        "Integer",
        "String",
        "DBRefUsers",
        "DBRefGroups",
        "NetworkRecordOld",
        "ReportingFilter",
        "SavedQuery",
    ):
        lists[tpe] = cb_list_factory(tpe, flavour[tpe])
    return lists


def to_net4(val):
    """
    Convert any given value to :py:class:`ipranges.IP4Range`.

    :param any flavour: Value to be converted
    :return: Converted value
    :rtype: ipranges.IP4Range
    """
    return ipranges.IP4Range(val)


def to_net6(val):
    """
    Convert any given value to :py:class:`ipranges.IP6Net`.

    :param any flavour: Value to be converted
    :return: Converted value
    :rtype: ipranges.IP6Net
    """
    return ipranges.IP6Net(val)


def gen_sid():
    """
    Generate random unique subidentifier for :py:class:`NetworkRecord`.

    :return: Unique identifier 8 characters long
    :rtype: str
    """
    return "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(8))


# -------------------------------------------------------------------------------
# CONVERSION FUNCTIONS
# -------------------------------------------------------------------------------


def t_net4(val):
    """
    Convert/validate: Convert anything to :py:mod:`ipranges` IPv4 object class.

    :param any val: Value to be converted/validated
    :return: Object representing IPv4 address/network/range
    :rtype: ipranges.IP4Net or ipranges.IP4Range or ipranges.IP4
    :raises ValueError: if the value could not be converted to :py:mod:`ipranges` object
    """
    for tconv in ipranges.IP4Net, ipranges.IP4Range, ipranges.IP4:
        try:
            return tconv(val)
        except ValueError:
            pass
    raise ValueError(f"'{val:s}' does not appear as IPv4 address, network or range string")


def t_net6(val):
    """
    Convert/validate: Convert anything to :py:mod:`ipranges` IPv6 object class.

    :param any val: Value to be converted/validated
    :return: Object representing IPv6 address/network/range
    :rtype: ipranges.IP6Net or ipranges.IP6Range or ipranges.IP6
    :raises ValueError: if the value could not be converted to :py:mod:`ipranges` object
    """
    for tconv in ipranges.IP6Net, ipranges.IP6Range, ipranges.IP6:
        try:
            return tconv(val)
        except ValueError:
            pass
    raise ValueError(f"'{val:s}' does not appear as IPv6 address, network or range string")


def t_net(val):
    """
    Convert/validate: Convert anything to :py:mod:`ipranges` IPvX object class.

    :param any val: Value to be converted/validated
    :return: Object representing IPvX address/network/range
    :rtype: ipranges.IP4Net or ipranges.IP4Range or ipranges.IP4 or ipranges.IP6Net or ipranges.IP6Range or ipranges.IP6
    :raises ValueError: if the value could not be converted to :py:mod:`ipranges` object
    """
    for tconv in (
        ipranges.IP4Net,
        ipranges.IP4Range,
        ipranges.IP4,
        ipranges.IP6Net,
        ipranges.IP6Range,
        ipranges.IP6,
    ):
        try:
            return tconv(val)
        except ValueError:
            pass
    raise ValueError(f"'{val:s}' does not appear as IP address, network or range string")


def t_ip_range(val):
    """
    Convert/validate: IP range.

    :param any val: Value to be converted/validated
    :return: IP range
    :rtype: str
    """
    return str(val)


def t_datetime(val):
    """
    Convert/validate: Datetime.

    :param any val: Value to be converted/validated
    :return: Datetime object
    :rtype: datetime.datetime
    :raises ValueError: if the value could not be converted to datetime.datetime object
    """
    # Maybe there is nothing to do
    if isinstance(val, datetime.datetime):
        return val

    # Try numeric type
    try:
        return datetime.datetime.fromtimestamp(float(val))
    except (TypeError, ValueError):
        pass

    if str(val) == "":
        return None

    # Try RFC3339 string
    res = RE_TIMESTAMP.match(val)
    if res is not None:
        year, month, day, hour, minute, second = (int(n or 0) for n in res.group(*range(1, 7)))
        usec_str = (res.group(7) or "0")[:6].ljust(6, "0")
        usec = int(usec_str)
        zonestr = res.group(8)
        zonespl = (0, 0) if zonestr in ["z", "Z"] else [int(i) for i in zonestr.split(":")]
        zonediff = datetime.timedelta(minutes=zonespl[0] * 60 + zonespl[1])
        return datetime.datetime(year, month, day, hour, minute, second, usec) - zonediff
    raise ValueError(f"Invalid datetime '{val:s}'")


def t_dbref(val):
    """
    Convert/validate: Database reference.
    """
    if isinstance(val, str):
        return val
    return val.id


def t_network_record_type_ip4(val):
    """
    Convert/validate: Network record type.

    :param any val: Value to be converted/validated
    :return: network record type.
    :rtype: str
    :raises ValueError: if the value is not valid network record type
    """
    if str(val) == "ipv4":
        return str(val)
    raise ValueError(f"Invalid type '{val:s}' for network record")


def t_network_record_type_ip6(val):
    """
    Convert/validate: Network record type.

    :param any val: Value to be converted/validated
    :return: network record type.
    :rtype: str
    :raises ValueError: if the value is not valid network record type
    """
    if str(val) == "ipv6":
        return str(val)
    raise ValueError(f"Invalid type '{val:s}' for network record")


def t_network_record_old(val, source=None):
    """
    Dummy convertor for legacy purposes.
    """
    return val


def t_network_record(val, source=None):
    """
    Convert/validate: Network record.

    :param any val: Value to be converted/validated
    :return: network record object.
    :rtype: NetworkRecord
    :raises ValueError: if the value is not valid network record
    """
    if isinstance(val, NetworkRecord):
        return val

    record = {}

    # 'network' and 'type' records come mainly from database
    if "network" in val:
        if "type" in val and val["type"] == NR_TYPE_IPV4:
            record["nrobj"] = ipranges.from_str_v4(val["network"])
            record["type"] = NR_TYPE_IPV4
        elif "type" in val and val["type"] == NR_TYPE_IPV6:
            record["nrobj"] = ipranges.from_str_v6(val["network"])
            record["type"] = NR_TYPE_IPV6
        else:
            record["nrobj"] = ipranges.from_str(val["network"])
            if isinstance(record["nrobj"], (ipranges.IP4Net, ipranges.IP4Range, ipranges.IP4)):
                record["type"] = NR_TYPE_IPV4
            else:
                record["type"] = NR_TYPE_IPV6

    # 'ip4_start' and 'ip4_end' come from Negistry whois file
    elif "ip4_start" in val and "ip4_end" in val:
        record["nrobj"] = to_net4("{}-{}".format(val["ip4_start"], val["ip4_end"]))
        record["type"] = NR_TYPE_IPV4

    # 'ip6_addr' and 'ip6_prefix' come from Negistry whois file
    elif "ip6_addr" in val and "ip6_prefix" in val:
        record["nrobj"] = to_net6("{}/{}".format(val["ip6_addr"], val["ip6_prefix"]))
        record["type"] = NR_TYPE_IPV6

    else:
        raise ValueError(f"Unknown network record {pprint.pformat(val)}")

    record["id"] = val.get("id", gen_sid())
    record["network"] = str(record["nrobj"])
    if record["type"] == NR_TYPE_IPV4:
        record["ip4_start"] = record["nrobj"].to_str(record["nrobj"].low())
        record["ip4_end"] = record["nrobj"].to_str(record["nrobj"].high())
    # base and cidr are only available for ipranges.IP6Net
    elif isinstance(record["nrobj"], ipranges.IP6Net):
        record["ip6_addr"] = record["nrobj"].to_str(record["nrobj"].base)
        record["ip6_prefix"] = record["nrobj"].cidr

    record["first"] = record["nrobj"].low()
    record["last"] = record["nrobj"].high()

    if "netnames" in val:
        if isinstance(val["netnames"], list):
            record["netname"] = ", ".join(val["netnames"])
        else:
            record["netname"] = val["netnames"]

    if "description" in val:
        if isinstance(val["description"], list):
            record["description"] = ", ".join(val["description"])
        else:
            record["description"] = val["description"]

    elif "descr" in val:
        if isinstance(val["descr"], list):
            record["description"] = ", ".join(val["descr"])
        else:
            record["description"] = val["descr"]

    if "source" in val:
        record["source"] = val["source"]
    else:
        if "feed" in val:
            record["source"] = source + "/" + val["feed"]
        else:
            record["source"] = source

    if "abuse_group" in val:
        record["abuse_group"] = val["abuse_group"]
        record["is_base"] = val.get("is_base", False)
    elif "resolved_abuses" in val:
        for severity in ["fallback"] + list(mentat.const.REPORT_SEVERITIES):
            if severity in val["resolved_abuses"]:
                record[f"emails_{severity}"] = val["resolved_abuses"][severity]

        # compute resulting abuse group from all emails
        emails = []
        for severity in (
            "emails_fallback",
            "emails_info",
            "emails_low",
            "emails_medium",
            "emails_high",
            "emails_critical",
        ):
            if severity in record:
                emails.extend(record[severity])
        if emails:
            record["abuse_group"] = "_".join(sorted(map(str.lower, list(set(emails)))))

        record["is_base"] = val["is_base"] if "is_base" in val else "fallback" in val["resolved_abuses"]

    if "emails" in val:
        record["emails"] = val["emails"]

    if "rank" in val:
        record["rank"] = val["rank"]

    if "client_id" in val:
        record["local_id"] = val["client_id"]

    if record["type"] == NR_TYPE_IPV4:
        return NetworkRecordIP4(record)
    return NetworkRecordIP6(record)


def t_reporting_mode(val):
    """
    Convert/validate: Reporting mode.
    """
    if str(val) in [
        AG_REPORTING_MODE_SUMMARY,
        AG_REPORTING_MODE_EXTRA,
        AG_REPORTING_MODE_BOTH,
    ]:
        return str(val)
    raise ValueError(f"Invalid reporting mode '{val:s}' for abuse group")


def t_reporting_filter(val):
    """
    Convert/validate: Reporting filter.
    """
    if isinstance(val, ReportingFilter):
        return val
    return ReportingFilter(val)


def t_filter_type(val):
    """
    Convert/validate: Reporting filter type.
    """
    if str(val) == "simple":
        val = "basic"
    return val


def t_saved_query(val):
    """
    Convert/validate: Saved query.
    """
    return val


def t_detector_record(val, source):
    """
    Convert/validate: Detector record.

    :param any val: Value to be converted/validated
    :return: detector record object
    :rtype: DetectorRecord
    :raises ValueError: if the value is not valid detector record
    """
    if isinstance(val, Detector):
        return val

    record = {}

    try:
        record["_id"] = val.get("id", gen_sid())
        record["source"] = source
        record["name"] = val["name"]
        if val.get("note"):
            record["description"] = val["note"]
        record["credibility"] = val.get("credibility", 1.0)
        if "registered" in val:
            record["registered"] = val["registered"]
    except Exception as exc:
        raise ValueError(f"Unknown detector record {pprint.pformat(val)}") from exc
    return Detector(record)


# -------------------------------------------------------------------------------
# DATATYPE DEFINITIONS
# -------------------------------------------------------------------------------


class NetworkRecord(typedcols.TypedDict):
    """
    Base class for all NetworkRecord structures.
    """

    allow_unknown = False

    def fingerprint(self):
        """
        Return network fingerprint (concatenation of network and source).
        """
        return "{:s}:{:s}".format(self["network"], self["source"])


types_internal = {
    "Boolean": bool,
    "Integer": int,
    "String": str,
    "Binary": str,
    "Float": float,
    "Ip4Numeric": int,
    "Ip6Numeric": int,
    "IPRange": t_ip_range,
    "Datetime": t_datetime,
    "DBRefUsers": t_dbref,
    "DBRefGroups": t_dbref,
    "NetRecTypeIP4": t_network_record_type_ip4,
    "NetRecTypeIP6": t_network_record_type_ip6,
    "NetworkRecordOld": t_network_record_old,
    "ReportingMode": t_reporting_mode,
    "ReportingFilter": t_reporting_filter,
    "FilterType": t_filter_type,
    "SavedQuery": t_saved_query,
}

types_internal_list = list_types(types_internal)


def typedef_network_record_ip4(flavour, list_flavour, addon=None):
    """
    Typedef generator for IPv4 network records.
    """
    tdef = {
        "id": {"type": flavour["String"]},
        "createtime": {
            "type": flavour["Datetime"],
            "required": True,
            "default": time.time,
        },
        "network": {"type": flavour["String"], "required": True},
        "source": {"type": flavour["String"], "required": True},
        "nrobj": {"type": flavour["IPRange"], "required": True},
        "type": {"type": flavour["NetRecTypeIP4"], "required": True},
        "netname": {"type": flavour["String"]},
        "description": {"type": flavour["String"]},
        "ip4_start": {"type": flavour["String"]},
        "ip4_end": {"type": flavour["String"]},
        "first": {"type": flavour["Ip4Numeric"]},
        "last": {"type": flavour["Ip4Numeric"]},
        "emails": {"type": list_flavour["String"]},
        "emails_fallback": {"type": list_flavour["String"]},
        "emails_info": {"type": list_flavour["String"]},
        "emails_low": {"type": list_flavour["String"]},
        "emails_medium": {"type": list_flavour["String"]},
        "emails_high": {"type": list_flavour["String"]},
        "emails_critical": {"type": list_flavour["String"]},
        "resolved_abuses": {"type": list_flavour["String"]},
        "is_base": {"type": flavour["Boolean"]},
        "abuse_group": {"type": flavour["String"]},
        "rank": {"type": flavour["Integer"]},
        "local_id": {"type": flavour["String"]},
        "_resolved_abuses_chain": typedcols.Discard,
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class NetworkRecordIP4(NetworkRecord):
    """
    Implementation of IPv4 network record structure.
    """

    typedef = typedef_network_record_ip4(types_internal, types_internal_list)


def typedef_network_record_ip6(flavour, list_flavour, addon=None):
    """
    Typedef generator for IPv6 network records.
    """
    tdef = {
        "id": {"type": flavour["String"]},
        "createtime": {
            "type": flavour["Datetime"],
            "required": True,
            "default": time.time,
        },
        "network": {"type": flavour["String"], "required": True},
        "source": {"type": flavour["String"], "required": True},
        "nrobj": {"type": flavour["IPRange"], "required": True},
        "type": {"type": flavour["NetRecTypeIP6"], "required": True},
        "netname": {"type": flavour["String"]},
        "description": {"type": flavour["String"]},
        "ip6_addr": {"type": flavour["String"]},
        "ip6_prefix": {"type": flavour["Integer"]},
        "first": {"type": flavour["Ip6Numeric"]},
        "last": {"type": flavour["Ip6Numeric"]},
        "emails": {"type": list_flavour["String"]},
        "emails_fallback": {"type": list_flavour["String"]},
        "emails_info": {"type": list_flavour["String"]},
        "emails_low": {"type": list_flavour["String"]},
        "emails_medium": {"type": list_flavour["String"]},
        "emails_high": {"type": list_flavour["String"]},
        "emails_critical": {"type": list_flavour["String"]},
        "resolved_abuses": {"type": list_flavour["String"]},
        "is_base": {"type": flavour["Boolean"]},
        "abuse_group": {"type": flavour["String"]},
        "rank": {"type": flavour["Integer"]},
        "local_id": {"type": flavour["String"]},
        "_resolved_abuses_chain": typedcols.Discard,
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class NetworkRecordIP6(NetworkRecord):
    """
    Implementation of IPv6 network record structure.
    """

    typedef = typedef_network_record_ip6(types_internal, types_internal_list)


# -------------------------------------------------------------------------------


def typedef_filter(flavour, list_flavour, addon=None):
    """
    Typedef generator reporting filter records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True, "default": gen_sid},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "filter": {"type": flavour["String"], "required": True},
        "description": {"type": flavour["String"], "required": True},
        "note": {"type": flavour["String"]},
        "type": {"type": flavour["FilterType"], "required": True},
        "validfrom": {"type": flavour["Datetime"]},
        "validto": {"type": flavour["Datetime"]},
        "analyzers": {"type": list_flavour["String"]},
        "categories": {"type": list_flavour["String"]},
        "ips": {"type": list_flavour["String"]},
        "enabled": {"type": flavour["Boolean"]},
        "hits": {"type": flavour["Integer"]},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class ReportingFilter(typedcols.TypedDict):
    """
    Implementation of reporting filter record structure.
    """

    typedef = typedef_filter(types_internal, types_internal_list)


# -------------------------------------------------------------------------------


def typedef_abuse_group(flavour, list_flavour, addon=None):
    """
    Typedef generator for abuse group records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "managers": {
            "type": list_flavour["DBRefUsers"],
            "required": True,
            "default": list,
        },
        "source": {
            "type": flavour["String"],
            "required": True,
            "default": NR_SOURCE_NEGISTRY,
        },
        "description": {"type": flavour["String"]},
        "subnet_cache": {
            "type": flavour["Boolean"],
            "required": True,
            "default": False,
        },
        "networks": {"type": list_flavour["NetworkRecordOld"]},
        "rep_mode": {
            "type": flavour["ReportingMode"],
            "required": True,
            "default": AG_REPORTING_MODE_SUMMARY,
        },
        "rep_emails_info": {"type": list_flavour["String"]},
        "rep_emails_low": {"type": list_flavour["String"]},
        "rep_emails_medium": {"type": list_flavour["String"]},
        "rep_emails_high": {"type": list_flavour["String"]},
        "rep_emails_critical": {"type": list_flavour["String"]},
        "rep_filters": {"type": list_flavour["ReportingFilter"]},
        "rep_mute": {"type": flavour["Boolean"], "required": True, "default": False},
        "rep_redirect": {"type": flavour["Boolean"], "required": True, "default": True},
        "query": {"type": list_flavour["SavedQuery"]},
        "subnet": {"type": list_flavour["String"]},
        "id": {"type": flavour["String"]},
        "local_id": {"type": flavour["String"]},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class AbuseGroup(typedcols.TypedDict):
    """
    Implementation of abuse group record structure.
    """

    allow_unknown = False
    typedef = typedef_abuse_group(types_internal, types_internal_list)

    @staticmethod
    def _is_network_in(network, netlist):
        """ """
        return any(net.fingerprint() == network.fingerprint() for net in netlist)

    def network_add(self, network):
        """
        Update abuse group network list coming from given source.
        """
        # if not isinstance(network, NetworkRecord):
        #    network = t_network_record(network)
        for net in self["networks"]:
            if net.fingerprint() == network.fingerprint():
                return "Network already exists"
        self["networks"].append(network)
        return "Network added"

    def networks_update(self, networks):
        """
        Update abuse group network list coming from given source.
        """
        changelog = []
        for net in networks:
            # if not isinstance(net, NetworkRecord):
            #    net = NetworkRecord(net)
            if not self._is_network_in(net, self["networks"]):
                changelog.append(f"Added network '{net.fingerprint():s}'")
                self["networks"].append(net)

        res = []
        for net in self["networks"]:
            if not self._is_network_in(net, networks):
                changelog.append(f"Removed network '{net.fingerprint():s}'")
            else:
                res.append(net)
        self["networks"] = res

        return changelog


# -------------------------------------------------------------------------------


def typedef_user(flavour, list_flavour, addon=None):
    """
    Typedef generator for user records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True},
        "id": {"type": flavour["String"]},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "name": {"type": flavour["String"], "required": True},
        "email": {"type": flavour["String"], "required": True},
        "organization": {"type": flavour["String"], "required": True},
        "roles": {"type": list_flavour["String"], "required": True, "default": list},
        "groups": {
            "type": list_flavour["DBRefGroups"],
            "required": True,
            "default": list,
        },
        "ts_last_login": {"type": flavour["Datetime"]},
        "certificate": {"type": flavour["String"]},
        "certificate_hash": {"type": flavour["String"]},
        "affiliations": {"type": list_flavour["String"], "default": list},
        "orggroups": {"type": list_flavour["String"], "default": list},
        "query": {"type": list_flavour["SavedQuery"], "default": list},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class User(typedcols.TypedDict):
    """
    Implementation of abuse group record structure.
    """

    allow_unknown = False
    typedef = typedef_user(types_internal, types_internal_list)


# -------------------------------------------------------------------------------


def typedef_event_stat(flavour, list_flavour, addon=None):
    """
    Typedef generator for event statistics records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "ts_from": {
            "type": flavour["Datetime"],
            "required": True,
            "default": time.time,
        },
        "ts_to": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "count": {"type": flavour["Integer"], "required": True},
        "internal": {"required": True},
        "external": {"required": True},
        "overall": {"required": True},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class EventStat(typedcols.TypedDict):
    """
    Implementation of event stat structure.
    """

    allow_unknown = True
    typedef = typedef_event_stat(types_internal, types_internal_list)


# -------------------------------------------------------------------------------


def typedef_detector(flavour, list_flavour, addon=None):
    """
    Typedef generator for detector records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "name": {"type": flavour["String"], "required": True},
        "source": {"type": flavour["String"], "required": True},
        "description": {"type": flavour["String"]},
        "credibility": {"type": flavour["Float"], "required": True},
        "registered": {"type": flavour["Datetime"], "default": time.time},
        "hits": {"type": flavour["Integer"]},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class Detector(typedcols.TypedDict):
    """
    Implementation of detector structure.
    """

    allow_unknown = True
    typedef = typedef_detector(types_internal, types_internal_list)


# -------------------------------------------------------------------------------


def typedef_report(flavour, list_flavour, addon=None):
    """
    Typedef generator for report records.
    """
    tdef = {
        "_id": {"type": flavour["String"], "required": True},
        "id": {"type": flavour["String"], "required": True},
        "ua_hash": {"type": flavour["String"], "required": True},
        "ts": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "ts_from": {
            "type": flavour["Datetime"],
            "required": True,
            "default": time.time,
        },
        "ts_to": {"type": flavour["Datetime"], "required": True, "default": time.time},
        "abuse": {"type": flavour["String"], "required": True},
        "severity": {"type": flavour["String"], "required": True},
        "type": {"type": flavour["String"], "required": True},
        "message": {"type": flavour["String"], "required": True},
        "flag_archived": {"type": flavour["Boolean"], "required": True},
        "flag_jarchived": {"type": flavour["Boolean"], "required": True},
        "flag_mail_sent": {"type": flavour["Boolean"], "required": True},
        "test_data": {"type": flavour["Boolean"], "required": True},
        "to": {"type": flavour["String"], "required": True},
        "mail_to": {"type": flavour["String"], "required": True},
        "mail_res": {"type": flavour["String"], "required": True},
        "mail_ts": {
            "type": flavour["Datetime"],
            "required": True,
            "default": time.time,
        },
        "cnt_all": {"type": flavour["Integer"], "required": True},
        "cnt_flt": {"type": flavour["Integer"], "required": True},
        "cnt_flt_blk": {"type": flavour["Integer"], "required": True},
        "cnt_det": {"type": flavour["Integer"], "required": True},
        "cnt_det_blk": {"type": flavour["Integer"], "required": True},
        "cnt_thr": {"type": flavour["Integer"], "required": True},
        "cnt_thr_blk": {"type": flavour["Integer"], "required": True},
        "cnt_rlp": {"type": flavour["Integer"], "required": True},
        "cnt_alerts": {"type": flavour["Integer"], "required": True},
        "cnt_analyzers": {"type": flavour["Integer"], "required": True},
        "list_analyzers": {"type": list_flavour["String"], "required": True},
        "analyzers": {"required": True},
        "cnt_detectorsws": {"type": flavour["Integer"], "required": True},
        "list_detectorsws": {"type": list_flavour["String"], "required": True},
        "detectorsws": {"required": True},
        "cnt_detectors": {"type": flavour["Integer"], "required": True},
        "list_detectors": {"type": list_flavour["String"], "required": True},
        "detectors": {"required": True},
        "cnt_categories": {"type": flavour["Integer"], "required": True},
        "list_categories": {"type": list_flavour["String"], "required": True},
        "categories": {"required": True},
        "cnt_category_sets": {"type": flavour["Integer"], "required": True},
        "list_category_sets": {"type": list_flavour["String"], "required": True},
        "category_sets": {"required": True},
        "cnt_ips": {"type": flavour["Integer"], "required": True},
        "list_ips": {"type": list_flavour["String"], "required": True},
        "ips": {"required": True},
        "list_ids": {"type": list_flavour["String"], "required": True},
        "frv": {"required": True},
    }
    if addon is not None:
        tdef.update(addon)
    return tdef


class Report(typedcols.TypedDict):
    """
    Implementation of report structure.
    """

    allow_unknown = True
    typedef = typedef_report(types_internal, types_internal_list)
