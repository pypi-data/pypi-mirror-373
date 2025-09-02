#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Library containing reporting utilities.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import pprint

import pytz
from sqlalchemy import null

import mentat.const
import mentat.datatype.internal
import mentat.idea.internal
from mentat.datatype.sqldb import FilterModel, GroupModel


class ReportingSettings:  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    Class for custom manipulations with group reporting settings.
    """

    def __init__(self, group, sql_storage, **kwargs):
        self.group_name = group.name
        self.filters = self._init_filters(group, sql_storage)
        self.networks = group.networks
        self.emails = self._init_emails(group.settings_rep)
        self.mode = self._init_mode(group.settings_rep.mode, **kwargs)
        self.template = self._init_template(**kwargs)
        self.locale = self._init_locale(group.settings_rep.locale, **kwargs)
        self.timezone = self._init_timezone(group.settings_rep.timezone, **kwargs)
        self.timing = self._init_timing(**kwargs)
        self.timing_cfg = self._init_timing_cfg(group.settings_rep)
        self.redirect = self._init_redirect(group.settings_rep.redirect, **kwargs)

    def __repr__(self):
        return (
            f"ReportingSettings("
            f"group_name={self.group_name};"
            f"filters={pprint.pformat(self.filters, compact=True)};"
            f"networks={pprint.pformat(self.networks, compact=True)};"
            f"emails={pprint.pformat(self.emails, compact=True)};"
            f"mode={pprint.pformat(self.mode, compact=True)};"
            f"template={pprint.pformat(self.template, compact=True)};"
            f"locale={pprint.pformat(self.locale, compact=True)};"
            f"timezone={pprint.pformat(self.timezone, compact=True)};"
            f"timing={pprint.pformat(self.timing, compact=True)};"
            f"timing_cfg={pprint.pformat(self.timing_cfg, compact=True, width=10000)};"
            f"redirect={pprint.pformat(self.redirect, compact=True)})"
        )

    @staticmethod
    def _init_filters(group, sql_storage):
        global_filters = sql_storage.session.query(FilterModel).filter(FilterModel.group == null()).all()
        return global_filters + group.filters

    @staticmethod
    def _init_emails(settings):
        return (
            settings.emails_info,
            settings.emails_low,
            settings.emails_medium,
            settings.emails_high,
            settings.emails_critical,
        )

    @staticmethod
    def _init_mode(group_value, **kwargs):
        if "force_mode" in kwargs and kwargs["force_mode"] is not None:
            if kwargs["force_mode"] not in mentat.const.REPORTING_MODES:
                raise ValueError("Invalid value '{:s}' for reporting mode.".format(kwargs["force_mode"]))
            return str(kwargs["force_mode"])
        if group_value is not None:
            return group_value
        return mentat.const.DFLT_REPORTING_MODE

    @staticmethod
    def _init_template(**kwargs):
        if "force_template" in kwargs and kwargs["force_template"] is not None:
            return str(kwargs["force_template"])
        return mentat.const.DFLT_REPORTING_TEMPLATE

    @staticmethod
    def _init_locale(group_value, **kwargs):
        if "force_locale" in kwargs and kwargs["force_locale"] is not None:
            return str(kwargs["force_locale"])
        if group_value is not None:
            return group_value
        if "default_locale" in kwargs and kwargs["default_locale"] is not None:
            return str(kwargs["default_locale"])
        return mentat.const.DFLT_REPORTING_LOCALE

    @staticmethod
    def _init_timezone(group_value, **kwargs):
        if "force_timezone" in kwargs and kwargs["force_timezone"] is not None:
            if kwargs["force_timezone"] not in pytz.common_timezones:
                raise ValueError(
                    "Invalid value '{}' for reporting timezone. Please use one of the values defined in pytz.common_timezones package.".format(
                        kwargs["force_timezone"]
                    )
                )
            return str(kwargs["force_timezone"])
        if group_value is not None:
            return group_value
        if "default_timezone" in kwargs and kwargs["default_timezone"] is not None:
            return str(kwargs["default_timezone"])
        return mentat.const.DFLT_REPORTING_TIMEZONE

    @staticmethod
    def _init_redirect(group_value, **kwargs):
        if "force_redirect" in kwargs and kwargs["force_redirect"] is not None:
            return bool(kwargs["force_redirect"])
        if group_value is not None:
            return group_value
        return mentat.const.DFLT_REPORTING_REDIRECT

    @staticmethod
    def _init_timing(**kwargs):
        if "force_timing" in kwargs and kwargs["force_timing"] is not None:
            if kwargs["force_timing"] not in mentat.const.REPORTING_TIMINGS:
                raise ValueError("Invalid value '{}' for reporting timing.".format(kwargs["force_timing"]))
            return str(kwargs["force_timing"])
        return mentat.const.DFLT_REPORTING_TIMING

    @staticmethod
    def _init_timing_cfg(settings_rep):
        return {
            mentat.const.EVENT_SEVERITY_INFO: {
                "per": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_INFO_PER]
                ),
                "thr": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_INFO_THR]
                ),
                "thr_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_INFO_THR]
                ),
                "rel": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_INFO_REL]
                ),
                "rel_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_INFO_REL]
                ),
            },
            mentat.const.EVENT_SEVERITY_LOW: {
                "per": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_PER]
                ),
                "thr": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_THR]
                ),
                "thr_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_LOW_THR]
                ),
                "rel": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_LOW_REL]
                ),
                "rel_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_LOW_REL]
                ),
            },
            mentat.const.EVENT_SEVERITY_MEDIUM: {
                "per": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_PER]
                ),
                "thr": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_THR]
                ),
                "thr_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_MEDIUM_THR]
                ),
                "rel": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_MEDIUM_REL]
                ),
                "rel_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_MEDIUM_REL]
                ),
            },
            mentat.const.EVENT_SEVERITY_HIGH: {
                "per": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_PER]
                ),
                "thr": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_THR]
                ),
                "thr_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_HIGH_THR]
                ),
                "rel": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_HIGH_REL]
                ),
                "rel_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_HIGH_REL]
                ),
            },
            mentat.const.EVENT_SEVERITY_CRITICAL: {
                "per": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_PER]
                ),
                "thr": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_THR]
                ),
                "thr_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_CRITICAL_THR]
                ),
                "rel": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_DEFAULT_CRITICAL_REL]
                ),
                "rel_target": datetime.timedelta(
                    seconds=mentat.const.REPORTING_INTERVALS[mentat.const.REPORTING_TIMING_TARGET_CRITICAL_REL]
                ),
            },
        }

    def setup_filters(self, parser, is_target):
        """
        Setup and return list of filters in format appropriate for direct filtering
        by :py:func:`mentat.reports.event.EventReporter.filter_events` function.

        :param ransack.parser.Parser parser: Parser object.
        :param bool is_target: If the reporting is target-based (or source-based if False).
                               Only target filters are applied for target-based reporting, and only
                               source (summary/extra) filters are applied for source-based reporting.
        :return: List of processed and compiled filters.
        :rtype: list
        """
        result = []
        for filter_obj in self.filters:
            if not filter_obj.enabled or not filter_obj.is_valid:
                continue
            # Check if the filter is filtering the particular type of reports.
            if filter_obj.source_based == is_target:
                continue
            flt = parser.parse(filter_obj.filter)
            result.append((filter_obj, flt))
        return result

    def setup_networks(self):
        """
        Setup and return list of network in format appropriate for populating the
        :py:class:`mentat.services.whois.WhoisModule`.

        :return: List of processed networks.
        :rtype: list
        """
        result = []
        for net in self.networks:
            result.append(
                mentat.datatype.internal.t_network_record({"network": net.network, "abuse_group": self.group_name})
            )
        return result


def get_recipients(groups: list[GroupModel], severity: str) -> tuple[list[str], list[str]]:
    """
    Determine email recipients for a report based on severity and group priority.

    For a given severity level, only email addresses matching that exact severity
    from the highest-priority group are added to the "To" list.

    If no such addresses are found for the requested severity, the function looks
    at lower severity levels (in descending order) only until it finds a group
    with addresses, and uses those for "To".

    Once "To" is set, the email addresses for lower severities are assigned in the "CC" field.

    All lower-priority groups' addresses for the same and lower severities
    are included in the "CC" field (without duplication).

    :param list[GroupModel] groups: List of GroupModel instances, ordered by priority (first is highest).
    :param str severity: Report severity level. Must be one of `mentat.const.REPORT_SEVERITIES`.
    :return: A tuple of two lists:
             - list of "To" recipients (highest priority group),
             - list of "CC" recipients (other groups without duplicates).
    :rtype: tuple[list[str], list[str]]
    :raises ValueError: If the provided severity is not in `REPORT_SEVERITIES`.
    """

    def get_emails(settings):
        return (
            settings.emails_info,
            settings.emails_low,
            settings.emails_medium,
            settings.emails_high,
            settings.emails_critical,
        )

    severities = list(mentat.const.REPORT_SEVERITIES)
    to: list[str] = []
    cc: list[str] = []
    for group in groups:
        i = severities.index(severity)
        emails = get_emails(group.settings_rep)
        while i >= 0:
            if emails[i]:
                if not to:
                    to = emails[i]
                else:
                    for email in emails[i]:
                        if email not in to and email not in cc:
                            cc.append(email)
            i -= 1

    return to, cc


class ThresholdingCache:
    """
    Base class for implementing event thresholding caches for periodical event
    reporting.
    """

    def event_is_thresholded(self, event, source, ttl, is_target):
        """
        Check, that given combination of event and source is thresholded within given TTL.

        :param mentat.idea.internal.Idea event: IDEA event to check.
        :param str source: Source to check.
        :param datetime.datetime ttl: TTL for the thresholding record.
        :param bool is_target: If the reporting is target-based (or source-based if False).
        :return: ``True`` in case the event is thresholded, ``False`` otherwise.
        :rtype: bool
        """
        cachekey = self._generate_cache_key(event, source, is_target)
        return self.check(cachekey, ttl)

    def set_threshold(
        self,
        event,
        source,
        thresholdtime,
        relapsetime,
        ttl,
        is_target,
        report_label=None,
    ):
        """
        Threshold given event with given TTL.

        :param mentat.idea.internal.Idea event: IDEA event to threshold.
        :param str source: Source address because of which to threshold the event.
        :param datetime.datetime thresholdtime: Threshold window start time.
        :param datetime.datetime relapsetime: Relapse window start time.
        :param datetime.datetime ttl: Record TTL.
        :param bool is_target: If the reporting is target-based (or source-based if False).
        :param str report_label: Label of the report in which source address was reported.
        """
        cachekey = self._generate_cache_key(event, source, is_target)
        self.set(cachekey, thresholdtime, relapsetime, ttl, report_label)

    def threshold_event(self, reporting_properties, event, source):
        """
        Threshold given event with given TTL.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param mentat.idea.internal.Idea event: IDEA event to threshold.
        :param str source: Source address because of which to threshold the event.
        """
        cachekey = self._generate_cache_key(event, source, reporting_properties.is_target)
        self.save(reporting_properties, event.get_id(), cachekey)

    # ---------------------------------------------------------------------------

    def check(self, key, ttl):
        """
        Check event thresholding cache for given key and TTL. This method always
        returns ``False``.

        :param str key: Thresholding cache key.
        :param datetime.datetime ttl: Cache record TTL.
        :return: ``True`` if given key was found with valid TTL,``False`` othrewise.
        :rtype: bool
        """
        raise NotImplementedError()

    def set(self, key, thresholdtime, relapsetime, ttl, report_label=None):
        """
        Set thresholding cache record with given key and TTL.

        :param str key: Thresholding cache key.
        :param datetime.datetime thresholdtime: Threshold window start time.
        :param datetime.datetime relapsetime: Relapse window start time.
        :param datetime.datetime ttl: Record TTL.
        :param str report_label: Label of the report in which source address was reported.
        """
        raise NotImplementedError()

    def save(self, reporting_properties, event_id, key_id):
        """
        Save event into registry of thresholded events.

        :param ReportingProperties reporting_properties: Properties of the current reporting.
        :param str event_id: Event ID.
        :param str key_id: Thresholding cache key.
        """
        raise NotImplementedError()

    def cleanup(self, ttl):
        """
        Cleanup records from thresholding cache with TTL older than given value.

        :param datetime.datetime ttl: Record TTL cleanup threshold.
        """
        raise NotImplementedError()

    # ---------------------------------------------------------------------------

    def _generate_cache_key(self, event, source, is_target):
        """
        Generate cache key for given event and source.

        :param mentat.idea.internal.Idea event: Event to process.
        :param str source: Source to process.
        :param bool is_target: If the reporting is target-based (or source-based if False).
        :return: Cache key as strings.
        :rtype: str
        """
        idea = mentat.idea.internal.Idea(event)
        event_class = idea.get_whole_target_class() if is_target else idea.get_whole_class()
        if not event_class:
            event_class = "/".join(idea.get_categories())
        return "+++".join((event_class, str(source)))

    def get_source_from_cache_key(self, key):
        """
        Return source from which was key generated.

        :param str key: Cache key.
        :return: Cached source.
        :rtype: str
        """
        return key.split("+++")[1] if key and len(key.split("+++")) > 1 else key


class NoThresholdingCache(ThresholdingCache):
    """
    Implementation of the :py:class:`mentat.reports.utils.ThresholdingCache` that
    does no thresholding at all. It can be used to disable the thresholding feature
    during reporting, for example for generating some kind of ad-hoc reports.
    """

    def check(self, key, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.check` method.
        """
        return False

    def set(self, key, thresholdtime, relapsetime, ttl, report_label=None):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.set` method.
        """
        return

    def save(self, reporting_properties, event_id, key_id):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.save` method.
        """
        return

    def cleanup(self, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.cleanup` method.
        """
        return {"thresholds": 0, "events": 0}


class SimpleMemoryThresholdingCache(ThresholdingCache):
    """
    Implementation of the :py:class:`mentat.reports.utils.ThresholdingCache` that
    performs thresholding within the memory structures.
    """

    def __init__(self):
        self.memcache = {}

    def check(self, key, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.check` method.
        """
        return bool(key in self.memcache)

    def set(self, key, thresholdtime, relapsetime, ttl, report_label=None):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.set` method.
        """
        self.memcache[key] = True

    def save(self, reporting_properties, event_id, key_id):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.save` method.
        """
        return

    def cleanup(self, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.cleanup` method.
        """
        result = {"thresholds": len(self.memcache), "events": 0}
        self.memcache = {}
        return result


class SingleSourceThresholdingCache(SimpleMemoryThresholdingCache):
    """
    Implementation of the :py:class:`mentat.reports.utils.ThresholdingCache` that
    performs thresholding within the memory structures.
    """

    def __init__(self, source):
        super().__init__()
        self.source = source

    def _generate_cache_key(self, event, source, is_target):
        """
        Generate cache key for given event and source.

        :param mentat.idea.internal.Idea event: Event to process.
        :param str source: Source to process.
        :param bool is_target: If the reporting is target-based (or source-based if False).
        :return: Cache key as strings.
        :rtype: str
        """
        return super()._generate_cache_key(event, self.source, is_target)


class StorageThresholdingCache(ThresholdingCache):
    """
    Implementation of the :py:class:`mentat.reports.utils.ThresholdingCache` that
    is using :py:class:`mentat.services.eventstorage` service for storing thresholding
    records.
    """

    def __init__(self, logger, eventservice):
        self.logger = logger
        self.eventservice = eventservice
        self.memcache_thresholded = {}
        self.memcache_set = {}

    def check(self, key, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.check` method.
        """
        if key not in self.memcache_thresholded:
            result = self.eventservice.threshold_check(key, ttl)
            self.memcache_thresholded[key] = bool(result)
        return self.memcache_thresholded[key]

    def set(self, key, thresholdtime, relapsetime, ttl, report_label=None):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.set` method.
        """
        if key not in self.memcache_set or not self.memcache_set[key]:
            try:
                self.eventservice.threshold_set(key, thresholdtime, relapsetime, ttl, report_label)
                self.logger.info(
                    "Updated thresholding cache with record - TTL=%s|RLP=%s|THR=%s|KEY=%s",
                    ttl.isoformat(),
                    relapsetime.isoformat(),
                    thresholdtime.isoformat(),
                    key,
                )
            except mentat.services.eventstorage.StorageIntegrityError:
                self.logger.info(
                    "Prolonged thresholding cache record - TTL=%s|RLP=%s|THR=%s|KEY=%s",
                    ttl.isoformat(),
                    relapsetime.isoformat(),
                    thresholdtime.isoformat(),
                    key,
                )
            self.memcache_thresholded[key] = True
            self.memcache_set[key] = True

    def save(self, reporting_properties, event_id, key_id):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.save` method.
        """
        record = "CT=%s|KEY=%s|EID=%s|GRP=%s|SEV=%s|istarget=%s|isshadow=%s"
        try:
            self.eventservice.threshold_save(
                event_id,
                key_id,
                reporting_properties.group.name,
                reporting_properties.severity,
                reporting_properties.upper_time_bound,
                reporting_properties.is_target,
                reporting_properties.is_shadow,
            )
            self.logger.info("Recorded thresholded event with record - %s", record)
        except mentat.services.eventstorage.StorageIntegrityError:
            self.logger.info("Event is already thresholded with record - %s", record)

    def cleanup(self, ttl):
        """
        *Interface implementation:* Implementation of :py:func:`mentat.reports.utils.ThresholdingCache.cleanup` method.
        """
        self.memcache_thresholded = {}
        self.memcache_set = {}

        count_tc = self.eventservice.thresholds_clean(ttl)
        self.logger.info(
            "Cleaned %d records from thresholding cache older than %s.",
            count_tc,
            ttl.isoformat(),
        )
        count_te = self.eventservice.thresholded_events_clean()
        self.logger.info(
            "Cleaned %d records from registry of thresholded events.",
            count_te,
        )
        return {"thresholds": count_tc, "events": count_te}
