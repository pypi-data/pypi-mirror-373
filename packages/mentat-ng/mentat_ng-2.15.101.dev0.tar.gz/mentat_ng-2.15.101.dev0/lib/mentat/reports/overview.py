#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Library for generating statistical overview reports.

The implementation is based on :py:class:`mentat.reports.base.BaseReporter`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import json
import os

import mentat.const
import mentat.stats.idea
from mentat.const import tr_
from mentat.datatype.sqldb import EventReportModel, EventStatisticsModel
from mentat.emails.informant import ReportEmail
from mentat.reports.base import BaseReporter

REPORT_SUBJECT = tr_("Periodical statistical summary report")
"""Subject for report emails."""


def json_default(val):
    """
    Helper function for JSON serialization of non basic data types.
    """
    if isinstance(val, datetime.datetime):
        return val.isoformat()
    return str(val)


class OverviewReporter(BaseReporter):
    """
    Implementation of reporting class providing Mentat system overview reports.
    """

    def _setup_renderer(self, templates_dir):
        """
        Overloaded implementation of base :py:func:`mentat.reports.base.BaseReporter._setup_renderer`
        method. This implementation adds additional global functions into Jinja2
        templating environment, that are necessary for report rendering.
        """
        renderer = super()._setup_renderer(templates_dir)

        renderer.globals["format_section_key"] = self.format_section_key

        return renderer

    # ---------------------------------------------------------------------------

    def format_section_key(self, section, key):
        """
        Helper function for section key translation and/or formating.
        """
        if key in (tr_("__REST__"), tr_("__unknown__")):
            return self.translator.gettext(key)
        if section == "asns":
            return f"AS {key}"
        return key

    # ---------------------------------------------------------------------------

    def report(
        self,
        time_h,
        time_l,
        sqlalchemy_session,
        template_id,
        mailer,
        template_vars=None,
    ):
        """
        Perform reporting for given time interval.

        :param datetime.datetime time_h: Upper threshold of reporting time interval.
        :param datetime.datetime time_l: Lower threshold of reporting time interval.
        :param sqlalchemy_session: SQLAlchemy session to be used to retrieve the raw data.
        :param str template_id: Identifier of the template to use to render the report.
        :param mailer: Mailer to use to mail the report.
        :param dict template_vars: Dictionary containing additional template variables.
        :return: Tuple containing generated report as dict and email text.
        :rtype: tuple
        """
        result = {}

        result["ts_from_s"] = time_l.isoformat()
        result["ts_to_s"] = time_h.isoformat()
        result["ts_from"] = int(time_l.timestamp())
        result["ts_to"] = int(time_h.timestamp())
        result["interval"] = "{}_{}".format(result["ts_from_s"], result["ts_to_s"])

        # Fetch event data.
        stats_query = sqlalchemy_session.query(EventStatisticsModel)
        stats_query = stats_query.filter(EventStatisticsModel.dt_from >= time_l)
        stats_query = stats_query.filter(EventStatisticsModel.dt_to <= time_h)
        stats_query = stats_query.order_by(EventStatisticsModel.interval)
        stats_raw_e = stats_query.all()
        sqlalchemy_session.commit()

        stats_events = mentat.stats.idea.truncate_evaluations(mentat.stats.idea.aggregate_stat_groups(stats_raw_e))
        result["stats_events"] = stats_events
        result["stats_events_cnt"] = len(stats_raw_e)

        # Fetch event report data.
        stats_query = sqlalchemy_session.query(EventReportModel)
        stats_query = stats_query.filter(EventReportModel.createtime >= time_l)
        stats_query = stats_query.filter(EventReportModel.createtime <= time_h)
        stats_query = stats_query.filter(EventReportModel.type == mentat.const.REPORT_TYPE_SUMMARY)
        stats_query = stats_query.order_by(EventReportModel.label)
        stats_raw_r = stats_query.all()
        sqlalchemy_session.commit()
        stats_reports = mentat.stats.idea.aggregate_stats_reports(stats_raw_r, time_l, time_h)
        result["stats_reports"] = stats_reports
        result["stats_reports_cnt"] = len(stats_raw_r)

        stats_query = sqlalchemy_session.query(EventReportModel)
        stats_query = stats_query.filter(EventReportModel.createtime >= time_l)
        stats_query = stats_query.filter(EventReportModel.createtime <= time_h)
        stats_raw_r = stats_query.all()
        sqlalchemy_session.commit()
        result["stats_reports_cnt_all"] = len(stats_raw_r)

        # Render reports.
        report_txt, report_html = self.render_report_overall(template_id, time_l, time_h, result, template_vars)

        # Send emails.
        report_msg_headers = {
            "subject": self.translator.gettext(REPORT_SUBJECT),
            "report_id": result["interval"],
            "report_type": "overall",
        }
        report_msg_params = {
            "text_plain": report_txt,
            "text_html": report_html,
            "data_events": stats_events,
            "data_reports": stats_events,
        }
        email = mailer.email_send(ReportEmail, report_msg_headers, report_msg_params)
        result["mail_to"] = list(set(email.get_destinations()))

        # Save report data to disk.
        self._save_to_json_file(
            stats_events,
            "report-overview-overall-{}-events.json".format(result["interval"]),
        )
        self._save_to_json_file(
            stats_reports,
            "report-overview-overall-{}-reports.json".format(result["interval"]),
        )

        return result

    # ---------------------------------------------------------------------------

    def render_report_overall(self, template_id, time_l, time_h, result, template_vars=None):
        """
        Render *summary* section of the event report email.

        :param mentat.datatype.sqldb.EventReportModel report: Event report.
        :param dict events: Dictionary structure with IDEA events to be reported.
        :param str locale_name: Name of the locale.
        :param str timezone_name: Name of the timezone.
        :param str template_file: Name of the template file.
        :param dict template_vars: Additional template variables.
        :return: Content of the extra section of report email.
        :rtype: str
        """
        # Render reports.
        template_txt = self.renderer.get_template(f"{template_id}.txt.j2")
        template_html = self.renderer.get_template(f"{template_id}.html.j2")
        report_txt = template_txt.render(
            title=self.translator.gettext(REPORT_SUBJECT),
            dt_c=datetime.datetime.utcnow(),
            dt_h=time_h,
            dt_l=time_l,
            stats_events=result["stats_events"],
            stats_events_cnt=result["stats_events_cnt"],
            stats_reports=result["stats_reports"],
            stats_reports_cnt=result["stats_reports_cnt"],
            stats_reports_cnt_all=result["stats_reports_cnt_all"],
            additional_vars=template_vars,
        )
        report_html = template_html.render(
            title=self.translator.gettext(REPORT_SUBJECT),
            dt_c=datetime.datetime.utcnow(),
            dt_h=time_h,
            dt_l=time_l,
            stats_events=result["stats_events"],
            stats_events_cnt=result["stats_events_cnt"],
            stats_reports=result["stats_reports"],
            stats_reports_cnt=result["stats_reports_cnt"],
            stats_reports_cnt_all=result["stats_reports_cnt_all"],
            additional_vars=template_vars,
        )
        return report_txt, report_html

    # ---------------------------------------------------------------------------

    def _save_to_json_file(self, data, filename):
        """
        Helper method for saving given data into given JSON file.

        :param dict data: Data to be serialized.
        :param str filename: Name of the target JSON file.
        """
        data_json = json.dumps(data, default=json_default, sort_keys=True, indent=4)

        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, "w", encoding="utf8") as imf:
            imf.write(data_json)

        return filepath
