#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains base class for various types of email messages and reports,
that are generated and sent by Mentat system.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from typing import Optional

REPORT_ID_HEADER = "X-Mentat-Report-Id"
"""Custom email header: Unique report identifier"""
REPORT_CLASS_HEADER = "X-Mentat-Report-Class"
"""Custom email header: Report class"""
REPORT_TYPE_HEADER = "X-Mentat-Report-Type"
"""Custom email header: Report type"""


class BaseEmail:
    """
    Base class for various types of email messages and reports.
    """

    report_class: Optional[str] = None
    report_type = None

    def __init__(self, headers, **kwargs):
        self.ident = None
        self.email = self._get_container()

        self._set_headers(headers)
        self._set_content(headers, **kwargs)

    def _get_container(self):
        """
        This method must return valid :py:mod:`email.mime` container to hold email
        contents (for example :py:class:`email.mime.text.MIMEText` for simple emails
        or :py:class:`email.mime.multipart.MIMEMultipart` for more complex ones).
        Returned object will be populated with email contents.
        """
        raise NotImplementedError()

    def _set_headers(self, headers):
        """
        Set appropriate email headers within the email container acquired by
        :py:func:`mentat.emails.base.BaseEmail._get_container`. The ``headers``
        parameter may contain following header configurations:

        * subject (``str``)
        * from (``str``)
        * to (``str`` or ``list of str``)
        * cc (``str`` or ``list of str``)
        * bcc (``str`` or ``list of str``)
        * reply_to (``str`` or ``list of str``)
        * report_class (``str``)
        * report_id (``str``)

        :param dict headers: Dictionary containing header configurations.
        """
        if "subject" in headers:
            self.email["Subject"] = str(headers["subject"])

        if "from" in headers:
            self.email["From"] = str(headers["from"])

        for item in (
            ("to", "To"),
            ("cc", "Cc"),
            ("bcc", "Bcc"),
            ("reply_to", "Reply-To"),
        ):
            if item[0] in headers:
                if isinstance(headers[item[0]], list):
                    self.email[item[1]] = ",".join(headers[item[0]])
                else:
                    self.email[item[1]] = str(headers[item[0]])

        if "return_path" in headers:
            self.email["Return-Path"] = str(headers["return_path"])

        if self.report_class:
            self.email[REPORT_CLASS_HEADER] = self.report_class
        if "report_class" in headers:
            self.email[REPORT_CLASS_HEADER] = str(headers["report_class"])

        if self.report_type:
            self.email[REPORT_TYPE_HEADER] = self.report_type
            self.email["X-Cesnet-Report-Type"] = self.report_type
        if "report_type" in headers:
            self.email[REPORT_TYPE_HEADER] = str(headers["report_type"])
            self.email["X-Cesnet-Report-Type"] = str(headers["report_type"])

        if "report_id" in headers:
            self.email[REPORT_ID_HEADER] = str(headers["report_id"])
            self.email["X-Cesnet-Report-Id"] = str(headers["report_id"])
            self.ident = str(headers["report_id"])

    def _set_content(self, headers, **kwargs):
        """
        This method should actualy construct the email object.
        """
        raise NotImplementedError()

    def get_header(self, name, default=None):
        """
        Return given email header.
        """
        return self.email.get(name, default)

    def as_string(self):
        """
        Return email as string ready to be passed to sendmail library.
        """
        return self.email.as_string()

    def get_destinations(self):
        """
        Return list of email destinations ('To', 'Cc').
        """
        destinations = []
        for item in ("To", "Cc"):
            if self.email.get(item):
                destinations.extend(self.email[item].split(","))
        return destinations

    def get_destinations_all(self):
        """
        Return list of all email destinations ('To', 'Cc', 'Bcc').
        """
        destinations = []
        for item in ("To", "Cc", "Bcc"):
            if item in self.email:
                destinations.extend(self.email[item].split(","))
        return destinations
