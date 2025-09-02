#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing functions for abuse group network management
for Mentat system database.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

.. note::

    Still work in progress, use with caution.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-netmngr.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-netmngr.py --debug

    # Run with increased logging level.
    mentat-netmngr.py --log-level debug


Available script commands
-------------------------

``status`` (*default*)
    Detect and display the state of internal whois database contents according
    to the data in given reference whois file.

``update``
    Attempt to update the state of internal whois database contents according
    to the data in given reference whois file.

``convert-exceptions``
    Attempt to convert given list of exception files into valid whois file.


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--whois-file file-path``
    Path to reference whois file containing network data.

    *Type:* ``string``, *default:* ``None``

``--source``
    Origin of the whois file.

    *Type:* ``string``, *default:* ``whois``

Custom config file options
^^^^^^^^^^^^^^^^^^^^^^^^^^

``exception_files``
    List of paths to exception files and their appropriate abuse groups.

    Example configuration::

        "exception_files": [
            {
                "path":  "/path/to/file",
                "abuse": "abuse_group_id"
            }
        ],

    *Type:* ``list of dicts``, *default:* ``None``


Exception file format
---------------------

The exception file is an ordinary text file containing single IPv(4|6)
address|network|range on each line. Blank lines and lines beginning with ``#``
are ignored. Whois exception files are very easy to be generated and they are meant
for specifying whois resolving exceptions. For example you may use it to describe
hosts with addresses from the domain of one particular abuse group, but actually
belonging to different group. This might be the case of routers belonging to service
provider but residing within the network address space of the customer. Another
example may be nodes of some cloud computing service that have addresses from
address space of the cloud computing organization member.


Whois file format
-----------------

Whois file is an ordinary text file containg whois information in specific structured
way. It is recognized by the :py:class:`mentat.services.whois.FileWhoisModule` and
can be used for whois resolving.

The structure of the data comes from the export format of CESNET's *Negistry*
tool, which is an internal custom copy of relevant RIPE whois data. It is JSON based
format. Following example content describes multiple valid syntaxes for describing
network records::

    [
        # Option 1: Pass IP4 start and end addresses
        {
            "primary_key": "78.128.128.0 - 78.128.255.255",
            "ip4_start": "78.128.128.0",
            "ip4_end": "78.128.255.255",
            "netnames": ["CZ-TEN-34-20070410"],
            "resolved_abuses": {
              "low": [
                "abuse@cesnet.cz"
              ]
            }
        },

        # Option 2: Pass network CIDR or range and type
        {
            "primary_key": "78.128.212.64 - 78.128.212.127",
            "network": "78.128.212.64/26",
            "type": "ipv4",
            "netnames": ["CESNET-HSM4"],
            "descr": [
              "CESNET, z.s.p.o.",
              "Ostrava"
            ],
            "resolved_abuses": {
              "low": [
                "abuse@cesnet.cz"
              ]
            }
        },

        # Option 3: Pass IP6 address and prefix
        {
            "primary_key": "2001:718::/29",
            "ip6_addr": "2001:718::",
            "ip6_prefix": 29,
            "netnames": ["CZ-TEN-34-20010521"],
            "descr": ["Extensive network description"],
            "resolved_abuses": {
              "low": [
                "abuse@cesnet.cz"
              ]
            }
        },

        # Option 4: Pass only IPv(4|6) network|range without type for autodetection (slower)
        {
            "primary_key": "2001:718::/29",
            "network": "2001:718::/29",
            "netnames": ["CZ-TEN-34-20010521"],
            "resolved_abuses": {
              "low": [
                "abuse@cesnet.cz"
              ]
            }
        },
        ...
    ]


The ``netname``, ``descr`` and ``description`` attributes are optional and will
be used/stored into database, if present.

The ``resolved_abuses`` attribute is mandatory and must contain list of abuse groups
(abuse contacts) for that particular network record.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import collections
import json
import re

import pyzenkit.jsonconf

import hawat.const
import mentat.const
import mentat.datatype.internal
import mentat.script.fetcher
from mentat.datatype.sqldb import (
    GroupModel,
    ItemChangeLogModel,
    NetworkModel,
    SettingsReportingModel,
    jsondiff,
    networkmodel_from_typeddict,
)

WHOIS_TYPE_GENERIC = "whois"
WHOIS_TYPE_NEGISTRY = "negistry"

PTRN_EXCEPTION_SKIP = re.compile(r"^\s*$|^\s*#")
PTRN_EXCEPTION_MATCH = re.compile(r"^([-.:/a-fA-F0-9]+)")


class MentatNetmngrScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing functions for abuse group
    network management for Mentat database.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_WHOIS_FILE = "whois_file"
    CONFIG_WHOIS_SOURCE = "source"
    CONFIG_EXCEPTION_FILES = "exception_files"

    def __init__(self):
        """
        Initialize netmngr script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.eventservice = None
        self.sqlservice = None

        super().__init__(
            description="mentat-netmngr.py - Abuse group network management script for Mentat database",
        )

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser. This method overrides the
        base implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this script object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for custom script arguments.
        #
        arggroup_script = argparser.add_argument_group("custom script arguments")

        arggroup_script.add_argument(
            "--whois-file",
            type=str,
            default=None,
            help="path to reference whois file containing network data",
        )

        arggroup_script.add_argument(
            "--source",
            type=str,
            default=WHOIS_TYPE_GENERIC,
            help="origin of the whois file",
        )

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default script configurations. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_WHOIS_FILE, None),
            (self.CONFIG_WHOIS_SOURCE, WHOIS_TYPE_GENERIC),
            (self.CONFIG_EXCEPTION_FILES, None),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "status"

    def cbk_command_status(self):
        """
        Implementation of the **status** command (*default*).

        Detect and display the status of abuse group collection with respect to
        network configurations.
        """
        return self._process_groups_and_networks(True)

    def cbk_command_update(self):
        """
        Implementation of the **update** command.

        Attempt to update the state of internal whois database contents according
        to the data in given reference whois file.
        """
        return self._process_groups_and_networks(False)

    def cbk_command_convert_exceptions(self):
        """
        Implementation of the **convert-exceptions** command.

        Attempt to convert given list of exception files into a valid whois file.
        """
        target_file = self.c(self.CONFIG_WHOIS_FILE)
        exception_files = self.c(self.CONFIG_EXCEPTION_FILES)

        if not target_file:
            raise pyzenkit.zenscript.ZenScriptException("Missing configuration for target whois file '--whois-file'")
        self.logger.info("Using file '%s' as target whois file", target_file)

        exceptions = []
        for excf in exception_files:
            exceptions += self._load_exceptions_file(excf["path"], excf["abuse"])
        self._save_network_exceptions(target_file, exceptions)

    # ---------------------------------------------------------------------------

    def _process_groups_and_networks(self, status_only):
        """
        The actual worker method for processing group and network records.

        :param bool status_only: Do not actually perform any database operations, just report status.
        :return: Structure containing information about changes.
        :rtype: dict
        """
        result = {"create": {}, "delete": {}, "update": {}}
        abuse_group_dict = {}

        wi_file = self.c(self.CONFIG_WHOIS_FILE)
        wi_file_type, wi_file_data_raw = self._load_whois_file(wi_file)
        wi_file_data = self._process_whois_data(wi_file_data_raw, wi_file_type)
        self.logger.info(
            "Number of abuse groups in reference whois file: %d",
            len(wi_file_data.keys()),
        )

        abuse_groups = (
            self.sqlservice.session.query(GroupModel).filter(GroupModel.enabled).order_by(GroupModel.name).all()
        )
        self.sqlservice.session.commit()

        for abg in abuse_groups:
            # The name of an abuse group is variable and may change anytime. In order to match abuse groups
            # from the whois file with those from the database, the name of each group from database is computed
            # in the same way as the name of a group from the whois file.
            emails = list(
                set(
                    (abg.settings_rep.emails_info or [])
                    + (abg.settings_rep.emails_low or [])
                    + (abg.settings_rep.emails_medium or [])
                    + (abg.settings_rep.emails_high or [])
                    + (abg.settings_rep.emails_critical or [])
                )
            )
            name = "_".join(sorted([e.lower().replace("+", "_") for e in emails]))
            abuse_group_dict[name] = abg
        self.logger.info("Number of abuse groups in database: %d", len(abuse_groups))

        self._check_emails(abuse_group_dict, wi_file_data)
        self._groups_create_missing(abuse_group_dict, wi_file_data, wi_file_type, result, status_only)
        self._groups_remove_extra(abuse_group_dict, wi_file_data, wi_file_type, result, status_only)
        self._groups_update_existing(abuse_group_dict, wi_file_data, wi_file_type, result, status_only)

        return result

    def _load_whois_file(self, whois_file):
        """
        Load reference whois file.

        :param str whois_file: Name of the reference whois file.
        :return: Data content of whois file.
        :rtype: dict
        """
        try:
            with open(whois_file, "r", encoding="utf8") as jsf:
                json_data = jsf.read()
            whois_file_data = json.loads(json_data)
        except Exception as exc:
            raise pyzenkit.zenscript.ZenScriptException(
                f"Invalid whois file '{whois_file}', expected JSON formatted file"
            ) from exc

        whois_file_type = self.c(self.CONFIG_WHOIS_SOURCE)
        self.logger.info("Loaded reference whois file '%s :: %s'", whois_file, whois_file_type)
        return (whois_file_type, whois_file_data)

    @staticmethod
    def _process_whois_data(whois_file_data, whois_file_type):
        """
        Process reference whois file data into format more appropriate for searching
        and comparisons.

        :param dict whois_file_data: Whois data as loaded by :py:func:`_load_whois_file`.
        :param str whois_file_type: Type of the whois file (value of ``__whois_type__`` meta attribute).
        :return: Processed whois file data into format more appropriate for searching.
        :rtype: dict
        """
        processed_data = collections.defaultdict(dict)
        for network_data in whois_file_data:
            nwr = mentat.datatype.internal.t_network_record(network_data, source=whois_file_type)
            nwrkey = nwr["network"]
            # abuse_group is created as a concatenation of sorted emails in lowercase across
            # all severities with '_' as the delimiter.
            if "abuse_group" not in nwr:
                continue
            abuse_group = nwr["abuse_group"]
            # It is possible to have multiple networks with the same nwrkey, because the
            # networks may come from different feeds.
            if nwrkey not in processed_data[abuse_group]:
                processed_data[abuse_group][nwrkey] = []
            processed_data[abuse_group][nwrkey].append(nwr)
        return processed_data

    # ---------------------------------------------------------------------------

    def _check_emails(self, abuse_group_dict, wi_file_data):
        """
        Check that each abuse group has the same emails in every severity across all networks.

        The name of an abuse group is created as a concatenation of all emails across all severities.
        The code is expecting that the distribution of emails of an abuse group is the same in every network.
        This function checks the consistency and logs an error in case of the inconsistency.

        :param dict abuse_group_dict: Abuse groups and network records loaded from database.
        :param dict wi_file_data: Abuse groups and network records loaded from reference whois file.
        """
        for abuse_group in wi_file_data:
            emails = {}
            for severity in mentat.const.REPORT_SEVERITIES:
                emails[severity] = []
            for nwrkey in wi_file_data[abuse_group]:
                for network in wi_file_data[abuse_group][nwrkey]:
                    if "emails_fallback" in network:
                        continue
                    for severity in mentat.const.REPORT_SEVERITIES:
                        emails[severity].append(
                            sorted(
                                map(
                                    str.lower,
                                    list(set(network.get(f"emails_{severity}", []))),
                                )
                            )
                        )

            if abuse_group in abuse_group_dict:
                s = abuse_group_dict[abuse_group].settings_rep
                emails["info"].append(sorted(map(str.lower, s.emails_info) or []))
                emails["low"].append(sorted(map(str.lower, s.emails_low) or []))
                emails["medium"].append(sorted(map(str.lower, s.emails_medium) or []))
                emails["high"].append(sorted(map(str.lower, s.emails_high) or []))
                emails["critical"].append(sorted(map(str.lower, s.emails_critical) or []))

            for severity in mentat.const.REPORT_SEVERITIES:
                if not all(x == emails[severity][0] for x in emails[severity]):
                    self.logger.error(
                        "Abuse group %s has inconsistent emails across networks",
                        abuse_group,
                    )

    def _create_item_changelog(self, item, module, operation, before, after):
        """
        Create a changelog entry for a specific item operation (e.g., create, update, delete).

        :param item: SQLAlchemy model instance being modified.
        :param str module: Name of the module where the change occurred.
        :param str operation: Operation type (e.g., create, update).
        :param dict before: Snapshot of the item's state before the operation.
        :param dict after: Snapshot of the item's state after the operation.
        """
        if operation == hawat.const.ACTION_ITEM_CREATE:
            self.sqlservice.session.add(item)
            self.sqlservice.session.flush()
            self.sqlservice.session.refresh(item)  # Refresh to get ID from DB.
            after = item.to_json()

        chlog = ItemChangeLogModel(
            author=None,  # system change
            model=item.__class__.__name__,
            model_id=item.id,
            endpoint=f"{module}.{operation}",
            module=module,
            operation=operation,
            before=before,
            after=after,
        )
        chlog.calculate_diff()
        self.sqlservice.session.add(chlog)

    def _create_network_changelog(self, network, operation, before="", after=""):
        """
        Create a changelog entry for a network item.

        :param mentat.datatype.sqldb.NetworkModel network: Network model instance.
        :param str operation: Operation type (e.g., create, update).
        :param str before: Optional string or JSON snapshot before the operation.
        :param str after: Optional string or JSON snapshot after the operation.
        """
        self._create_item_changelog(network, "networks", operation, before, after)

    def _create_group_changelog(self, group, operation, before="", after=""):
        """
        Create a changelog entry for a group item.

        :param mentat.datatype.sqldb.GroupModel group: Group model instance.
        :param str operation: Operation type (e.g., create, update).
        :param str before: Optional string or JSON snapshot before the operation.
        :param str after: Optional string or JSON snapshot after the operation.
        """
        self._create_item_changelog(group, "groups", operation, before, after)

    def _groups_create_missing(self, abuse_group_dict, wi_file_data, wi_file_type, result, status_only):
        """
        Create missing abuse groups and their appropriate whois records within
        the database.

        :param dict abuse_group_dict: Abuse groups and network records loaded from database.
        :param dict wi_file_data: Abuse groups and network records loaded from reference whois file.
        :param str wi_file_type: Value of ``__whois_type__`` meta attribute from reference whois file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        # abuse_group_names is a list of actual names of abuse groups stored in the database,
        # abuse_group_dict.keys() is a list of group names created from emails
        abuse_group_names = [group.name for group in abuse_group_dict.values()]
        for group_name in sorted(wi_file_data.keys()):
            # Try finding the group from the file primarily by emails and secondarily by name of the group.
            if group_name not in abuse_group_dict and group_name not in abuse_group_names:
                gkey = f"{group_name}::{wi_file_type}"
                result["create"][gkey] = []

                if status_only:
                    self.logger.warning("'%s' Found new abuse group.", gkey)
                    for network in [network for networks in wi_file_data[group_name].values() for network in networks]:
                        nkey = "{}::{}".format(network["network"], network["source"])
                        result["create"][gkey].append(nkey)
                        self.logger.warning("'%s' Found new network '%s'.", gkey, nkey)
                    continue

                sqlgrp = GroupModel()
                sqlgrp.name = group_name
                sqlgrp.source = wi_file_type
                sqlgrp.description = "Group created automatically by mentat-netmngr.py utility."
                sqlgrp.settings_rep = SettingsReportingModel()
                self.logger.warning("'%s' Creating new abuse group.", gkey)

                group_emails_set = False
                for network in [network for networks in wi_file_data[group_name].values() for network in networks]:
                    if not group_emails_set and "emails_fallback" not in network:
                        sqlgrp.settings_rep.emails_info = network.get("emails_info", [])
                        sqlgrp.settings_rep.emails_low = network.get("emails_low", [])
                        sqlgrp.settings_rep.emails_medium = network.get("emails_medium", [])
                        sqlgrp.settings_rep.emails_high = network.get("emails_high", [])
                        sqlgrp.settings_rep.emails_critical = network.get("emails_critical", [])
                        group_emails_set = True

                    sqlnet = networkmodel_from_typeddict(
                        network,
                        {"description": "Network created automatically by mentat-netmngr.py utility."},
                    )
                    sqlgrp.networks.append(sqlnet)
                    nkey = f"{sqlnet.network}::{sqlnet.source}"
                    result["create"][gkey].append(nkey)
                    self.logger.warning("'%s' Creating new network '%s'.", gkey, nkey)

                    self._create_network_changelog(sqlnet, operation=hawat.const.ACTION_ITEM_CREATE)

                self._create_group_changelog(sqlgrp, operation=hawat.const.ACTION_ITEM_CREATE)
                self.sqlservice.session.commit()

    def _groups_remove_extra(self, abuse_group_dict, wi_file_data, wi_file_type, result, status_only):
        """
        Remove extra abuse groups and their appropriate whois records from database.

        **Do not delete anything, just report and let the admin get the potential blame.**

        :param dict abuse_group_dict: Abuse groups and network records loaded from database.
        :param dict wi_file_data: Abuse groups and network records loaded from reference whois file.
        :param str wi_file_type: Value of ``__whois_type__`` meta attribute from reference whois file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        for group_name in sorted(abuse_group_dict.keys()):
            abg = abuse_group_dict[group_name]

            # For deletion consider only groups with the same origin (source) as
            # the loaded whois file.
            if abg.source == wi_file_type and group_name not in wi_file_data and abg.name not in wi_file_data:
                gkey = f"{abg.name}::{abg.source}"
                result["delete"][gkey] = []
                self.logger.warning(
                    "'%s' Group was not found in loaded whois file, consider deletion.",
                    gkey,
                )

                for net in abg.networks:
                    nkey = f"{net.network}::{net.source}"
                    result["delete"][gkey].append(nkey)
                    self.logger.warning(
                        "'%s' Network '%s' was not found in loaded whois file, consider deletion.",
                        gkey,
                        nkey,
                    )

    def _groups_update_existing(self, abuse_group_dict, wi_file_data, wi_file_type, result, status_only):
        """
        Update existing abuse groups and their appropriate whois records within
        the database.

        :param dict abuse_group_dict: Abuse groups and network records loaded from database.
        :param dict wi_file_data: Abuse groups and network records loaded from reference whois file.
        :param str wi_file_type: Value of ``__whois_type__`` meta attribute from reference whois file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        for group_name in sorted(abuse_group_dict.keys()):
            name = None
            if group_name in wi_file_data:
                name = group_name
            if abuse_group_dict[group_name].name in wi_file_data:
                name = abuse_group_dict[group_name].name
            if name:
                sql_group = abuse_group_dict[group_name]
                before = sql_group.to_json()
                self._group_update_networks(
                    sql_group,
                    [network for networks in wi_file_data[name].values() for network in networks],
                    wi_file_type,
                    result,
                    status_only,
                )
                after = sql_group.to_json()
                if jsondiff(before, after):
                    self._create_group_changelog(
                        sql_group, operation=hawat.const.ACTION_ITEM_UPDATE, before=before, after=after
                    )
                self.sqlservice.session.commit()

    def _group_update_networks(self, group, networks, wi_file_type, result, status_only):
        """
        Update abuse group network list coming from given source.

        :param mentat.datatype.sqldb.GroupModel group: Abuse group to be processed.
        :param list networks: List of network records loaded from reference whois file.
        :param str wi_file_type: Value of ``__whois_type__`` meta attribute from reference whois file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        gkey = f"{group.name}::{group.source}"
        for net in networks:
            nkey = "{}::{}".format(net["network"], net["source"])
            index = self._get_index_of_network(net, group.networks)
            if index == -1:
                result["create"].setdefault(gkey, []).append(nkey)
                if status_only:
                    self.logger.warning("'%s' Found new network '%s'.", gkey, nkey)
                    continue

                sqlnet = networkmodel_from_typeddict(
                    net,
                    {"description": "Network created automatically by mentat-netmngr.py utility."},
                )
                self.logger.warning("'%s' Creating new network '%s'.", gkey, nkey)
                group.networks.append(sqlnet)
                self._create_network_changelog(sqlnet, operation=hawat.const.ACTION_ITEM_CREATE)

            elif self._network_has_changed(net, group.networks[index]):
                result["update"].setdefault(gkey, []).append(nkey)
                if status_only:
                    self.logger.warning("'%s' Network '%s' has changed.", gkey, nkey)
                    if group.networks[index].rank != net.get("rank", None):
                        self.logger.debug(
                            "Rank: '%s' -> '%s'",
                            group.networks[index].rank,
                            net.get("rank", None),
                        )
                    if group.networks[index].source != net["source"]:
                        self.logger.debug(
                            "Source: '%s' -> '%s'",
                            group.networks[index].source,
                            net["source"],
                        )
                    if group.networks[index].netname != net["netname"]:
                        self.logger.debug(
                            "Netname: '%s' -> '%s'",
                            group.networks[index].netname,
                            net["netname"],
                        )
                    if group.networks[index].is_base != net["is_base"]:
                        self.logger.debug(
                            "is_base: '%s' -> '%s'",
                            str(group.networks[index].is_base),
                            str(net["is_base"]),
                        )
                    continue

                self.logger.warning("'%s' Updating existing network '%s'.", gkey, nkey)
                before = group.networks[index].to_json()
                group.networks[index].rank = net.get("rank", None)
                group.networks[index].source = net["source"]
                group.networks[index].netname = net["netname"]
                group.networks[index].is_base = net["is_base"]
                after = group.networks[index].to_json()

                self._create_network_changelog(
                    group.networks[index], operation=hawat.const.ACTION_ITEM_UPDATE, before=before, after=after
                )

            # Set local id if no local id is set.
            elif not group.networks[index].local_id and "local_id" in net:
                result["update"].setdefault(gkey, []).append(nkey)
                if status_only:
                    self.logger.warning("'%s' The local id of network '%s' has changed.", gkey, nkey)
                    self.logger.debug("New client id: '%s'", net.get("client_id", None))
                    continue
                self.logger.warning(
                    "'%s' Updating existing network '%s', setting new local id.",
                    gkey,
                    nkey,
                )
                group.networks[index].local_id = net.get("local_id", None)

        for net in group.networks:
            if not self._is_network_in(net, networks) and wi_file_type in net.source:
                nkey = f"{net.network}::{net.source}"
                result["delete"].setdefault(gkey, []).append(nkey)
                if status_only:
                    self.logger.warning(
                        "'%s' Network '%s' was not found in loaded whois file, consider deletion.",
                        gkey,
                        nkey,
                    )
                    continue

                group.networks.remove(net)
                self.logger.warning(
                    "'%s' Network '%s' was not found in loaded whois file and was removed.",
                    gkey,
                    nkey,
                )
                self._create_network_changelog(net, operation=hawat.const.ACTION_ITEM_DELETE, before=net.to_json())

    # ---------------------------------------------------------------------------

    @staticmethod
    def _get_index_of_network(network, netlist):
        """
        Get the index of a network in a given network list or return -1 if the list doesn't contain the network.

        :param network: Instance of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :param netlist: List of instances of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :return: index of network
        :rtype: int
        """
        network = network if isinstance(network, NetworkModel) else networkmodel_from_typeddict(network)
        for index, net in enumerate(netlist):
            net = net if isinstance(net, NetworkModel) else networkmodel_from_typeddict(net)
            # Convert to ipranges object so ranges and CIDRs can be compared.
            # e.g. 195.113.220.80-195.113.220.95 should be equal to 195.113.220.80/28
            iprange_net = mentat.datatype.internal.t_net(net.network)
            iprange_network = mentat.datatype.internal.t_net(network.network)
            if iprange_net == iprange_network and (net.netname == network.netname or net.source == network.source):
                return index
        return -1

    @staticmethod
    def _is_network_in(network, netlist):
        """
        Check if given network is in given network list.

        :param network: Instance of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :param netlist: List of instances of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :return: True or False
        :rtype: bool
        """
        return MentatNetmngrScript._get_index_of_network(network, netlist) != -1

    @staticmethod
    def _network_has_changed(original_network, new_network):
        """
        Check if the given network has changed.
        Currently, two networks with the same key differ if their ranks or is_base flags differ.

        :param orignal_network: Instance of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :param new_network: Instance of :py:class:`mentat.datatype.sqldb.NetworkModel` or :py:class:`mentat.datatype.internal.NetworkRecord`
        :return: True or False
        :rtype: bool
        """
        if isinstance(original_network, NetworkModel):
            if isinstance(new_network, NetworkModel):
                return original_network.rank != new_network.rank or original_network.is_base != new_network.is_base
            return original_network.rank != new_network.get(
                "rank", None
            ) or original_network.is_base != new_network.get("is_base")
        if isinstance(new_network, NetworkModel):
            return (
                original_network.get("rank", None) != new_network.rank
                or original_network.get("is_base") != new_network.is_base
            )
        return original_network.get("rank", None) != new_network.get("rank", None) or original_network.get(
            "is_base"
        ) != new_network.get("is_base")

    def _load_exceptions_file(self, path, abuse):
        """
        Load given whois exceptions file.

        :param str path: Path to exceptions file.
        :param str abuse: Abuse group.
        :return: Complex structure containing abuse grou names as keys and list of network records as values.
        :rtype: dict
        """
        exceptions = []
        with open(path, "r", encoding="utf8") as excfh:
            self.logger.info("Loading whois exceptions file '%s'", path)
            for line in excfh:
                line = line.strip()
                if PTRN_EXCEPTION_SKIP.match(line):
                    continue

                match = PTRN_EXCEPTION_MATCH.match(line)
                if match:
                    exc = {"network": match.group(1), "abuse_group": abuse}
                    exc = mentat.datatype.internal.t_network_record(exc, source="exception")
                    self.logger.info(
                        "Found whois exception '%s' for abuse group '%s'",
                        exc["network"],
                        abuse,
                    )
                    exceptions.append(exc)
        return exceptions

    def _save_network_exceptions(self, whois_file, exceptions):
        """
        Save given whois exceptions into valid whois file.

        :param str whois_file: path to target whois file.
        :param dict exceptions: Structure containing whois exceptions.
        """
        exception_dict = []
        for exc in exceptions:
            exception_dict.append(
                {
                    "primary_key": exc["network"],
                    "type": exc["type"],
                    "resolved_abuses": {"low": list(exc["resolved_abuses"])},
                }
            )
        with open(whois_file, "w", encoding="utf8") as excfh:
            json.dump(exception_dict, excfh, indent=4, sort_keys=True)
        self.logger.info(
            "Saved '%d' whois exceptions into target file '%s'",
            len(exceptions),
            whois_file,
        )
