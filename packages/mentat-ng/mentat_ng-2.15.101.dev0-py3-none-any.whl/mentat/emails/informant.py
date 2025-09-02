#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains implementation of email reports send by the *mentat-informant.py*
component. It is based on :py:class:`mentat.emails.base.BaseEmail`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mentat.emails.base import BaseEmail

REPORT_CLASS_INFORMANT = "overview"
"""Module contant for informant report class."""


def json_default(val):
    """
    Helper function for JSON serialization of non basic data types.
    """
    if isinstance(val, datetime.datetime):
        return val.isoformat()
    return str(val)


class ReportEmail(BaseEmail):
    """
    Implementation of email reports send by the *mentat-informant.py* Mentat component.
    """

    report_class = REPORT_CLASS_INFORMANT

    def _get_container(self):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._get_container` method.
        """
        return MIMEMultipart("mixed")

    def _set_content(self, headers, text_plain, text_html, data_events, data_reports):  # pylint: disable=locally-disabled,arguments-differ
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._set_content` method.
        """
        msg_text = MIMEMultipart("alternative")
        msg_text_part1 = MIMEText(text_plain, "plain")
        msg_text_part2 = MIMEText(text_html, "html")

        # Attach parts into message container. According to RFC 2046, the last
        # part of a multipart message, in this case the HTML variant, is best
        # and therefore preferred.
        msg_text.attach(msg_text_part1)
        msg_text.attach(msg_text_part2)

        # Attach the text content to the message container.
        self.email.attach(msg_text)

        # Construct attachment file name.
        filename_events = "report-overview-overall-events.json.txt"
        filename_reports = "report-overview-overall-reports.json.txt"
        if self.ident:
            filename_events = f"report-overview-overall-{self.ident}-events.json.txt"
            filename_reports = f"report-overview-overall-{self.ident}-reports.json.txt"

        # Attach data, ehm...attachments.
        self._set_attachment(filename_events, data_events)
        self._set_attachment(filename_reports, data_reports)

    def _set_attachment(self, attachment_filename, attachment_data):
        """
        Add given attachment to internal email object.
        """
        msg_attach = MIMEText(
            json.dumps(attachment_data, default=json_default, sort_keys=True, indent=4),
            "plain",
            _charset="utf-8",
        )
        msg_attach.add_header("Content-Disposition", "attachment", filename=attachment_filename)
        self.email.attach(msg_attach)
