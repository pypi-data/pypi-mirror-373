#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2018 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#
# -------------------------------------------------------------------------------


"""
Enricher plugins performing DNS lookup of all Source/IPx addresses using
*CESNET* PassiveDNS service.

The implementation consists of PassiveDNS connector and its Enricher plugin.
The connector provides information about domains linked to a user defined IP address.
Each domain record provides at least information when the domain name in combination
with the IP address was seen for the first and the last time from the point of
a DNS sniffer.

.. warning::

    Still a work in progress and alpha code.

"""

__author__ = "Lukáš Huták <lukas.hutak@cesnet.cz>"
__credits__ = (
    "Václav Bartoš <bartos@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, "
    "Jan Mach <jan.mach@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)

import ipaddress
import json
import math
import pprint
import time
from datetime import datetime, timedelta

import requests

from ransack import get_values

import mentat.plugin.enricher
from mentat.idea.internal import jpath_set


class PassiveDNSConnectorError(RuntimeError):
    """
    Custom error of the PassiveDNSConnector
    """


class PassiveDNSConnectorBase:
    """
    The abstract base class for PassiveDNS connectors.

    The class provides common interface and basic record caching.
    """

    def __init__(self, api_timeout=0.5, rec_validity=168):
        """
        Base connector initializer

        :param int api_timeout:  Query timeout (seconds)
        :param int rec_validity: Return only records X hours old
        """
        self._cfg_api_timeout = api_timeout
        self._cfg_rec_validity = rec_validity

    def _create_rec(self, name, time_first, time_last, **kwargs):
        """
        Create an internal record format

        :param str name:       Domain name
        :param int time_first: First seen timestamp (seconds since UNIX epoch)
        :param int time_last:  Last seen timestamp (seconds since UNIX epoch)
        :param kwargs:         Additional extra parameters
        :return: Internal record format
        :rtype: dict
        """
        time2str = lambda ts: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))
        ret = {
            "Name": name,
            "FirstSeenTime": time2str(time_first),
            "LastSeenTime": time2str(time_last),
        }

        if kwargs:
            ret.update(**kwargs)
        return ret

    def _query_fn(self, ip_addr, timeout):
        """
        PassiveDNS query function

        This function is intended to be implemented in subclasses. The function will
        send a request to a PassiveDNS API and return parsed records in the internal
        format or raise an exception.
        :param str ip_addr: IP address to query
        :param int timeout: Query timeout in seconds
        :return: Parsed domains as a list of internal records (can be empty)
        :rtype: list of dict
        """
        raise NotImplementedError("The function is not implemented in the subclass")

    def query(self, ip_addr, timeout=None):
        """
        Get domains of an IP address based on PassiveDNS

        A new query is sent to the remote server and results are
        successfully processed and returned.

        :param str ip_addr: IP address to query
        :param int timeout: Query timeout in seconds (if None, default timeout is used)
        :return: Parsed domains as a list of internal records (can be empty)
        :rtype:  list of dict
        """
        if not timeout:
            timeout = self._cfg_api_timeout

        return self._query_fn(ip_addr, timeout)

    def query_multi(self, ip_addrs, timeout=None):
        """
        Get domains of multiple IP addresses based on PassiveDNS

        Similar to the casual query, however, results of multiple IP addresses are returned
        as dictionary where keys are IP addresses and values are lists of parsed domains.
        IP addresses without known domain records are not present in the result.

        :param list of str ip_addrs: List of IP addresses to query
        :param int timeout:          Single query timeout in seconds (if None, default
          timeout is used)
        :return: IP addresses and their domains (can be empty)
        :rtype:  dict [str, list of dict]
        """
        domain_dict = {}
        for i in ip_addrs:
            domains = self.query(i, timeout)
            if not domains:
                continue
            domain_dict[str(i)] = domains
        return domain_dict

    def status(self):
        """
        Determine and return the status of configuration

        :return: Dictionary containing various subkeys
        :rtype:  dict
        """
        return {
            "api_timeout": self._cfg_api_timeout,
            "rec_validity": self._cfg_rec_validity,
        }


class PassiveDNSConnectorCESNET(PassiveDNSConnectorBase):
    """
    PassiveDNS connector for 'CESNET' PassiveDNS API
    """

    # List of configuration parameters
    API_SERVER = "https://passivedns.cesnet.cz"
    API_URL = "/pdns/ip/{ip_address}?from={start}&to={end}"

    def __init__(self, api_limit=100, **kwargs):
        """
        Connector initializer

        Due to remote API limitation the common parameter 'api_validity' (in hours) is
        rounded up to represent full days.

        :param int api_limit: Maximum number of domains per one IP address
          (if the value is None, no limit is applied)
        :param kwargs: Additional parameters to override base connector parameters
            (see :py:class:`PassiveDNSConnectorBase`)
        """
        super().__init__(**kwargs)
        self._session = requests.Session()
        self._cfg_rec_validity = math.ceil(self._cfg_rec_validity / 24.0) * 24
        self._cfg_api_limit = api_limit

    def _query_url(self, ip_addr):
        """
        Create a query URL for a new HTTP Get request

        :param str ip_addr: IP address
        :return: Formatted URL address
        :rtype: str
        """
        addr = ipaddress.ip_address(ip_addr)

        # Determine time range
        date2str = lambda date: date.strftime("%Y-%m-%d")
        date_start = date2str(datetime.now() - timedelta(hours=self._cfg_rec_validity))
        date_end = date2str(datetime.now() + timedelta(days=1))

        return self.API_SERVER + self.API_URL.format(
            ip_address=str(addr),
            start=date_start,
            end=date_end,
        )

    def _query_parser(self, json_txt):
        """
        Process a JSON response retrieved from the PassiveDNS API

        Check validity of received DNS records and convert them into the internal format.
        :param str json_txt: Response from the PassiveDNS API
        :return: Parsed information about associated domain names (can be empty)
        :rtype:  list of dict
        """
        # Domain main sanitizer removes the last doc if present
        name_sanitizer = lambda name: name[:-1] if name[-1] == "." else name
        # Timestamp parser converts date to number of seconds from Unix Epoch
        ts_parser = lambda ts: time.mktime(datetime.strptime(ts, "%Y-%m-%d").timetuple())

        domains = []
        try:
            data = json.loads(json_txt)
            for rec in data:
                name = name_sanitizer(str(rec["domain"]))
                ts_first = int(ts_parser(str(rec["time_first"])))
                ts_last = int(ts_parser(str(rec["time_last"])))
                rec_type = str(rec["type"]).upper()

                new_domain = self._create_rec(name, ts_first, ts_last, Type=rec_type)
                domains.append(new_domain)
        except json.decoder.JSONDecodeError as err:
            raise PassiveDNSConnectorError("Failed to parse JSON response: " + str(err)) from err
        except (KeyError, TypeError, ValueError) as err:
            raise PassiveDNSConnectorError("Unexpected response structure: " + str(err)) from err

        limit = self._cfg_api_limit
        if limit is not None and limit < len(domains):
            # Sort from the newest to the older and remove exceeding records
            cmp_fn = lambda rec: time.mktime(time.strptime(rec["LastSeenTime"], "%Y-%m-%dT%H:%M:%SZ"))
            domains.sort(key=cmp_fn)
            domains = domains[-self._cfg_api_limit :]

        return domains

    def _query_fn(self, ip_addr, timeout):
        """
        PassiveDNS query function

        The function will send a request to a PassiveDNS API and return parsed
        records in the internal format or raise an exception.
        :param str ip_addr:      IP address to query
        :param int timeout: Query timeout in seconds
        :return: Parsed domains as a list of internal records (can be empty)
        :rtype: list of dict
        """
        url = self._query_url(ip_addr)

        try:
            response = self._session.get(url, timeout=timeout)
            ret_code = response.status_code
        except requests.exceptions.RequestException as err:
            raise PassiveDNSConnectorError("API request failed: " + str(err)) from err

        if ret_code == 200:  # Success
            domains = self._query_parser(response.text)
        elif ret_code == 404:  # IP address not found
            domains = []
        else:
            err_msg = f"Unexpected return code '{ret_code}' from the PassiveDNS server (request '{url}')."
            raise PassiveDNSConnectorError(err_msg)
        return domains


# -------------------------------------------------------------------------------------


def _format_results(source_id, pairs):
    """
    Prepare a formatted result for an IDEA messsage.

    The function wraps each item in a new dictionary with identification of
    the type of IDEA enrichment block (key, type, reference, etc).
    :param str source_id: Identification string of the API provider
    :param dict [str, list of dict] pairs: IP address and their domains
    :return: Formatter result
    :rtype: list of dict
    """
    res = []
    for ip_addr, domains in pairs.items():
        res.append(
            {
                "Key": str(ip_addr),
                "Type": ["PassiveDNS"],
                "Ref": str(source_id),
                "DNS": domains,
            }
        )
    return res


class PassiveDNSCESNETEnricherPlugin(mentat.plugin.enricher.EnricherPlugin):
    """
    Enricher plugin performing PassiveDNS lookup of all Source/IPx addresses using
    *CESNET* PassiveDNS service.
    """

    SOURCE_ID = "https://passivedns.cesnet.cz/"

    def __init__(self):
        """
        Initializer of the plugin
        """
        self.connector = None

    def setup(self, daemon, config_updates=None):
        """
        Process configuration parameters and prepare PassiveDNS connector
        """

        # Initialized connector
        self.connector = PassiveDNSConnectorCESNET(**config_updates)
        daemon.logger.info(
            f"Initialized '{self.__class__.__name__}' enricher plugin: {pprint.pformat(self.connector.status())}"
        )

    def process(self, daemon, message_id, message):
        """
        Process and enrich given message.
        """
        daemon.logger.debug(f"PassiveDNSCESNET - message '{message_id}'")

        sources = []
        sources += get_values(message, "Source.IP4")
        sources += get_values(message, "Source.IP6")

        # Process only global IP addresses
        sources = [x for x in sources if ipaddress.ip_address(x).is_global]

        # Start PasssiveDNS lookup
        try:
            pairs = self.connector.query_multi(sources)
        except PassiveDNSConnectorError as err:
            daemon.logger.warn("PassiveDNSCESNET lookup failed: " + str(err))
            return (daemon.FLAG_CONTINUE, self.FLAG_UNCHANGED)

        # Store results
        changed = False
        enrichments = _format_results(self.SOURCE_ID, pairs)

        if enrichments:
            data = get_values(message, "Enrich")
            data.extend(enrichments)
            jpath_set(message, "Enrich", data)
            daemon.logger.debug(f"Enriched message '{message_id}' with attribute 'Enriched'")
            changed = True

        return (daemon.FLAG_CONTINUE, changed)
