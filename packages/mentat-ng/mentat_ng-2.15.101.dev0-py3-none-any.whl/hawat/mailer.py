#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains mailer setup for *Hawat* application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask

import mentat.plugin.app.mailer
from mentat.emails.simple import SimpleEmail


class _mailer:
    def __init__(self):
        self.mailer = mentat.plugin.app.mailer.MailerPlugin()

    def send(self, email_headers, email_body):
        if flask.current_app.config["DEBUG"] or flask.current_app.config["TESTING"]:
            flask.current_app.logger.info(
                "Email '%s' was not sent because either DEBUG or TESTING flag is set",
                email_headers.get("subject", None),
            )
            return
        if "from" not in email_headers:
            email_headers["from"] = flask.current_app.config["MAIL_DEFAULT_SENDER"]

        self.mailer.mail_sendmail(SimpleEmail(email_headers, text_plain=email_body))

        flask.current_app.logger.info(
            "Sent email '%s' to '%s'",
            email_headers.get("subject", None),
            ", ".join(email_headers.get("to", [])),
        )


MAILER = _mailer()
"""Global application resource: :py:mod:`flask_sendmail` mailer."""
