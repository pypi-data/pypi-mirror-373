#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing functions for detectors management
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
    mentat-detmngr.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-detmngr.py --debug

    # Run with increased logging level.
    mentat-detmngr.py --log-level debug


Available script commands
-------------------------

``status`` (*default*)
    Detect and display the state of internal whois database contents according
    to the data in given reference whois file.

``update``
    Attempt to update the state of internal whois database contents according
    to the data in given reference whois file.


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--detectors-file file-path``
    Path to reference detectors file containing data.

    *Type:* ``string``, *default:* ``None``

``--source``
    Origin of the whois file.

    *Type:* ``string``, *default:* ``detectors-file``
"""

__author__ = "Rajmund Hruška <rajmund.hruska@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)


import collections
import json

import pyzenkit.jsonconf

import mentat.const
import mentat.datatype.internal
import mentat.script.fetcher
from mentat.datatype.sqldb import DetectorModel, detectormodel_from_typeddict

DETECTORS_FILE_GENERIC = "detectors-file"
DETECTORS_FILE_WARDEN = "warden"


class MentatDetmngrScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing functions for detectors
    management for Mentat database.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_DETECTORS_FILE = "detectors_file"
    CONFIG_DETECTORS_SOURCE = "source"

    def __init__(self):
        """
        Initialize detmngr script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.eventservice = None
        self.sqlservice = None

        super().__init__(
            description="mentat-detmngr.py - Detector management script for Mentat database",
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
            "--detectors-file",
            type=str,
            default=None,
            help="path to reference detectors file containing data",
        )

        arggroup_script.add_argument(
            "--source",
            type=str,
            default=DETECTORS_FILE_GENERIC,
            help="origin of the detectors file",
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
            (self.CONFIG_DETECTORS_FILE, None),
            (self.CONFIG_DETECTORS_SOURCE, DETECTORS_FILE_GENERIC),
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

        Detect and display the status of detectors collection.
        """
        return self._process_detectors(True)

    def cbk_command_update(self):
        """
        Implementation of the **update** command.

        Attempt to update the state of internal detectors database contents according
        to the data in given reference detectors file.
        """
        return self._process_detectors(False)

    # ---------------------------------------------------------------------------

    def _process_detectors(self, status_only):
        """
        The actual worker method for processing detectors records.

        :param bool status_only: Do not actually perform any database operations, just report status.
        :return: Structure containing information about changes.
        :rtype: dict
        """
        result = {"create": [], "delete": [], "update": []}
        det_db = {}

        det_file = self.c(self.CONFIG_DETECTORS_FILE)
        det_file_type, det_file_data_raw = self._load_detectors_file(det_file)
        self.logger.debug("Raw data: %s", str(det_file_data_raw))
        det_file_data = self._process_detectors_data(det_file_data_raw, det_file_type)
        self.logger.info(
            "Number of detectors in reference detectors file: %d",
            len(det_file_data.keys()),
        )

        detectors = self.sqlservice.session.query(DetectorModel).order_by(DetectorModel.name).all()
        self.sqlservice.session.commit()
        self.logger.info("Number of detectors in the database: %d", len(detectors))
        for detector in detectors:
            det_db[detector.name] = detector

        self._detectors_create_missing(det_db, det_file_data, det_file_type, result, status_only)
        self._detectors_report_extra(det_db, det_file_data, det_file_type, result, status_only)
        self._detectors_update_existing(det_db, det_file_data, det_file_type, result, status_only)
        return result

    def _load_detectors_file(self, detectors_file):
        """
        Load reference detectors file.

        :param str detectors_file: Name of the reference detectors file.
        :return: Data content of detectors file.
        :rtype: dict
        """
        try:
            with open(detectors_file, "r", encoding="utf8") as jsf:
                json_data = jsf.read()
            detectors_file_data = json.loads(json_data)
        except Exception as exc:
            raise pyzenkit.zenscript.ZenScriptException(
                f"Invalid detectors file '{detectors_file}', expected JSON formatted file"
            ) from exc

        detectors_file_type = self.c(self.CONFIG_DETECTORS_SOURCE)
        self.logger.info(
            "Loaded reference detectors file '%s :: %s'",
            detectors_file,
            detectors_file_type,
        )
        return (detectors_file_type, detectors_file_data)

    def _process_detectors_data(self, detectors_file_data, detectors_file_type):
        """
        Process reference detectors file data into format more appropriate for searching
        and comparisons.

        :param dict whois_file_data: Whois data as loaded by :py:func:`_load_whois_file`.
        :param str whois_file_type: Type of the whois file (value of ``__whois_type__`` meta attribute).
        :return: Processed whois file data into format more appropriate for searching.
        :rtype: dict
        """
        if "clients" not in detectors_file_data:
            raise pyzenkit.zenscript.ZenScriptException("Invalid detectors file format, expected 'clients' key.")
        processed_data = collections.defaultdict(dict)
        for client in detectors_file_data["clients"]:
            det = mentat.datatype.internal.t_detector_record(client, source=detectors_file_type)
            self.logger.debug(det)
            processed_data[det["name"]] = det
        return processed_data

    def _detectors_create_missing(self, det_db, det_file_data, det_file_type, result, status_only):
        """
        Create missing detector records in the database.

        :param dict det_db: Detectors loaded from the database.
        :param dict det_file_data: Detectors loaded from the reference detectors file.
        :param str det_file_type: Source of the detectors in the reference detectors file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        for detector_name in sorted(det_file_data.keys()):
            # Try finding the detector from the file in the database by the name.
            if detector_name not in det_db:
                gkey = f"{detector_name}::{det_file_type}"
                result["create"].append(gkey)

                if status_only:
                    self.logger.warning("'%s' Found new detector.", gkey)
                    continue

                sqldet = detectormodel_from_typeddict(
                    det_file_data[detector_name],
                    {"description": "Detector created automatically by mentat-detmngr.py utility."},
                )
                self.logger.warning("'%s' Creating new detector.", gkey)
                self.sqlservice.session.add(sqldet)
                self.sqlservice.session.commit()

    def _detectors_report_extra(self, det_db, det_file_data, det_file_type, result, status_only):
        """
        Report extra detectors from database.

        :param dict det_db: Detectors loaded from the database.
        :param dict det_file_data: Detectors loaded from the reference detectors file.
        :param str det_file_type: Source of the detectors in the reference detectors file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        for detector_name in sorted(det_db.keys()):
            det = det_db[detector_name]

            # For deletion consider only detectors with the same origin (source) as
            # the loaded detectors file.
            if det.source == det_file_type and detector_name not in det_file_data:
                detkey = f"{det.name}::{det.source}"
                result["delete"].append(detkey)
                self.logger.warning(
                    "'%s' Detector was not found in the loaded detectors file, consider deletion.",
                    detkey,
                )

    def _detectors_update_existing(self, det_db, det_file_data, det_file_type, result, status_only):
        """
        Update existing detectors within the database.

        :param dict det_db: Detectors loaded from the database.
        :param dict det_file_data: Detectors loaded from the reference detectors file.
        :param str det_file_type: Source of the detectors in the reference detectors file.
        :param dict result: Structure containing processing log, will be appended to script runlog.
        :param bool status_only: Do not actually perform any database operations, just report status.
        """
        for detector_name in sorted(det_db.keys()):
            if det_db[detector_name].source != det_file_type or detector_name not in det_file_data:
                continue
            detector_db = det_db[detector_name]
            detector_file = det_file_data[detector_name]
            if self._detectors_differ(detector_db, detector_file):
                detkey = f"{detector_db.name}::{detector_db.source}"
                result["update"].append(detkey)
                if status_only:
                    self.logger.warning("Detector '%s' has changed.", detkey)
                    continue
                self.logger.warning("Updating existing detector '%s'.", detkey)
                detector_db.credibility = detector_file["credibility"]
                detector_db.registered = detector_file["registered"]

        self.sqlservice.session.commit()

    @staticmethod
    def _detectors_differ(det_db, det_file):
        """
        Check if the given detectors differ.
        It is assumed that detectors have the same name and source.

        :param det_db: Instance of :py:class:`mentat.datatype.sqldb.DetectorModel`
        :param det_file: Instance of :py:class:`mentat.datatype.internal.Detector`
        :return: True or False
        :rtype: bool
        """
        return det_db.credibility != det_file["credibility"] or det_db.registered != det_file["registered"]
