#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains logging setup for *Hawat* application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import logging
from logging.handlers import WatchedFileHandler

import mentat.plugin.app.mailer
from mentat.emails.simple import SimpleEmail


def setup_logging_default(app):
    """
    Setup default application logging features.
    """
    log_level_str = app.config["LOG_DEFAULT_LEVEL"].upper()
    log_level = getattr(logging, log_level_str, None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid default log level: {log_level_str}")

    app.logger.setLevel(log_level)
    app.logger.debug(
        "%s: Default logging services successfully started with level %s",
        app.config["APPLICATION_NAME"],
        log_level_str,
    )

    return app


def setup_logging_file(app):
    """
    Setup application logging via watched file (rotated by external command).
    """
    log_level_str = app.config["LOG_FILE_LEVEL"].upper()
    log_level = getattr(logging, log_level_str, None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log file level: {log_level_str}")

    file_handler = WatchedFileHandler(app.config["LOG_FILE"])
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"))

    app.logger.addHandler(file_handler)
    app.logger.debug(
        "%s: File logging services successfully started to file %s with level %s",
        app.config["APPLICATION_NAME"],
        app.config["LOG_FILE"],
        log_level_str,
    )

    return app


class SendmailHandler(logging.Handler):
    """
    A handler class which sends an email using sendmail for each logging event.
    """

    def __init__(self, fromaddr, toaddrs, subject):
        """
        Initialize the handler.

        The handler uses the :py:class:`mentat.plugin.app.mailer.MailerPlugin`.
        Initialize the instance with the from and to addresses and subject
        line of the email.
        """
        logging.Handler.__init__(self)
        self.mailer = mentat.plugin.app.mailer.MailerPlugin()
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject

    def emit(self, record):
        """
        Emit a record.

        Format the record, create :py:class:`mentat.emails.simple.SimpleEmail` email
        and send it to the specified addresses.
        """
        email_headers = {
            "to": self.toaddrs,
            "from": self.fromaddr,
            "subject": self.subject,
        }
        email_params = {"text_plain": self.format(record)}
        email = SimpleEmail(email_headers, **email_params)
        self.mailer.mail_sendmail(email)


def setup_logging_email(app):
    """
    Setup application logging via email.
    """
    if app.config["DISABLE_MAIL_LOGGING"]:
        return app

    log_level_str = app.config["LOG_EMAIL_LEVEL"].upper()
    log_level = getattr(logging, log_level_str, None)
    if not isinstance(log_level, int):
        raise ValueError(f"Invalid log email level: {log_level_str}")

    mail_handler = SendmailHandler(
        fromaddr=app.config["MAIL_DEFAULT_SENDER"],
        toaddrs=app.config["EMAIL_ADMINS"],
        subject=app.config["MAIL_SUBJECT_PREFIX"] + " Application Error",
    )
    mail_handler.setLevel(log_level)
    mail_handler.setFormatter(
        logging.Formatter("""
Message type: %(levelname)s
Location:     %(pathname)s:%(lineno)d
Module:       %(module)s
Function:     %(funcName)s
Time:         %(asctime)s

Message:

%(message)s
""")
    )

    app.logger.addHandler(mail_handler)
    app.logger.debug(
        "%s: Email logging services successfully started with level %s",
        app.config["APPLICATION_NAME"],
        log_level_str,
    )

    return app
