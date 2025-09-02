#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides classess and tools for object representation of
`IDEA <https://idea.cesnet.cz/en/index>`__ messages in Mentat project.

This module is based on ``idea.lite`` module from `idea <https://gitlab.cesnet.cz/713/warden/idea.git>`__
package. It is attempting to reuse already defined structures wherever
and whenever possible and only append few custom datatypes to existing
definition.

The most important part of this module, which is available to users, is
the :py:class:`mentat.idea.internal.Idea` class. Following code snippet
demonstates use case scenario:

.. code-block:: python

    >>> import mentat.idea.internal

    # IDEA messages ussually come from regular dicts or JSON
    >>> idea_raw = {...}

    # Just pass the dict as parameter to constructor
    >>> idea_msg = mentat.idea.internal.Idea(idea_raw)

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import json
import pprint
import re
from base64 import b64decode
from collections.abc import Mapping, MutableSequence

import idea.base
import idea.lite

import ipranges
import typedcols
from ransack import get_values


def mentat_dict_typedef(flavour, list_flavour, errors_list, abuses_list, addon=None):
    """
    Typedef generator helper for easy usage of custom definitions at
    multiple places.
    """
    mentat_def = {
        "InspectionErrors": {
            "description": "List of event pecularities found during inspection",
            "type": errors_list,
        },
        "StorageTime": {
            "description": "Unix timestamp of the moment the message was stored into database",
            "type": flavour["Timestamp"],
        },
        "EventTemplate": {
            "description": "Template used to generate the event (deprecated)",
            "type": flavour["String"],
        },
        "EventClass": {
            "description": "Event class determined by inspection",
            "type": flavour["String"],
        },
        "EventSeverity": {
            "description": "Event severity determined by inspection",
            "type": flavour["String"],
        },
        "Impact": {
            "description": "More user friendly description of event impact, used for reporting (IDMEF legacy)",
            "type": flavour["String"],
        },
        "ResolvedAbuses": {
            "description": "Abuse contacts related to any alert source",
            "type": abuses_list,
        },
        "SourceResolvedASN": {
            "description": "AS numbers related to any alert source",
            "type": list_flavour["Integer"],
        },
        "SourceResolvedCountry": {
            "description": "Coutry ISO codes related to any alert source",
            "type": list_flavour["String"],
        },
    }
    if addon is not None:
        mentat_def.update(addon)
    return mentat_def


# Extracted methods from Pynspect's JPath

#: Status code for ``success``, returned by function :py:func:`jpath_set`.
JPATH_RC_VALUE_SET = 0

#: Status code for ``already-exists``, returned by function :py:func:`jpath_set`.
JPATH_RC_VALUE_EXISTS = 1

#: Status code for ``not-unique``, returned by function :py:func:`jpath_set`.
JPATH_RC_VALUE_DUPLICATE = 2


def jpath_parse(jpath):
    """
    Parse given JPath into chunks.

    Returns list of dictionaries describing all of the JPath chunks.

    :param str jpath: JPath to be parsed into chunks
    :return: JPath chunks as list of dicts
    :rtype: :py:class:`list`
    :raises ValueError: in case of invalid JPath syntax
    """
    result = []
    breadcrumbs = []
    RE_JPATH_CHUNK = re.compile(r"^([a-zA-Z0-9_]+)(\[(#|\*|\d+)\])?$")

    # Split JPath into chunks based on '.' character.
    chunks = jpath.split(".")
    for chnk in chunks:
        match = RE_JPATH_CHUNK.match(chnk)
        if match:
            res = {}

            # Record whole match.
            res["m"] = chnk

            # Record breadcrumb path.
            breadcrumbs.append(chnk)
            res["p"] = ".".join(breadcrumbs)

            # Handle node name.
            res["n"] = match.group(1)

            # Handle node index (optional, may be omitted).
            if match.group(2):
                res["i"] = match.group(3)
                if str(res["i"]) == "#":
                    res["i"] = -1
                elif str(res["i"]) == "*":
                    pass
                else:
                    res["i"] = int(res["i"]) - 1

            result.append(res)
        else:
            raise ValueError(f"Invalid JPath chunk '{chnk}'")
    return result


def jpath_set(structure, jpath, value, overwrite=True, unique=False):
    """
    Set given JPath to given value within given structure.

    For performance reasons this method is intentionally not written as
    recursive.

    :param Mapping structure: data structure to be searched
    :param str jpath: JPath to be evaluated
    :param any value: value of any type to be set at given path
    :param bool overwrite: enable/disable overwriting of already existing value
    :param bool unique: ensure uniqueness of value, works only for lists
    :return: numerical return code, one of the (:py:data:`JPATH_RC_VALUE_SET`,
             :py:data:`JPATH_RC_VALUE_EXISTS`, :py:data:`JPATH_RC_VALUE_DUPLICATE`)
    :rtype: int
    """
    chunks = jpath_parse(jpath)
    size = len(chunks) - 1
    current = structure

    # Process chunks in order, enumeration is used for detection of the last JPath chunk.
    for i, chnk in enumerate(chunks):
        key = chnk["n"]

        if not isinstance(current, dict) and not isinstance(current, Mapping):
            raise ValueError(f"Expected dict-like structure to attach node '{chnk['p']}'")

        # Process indexed nodes.
        if "i" in chnk:
            idx = chnk["i"]

            # Automatically create nodes for non-existent keys.
            if key not in current:
                current[key] = []
            if not isinstance(current[key], list) and not isinstance(current[key], MutableSequence):
                raise ValueError(f"Expected list-like object under structure key '{key}'")

            # Detection of the last JPath chunk - node somewhere in the middle.
            if i != size:
                # Attempt to access node at given index.
                try:
                    current = current[key][idx]
                # IndexError: list index out of range
                # Node at given index does not exist, append new one. Using insert()
                # does not work, item is appended to the end of the list anyway.
                # TypeError: list indices must be integers or slices, not str
                # In the case list index was '*', we are appending to the end of
                # list.
                except (IndexError, TypeError):
                    current[key].append({})
                    current = current[key][-1]

            # Detection of the last JPath chunk - node at the end.
            else:
                # Attempt to insert value at given index.
                try:
                    if overwrite or not current[key][idx]:
                        current[key][idx] = value
                    else:
                        return JPATH_RC_VALUE_EXISTS
                # IndexError: list index out of range
                # Node at given index does not exist, append new one. Using insert()
                # does not work, item is appended to the end of the list anyway.
                # TypeError: list indices must be integers or slices, not str
                # In the case list index was '*', we are appending to the end of
                # list.
                except (IndexError, TypeError):
                    # At this point only deal with unique, overwrite does not make
                    # sense, because we would not be here otherwise.
                    if not unique or value not in current[key]:
                        current[key].append(value)
                    else:
                        return JPATH_RC_VALUE_DUPLICATE

        # Process unindexed nodes.
        else:
            # Detection of the last JPath chunk - node somewhere in the middle.
            if i != size:
                # Automatically create nodes for non-existent keys.
                if key not in current:
                    current[key] = {}
                if not isinstance(current[key], dict) and not isinstance(current[key], Mapping):
                    raise ValueError(f"Expected dict-like object under structure key '{key}'")

                current = current[key]

            # Detection of the last JPath chunk - node at the end.
            else:
                if overwrite or key not in current:
                    current[key] = value
                else:
                    return JPATH_RC_VALUE_EXISTS
    return JPATH_RC_VALUE_SET


class MentatDict(typedcols.TypedDict):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    This type definition represents a custom subdictionary under key
    *_Mentat* in message root dictionary.
    """

    allow_unknown = True
    typedef = mentat_dict_typedef(
        idea.lite.idea_types,
        idea.lite.idea_lists,
        typedcols.typed_list("InspectionErrorsList", str),
        typedcols.typed_list("ResolvedAbusesList", str),
    )


def internal_base_addon_typedef(flavour, list_flavour, mentat_dict, addon=None):  # pylint: disable=locally-disabled,unused-argument
    """
    Typedef generator helper for easy usage of custom definitions at
    multiple places.
    """
    addon_def = {
        "ts": {
            "description": "CESNET specific timestamp as NTP timestamp",
            "type": flavour["Timestamp"],
        },
        "ts_u": {
            "description": "CESNET specific timestamp as native Unix timestamp",
            "type": flavour["Integer"],
        },
        "_Mentat": {
            "description": "Custom CESNET/Mentat abominations to IDEA definition",
            "type": mentat_dict,
        },
    }
    if addon is not None:
        addon_def.update(addon)
    return addon_def


class Idea(idea.lite.Idea):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    This class attempts to make only very contained changes to original
    ``idea.lite.Idea`` class, so that there is no need to update this class
    in case underlying definition changes.

    To make these changes, the *addon* feature of ``typedcols`` library is
    used.
    """

    allow_unknown = True
    typedef = idea.base.idea_typedef(
        idea.lite.idea_types,
        idea.lite.idea_lists,
        idea.lite.idea_defaults,
        typedcols.typed_list("SourceList", idea.lite.SourceTargetDict),
        typedcols.typed_list("TargetList", idea.lite.SourceTargetDict),
        typedcols.typed_list("AttachList", idea.lite.AttachDict),
        typedcols.typed_list("NodeList", idea.lite.NodeDict),
        internal_base_addon_typedef(idea.lite.idea_types, idea.lite.idea_lists, MentatDict),
    )

    json_default = staticmethod(idea.lite.Idea.json_default)
    """
    Helper method for JSON serialization of :py:class:`mentat.idea.internal.Idea`
    messages.

    Example usage:

    .. code-block:: python

        >>>import json
        >>>idea_internal = ...
        >>>json.dumps(idea_internal, indent=4, sort_keys=True, default=idea_internal.json_default)
    """

    @staticmethod
    def from_json(json_string):
        """
        Instantinate message object directly from given JSON serialized string.
        """
        return Idea(json.loads(json_string))

    def get_id(self):
        """
        Convenience method for returning message identifier.

        :return: Value of message attribute ``idea['ID']``.
        :rtype: str
        """
        return self["ID"]

    def get_tlp(self):
        """
        Convenience method for returning message TLP (Traffic Light Protocol).

        :return: Value of message attribute ``idea['TLP']``.
        :rtype: str | None
        """
        if self.get("TLP"):
            return self["TLP"].upper()
        return None

    def has_restricted_access(self) -> bool:
        """
        Convenience method to check if access to this event is restricted
        based on the value of TLP field.

        :return: True if the access is restricted, False otherwise.
        """
        return self.get_tlp() in ["AMBER-STRICT", "AMBER", "RED"]

    def get_detect_time(self):
        """
        Convenience method for returning message detection time.

        :return: Value of message attribute ``idea['DetectTime']``.
        :rtype: datetime.datetime
        """
        return self["DetectTime"]

    def get_custom_key(self):
        """
        Convenience method for returning the correct custom key.

        :return: The value of _Mentat if present, otherwise an empty dictionary is returned.
        :rtype: mentat_dict
        """
        return self.get("_Mentat", {})

    def get_storage_time(self):
        """
        Convenience method for returning message storage time.

        :return: Value of message attribute ``idea['_Mentat']['StorageTime']``.
        :rtype: datetime.datetime
        """
        return self.get_custom_key().get("StorageTime", None)

    def get_class(self):
        """
        Convenience method for returning message source class.

        :return: Value of message attribute ``idea['_Mentat']['EventClass']``.
        :rtype: str
        """
        return self.get_custom_key().get("EventClass", None)

    def get_target_class(self):
        """
        Convenience method for returning message target class.

        :return: Value of message attribute ``idea['_Mentat']['TargetClass']``.
        :rtype: str
        """
        return self.get_custom_key().get("TargetClass", None)

    def get_subclass(self):
        """
        Convenience method for returning message source subclass.

        :return: Value of message attribute ``idea['_Mentat']['EventSubclass']``.
        :rtype: str
        """
        return ", ".join(self.get_custom_key().get("EventSubclass", []))

    def get_target_subclass(self):
        """
        Convenience method for returning message target subclass.

        :return: Value of message attribute ``idea['_Mentat']['TargetSubclass']``.
        :rtype: str
        """
        return ", ".join(self.get_custom_key().get("TargetSubclass", []))

    def get_whole_class(self):
        """
        Convenience method for returning message event class and subclass.

        :rtype: str
        """
        if self.get_class() and self.get_subclass():
            return f"{self.get_class()}/{self.get_subclass()}"
        return self.get_class()

    def get_whole_target_class(self):
        """
        Convenience method for returning message target event class and target subclass.

        :rtype: str
        """
        if self.get_target_class() and self.get_target_subclass():
            return f"{self.get_target_class()}/{self.get_target_subclass()}"
        return self.get_target_class()

    def get_severity(self):
        """
        Convenience method for returning message event severity.

        :return: Value of message attribute ``idea['_Mentat']['EventSeverity']``.
        :rtype: str
        """
        return self.get_custom_key().get("EventSeverity", None)

    def get_target_severity(self):
        """
        Convenience method for returning message target severity.

        :return: Value of message attribute ``idea['_Mentat']['TargetSeverity']``.
        :rtype: str
        """
        return self.get_custom_key().get("TargetSeverity", None)

    def get_source_groups(self):
        """
        Convenience method for returning list of all resolved source groups.

        :return: Value of message attribute ``idea['_Mentat']['ResolvedAbuses']``.
        :rtype: list of strings
        """
        return list(self.get_custom_key().get("ResolvedAbuses", []))

    def get_target_groups(self):
        """
        Convenience method for returning list of all target groups.

        :return: Value of message attribute ``idea['_Mentat']['TargetAbuses']``.
        :rtype: list of strings
        """
        return list(self.get_custom_key().get("TargetAbuses", []))

    def get_all_groups(self):
        """
        Convenience method for returning a deduplicated list of all groups in an event.

        :return: Deduplicated list of source and target groups.
        :rtype: list of strings
        """
        return list(set(self.get_source_groups() + self.get_target_groups()))

    def get_categories(self):
        """
        Convenience method for returning list of all message categories.

        :return: Value of message attribute ``idea['Category']``.
        :rtype: list of strings
        """
        return list(self["Category"])

    def get_description(self):
        """
        Convenience method for returning message description.

        :return: Value of message attribute ``idea['description']``.
        :rtype: list of strings
        """
        return self.get("Description", None)

    def get_detectors(self):
        """
        Convenience method for returning list of all message detectors.

        :return: Value of message attribute ``idea['Node']['Name']``.
        :rtype: list of strings
        """
        return [name for name in (node.get("Name", None) for node in self.get("Node", [])) if name]

    def get_last_detector_name(self) -> str:
        """
        Convenience method for returning the name of the last detector,
        or UNKNOWN if the last detector does not have a name.
        This is used to uniquely identify detectors.
        """
        if self.get_detectors()[-1]:
            return str(self.get_detectors()[-1])
        return "UNKNOWN"

    @staticmethod
    def get_ranges(addresses, rngcls, ipcls):
        """
        Helper function for making ranges of IP addresses.

        :param list addrs: List of single addresses, nets or ranges of IP4 or IP6 addresses.
        :param class rngcls: The class of returned list (either IP4Range or IP6Range).
        :param class ipcls: The class of single IP address (either IP4 or IP6).
        :return: The list of ranges of IP addresses.
        :rtype: list of ``rngcls`` objects
        """
        addrs = sorted(addresses, reverse=True, key=lambda ip: ip.high())

        result = []
        prev = None
        ipmin = None
        ipmax = None

        for curr in addrs:
            if not prev:
                ipmin = curr.low()
                ipmax = curr.high()
            else:
                if curr.high() + 1 >= ipmin:
                    ipmin = min(curr.low(), ipmin)
                else:
                    result.append(rngcls((ipmin, ipmax)) if ipmin != ipmax else ipcls(ipmin))
                    ipmin = curr.low()
                    ipmax = curr.high()
            prev = curr

        if ipmin and ipmax:
            result.append(rngcls((ipmin, ipmax)) if ipmin != ipmax else ipcls(ipmin))

        return result

    def get_addresses(self, node, get_v4=True, get_v6=True):
        """
        Convenience method for returning list of all addresses (both v4 and v6)
        for given node (``Source`` and ``Target``).

        :param str node: Type of the node (``Source`` or ``Target``).
        :param bool get_v4: Fetch IPv4 addressess.
        :param bool get_v6: Fetch IPv6 addressess.
        :return: Value of message attributes ``idea[node]['IP4']`` and ``idea[node]['IP6']``.
        :rtype: list of ipranges
        """
        result = []
        ip4s = []
        ip6s = []

        if node in self:
            for src in self[node]:
                if get_v4 and "IP4" in src:
                    ip4s.extend(list(src["IP4"]))
                if get_v6 and "IP6" in src:
                    ip6s.extend(list(src["IP6"]))

            result.extend(self.get_ranges(ip4s, ipranges.IP4Range, ipranges.IP4))
            result.extend(self.get_ranges(ip6s, ipranges.IP6Range, ipranges.IP6))

        return result

    def get_ports(self, node):
        """
        Convenience method for returning list of all ports for given node
        (``Source`` and ``Target``).

        :param str node: Type of the node (``Source`` or ``Target``).
        :return: Value of message attributes ``idea[node]['Port']``.
        :rtype: list of int
        """
        result = set()
        if node in self:
            for src in self[node]:
                if "Port" in src:
                    for item in list(src["Port"]):
                        result.add(item)
        return sorted(result)

    def get_protocols(self, node):
        """
        Convenience method for returning list of all protocols for given node
        (``Source`` and ``Target``).

        :param str node: Type of the node (``Source`` or ``Target``).
        :return: Value of message attributes ``idea[node]['Port']``.
        :rtype: list of int
        """
        result = set()
        if node in self:
            for src in self[node]:
                if "Proto" in src:
                    for item in list(src["Proto"]):
                        result.add(str(item).lower())
        return sorted(result)

    def get_types(self, node):
        """
        Convenience method for returning list of all types for given node
        (``Source``, ``Target`` and ``Node``).

        :param str node: Type of the node (``Source``, ``Target`` or ``Node``).
        :return: Value of message attributes ``idea[node]['Port']``.
        :rtype: list of int
        """
        result = set()
        if node in self:
            for src in self[node]:
                if "Type" in src:
                    for item in list(src["Type"]):
                        result.add(item)
        return sorted(result)

    def get_countries_src(self):
        """
        Convenience method for returning list of all resolved source countries.

        :return: Value of message attribute ``idea['_Mentat']['SourceResolvedCountry']``.
        :rtype: list of strings
        """
        return list(self.get_custom_key().get("SourceResolvedCountry", []))

    def get_asns_src(self):
        """
        Convenience method for returning list of all resolved source ASNs.

        :return: Value of message attribute ``idea['_Mentat']['SourceResolvedASN']``.
        :rtype: list of strings
        """
        return list(self.get_custom_key().get("SourceResolvedASN", []))

    def get_inspection_errors(self):
        """
        Convenience method for returning a list of inspection errors.

        :return: List of values of ``idea['_Mentat']['InspectionErrors']``.
        :rtype: list
        """
        return self.get_jpath_values("_Mentat.InspectionErrors")

    def is_shadow(self):
        """
        Convenience method for returning if the event should be shadow reported (in source-based reporting).

        :return: True if ``idea['_Mentat']['ShadowReporting']`` is True, False otherwise.
        :rtype: bool
        """
        return self.get_jpath_value("_Mentat.ShadowReporting") is True

    def is_shadow_target(self):
        """
        Convenience method for returning if the event should be shadow reported (in target-based reporting).

        :return: True if ``idea['_Mentat']['ShadowReportingTarget']`` is True, False otherwise.
        :rtype: bool
        """
        return self.get_jpath_value("_Mentat.ShadowReportingTarget") is True

    def get_jpath_value(self, path):
        """
        Return single (first in case of a list) value on a given path within the
        IDEA message.

        :param str path: A string representing a path of keys, separated by dots.
        :return: Single (or first) value on the given path or None if not found.
        """
        values = get_values(self, path)
        if values:
            return values[0]
        return None

    def get_jpath_values(self, path):
        """
        Return all values on a given path within the IDEA message.

        :param str path: A string representing a path of keys, separated by dots.
        :return: List of all values on the given path.
        :rtype: list
        """
        return get_values(self, path)

    def get_attachment(self, index):
        """
        Returns attachment with the given index (starting from 1) from the IDEA.

        :param int index: index of the attachment, starting from 1.
        :return: attachment with the given index, or None if it was not found.
        """
        try:
            return self.get_jpath_values("Attach")[index - 1]
        except Exception:
            return None

    @staticmethod
    def convert_json(content):
        """
        Used to convert JSON from attachments in IDEA to readable JSON string.
        If it is unable to parse as JSON, exception is thrown and it must be catched later.

        :param str content: string from Attach.Content in IDEA message.
        :return: Newly formatted (more readable) string.
        """
        try:
            json_format = json.loads(content)
            return json.dumps(json_format, indent=4)
        except json.JSONDecodeError:
            json_format = json.loads(content.replace('"', '\\"').replace("'", '"'))
            return json.dumps(json_format, indent=4)

    def get_attachment_content(self, index):
        """
        Returns a tuple consisting of:
        - the attachment content
        - its file name extension
        - its MIME type (ContentType)
        or None if it is unable to decode/parse and the original content cannot be
        shown or downloaded.

        :param int index: index of the attachment, starting from 1.
        :rtype: Optional[Tuple[str, str, str]]
        """
        attachment = self.get_attachment(index)
        if attachment and "Content" in attachment:
            if attachment.get("ContentEncoding", "").lower() == "base64":
                try:
                    decoded = b64decode(attachment["Content"], validate=True)
                except Exception:  # Decoding failed - it is not a valid base64
                    return None

                # Try to decode it to UTF-8, and if it fails because it is a binary
                # and not a text, return it as a binary.
                try:
                    return (decoded.decode("utf-8"), "txt", "text/plain")
                except Exception:
                    return (decoded, "BIN", "application/octet-stream")

            content_type = attachment.get("ContentType", "").lower()
            if content_type == "application/json":
                try:
                    return (
                        self.convert_json(attachment["Content"]),
                        "json",
                        content_type,
                    )
                except json.JSONDecodeError:
                    return (attachment["Content"], "txt", "text/plain")
                except Exception:
                    return None
            if content_type == "text/csv":
                return (attachment["Content"], "csv", content_type)
            if content_type == "text/tab-separated-values":
                return (attachment["Content"], "tsv", content_type)
            return (attachment["Content"], "txt", "text/plain")

        if attachment and "Credentials" in attachment:
            try:
                return (
                    self.convert_json(str(attachment["Credentials"])),
                    "json",
                    "application/json",
                )
            except Exception:
                return None

        return None

    def get_credentials_as_json_string(self):
        """
        Convenience method for returning string representation
        of the Credentials JSON field.

        :return: string representation of Dict of ``idea['Credentials']``.
        :rtype: str
        """
        return json.dumps(self.get("Credentials"), indent=4, sort_keys=True, default=self.json_default)


class IdeaGhost(Idea):
    """
    This class represents simplified IDEA message objects as reconstructed from
    SQL records retrieved from database. These records are represented by the
    :py:class:`mentat.idea.sqldb.Idea` class, however the native database record
    object is used when the message is fetched from database.

    Objects of this class ARE NOT a perfect 1to1 match with original objects based
    on :py:class:`mentat.idea.internal.Idea`. During the conversion to database
    representation some of the information gets lost due to the design of the data
    model optimized for database search. However from the point of view of the
    searching these objects are same, because there is the same set of categories,
    source and target IPs and all other message attributes, so they can be used
    as representatives in use cases where the full message is not necessary. The
    big pro in using these ghost objects is that they are much cheaper to construct
    in comparison with the full IDEA message representation.
    """

    @classmethod
    def from_record(cls, record):
        """
        Construct the IDEA ghost object from the given SQL record.
        """
        idea_raw = {
            "ID": record.id,
            "TLP": record.tlp,
            "DetectTime": record.detecttime,
            "Category": list(record.category),
            "Description": record.description,
        }

        for whatfrom, whereto in (("source", "Source"), ("target", "Target")):
            datastore = {}
            ip_list = getattr(record, f"{whatfrom}_ip", "").replace("{", "").replace("}", "")
            if ip_list:
                ip_list = ip_list.split(",")
            if ip_list:
                for ipaddr in ip_list:
                    if ipaddr.find(":") != -1:
                        datastore.setdefault("IP6", []).append(ipaddr)
                    else:
                        datastore.setdefault("IP4", []).append(ipaddr)
            if getattr(record, f"{whatfrom}_type", []):
                datastore["Type"] = list(getattr(record, f"{whatfrom}_type", []))
            if getattr(record, f"{whatfrom}_port", []):
                datastore["Port"] = list(getattr(record, f"{whatfrom}_port", []))
            if record.protocol:
                datastore["Proto"] = list(record.protocol)
            if datastore:
                idea_raw[whereto] = [datastore]

        if record.node_name:
            for node_name in record.node_name:
                node = {}
                node["Name"] = node_name
                if record.node_type:
                    node["Type"] = list(record.node_type)
                idea_raw.setdefault("Node", []).append(node)

        if record.resolvedabuses:
            idea_raw.setdefault("_Mentat", {})["ResolvedAbuses"] = list(record.resolvedabuses)
        if record.targetabuses:
            idea_raw.setdefault("_Mentat", {})["TargetAbuses"] = list(record.targetabuses)
        if record.storagetime:
            idea_raw.setdefault("_Mentat", {})["StorageTime"] = record.storagetime
        if record.eventclass:
            idea_raw.setdefault("_Mentat", {})["EventClass"] = record.eventclass
        if record.targetclass:
            idea_raw.setdefault("_Mentat", {})["TargetClass"] = record.targetclass
        if record.eventseverity:
            idea_raw.setdefault("_Mentat", {})["EventSeverity"] = record.eventseverity
        if record.targetseverity:
            idea_raw.setdefault("_Mentat", {})["TargetSeverity"] = record.targetseverity
        if record.inspectionerrors:
            idea_raw.setdefault("_Mentat", {})["InspectionErrors"] = list(record.inspectionerrors)
        if record.shadow_reporting is not None:
            idea_raw.setdefault("_Mentat", {})["ShadowReporting"] = True
        if record.shadow_reporting_target is not None:
            idea_raw.setdefault("_Mentat", {})["ShadowReportingTarget"] = True

        try:
            return cls(idea_raw)
        except Exception:
            print("Record:")
            pprint.pprint(record)
            print("IDEA raw:")
            pprint.pprint(idea_raw)
            raise
