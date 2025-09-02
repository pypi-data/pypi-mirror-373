#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Library for generating event reports.

The implementation is based on :py:class:`mentat.reports.base.BaseReporter`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import json
import os
import socket
import zipfile
from copy import deepcopy
from dataclasses import asdict
from typing import Any, cast

from sqlalchemy.orm.attributes import flag_modified

from ransack import Filter, Parser, RansackError, get_values

import mentat.const
import mentat.datatype.internal
import mentat.idea.internal
import mentat.services.whois
import mentat.stats.idea
from mentat.const import EventSections, tr_
from mentat.datatype.sqldb import DetectorModel, EventClassModel, EventReportModel
from mentat.emails.event import ReportEmail
from mentat.idea.internal import Idea
from mentat.reports.aggregations import EventAggregator
from mentat.reports.base import BaseReporter
from mentat.reports.data import ReportingProperties, SourceReportData, TargetReportData
from mentat.reports.utils import NoThresholdingCache, StorageThresholdingCache, get_recipients
from mentat.services.eventstorage import record_to_idea

REPORT_SUBJECT_SUMMARY = tr_("[{:s}] {:s} - Notice about possible problems in your network")
"""Subject for summary report emails."""

REPORT_SUBJECT_EXTRA = tr_("[{:s}] {:s} - Notice about possible problems regarding host {:s}")
"""Subject for extra report emails."""

REPORT_SUBJECT_TARGET = tr_("[{:s}] {:s} - Notice about attacks against your network")
"""Subject for target report emails."""

REPORT_EMAIL_TEXT_WIDTH = 90
"""Width of the report email text."""


def json_default(val):
    """
    Helper function for JSON serialization of non-basic data types.
    """
    if isinstance(val, datetime.datetime):
        return val.isoformat()
    return str(val)


class EventReporter(BaseReporter):
    """
    Implementation of reporting class providing Mentat event reports.
    """

    def __init__(
        self,
        logger,
        reports_dir,
        templates_dir,
        global_fallback,
        locale,
        timezone,
        eventservice,
        sqlservice,
        mailer,
        groups_dict,
        settings_dict,
        whoismodule,
        thresholding=True,
        item_limit=15,
    ):
        super().__init__(logger, reports_dir, templates_dir, locale, timezone)

        self.eventservice = eventservice
        self.sqlservice = sqlservice
        self.mailer = mailer

        self.global_fallback = global_fallback

        self.renderer.globals["item_limit"] = item_limit

        self.ransack_parser = Parser()
        self.ransack_filter = Filter()

        self.whoismodule = whoismodule

        self.groups_dict = groups_dict
        self.settings_dict = settings_dict
        self.detectors_dict = {det.name: det for det in self.sqlservice.session.query(DetectorModel).all()}

        self.message_id_dict = self._init_message_id_dict()

        if thresholding:
            self.tcache = StorageThresholdingCache(logger, eventservice)
        else:
            self.tcache = NoThresholdingCache()

    def _init_message_id_dict(self):
        result = {"thresholds": {}}
        thresholds = self.eventservice.fetch_thresholds()
        for key, label in thresholds:
            if not label:
                continue
            result["thresholds"][key] = label
        return result

    # ---------------------------------------------------------------------------

    def cleanup(self, ttl):
        """
        Cleanup thresholding cache and remove all records with TTL older than given
        value.

        :param datetime.datetime ttl: Upper cleanup time threshold.
        :return: Number of removed records.
        :rtype: int
        """
        return self.tcache.cleanup(ttl)

    def report(self, reporting_properties):
        """
        Perform reporting for given most specific group, event severity and time window.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :rtype: dict
        """
        result = {
            "ts_from_s": reporting_properties.lower_time_bound.isoformat(),
            "ts_to_s": reporting_properties.upper_time_bound.isoformat(),
            "ts_from": int(reporting_properties.lower_time_bound.timestamp()),
            "ts_to": int(reporting_properties.upper_time_bound.timestamp()),
        }

        # First do normal reporting, then shadow reporting.
        for is_shadow in [False, True]:
            reporting_properties.is_shadow = is_shadow
            # First do source-based reporting, then target-based reporting.
            for is_target in [False, True]:
                reporting_properties.is_target = is_target
                section = reporting_properties.get_current_section()
                result[section] = {}
                events = {}
                while True:
                    # A: Fetch events from database.
                    events_fetched = self.fetch_severity_events(reporting_properties)

                    result[section]["evcount_new"] = len(events_fetched) + result.get("evcount_new", 0)
                    if not events_fetched:
                        break

                    # B: Perform event filtering according to custom group filters and aggregate by source/target.
                    events_passed_filters, aggregated_events, fltlog, passed_cnt = self.filter_events(
                        reporting_properties, events_fetched
                    )
                    for groups in aggregated_events:
                        group_chain = groups[0]
                        if str(group_chain) not in result:
                            result[section][str(group_chain)] = {}
                        result[section][str(group_chain)]["evcount_all"] = len(events_passed_filters[groups])
                        result[section][str(group_chain)]["evcount_new"] = result[section][str(group_chain)][
                            "evcount_all"
                        ]

                    result[section]["evcount_flt"] = passed_cnt
                    result[section]["evcount_flt_blk"] = len(events_fetched) - passed_cnt
                    result[section]["filtering"] = fltlog

                    if result[section]["evcount_flt"]:
                        self.logger.info(
                            "%s: Filters let %d events through, %d blocked.",
                            reporting_properties.group.name,
                            result[section]["evcount_flt"],
                            result[section]["evcount_flt_blk"],
                        )
                    else:
                        self.logger.info(
                            "%s: Filters blocked all %d new events, nothing to report.",
                            reporting_properties.group.name,
                            result[section]["evcount_flt_blk"],
                        )
                        # Save changes to filter hits.
                        self.sqlservice.session.commit()
                        break

                    # Create new dictionary to store events coming from credible detectors.
                    aggregated_credible_events = {}
                    for groups, events_aggr in aggregated_events.items():
                        group_chain = groups[0]
                        # C: Discard events from detectors with low credibility.
                        _events_aggr, blocked_cnt = self.filter_events_by_credibility(events_aggr)
                        # If all events were discarded, _events_aggr is None.
                        if _events_aggr:
                            aggregated_credible_events[groups] = _events_aggr
                        # Save information about how many events passed and how many were discarded.
                        result[section][str(group_chain)]["evcount_det"] = result[section]["evcount_flt"] - blocked_cnt
                        result[section][str(group_chain)]["evcount_det_blk"] = blocked_cnt

                    for groups, events_aggr in aggregated_credible_events.items():
                        group_chain = groups[0]
                        # D: Perform event thresholding.
                        events_thr, events_aggr = self.threshold_events(reporting_properties, events_aggr, group_chain)

                        result[section][str(group_chain)]["evcount_thr"] = len(events_thr)
                        result[section][str(group_chain)]["evcount_thr_blk"] = result[section][str(group_chain)][
                            "evcount_det"
                        ] - len(events_thr)
                        if not events_thr:
                            continue

                        # E: Save aggregated events for further processing.
                        events[groups] = {}
                        events[groups]["regular"] = events_thr
                        events[groups]["regular_aggr"] = events_aggr

                    break

                while True:
                    # A: Detect possible event relapses.
                    events_rel = self.relapse_events(reporting_properties)
                    if not events_rel:
                        break

                    # B: Aggregate events by sources for further processing.
                    events_rel, events_aggregated, fltlog, passed_cnt = self.filter_events(
                        reporting_properties, map(record_to_idea, events_rel)
                    )
                    for groups, events_aggr in events_aggregated.items():
                        group_chain = groups[0]
                        if str(group_chain) not in result:
                            result[section][str(group_chain)] = {}
                            result[section][str(group_chain)]["evcount_all"] = 0
                        result[section][str(group_chain)]["evcount_rlp"] = len(events_rel[groups])
                        result[section][str(group_chain)]["evcount_all"] += result[section][str(group_chain)][
                            "evcount_rlp"
                        ]
                        if groups not in events:
                            events[groups] = {}
                        events[groups]["relapsed"] = events_rel[groups]
                        events[groups]["relapsed_aggr"] = events_aggr

                    break

                for groups, groups_events in events.items():
                    (group_chain, fallback_groups) = groups
                    # Check, that there is anything to report (regular and/or relapsed events).
                    if "regular" not in groups_events and "relapsed" not in groups_events:
                        result[section][str(group_chain)]["evcount_rep"] = 0
                        result[section][str(group_chain)]["result"] = "skipped-no-events"
                        continue
                    result[section][str(group_chain)]["evcount_rep"] = len(groups_events.get("regular", [])) + len(
                        groups_events.get("relapsed", [])
                    )

                    main_group_settings = self.settings_dict[group_chain[0]]
                    original_group_only = len(group_chain) == 1 and group_chain[0] == reporting_properties.group.name

                    if not is_target:
                        # Generate summary report.
                        report_summary = self.report_summary(
                            reporting_properties,
                            result,
                            groups_events,
                            group_chain,
                            fallback_groups,
                            main_group_settings,
                            original_group_only,
                        )
                        # Generate extra reports.
                        self.report_extra(
                            reporting_properties,
                            report_summary,
                            result,
                            groups_events,
                            group_chain,
                            fallback_groups,
                            main_group_settings,
                        )
                    else:
                        # Generate target reports.
                        self.report_target(
                            reporting_properties,
                            result,
                            groups_events,
                            group_chain,
                            fallback_groups,
                            main_group_settings,
                            original_group_only,
                        )

                    # Update the thresholding cache if necessary.
                    self.check_and_update_thresholding_cache(reporting_properties, groups_events, main_group_settings)

                    result["result"] = "reported"
                    result[section][str(group_chain)]["result"] = "reported"

        if not result.get("result"):
            result["result"] = "skipped-no-events"
        return result

    def _create_report_object(self, reporting, result, events, group_chain, timezone, original_group_only):
        """
        Creates a report object from results.

        :param ReportingProperties reporting: Properties of the current reporting.
        :param dict result: Reporting result structure with various usefull metadata.
        :param dict events: Dictionary structure with IDEA events to be reported.
        :param list group_chain: List of resolved groups.
        :param str timezone: Timezone of the group.
        :param bool original_group_only: Check if there is only the most specific group.
        """
        section = reporting.get_current_section()
        evcount_flt_blk = result[section].get("evcount_flt_blk", 0) if original_group_only else 0
        report = EventReportModel(
            groups=[self.groups_dict[group] for group in group_chain],
            severity=reporting.severity,
            type=mentat.const.REPORT_TYPE_TARGET if reporting.is_target else mentat.const.REPORT_TYPE_SUMMARY,
            dt_from=reporting.lower_time_bound,
            dt_to=reporting.upper_time_bound,
            evcount_rep=result[section][str(group_chain)].get("evcount_rep", 0),
            evcount_all=result[section][str(group_chain)].get("evcount_all", 0) + evcount_flt_blk,
            evcount_new=result[section][str(group_chain)].get("evcount_new", 0) + evcount_flt_blk,
            evcount_flt=result[section][str(group_chain)].get("evcount_new", 0),
            evcount_flt_blk=evcount_flt_blk,
            evcount_det=result[section][str(group_chain)].get("evcount_det", 0),
            evcount_det_blk=result[section][str(group_chain)].get("evcount_det_blk", 0),
            evcount_thr=result[section][str(group_chain)].get("evcount_thr", 0),
            evcount_thr_blk=result[section][str(group_chain)].get("evcount_thr_blk", 0),
            evcount_rlp=result[section][str(group_chain)].get("evcount_rlp", 0),
            flag_testdata=reporting.has_test_data,
            flag_shadow=reporting.is_shadow,
            filtering=result.get("filtering", {}) if original_group_only else {},
        )
        report.generate_label()
        report.calculate_delta()

        events_all = events.get("regular", []) + events.get("relapsed", [])
        report.statistics = mentat.stats.idea.truncate_evaluations(
            mentat.stats.idea.evaluate_events(events_all, reporting.is_target)
        )
        # Save report data to disk in JSON format.
        self._save_to_json_files(events_all, f"security-report-{report.label}.json")
        report.structured_data = self.prepare_structured_data(
            events.get("regular_aggr", {}),
            events.get("relapsed_aggr", {}),
            timezone,
            reporting.is_target,
        )
        # Add report to database session.
        self.sqlservice.session.add(report)
        return report

    def report_target(
        self,
        reporting_properties,
        result,
        events,
        group_chain,
        fallback_groups,
        settings,
        original_group_only,
        template_vars=None,
    ):
        """
        Generate target report for given events for given group, severity and period.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param dict result: Reporting result structure with various usefull metadata.
        :param dict events: Dictionary structure with IDEA events to be reported.
        :param list group_chain: List of resolved groups.
        :param list fallback_groups: List of fallback groups.
        :param mentat.reports.utils.ReportingSettings settings: Reporting settings.
        :param bool original_group_only: Check if there is only the most specific group.
        :param dict template_vars: Dictionary containing additional template variables.
        """
        report = self._create_report_object(
            reporting_properties,
            result,
            events,
            group_chain,
            settings.timezone,
            original_group_only,
        )
        # Remove groups which don't want to receive any reports.
        final_group_list = [g for g in group_chain if self.settings_dict[g].mode != mentat.const.REPORTING_MODE_NONE]
        # Send report via email.
        if final_group_list and not reporting_properties.is_shadow:
            self._mail_report(
                report,
                self.settings_dict[final_group_list[0]],
                final_group_list,
                fallback_groups,
                result,
                template_vars,
            )
        # Commit all changes on report object to database.
        self.sqlservice.session.commit()
        result[reporting_properties.get_current_section()].setdefault("target_id", []).append(report.label)
        return report

    def report_summary(
        self,
        reporting_properties,
        result,
        events,
        group_chain,
        fallback_groups,
        settings,
        original_group_only,
    ):
        """
        Generate summary report from given events for given group, severity and period.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param dict result: Reporting result structure with various useful metadata.
        :param dict events: Dictionary structure with IDEA events to be reported.
        :param list group_chain: List of resolved groups.
        :param list fallback_groups: List of fallback groups.
        :param mentat.reports.utils.ReportingSettings settings: Reporting settings.
        :param bool original_group_only: Check if there is only the most specific group.
        """
        report = self._create_report_object(
            reporting_properties,
            result,
            events,
            group_chain,
            settings.timezone,
            original_group_only,
        )
        # Remove groups which don't want to receive a summary.
        final_group_list = [
            g
            for g in group_chain
            if self.settings_dict[g].mode in (mentat.const.REPORTING_MODE_SUMMARY, mentat.const.REPORTING_MODE_BOTH)
        ]
        # Send report via email.
        if final_group_list and not reporting_properties.is_shadow:
            self._mail_report(
                report,
                self.settings_dict[final_group_list[0]],
                final_group_list,
                fallback_groups,
                result,
                reporting_properties.template_vars,
            )
        # Commit all changes on report object to database.
        self.sqlservice.session.commit()
        result[reporting_properties.get_current_section()].setdefault("summary_id", []).append(report.label)
        return report

    def report_extra(self, reporting_properties, parent_rep, result, events, group_chain, fallback_groups, settings):
        """
        Generate extra reports from given events for given group, severity and period.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param mentat.datatype.sqldb.EventReportModel parent_rep: Parent summary report.
        :param dict result: Reporting result structure with various usefull metadata.
        :param dict events: Dictionary structure with IDEA events to be reported.
        :param list group_chain: List of resolved groups.
        :param list fallback_groups: List of fallback groups.
        :param mentat.reports.utils.ReportingSettings settings: Reporting settings.
        """
        if all(
            self.settings_dict[g].mode not in (mentat.const.REPORTING_MODE_EXTRA, mentat.const.REPORTING_MODE_BOTH)
            for g in group_chain
        ):
            return

        sources = list(set(list(events.get("regular_aggr", {}).keys()) + list(events.get("relapsed_aggr", {}).keys())))
        section = reporting_properties.get_current_section()

        for src in sorted(sources):
            events_regular_aggr = events.get("regular_aggr", {}).get(src, [])
            events_relapsed_aggr = events.get("relapsed_aggr", {}).get(src, [])
            events_all = events_regular_aggr + events_relapsed_aggr

            # Instantinate the report object.
            report = EventReportModel(
                groups=[self.groups_dict[group] for group in group_chain],
                parent=parent_rep,
                severity=reporting_properties.severity,
                type=mentat.const.REPORT_TYPE_EXTRA,
                dt_from=reporting_properties.lower_time_bound,
                dt_to=reporting_properties.upper_time_bound,
                evcount_rep=len(events_all),
                evcount_all=result[section][str(group_chain)]["evcount_rep"],
                flag_testdata=reporting_properties.has_test_data,
                flag_shadow=reporting_properties.is_shadow,
            )
            report.generate_label()
            report.calculate_delta()

            report.statistics = mentat.stats.idea.truncate_evaluations(
                mentat.stats.idea.evaluate_events(events_all),
            )

            # Save report data to disk in JSON format.
            self._save_to_json_files(events_all, f"security-report-{report.label}.json")

            report.structured_data = self.prepare_structured_data(
                {src: events_regular_aggr}, {src: events_relapsed_aggr}, settings.timezone, False
            )

            # Save the generated report label for the given source.
            self.message_id_dict[src] = report.label

            # Add report to database session.
            self.sqlservice.session.add(report)

            # Send report via email.
            final_group_list = [
                g
                for g in group_chain
                if self.settings_dict[g].mode in (mentat.const.REPORTING_MODE_EXTRA, mentat.const.REPORTING_MODE_BOTH)
            ]
            if final_group_list and not reporting_properties.is_shadow:
                self._mail_report(
                    report,
                    self.settings_dict[final_group_list[0]],
                    final_group_list,
                    fallback_groups,
                    result,
                    reporting_properties.template_vars,
                    src,
                )

            # Commit all changes on report object to database.
            self.sqlservice.session.commit()

            result[section].setdefault("extra_id", []).append(report.label)

    # ---------------------------------------------------------------------------

    @staticmethod
    def prepare_structured_data(
        events_reg_aggr: dict, events_rel_aggr: dict, timezone: str, is_target: bool
    ) -> dict[str, Any]:
        """
        Prepare structured data for report column.

        :param dict events_reg_aggr: List of events as :py:class:`mentat.idea.internal.Idea` objects.
        :param dict events_rel_aggr: List of relapsed events as :py:class:`mentat.idea.internal.Idea` objects.
        :param str timezone: Timezone of the group.
        :param bool is_target: If the reporting is target-based (or source-based if False).
        :return: Structured data that can be used to generate report message
        """
        if is_target:
            return asdict(
                TargetReportData(
                    EventAggregator.aggregate_target(events_reg_aggr),
                    EventAggregator.aggregate_target(events_rel_aggr),
                    str(timezone),
                )
            )
        return asdict(
            SourceReportData(
                EventAggregator.aggregate_source(events_reg_aggr),
                EventAggregator.aggregate_source(events_rel_aggr),
                str(timezone),
            )
        )

    # ---------------------------------------------------------------------------

    def fetch_severity_events(self, reporting: ReportingProperties) -> list[Idea]:
        """
        Fetch events based on the current reporting properties.
        """
        count, events = self.eventservice.search_events(reporting.get_event_search_parameters())
        if count > 0:
            self.logger.info("%s: Found %d event(s) with %s.", reporting.group.name, count, reporting.to_log_text())
        else:
            self.logger.debug("%s: Found 0 event(s) with %s.", reporting.group.name, reporting.to_log_text())
        return cast(list[Idea], events)

    def _filter_groups(self, groups, event, fltlog, is_target):
        filtered_groups = []
        for group in groups:
            filter_list = self.settings_dict[group].setup_filters(self.ransack_parser, is_target)
            match = self.filter_event(filter_list, event)
            if match:
                self.logger.debug("Event matched filtering rule '%s' of group %s.", match, group)
                fltlog[match] = fltlog.get(match, 0) + 1
            else:
                filtered_groups.append(group)
        return filtered_groups, fltlog

    def filter_one_event(self, reporting_properties, src, event, fltlog):
        """
        Compute and filter resolved groups for an event with only one source IP address.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param ipranges.IP/Net/Range src: Source IP address
        :param mentat.idea.internal.Idea event: Event to be filtered.
        :param dict fltlog: Filtering log.
        :return: List of resolved groups, list of fallback groups and filtering log as dictionary.
        :rtype: tuple
        """
        # Get resolved groups for a given source sorted by the priority.
        groups = []
        fallback_groups = []
        for net in self.whoismodule.lookup(src)[::-1]:
            if net["is_base"]:
                self.logger.debug(
                    "Adding group '%s' to fallback groups of event with ID '%s' because '%s' belongs to base network.",
                    net["abuse_group"],
                    event["ID"],
                    str(src),
                )
                fallback_groups.append(net["abuse_group"])
            else:
                groups.append(net["abuse_group"])
        # dict.fromkeys uniquifies the list while preserving the order of the elements.
        groups = list(dict.fromkeys(groups))
        fallback_groups = list(dict.fromkeys(fallback_groups))

        # Ignore sources where the main group is different from the currently processed one.
        if reporting_properties.group.name not in groups:
            return [], [], fltlog

        filtered_groups, fltlog = self._filter_groups(groups, event, fltlog, reporting_properties.is_target)

        # If any filtering rule of at least one of the groups was matched then this event shall not be reported to anyone.
        if filtered_groups != groups:
            self.logger.debug("Discarding event with ID '%s' from reports.", event["ID"])
            return [], [], fltlog

        fallback_groups, fltlog = self._filter_groups(fallback_groups, event, fltlog, reporting_properties.is_target)
        return filtered_groups, fallback_groups, fltlog

    def filter_events_by_credibility(self, events_aggr):
        """
        Filter given dictionary of IDEA events aggregated by the source IP address by detector credibility.
        If the resulting credibility is less than 0.5, the event is discarded from the report.

        :param dict events_aggr: Dictionary of IDEA events as :py:class:`mentat.idea.internal.Idea` objects.
        :return: Tuple with filtered dictionary, number of events passed, number of events discarded.
        :rtype: tuple
        """
        blocked = set()
        _events_aggr = {}
        for ip in events_aggr:
            for event in events_aggr[ip]:
                _pass = 1.0
                for detector in event.get_detectors():
                    if detector not in self.detectors_dict:
                        self.logger.info(
                            "Event with ID '%s' contains unknown detector '%s'. Assuming full credibility.",
                            event.get_id(),
                            detector,
                        )
                        continue
                    _pass *= self.detectors_dict[detector].credibility
                if _pass < 0.5:
                    if event.get_id() in blocked:
                        continue
                    self.logger.info("Discarding event with ID '%s'.", event.get_id())
                    blocked.add(event.get_id())
                    # Increase number of hits.
                    sql_detector = self.detectors_dict[event.get_detectors()[-1]]
                    sql_detector.hits += 1
                    # Inefficient but rare so should be alright.
                    self.sqlservice.session.add(sql_detector)
                    self.sqlservice.session.commit()
                else:
                    if ip not in _events_aggr:
                        _events_aggr[ip] = []
                    _events_aggr[ip].append(event)
        return _events_aggr, len(blocked)

    def filter_events(self, reporting_properties, events):
        """
        Filter given list of IDEA events according to given group settings.
        Events are aggregated by resolved groups and source/target IP addresses.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param list events: List of IDEA events as :py:class:`mentat.idea.internal.Idea` objects.
        :return: Tuple with list of events that passed filtering, aggregation of them, filtering log as a dictionary and number of passed events.
        :rtype: tuple
        """
        result = {}
        aggregated_result = {}
        fltlog = {}
        filtered_cnt = 0
        seen = {}

        section = EventSections.TARGET if reporting_properties.is_target else EventSections.SOURCE

        for event in events:
            acc = []
            passed = False
            if len(get_values(event, section + ".IP4") + get_values(event, section + ".IP6")) > 1:
                event_copy = deepcopy(event)
                for source in event_copy[section]:
                    source["IP4"] = []
                    source["IP6"] = []
                for src in set(get_values(event, section + ".IP4")):
                    event_copy[section][0]["IP4"] = [src]
                    filtered_groups, fallback_groups, fltlog = self.filter_one_event(
                        reporting_properties, src, event_copy, fltlog
                    )
                    acc.append((src, filtered_groups, fallback_groups))
                event_copy[section][0]["IP4"] = []
                for src in set(get_values(event, section + ".IP6")):
                    event_copy[section][0]["IP6"] = [src]
                    filtered_groups, fallback_groups, fltlog = self.filter_one_event(
                        reporting_properties, src, event_copy, fltlog
                    )
                    acc.append((src, filtered_groups, fallback_groups))
            else:
                for src in set(get_values(event, section + ".IP4") + get_values(event, section + ".IP6")):
                    filtered_groups, fallback_groups, fltlog = self.filter_one_event(
                        reporting_properties, src, event, fltlog
                    )
                    acc.append((src, filtered_groups, fallback_groups))

            for src, filtered_groups, fallback_groups in acc:
                if not filtered_groups:
                    if not fallback_groups:
                        continue
                    filtered_groups = fallback_groups
                passed = True
                groups = (tuple(filtered_groups), tuple(fallback_groups))
                if groups not in result:
                    result[groups] = []
                    seen[groups] = []
                if groups not in aggregated_result:
                    aggregated_result[groups] = {}
                if str(src) not in aggregated_result[groups]:
                    aggregated_result[groups][str(src)] = []
                aggregated_result[groups][str(src)].append(event)
                if event["ID"] not in seen[groups]:
                    result[groups].append(event)
                    seen[groups].append(event["ID"])

            if passed:
                filtered_cnt += 1
            else:
                self.logger.debug("Event matched filtering rules, all sources filtered")

        return result, aggregated_result, fltlog, filtered_cnt

    @staticmethod
    def _whois_filter(sources, src, _whoismodule, whoismodule_cache):
        """
        Help method for filtering sources by group's networks
        """
        if src not in whoismodule_cache:
            # Source IP must belong to network range of given group.
            whoismodule_cache[src] = bool(_whoismodule.lookup(src))
        if whoismodule_cache[src]:
            sources.add(src)
        return sources

    def threshold_events(self, reporting_properties, events_aggr, group_chain):
        """
        Threshold given list of IDEA events according to given group settings.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param dict events_aggr: Aggregation of IDEA events as :py:class:`mentat.idea.internal.Idea` objects by source.
        :return: List of events that passed thresholding.
        :rtype: list
        """
        result = {}
        aggregated_result = {}
        filtered = set()
        for source, events in events_aggr.items():
            for event in events:
                if not self.tcache.event_is_thresholded(
                    event, source, reporting_properties.upper_time_bound, reporting_properties.is_target
                ):
                    if source not in aggregated_result:
                        aggregated_result[source] = []
                    aggregated_result[source].append(event)
                    result[event["ID"]] = event
                else:
                    filtered.add(event["ID"])
                    self.tcache.threshold_event(reporting_properties, event, source)

        filtered -= set(result.keys())
        if result:
            self.logger.info(
                "%s: Thresholds let %d events through, %d blocked.",
                group_chain,
                len(result),
                len(filtered),
            )
        else:
            self.logger.info(
                "%s: Thresholds blocked all %d events, nothing to report.",
                group_chain,
                len(filtered),
            )
        return list(result.values()), aggregated_result

    def relapse_events(self, reporting_properties: ReportingProperties) -> Any:
        """
        Detect IDEA event relapses for given group settings.

        :rtype: list
        """
        events = self.eventservice.search_relapsed_events(
            reporting_properties.group.name,
            reporting_properties.severity,
            reporting_properties.upper_time_bound,
            reporting_properties.is_target,
            reporting_properties.is_shadow,
        )
        if not events:
            self.logger.debug(
                f"%s: No relapsed {'target' if reporting_properties.is_target else 'source'} events with severity '%s' and relapse threshold TTL '%s'. (%s)",
                reporting_properties.group.name,
                reporting_properties.severity,
                reporting_properties.upper_time_bound.isoformat(),
                "shadow reporting" if reporting_properties.is_shadow else "normal reporting",
            )
        else:
            self.logger.info(
                f"%s: Found %d relapsed {'target' if reporting_properties.is_target else 'source'} event(s) with severity '%s' and relapse threshold TTL '%s'. (%s)",
                reporting_properties.group.name,
                len(events),
                reporting_properties.severity,
                reporting_properties.upper_time_bound.isoformat(),
                "shadow reporting" if reporting_properties.is_shadow else "normal reporting",
            )
        return events

    def aggregate_relapsed_events(self, relapsed):
        """
        :param dict relapsed: Dictionary of events aggregated by threshold key.
        :return: Events aggregated by source.
        :rtype: dict
        """
        result = []
        aggregated_result = {}
        for event in relapsed:
            result.append(record_to_idea(event))
            for key in event.keyids:
                source = self.tcache.get_source_from_cache_key(key)
                if source not in aggregated_result:
                    aggregated_result[source] = []
                aggregated_result[source].append(result[-1])
        return result, aggregated_result

    def check_and_update_thresholding_cache(self, reporting, events, settings):
        """
        Checks the thresholding period, and if it is a non-zero value, then it
        updates the thresholding records for the aggregated events.

        :param ReportingProperties reporting: Properties of the current reporting.
        :param dict events: Dictionary structure with IDEA events that were reported.
        :param mentat.reports.utils.ReportingSettings settings: Reporting settings.
        """
        threshold_period = settings.timing_cfg[reporting.severity][f"thr{'_target' if reporting.is_target else ''}"]
        relapse_period = settings.timing_cfg[reporting.severity][f"rel{'_target' if reporting.is_target else ''}"]
        ttl = reporting.upper_time_bound + threshold_period
        for events_aggr_key in ("regular_aggr", "relapsed_aggr"):
            for source in events.get(events_aggr_key, {}):
                for event in events[events_aggr_key][source]:
                    self.tcache.set_threshold(
                        event,
                        source,
                        reporting.upper_time_bound,
                        ttl - relapse_period,
                        ttl,
                        reporting.is_target,
                        self.message_id_dict.get(source, None),
                    )

    # ---------------------------------------------------------------------------

    def filter_event(self, filter_rules, event, to_db=True):
        """
        Filter given event according to given list of filtering rules.

        :param list filter_rules: Filters to be used.
        :param mentat.idea.internal.Idea event: Event to be filtered.
        :param bool to_db: Save hit to db.
        :return: ``True`` in case any filter matched, ``False`` otherwise.
        :rtype: bool
        """
        for flt in filter_rules:
            try:
                filter_result = self.ransack_filter.eval(flt[1], event)
            except RansackError as e:
                self.logger.error(
                    "Filter '%s' failed evaluation on event with ID '%s'\n%s", flt[0].name, event.get_id(), str(e)
                )
                continue
            if filter_result:
                if to_db:
                    flt[0].hits += 1
                    flt[0].last_hit = datetime.datetime.utcnow()
                return flt[0].name
        return False

    # ---------------------------------------------------------------------------

    def _save_to_json_files(self, data, filename):
        """
        Helper method for saving given data into given JSON file. This method can
        be used for saving report data attachments to disk.

        :param dict data: Data to be serialized.
        :param str filename: Name of the target JSON file.
        :return: Paths to the created files.
        :rtype: tuple
        """
        dirpath = mentat.const.construct_report_dirpath(self.reports_dir, filename)
        filepath = os.path.join(dirpath, filename)

        while True:
            try:
                with open(filepath, "w", encoding="utf8") as jsonf:
                    json.dump(
                        data,
                        jsonf,
                        default=mentat.idea.internal.Idea.json_default,
                        sort_keys=True,
                        indent=4,
                    )
                break
            except FileNotFoundError:
                os.makedirs(dirpath)

        zipfilepath = f"{filepath}.zip"
        with zipfile.ZipFile(zipfilepath, mode="w") as zipf:
            zipf.write(filepath, compress_type=zipfile.ZIP_DEFLATED)

        return filepath, zipfilepath

    def _save_to_files(self, data, filename):
        """
        Helper method for saving given data into given file. This method can be
        used for saving copies of report messages to disk.

        :param dict data: Data to be serialized.
        :param str filename: Name of the target file.
        :return: Path to the created file.
        :rtype: str
        """
        dirpath = mentat.const.construct_report_dirpath(self.reports_dir, filename)
        filepath = os.path.join(dirpath, filename)

        while True:
            try:
                with open(filepath, "w", encoding="utf8") as imf:
                    imf.write(data)
                break
            except FileNotFoundError:
                os.makedirs(dirpath)

        zipfilepath = f"{filepath}.zip"
        with zipfile.ZipFile(zipfilepath, mode="w") as zipf:
            zipf.write(filepath, compress_type=zipfile.ZIP_DEFLATED)

        return filepath, zipfilepath

    def get_event_class(self, name):
        """
        Returns object of an event class with the name from input.
        """
        # Get event class name from whole class. (whole class = "{event_class}/{subclass}")
        if "/" in name:
            name = name.split("/")[0]
        return self.sqlservice.session.query(EventClassModel).filter(EventClassModel.name == name).one_or_none()

    def render_report(self, report, settings, template_vars=None, srcip=None):
        # Render report section.
        template = self.renderer.get_template(f"{settings.template}.{report.type}_v2.txt.j2")

        # Force locale to given value.
        self.set_locale(settings.locale)

        # Force timezone to given value.
        self.set_timezone(settings.timezone)

        return template.render(
            dt_c=datetime.datetime.utcnow(),
            report=report,
            structured_data=report.get_structured_data_as_dataclass(),
            source=srcip,
            settings=settings,
            text_width=REPORT_EMAIL_TEXT_WIDTH,
            additional_vars=template_vars,
            get_event_class=self.get_event_class,
        )

    def _mail_report(
        self,
        report,
        settings,
        groups,
        fallback_groups,
        result,
        template_vars,
        srcip=None,
        additional_headers=None,
    ):
        """
        Construct email report object and send it.
        """

        def get_message_id(label):
            return f"<{label}@{socket.getfqdn()}>"

        def get_relapsed_event_classes(data):
            if "relapsed" in data:
                return data["relapsed"].keys()
            return []

        def get_categories() -> list[str]:
            return list(report.statistics.get("categories", {}).keys())

        def get_classes() -> list[str]:
            return list(report.statistics.get("classes", {}).keys())

        additional_headers = additional_headers if additional_headers is not None else {}

        to, cc = get_recipients([self.groups_dict[name] for name in groups], report.severity)

        # Use fallback option if no email addresses are found for the given severity.
        if not to:
            to, cc = get_recipients([self.groups_dict[name] for name in fallback_groups], report.severity)
            to = to if to else self.global_fallback
            self.logger.info(
                "No email addresses found for the given severity, using fallback: %s",
                to,
            )

        # Set custom message id, which can be referenced later.
        message_id = get_message_id(report.label)

        # Common report email headers.
        report_msg_headers = {
            "to": to,
            "cc": cc,
            "report_id": report.label,
            "report_type": report.type,
            "report_severity": report.severity,
            "report_categories": get_categories(),
            "report_classes": get_classes(),
            "report_evcount": report.evcount_rep,
            "report_window": f"{report.dt_from.isoformat()}___{report.dt_to.isoformat()}",
            "report_testdata": report.flag_testdata,
            "message_id": message_id,
        } | additional_headers

        message = self.render_report(report, settings, template_vars, srcip)

        # Report email headers specific for 'summary' and 'target' reports.
        if report.type in [
            mentat.const.REPORT_TYPE_SUMMARY,
            mentat.const.REPORT_TYPE_TARGET,
        ]:
            subject = (
                REPORT_SUBJECT_SUMMARY if report.type == mentat.const.REPORT_TYPE_SUMMARY else REPORT_SUBJECT_TARGET
            )
            report_msg_headers["subject"] = self.translator.gettext(subject).format(
                report.label, self.translator.gettext(report.severity).title()
            )
        # Report email headers specific for 'extra' reports.
        else:
            report_msg_headers["subject"] = self.translator.gettext(REPORT_SUBJECT_EXTRA).format(
                report.label, self.translator.gettext(report.severity).title(), srcip
            )
            report_msg_headers["report_id_par"] = report.parent.label
            report_msg_headers["report_srcip"] = srcip
            event_classes = get_relapsed_event_classes(report.structured_data)
            for event_class in event_classes:
                key = str(event_class + "+++" + srcip)
                if key in self.message_id_dict["thresholds"]:
                    reference_report = self.message_id_dict["thresholds"][key]
                    # Save the report reference so it can be viewed later in GUI.
                    report.structured_data["relapsed"][event_class][srcip]["reference"] = reference_report
                    if "references" not in report_msg_headers:
                        report_msg_headers["references"] = []
                    # Add the report reference to references headers.
                    report_msg_headers["references"].append(get_message_id(reference_report))

            # Set flag so sqlalchemy knows to update this object.
            if "references" in report_msg_headers:
                flag_modified(report, "structured_data")

        report_msg_params = {"text_plain": message, "attachments": []}
        report_msg = self.mailer.email_send(ReportEmail, report_msg_headers, report_msg_params, settings.redirect)
        report.flag_mailed = True
        report.mail_to = ["to:" + str(x) for x in to] + ["cc:" + str(x) for x in cc]
        report.mail_dt = datetime.datetime.utcnow()
        result["mail_to"] = list(set(result.get("mail_to", []) + report_msg.get_destinations()))
