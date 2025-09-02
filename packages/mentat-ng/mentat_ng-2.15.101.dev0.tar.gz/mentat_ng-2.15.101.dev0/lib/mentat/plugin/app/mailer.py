#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat application plugin provides functions for sending emails. It
is usable both in script and daemon modules.


Example usage
^^^^^^^^^^^^^

Using the plugin like in following way::

    mentat.plugin.app.eventstorage.MailerPlugin()

That will yield following results:

* The application object will have a ``mailerservice`` attribute containing reference to
  mailer service represented by :py:class:`mentat.plugin.app.MailerPlugin`.

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import smtplib
import weakref
from subprocess import PIPE, Popen

import pyzenkit.baseapp


class MailerPlugin(pyzenkit.baseapp.ZenAppPlugin):
    """
    Implementation of Mentat application plugin providing functions for sending
    emails.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_MAIL_SUBJECT = "mail_subject"
    CONFIG_MAIL_FROM = "mail_from"
    CONFIG_MAIL_TO = "mail_to"
    CONFIG_MAIL_CC = "mail_cc"
    CONFIG_MAIL_BCC = "mail_bcc"
    CONFIG_MAIL_REPLY_TO = "mail_reply_to"
    CONFIG_MAIL_RETURN_PATH = "mail_return_path"
    CONFIG_MAIL_ADMIN = "mail_admin"
    CONFIG_MAIL_TEST_MODE = "mail_test_mode"
    CONFIG_MAIL_DEV_MODE = "mail_dev_mode"
    CONFIG_MAIL_DEV_SERVER = "mail_dev_server"
    CONFIG_MAIL_DEV_PORT = "mail_dev_port"

    def __init__(self, settings=None):
        """
        Initialize internal plugin configuration.
        """
        self.get_application = None

        if settings is None:
            settings = {}
        self.settings = settings

    # ---------------------------------------------------------------------------

    def init_argparser(self, app, argparser, **kwargs):
        """
        Callback to be called during argparser initialization phase.
        """
        #
        # Create and populate options group for custom script arguments.
        #
        arggroup_plugin = argparser.add_argument_group("mailer plugin arguments")

        arggroup_plugin.add_argument("--mail-subject", type=str, default=None, help="email subject")
        arggroup_plugin.add_argument("--mail-from", type=str, default=None, help="source email address")
        arggroup_plugin.add_argument(
            "--mail-to",
            type=str,
            default=None,
            help="target email address (repeatable)",
            action="append",
        )
        arggroup_plugin.add_argument(
            "--mail-cc",
            type=str,
            default=None,
            help="target copy email address (repeatable)",
            action="append",
        )
        arggroup_plugin.add_argument(
            "--mail-bcc",
            type=str,
            default=None,
            help="target blind copy email address (repeatable)",
            action="append",
        )
        arggroup_plugin.add_argument(
            "--mail-reply-to",
            type=str,
            default=None,
            help="reply to email address (repeatable)",
            action="append",
        )
        arggroup_plugin.add_argument(
            "--mail-return-path",
            type=str,
            default=None,
            help="return address for undeliverable emails",
        )
        arggroup_plugin.add_argument(
            "--mail-admin",
            type=str,
            default=None,
            help="admin email address (repeatable)",
            action="append",
        )
        arggroup_plugin.add_argument(
            "--mail-dev-server",
            type=str,
            default=None,
            help="development SMTP server hostname",
        )
        arggroup_plugin.add_argument(
            "--mail-dev-port",
            type=int,
            default=None,
            help="development SMTP server port",
        )

        arggroup_plugin.add_argument(
            "--mail-test-mode",
            help="send emails in test mode (flag)",
            action="store_true",
            default=None,
        )
        arggroup_plugin.add_argument(
            "--mail-dev-mode",
            help="send emails in development mode (flag)",
            action="store_true",
            default=None,
        )

        return argparser

    def init_config(self, app, config, **kwargs):
        """
        Callback to be called during default configuration initialization phase.
        """
        config.update(
            {
                self.CONFIG_MAIL_SUBJECT: None,
                self.CONFIG_MAIL_FROM: None,
                self.CONFIG_MAIL_TO: None,
                self.CONFIG_MAIL_CC: None,
                self.CONFIG_MAIL_BCC: None,
                self.CONFIG_MAIL_REPLY_TO: None,
                self.CONFIG_MAIL_RETURN_PATH: None,
                self.CONFIG_MAIL_ADMIN: "root",
                self.CONFIG_MAIL_TEST_MODE: False,
                self.CONFIG_MAIL_DEV_MODE: False,
                self.CONFIG_MAIL_DEV_SERVER: None,
                self.CONFIG_MAIL_DEV_PORT: None,
            }
        )
        return config

    def configure(self, app):
        """
        Configure application. This method will be called from :py:func:`pyzenkit.baseapp.BaseApp._configure_plugins`
        and it further updates current application configurations.

        This method is part of the **setup** stage of application`s life cycle.

        :param app: Reference to the parent application.
        """

    def setup(self, app):
        """
        Configure application. This method will be called from :py:func:`pyzenkit.baseapp.BaseApp._stage_setup_plugins`
        and it further updates current application configurations.

        This method is part of the **setup** stage of application`s life cycle.

        :param app: Reference to the parent application.
        """
        self.get_application = weakref.ref(app)
        app.mailerservice = self
        app.logger.debug("[STATUS] Set up mailer service plugin.")

    # ---------------------------------------------------------------------------

    @staticmethod
    def mail_sendmail(email):
        """
        Send given email directly through local sendmail binary. This method is
        usefull for fire and forget scenarios.

        :param mentat.emails.base.BaseEmail email: Email object.
        """
        envelope_from = email.get_header("return-path", email.get_header("from"))
        with Popen(["/usr/sbin/sendmail", "-t", "-oi", "-f", envelope_from], stdin=PIPE) as proc:
            proc.communicate(bytes(email.as_string(), "UTF-8"))

    @staticmethod
    def mail_smtplib(email, server, port):
        """
        Send given email via smtplib.

        :param mentat.emails.base.BaseEmail email: Email object.
        """
        envelope_from = email.get_header("return-path", email.get_header("from"))
        server = server or "localhost"
        port = port or 25
        with smtplib.SMTP(server, port) as smtp:
            smtp.send_message(email, from_addr=envelope_from)

    # ---------------------------------------------------------------------------

    def email_send(self, email_class, email_headers, email_params, flag_redirect=False):
        """
        Create email according to given class, headers and parameters and send
        it via :py:func:`mail_sendmail` method.

        :param class email_class: Email class to be instantinated.
        :param dict email_headers: Explicitly specified email headers.
        :param dict email_params: Additional email class constructor parameters.
        :param bool flag_redirect: Redirect email from original recipient to administrator.
        :return: Constructed email object.
        :rtype: mentat.emails.base.BaseEmail
        """
        if flag_redirect or self.get_application().c(self.CONFIG_MAIL_TEST_MODE):
            self.get_application().logger.info(
                "Redirecting report {} to {} from original {} (rdr: {}, mtm: {})".format(
                    email_headers.get("report_id", "None"),
                    self.get_application().c(self.CONFIG_MAIL_ADMIN),
                    email_headers.get("to", "None"),
                    str(flag_redirect),
                    str(self.get_application().c(self.CONFIG_MAIL_TEST_MODE)),
                )
            )
            email_headers["to"] = self.get_application().c(self.CONFIG_MAIL_ADMIN)

            if email_headers.get("cc"):
                self.get_application().logger.info(
                    "Modifying report {}: header cc changed from {} to [] (rdr: {}, mtm: {})".format(
                        email_headers.get("report_id", "None"),
                        email_headers.get("cc", "[]"),
                        str(flag_redirect),
                        str(self.get_application().c(self.CONFIG_MAIL_TEST_MODE)),
                    )
                )
                email_headers["cc"] = []
        else:
            for item in (
                (self.CONFIG_MAIL_TO, "to"),
                (self.CONFIG_MAIL_CC, "cc"),
                (self.CONFIG_MAIL_BCC, "bcc"),
            ):
                if self.get_application().c(item[0]):
                    self.get_application().logger.info(
                        "Modifying report {}: header {} changed from {} to {}".format(
                            email_headers.get("report_id", "None"),
                            item[1],
                            email_headers.get(item[1], "None"),
                            self.get_application().c(item[0]),
                        )
                    )
                    email_headers[item[1]] = self.get_application().c(item[0])

        for item in (
            (self.CONFIG_MAIL_SUBJECT, "subject"),
            (self.CONFIG_MAIL_FROM, "from"),
            (self.CONFIG_MAIL_REPLY_TO, "reply_to"),
            (self.CONFIG_MAIL_RETURN_PATH, "return_path"),
        ):
            if self.get_application().c(item[0]):
                self.get_application().logger.info(
                    "Modifying report {}: header {} changed from {} to {}".format(
                        email_headers.get("report_id", "None"),
                        item[1],
                        email_headers.get(item[1], "None"),
                        self.get_application().c(item[0]),
                    )
                )
                email_headers[item[1]] = self.get_application().c(item[0])

        self.get_application().logger.info(f"Sending email: '{email_headers!s}'")
        msg = email_class(email_headers, **email_params)

        if self.get_application().c(self.CONFIG_MAIL_DEV_MODE):
            self.mail_smtplib(
                msg,
                self.get_application().c(self.CONFIG_MAIL_DEV_SERVER),
                self.get_application().c(self.CONFIG_MAIL_DEV_PORT),
            )
        else:
            self.mail_sendmail(msg)

        return msg
