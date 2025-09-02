#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains simple class for simple emails.
"""

__author__ = "Rajmund Hruška <rajmund.hruska@cesnet.cz>"
__credits__ = (
    "Jan Mach <jan.mach@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"
)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from mentat.emails.base import BaseEmail


class SimpleEmail(BaseEmail):
    """
    Base class for various types of email messages.
    """

    def _get_container(self):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._get_container` method.
        """
        return MIMEMultipart("mixed")

    def _set_content(self, headers, text_plain):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.emails.base.BaseEmail._set_content` method.
        """
        msg_text = MIMEMultipart("alternative")
        msg_text_part1 = MIMEText(text_plain, "plain")

        msg_text.attach(msg_text_part1)
        self.email.attach(msg_text)
