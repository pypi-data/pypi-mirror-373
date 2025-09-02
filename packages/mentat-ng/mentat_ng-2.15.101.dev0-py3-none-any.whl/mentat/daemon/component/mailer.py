#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component providing configurable mailing services to daemons.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import json
from email.mime.multipart import MIMEMultipart

# from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from subprocess import PIPE, Popen

from jinja2 import Environment, PackageLoader

import pyzenkit.zendaemon


class MailerDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Implementation of ZenDaemonComponent for mailing services.
    """

    EVENT_EMAIL_SEND_IDEA = "email_send_idea"
    EVENT_LOG_STATISTICS = "log_statistics"

    STATS_CNT_MAILED = "cnt_mailed"
    STATS_CNT_ERRORS = "cnt_errors"
    STATS_COUNTERS = "counters"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "mailer")

        # Initialize Jinja2 template environment
        self.templ_env = Environment(loader=PackageLoader("mentat", "templates_email"))

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_EMAIL_SEND_IDEA: self.EVENT_EMAIL_SEND_IDEA,
                self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS,
            },
        )

        self.statistics_cur[self.STATS_COUNTERS] = {}

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_EMAIL_SEND_IDEA],
                "callback": self.cbk_event_email_send_idea,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_LOG_STATISTICS],
                "callback": self.cbk_event_log_statistics,
                "prepend": False,
            },
        ]

    @staticmethod
    def _sendmail(email):
        """
        Send email directly through local sendmail binary.
        """
        with Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE) as proc:
            proc.communicate(bytes(email.as_string(), "UTF-8"))

    # ---------------------------------------------------------------------------

    def cbk_event_email_send_idea(self, daemon, args):
        """
        Send email containing various number of idea messages.
        """
        template_name = args.get("template", "idea")
        template_txt = self.templ_env.get_template(f"{template_name}.txt.j2")
        template_html = self.templ_env.get_template(f"{template_name}.html.j2")

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart("mixed")
        msg["Subject"] = args["subject"]
        msg["From"] = args["from"]
        msg["To"] = args["to"]
        if "reply_to" in args:
            msg["Reply-To"] = args["reply_to"]
        msg["X-Cesnet-Report-Type"] = args["report_type"]

        # Create the body of the message (a plain-text and an HTML version).
        text_plain = template_txt.render(**args)
        text_html = template_html.render(**args)

        # Record the MIME types of both parts - text/plain and text/html.
        msg_text = MIMEMultipart("alternative")
        msg_text_part1 = MIMEText(text_plain, "plain")
        msg_text_part2 = MIMEText(text_html, "html")

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg_text.attach(msg_text_part1)
        msg_text.attach(msg_text_part2)

        # Attach the text message
        msg.attach(msg_text)

        # Attach IDEA message
        attach_idea = MIMEText(
            json.dumps(args["idea"], default=args["idea"].json_default, sort_keys=True, indent=4),
            "plain",
            _charset="utf-8",
        )
        attach_idea.add_header(
            "Content-Disposition",
            "attachment",
            filename="{}.idea.json.txt".format(args["id"]),
        )
        msg.attach(attach_idea)

        daemon.logger.info(
            "Reporting message '{}':'{}' via email to '{}'".format(args["id"], args["idea_id"], args["to"])
        )
        self.statistics_cur[self.STATS_COUNTERS][args["to"]] = (
            self.statistics_cur[self.STATS_COUNTERS].get(args["to"], 0) + 1
        )
        self.inc_statistic(self.STATS_CNT_MAILED)
        self._sendmail(msg)
        return (daemon.FLAG_CONTINUE, None)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [self.STATS_CNT_MAILED, self.STATS_CNT_ERRORS]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        stats_str = f"{stats_str}\n\t--- Destination stats ---"
        for k in stats[self.STATS_COUNTERS]:
            stats_str = "{}\n\t{:40s} {:12,d} (+{:8,d}, {:8,.2f} #/s)".format(
                stats_str,
                k,
                stats[self.STATS_COUNTERS][k]["cnt"],
                stats[self.STATS_COUNTERS][k]["inc"],
                stats[self.STATS_COUNTERS][k]["spd"],
            )

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (pyzenkit.zendaemon.ZenDaemon.FLAG_CONTINUE, args)
