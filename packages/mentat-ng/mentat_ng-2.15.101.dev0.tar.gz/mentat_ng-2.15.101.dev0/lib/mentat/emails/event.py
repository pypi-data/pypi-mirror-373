#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains implementation of email reports send by the *mentat-reporter.py*
component. It is based on :py:class:`mentat.emails.base.BaseEmail`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mimetypes
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mentat.emails.base import BaseEmail

REPORT_CLASS_EVENT = "events"
"""Module constant for event report types."""

REPORT_ID_PARENT_HEADER = "X-Mentat-Report-Parent-Id"
"""Custom email header: Parent report identifier"""
REPORT_SEVERITY_HEADER = "X-Mentat-Report-Severity"
"""Custom email header: Report severity"""
REPORT_CATEGORIES_HEADER = "X-Mentat-Report-Categories"
"""Custom email header: Report categories"""
REPORT_CLASSES_HEADER = "X-Mentat-Report-Classes"
"""Custom email header: Report event classes"""
REPORT_EVCOUNT_HEADER = "X-Mentat-Report-Event-Count"
"""Custom email header: Report event count"""
REPORT_SRCIP_HEADER = "X-Mentat-Report-Src-IP"
"""Custom email header: Report source IP"""
REPORT_WINDOW_HEADER = "X-Mentat-Report-Time-Window"
"""Custom email header: Report time window"""
REPORT_TESTDATA_HEADER = "X-Mentat-Report-Test-Data"
"""Custom email header: Report type"""


class ReportEmail(BaseEmail):
    """
    Implementation of email reports send by the *mentat-reporter.py* Mentat component.
    """

    report_class = REPORT_CLASS_EVENT

    def _get_container(self):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._get_container` method.
        """
        return MIMEMultipart("mixed")

    def _set_headers(self, headers):
        """
        *Interface reimplementation:* Reimplementation of :py:func:`mentat.emails.base.BaseEmail._set_headers` method.
        """
        super()._set_headers(headers)

        if "report_id_par" in headers:
            self.email[REPORT_ID_PARENT_HEADER] = str(headers["report_id_par"])
        if "report_severity" in headers:
            self.email[REPORT_SEVERITY_HEADER] = str(headers["report_severity"])
            self.email["X-Cesnet-Report-Severity"] = str(headers["report_severity"])
        if "report_categories" in headers:
            self.email[REPORT_CATEGORIES_HEADER] = " ".join(headers["report_categories"])
        if "report_classes" in headers:
            self.email[REPORT_CLASSES_HEADER] = " ".join(headers["report_classes"])
        if "report_srcip" in headers:
            self.email[REPORT_SRCIP_HEADER] = str(headers["report_srcip"])
            self.email["X-Cesnet-Report-Srcip"] = str(headers["report_srcip"])
        if "report_evcount" in headers:
            self.email[REPORT_EVCOUNT_HEADER] = str(headers["report_evcount"])
        if "report_window" in headers:
            self.email[REPORT_WINDOW_HEADER] = str(headers["report_window"])
        if "report_testdata" in headers:
            self.email[REPORT_TESTDATA_HEADER] = str(headers["report_testdata"])
        if "message_id" in headers:
            self.email["Message-Id"] = str(headers["message_id"])
        if "references" in headers:
            self.email["References"] = " ".join(headers["references"])

    def _set_content(self, headers, text_plain, attachments):  # pylint: disable=locally-disabled,arguments-differ
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._set_content` method.
        """
        msg_text = MIMEMultipart("alternative")
        msg_text_part1 = MIMEText(text_plain, "plain")
        # msg_text_part2 = MIMEText(text_html, 'html')

        # Attach parts into message container. According to RFC 2046, the last
        # part of a multipart message, in this case the HTML variant, is best
        # and therefore preferred.
        msg_text.attach(msg_text_part1)
        # msg_text.attach(msg_text_part2)

        # Attach the text content to the message container.
        self.email.attach(msg_text)

        # Attach data, ehm...attachments.
        for attch in attachments:
            self._set_attachment(attch)

    def _set_attachment(self, attachment):
        """
        Add given attachment to internal email object.
        """
        msg_attach = None
        att_type = self.guess_attachment(attachment)
        maintype, subtype = att_type.split("/", 1)

        with open(attachment, "rb") as attfh:
            if maintype in ["application", "text"]:
                msg_attach = MIMEApplication(attfh.read(), subtype)

            msg_attach.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(attachment),
            )
            msg_attach.add_header("Content-Description", "Raw data relevant to report")
            self.email.attach(msg_attach)

    @staticmethod
    def guess_attachment(filepath):
        """
        Guess the mimetype for given attachment file.

        :param str filepath: Path to the attachment file.
        :return: Email mimetype for the given attachment file.
        :rtype: str
        """
        ctype, encoding = mimetypes.guess_type(filepath)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = "application/octet-stream"
        return ctype
