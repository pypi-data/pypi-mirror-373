#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Library for calculating various statistics from given list of IDEA messages.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import bisect
import datetime
import math
from collections import OrderedDict
from collections.abc import Iterable, Iterator
from enum import Enum
from typing import NamedTuple, Optional, Self, cast

from ransack import get_values

from mentat.const import REPORT_TYPE_SUMMARY, REPORT_TYPE_TARGET
from mentat.reports.utils import (
    SimpleMemoryThresholdingCache,
    SingleSourceThresholdingCache,
)

KEY_UNKNOWN = "__unknown__"
KEY_NONE = "__none__"

#
# Literal constants for keywords of statistical categories.
#
ST_INTERNAL = "stats_internal"
ST_EXTERNAL = "stats_external"
ST_OVERALL = "stats_overall"

#
# Literal constants for keywords of calculated statistics.
#
ST_SKEY_SOURCES = "sources"
ST_SKEY_TARGETS = "targets"
ST_SKEY_IP4S = "ip4s"
ST_SKEY_IP6S = "ip6s"
ST_SKEY_ANALYZERS = "analyzers"
ST_SKEY_CATEGORIES = "categories"
ST_SKEY_CATEGSETS = "category_sets"
ST_SKEY_DETECTORS = "detectors"
ST_SKEY_DETECTORSWS = "detectorsws"
ST_SKEY_DETECTORTPS = "detector_types"
ST_SKEY_ABUSES = "abuses"
ST_SKEY_TGTABUSES = "target_abuses"
ST_SKEY_EMAILS = "emails"
ST_SKEY_ASNS = "asns"
ST_SKEY_COUNTRIES = "countries"
ST_SKEY_CLASSES = "classes"
ST_SKEY_TGTCLASSES = "target_classes"
ST_SKEY_SEVERITIES = "severities"
ST_SKEY_TGTSEVERITIES = "target_severities"
ST_SKEY_PORTS = "ports"
ST_SKEY_SRCPORTS = "source_ports"
ST_SKEY_TGTPORTS = "target_ports"
ST_SKEY_SRCTYPES = "source_types"
ST_SKEY_TGTTYPES = "target_types"
ST_SKEY_PROTOCOLS = "protocols"
ST_SKEY_LIST_IDS = "list_ids"
ST_SKEY_TLPS = "tlps"
ST_SKEY_CNT_ALERTS = "cnt_alerts"
ST_SKEY_CNT_EVENTS = "cnt_events"
ST_SKEY_CNT_EVTS_A = "cnt_events_all"
ST_SKEY_CNT_EVTS_F = "cnt_events_filtered"
ST_SKEY_CNT_EVTS_T = "cnt_events_thresholded"
ST_SKEY_CNT_EVTS_N = "cnt_events_new"
ST_SKEY_CNT_EVTS_R = "cnt_events_relapsed"
ST_SKEY_CNT_RECURR = "cnt_recurring"
ST_SKEY_CNT_UNIQUE = "cnt_unique"
ST_SKEY_CNT_REPORTS = "cnt_reports"
ST_SKEY_CNT_EMAILS = "cnt_emails"
ST_SKEY_CNT_REPS_S = "cnt_reports_summary"
ST_SKEY_CNT_REPS_E = "cnt_reports_extra"
ST_SKEY_CNT_REPS_T = "cnt_reports_target"
ST_SKEY_COUNT = "count"
ST_SKEY_DT_FROM = "dt_from"
ST_SKEY_DT_TO = "dt_to"
ST_SKEY_ST_FROM = "st_from"
ST_SKEY_ST_TO = "st_to"
ST_SKEY_TIMELINE = "timeline"
ST_SKEY_TLCFG = "timeline_cfg"
ST_SKEY_TOTALS = "totals"
ST_SKEY_TIMESCATTER = "timescatter"
ST_SKEY_DESCRIPTION = "description"
ST_SKEY_REST = "__REST__"

LIST_STAT_GROUPS = (
    ST_INTERNAL,
    ST_EXTERNAL,
    ST_OVERALL,
)
"""List of statistical groups. The statistics will be calculated separatelly for these."""


def get_list_aggregations(is_target):
    """
    Returns a list of statistical aggregations.
    """
    return (
        [ST_SKEY_SOURCES, ("Source.IP4", "Source.IP6"), KEY_UNKNOWN],
        [ST_SKEY_TARGETS, ("Target.IP4", "Target.IP6"), KEY_UNKNOWN],
        # [ST_SKEY_IP4S,      ('Source.IP4',),                                                KEY_UNKNOWN],
        # [ST_SKEY_IP6S,      ('Source.IP6',),                                                KEY_UNKNOWN],
        [ST_SKEY_ANALYZERS, "SW", KEY_UNKNOWN],
        [ST_SKEY_CATEGORIES, ("Category",), KEY_UNKNOWN],
        [ST_SKEY_DETECTORS, "Name", KEY_UNKNOWN],
        [ST_SKEY_ABUSES, (f"_Mentat.{'Target' if is_target else 'Resolved'}Abuses",), KEY_UNKNOWN],
        [ST_SKEY_ASNS, ("_Mentat.SourceResolvedASN",), KEY_UNKNOWN],
        [ST_SKEY_COUNTRIES, ("_Mentat.SourceResolvedCountry",), KEY_UNKNOWN],
        [ST_SKEY_CLASSES, (f"_Mentat.{'Target' if is_target else 'Event'}Class",), KEY_UNKNOWN],
        [ST_SKEY_SEVERITIES, (f"_Mentat.{'Target' if is_target else 'Event'}Severity",), KEY_UNKNOWN],
        [ST_SKEY_TLPS, ("TLP",), KEY_UNKNOWN],
    )


LIST_SKIP_SINGLEHOST = (
    ST_SKEY_SOURCES,
    ST_SKEY_ABUSES,
    ST_SKEY_ASNS,
    ST_SKEY_COUNTRIES,
)

TRUNCATION_WHITELIST = {
    ST_SKEY_ANALYZERS: True,
    ST_SKEY_CATEGORIES: True,
    ST_SKEY_CATEGSETS: True,
    ST_SKEY_DETECTORS: True,
    ST_SKEY_DETECTORSWS: True,
    ST_SKEY_DETECTORTPS: True,
    ST_SKEY_SRCTYPES: True,
    ST_SKEY_TGTTYPES: True,
    ST_SKEY_PROTOCOLS: True,
    ST_SKEY_ABUSES: True,
    ST_SKEY_COUNTRIES: True,
    ST_SKEY_CLASSES: True,
    ST_SKEY_SEVERITIES: True,
    ST_SKEY_TLPS: True,
}
"""Whitelist for truncating statistics."""

TRUNCATION_THRESHOLD = 100
"""Threshold for truncated statistics."""

TRUNCATION_WHITELIST_THRESHOLD = 1000
"""Threshold for whitelisted truncated statistics."""

LIST_CALCSTAT_KEYS = tuple(
    [x[0] for x in get_list_aggregations(False)]
    + [
        ST_SKEY_CATEGSETS,
        ST_SKEY_DETECTORSWS,
        ST_SKEY_DETECTORTPS,
        ST_SKEY_SRCTYPES,
        ST_SKEY_TGTTYPES,
        ST_SKEY_SRCPORTS,
        ST_SKEY_TGTPORTS,
        ST_SKEY_PROTOCOLS,
    ]
)
"""List of subkey names of all calculated statistics."""


LIST_OPTIMAL_STEPS = [
    datetime.timedelta(seconds=x)
    for x in (
        1,
        2,
        3,
        4,
        5,
        6,
        10,
        12,
        15,
        20,
        30,  # seconds
        1 * 60,
        2 * 60,
        3 * 60,
        4 * 60,
        5 * 60,
        6 * 60,
        10 * 60,
        12 * 60,
        15 * 60,
        20 * 60,
        30 * 60,  # minutes
        1 * 3600,
        2 * 3600,
        3 * 3600,
        4 * 3600,
        6 * 3600,
        8 * 3600,
        12 * 3600,  # hours
        1 * 24 * 3600,
        2 * 24 * 3600,
        3 * 24 * 3600,
        4 * 24 * 3600,
        5 * 24 * 3600,
        6 * 24 * 3600,
        7 * 24 * 3600,
        10 * 24 * 3600,
        14 * 24 * 3600,  # days
    )
]
"""List of optimal timeline steps. This list is populated with values, that round nicely in time calculations."""

StatType = dict[str, int | float]
StatisticsDataType = dict[str, int | float | StatType]
DataWideType = Iterable[
    tuple[datetime.datetime, StatisticsDataType]
]  # In reality List of Lists, but this makes typing easier
DataRowType = dict[str, datetime.datetime | int | float]
DataLongType = Iterable[DataRowType]


class TimeBounds(NamedTuple):
    """Named tuple for timeline bounds."""

    t_from: str
    t_to: str


class TimeBoundType(Enum):
    """Time bound type enumeration."""

    NONE = TimeBounds("t_from", "t_to")
    DETECTION_TIME = TimeBounds(ST_SKEY_DT_FROM, ST_SKEY_DT_TO)
    STORAGE_TIME = TimeBounds(ST_SKEY_ST_FROM, ST_SKEY_ST_TO)

    @classmethod
    def iter_bound_names(cls, include_none: bool = False) -> Iterator[str]:
        """
        Iterate over all bound names.
        e.g., ('dt_from', 'dt_to', 'st_from', 'st_to')
        """
        for e in cls:
            if include_none or e != cls.NONE:
                yield from e.value


# -------------------------------------------------------------------------------


def truncate_stats(stats, top_threshold=TRUNCATION_THRESHOLD, force=False):
    """
    Make statistics more brief. For each of the statistical aggregation subkeys
    generate toplist containing given number of items at most.

    :param dict stats: Structure containing statistics.
    :param int top_threshold: Toplist threshold size.
    :param bool force: Force the toplist threshold even to whitelisted keys.
    :return: Updated structure containing statistics.
    :rtype: dict
    """
    # If present, remove the list of event identifiers. This list can possibly
    # contain thousands of items or even more.
    if ST_SKEY_LIST_IDS in stats:
        del stats[ST_SKEY_LIST_IDS]

    # Create toplists for all statistical aggregation subkeys.
    if stats.get(ST_SKEY_CNT_ALERTS, 0) > 0 or stats.get(ST_SKEY_CNT_EVENTS, 0) > 0:
        for key in LIST_CALCSTAT_KEYS:
            if key in stats:
                stats = _make_toplist(stats, key, top_threshold, force)

    return stats


def truncate_stats_with_mask(stats, mask, top_threshold=TRUNCATION_THRESHOLD, force=False):
    """
    Make statistics more brief. For each of the statistical aggregation subkeys
    generate toplist containing at most given number of items, but in this case
    use given precalculated mask to decide which items should be hidden. The use
    case for this method is during calculation of timeline statistics. In that
    case the global toplists must be given to mask out the items in every time
    interval, otherwise every time interval might have different item toplist and
    it would not be possible to draw such a chart.

    :param dict stats: Structure containing single statistic category.
    :param dict mask: Global truncated statistics to serve as a mask.
    :param int top_threshold: Toplist threshold size.
    :param bool force: Force the toplist threshold even to whitelisted keys.
    :return: Updated structure containing statistics.
    :rtype: dict
    """
    # If present, remove the list of event identifiers. This list can possibly
    # contain thousands of items or even more.
    if ST_SKEY_LIST_IDS in stats:
        del stats[ST_SKEY_LIST_IDS]

    # Create masked toplists for all statistical aggregation subkeys.
    if stats.get(ST_SKEY_CNT_ALERTS, 0) > 0 or stats.get(ST_SKEY_CNT_EVENTS, 0) > 0:
        for key in LIST_CALCSTAT_KEYS:
            if key in stats:
                stats = _mask_toplist(stats, mask, key, top_threshold, force)

    return stats


def truncate_evaluations(stats, top_threshold=TRUNCATION_THRESHOLD, force=False):
    """
    Make all statistical groups more brief with :py:func:`truncate_stats`.

    :param dict stats: Structure containing statistics for all groups.
    :param int top_threshold: Toplist threshold size.
    :param bool force: Force the toplist threshold even to whitelisted keys.
    :return: Updated structure containing statistics.
    :rtype: dict
    """
    for key in LIST_STAT_GROUPS:
        if key in stats:
            stats[key] = truncate_stats(stats[key], top_threshold, force)
    return stats


# -------------------------------------------------------------------------------


def evaluate_events(events, is_target=False, stats=None):
    """
    Evaluate statistics for given list of IDEA events.

    :param list events: List of IDEA events to be evaluated.
    :param bool is_target: If the reporting is target-based (or source-based if False).
    :param dict stats: Optional data structure to which to append the calculated statistics.
    :return: Structure containing calculated event statistics.
    :rtype: dict
    """
    if stats is None:
        stats = {}

    stats.setdefault(ST_SKEY_CNT_EVENTS, 0)
    stats.setdefault(ST_SKEY_CNT_RECURR, 0)
    stats[ST_SKEY_CNT_ALERTS] = len(events)

    # Do not calculate anything for empty event list.
    if not events:
        return stats

    # Prepare structure for storing IDEA event identifiers.
    if ST_SKEY_LIST_IDS not in stats:
        stats[ST_SKEY_LIST_IDS] = []

    for event in events:
        # Remember the event ID.
        stats[ST_SKEY_LIST_IDS].append(event["ID"])

        # Include event into global statistics.
        _include_event_to_stats(stats, event, is_target)

    return _calculate_secondary_stats(stats)


def evaluate_timeline_events(
    events,
    t_from,
    t_to,
    max_count,
    timezone=None,
    stats=None,
    time_type=TimeBoundType.DETECTION_TIME,
):
    """
    Evaluate statistics for given list of IDEA events and produce statistical
    record for timeline visualisations.

    :param list events: List of IDEA events to be evaluated.
    :param datetime.datetime dt_from: Lower timeline boundary.
    :param datetime.datetime dt_to: Upper timeline boundary.
    :param int max_count: Maximal number of items for generating toplists.
    :param dict stats: Data structure to which to append calculated statistics.
    :return: Structure containing evaluated event timeline statistics.
    :rtype: dict
    """
    if stats is None:
        stats = {}

    stats.setdefault(ST_SKEY_CNT_EVENTS, 0)
    stats.setdefault(ST_SKEY_CNT_RECURR, 0)
    stats[ST_SKEY_CNT_ALERTS] = len(events)

    # Do not calculate anything for empty event list.
    if not events:
        return stats

    # Prepare structure for storing IDEA event timeline statistics.
    if ST_SKEY_TIMELINE not in stats:
        stats[ST_SKEY_TLCFG] = timeline_cfg = TimelineCFG.get_optimized(
            t_from, t_to, max_count, user_timezone=timezone, time_type=time_type
        )
        stats[ST_SKEY_TIMELINE] = _init_timeline(timeline_cfg)

    # Prepare event thresholding cache for detection of recurring events.
    tcache = SimpleMemoryThresholdingCache()

    # Precalculate list of timeline keys for further bisection search.
    tl_keys = [x[0] for x in stats[ST_SKEY_TIMELINE]]

    for event in events:
        # Detect recurring events.
        recurring = tcache.event_is_thresholded(event, None, None, False)
        tcache.set_threshold(event, None, None, None, None, False)

        # Include event into global statistics.
        _include_event_to_stats(stats, event, recurring)

        # Include event into appropriate timeline window.
        event_dt = get_values(event, "DetectTime")[0]
        tl_key_idx = bisect.bisect_left(tl_keys, event_dt) - 1
        if tl_key_idx < 0:
            raise ValueError(f"Event does not fit into timeline with detect time {event_dt!s}")
        _include_event_to_stats(stats[ST_SKEY_TIMELINE][tl_key_idx][1], event, recurring)

    # Calculate secondary statistics and truncate result to toplist of given size.
    stats = _calculate_secondary_stats(stats)
    stats = truncate_stats(stats)

    # Calculate secondary statistics and mask the result to toplist of given size
    # for all timeline time windows.
    for tl_stat in stats[ST_SKEY_TIMELINE]:
        tl_stat[1] = truncate_stats_with_mask(tl_stat[1], stats)

    return stats


def evaluate_singlehost_events(host, events, dt_from, dt_to, max_count, timezone=None, stats=None):
    """
    Evaluate statistics for given list of IDEA events and produce statistical
    record for single host visualisations.

    :param str source: Event host.
    :param list events: List of IDEA events to be evaluated.
    :param datetime.datetime dt_from: Lower timeline boundary.
    :param datetime.datetime dt_to: Upper timeline boundary.
    :param int max_count: Maximal number of items for generating toplists.
    :param dict stats: Data structure to which to append calculated statistics.
    :return: Structure containing evaluated event timeline statistics.
    :rtype: dict
    """
    if stats is None:
        stats = {}

    stats.setdefault(ST_SKEY_CNT_EVENTS, 0)
    stats.setdefault(ST_SKEY_CNT_RECURR, 0)
    stats[ST_SKEY_CNT_ALERTS] = len(events)

    # Do not calculate anything for empty event list.
    if not events:
        return stats

    # Prepare structure for storing IDEA event timeline statistics.
    if ST_SKEY_TIMELINE not in stats:
        stats[ST_SKEY_TLCFG] = timeline_cfg = TimelineCFG.get_optimized(
            dt_from,
            dt_to,
            max_count,
            user_timezone=timezone,
            time_type=TimeBoundType.DETECTION_TIME,
        )
        stats[ST_SKEY_TIMELINE] = _init_timeline(timeline_cfg)

    # Prepare event thresholding cache for detection of recurring events.
    tcache = SingleSourceThresholdingCache(host)

    # Precalculate list of timeline keys for further bisection search.
    tl_keys = [x[0] for x in stats[ST_SKEY_TIMELINE]]

    for event in events:
        # Detect recurring events.
        recurring = tcache.event_is_thresholded(event, None, None, False)
        tcache.set_threshold(event, None, None, None, None, False)

        # Include event into global statistics.
        _include_event_to_stats(stats, event, recurring, LIST_SKIP_SINGLEHOST)

        # Include event into appropriate timeline window.
        event_dt = get_values(event, "DetectTime")[0]
        tl_key_idx = bisect.bisect_left(tl_keys, event_dt) - 1
        if tl_key_idx < 0:
            raise ValueError(f"Event does not fit into timeline with detect time {event_dt!s}")
        _include_event_to_stats(
            stats[ST_SKEY_TIMELINE][tl_key_idx][1],
            event,
            recurring,
            LIST_SKIP_SINGLEHOST,
        )

    # Calculate secondary statistics and truncate result to toplist of given size.
    stats = _calculate_secondary_stats(stats)
    stats = truncate_stats(stats)

    # Calculate secondary statistics and mask the result to toplist of given size
    # for all timeline time windows.
    for tl_stat in stats[ST_SKEY_TIMELINE]:
        tl_stat[1] = truncate_stats_with_mask(tl_stat[1], stats)

    return stats


def aggregate_stats_reports(report_list, t_from, t_to, result=None):
    """
    Aggregate multiple reporting statistical records.

    :param list report_list: List of report objects as retrieved from database.
    :param datetime.datetime dt_from: Lower timeline boundary.
    :param datetime.datetime dt_to: Upper timeline boundary.
    :param dict result: Optional data structure for storing the result.
    :return: Single aggregated statistical record.
    :rtype: dict
    """
    if result is None:
        result = {}

    if not report_list:
        return result

    # Prepare structure for storing report timeline statistics.
    if ST_SKEY_TIMELINE not in result:
        result[ST_SKEY_TLCFG] = timeline_cfg = TimelineCFG.get_daily(t_from, t_to, time_type=TimeBoundType.NONE)
        result[ST_SKEY_TIMELINE] = _init_timeline(timeline_cfg)

    # Prepare structure for storing report time scatter statistics.
    if ST_SKEY_TIMESCATTER not in result:
        result[ST_SKEY_TIMESCATTER] = _init_time_scatter()

    # Precalculate list of timeline keys for further bisection search.
    tl_keys = [x[0] for x in result[ST_SKEY_TIMELINE]]

    # Set the default count of report types to 0. Fixes issue #7627.
    for report_type_key in (ST_SKEY_CNT_REPS_S, ST_SKEY_CNT_REPS_E, ST_SKEY_CNT_REPS_T):
        if report_type_key not in result:
            result[report_type_key] = 0

    for report in report_list:
        # Do not include shadow reports into statistics.
        if report.flag_shadow:
            continue

        report_ct = report.createtime

        # Include report into global statistics.
        _include_report_to_stats(result, report)

        # Include report into appropriate timeline window.
        tl_key_idx = bisect.bisect_left(tl_keys, report_ct) - 1
        if tl_key_idx < 0:
            raise ValueError(f"Report does not fit into timeline with create time {report_ct!s}")
        _include_report_to_stats(result[ST_SKEY_TIMELINE][tl_key_idx][1], report)

        # Include report into appropriate time scatter window.
        _include_report_to_stats(result[ST_SKEY_TIMESCATTER][report_ct.weekday()][report_ct.hour], report)

    # Calculate secondary statistics and truncate result to toplist of given size.
    result = _calculate_secondary_stats(result)
    result = truncate_stats(result)

    # Mask the result to toplist of given size for all timeline windows.
    for tl_stat in result[ST_SKEY_TIMELINE]:
        tl_stat[1] = truncate_stats_with_mask(tl_stat[1], result)

    # Mask the result to toplist of given size for all time scatter windows.
    for ts_stat in result[ST_SKEY_TIMESCATTER]:
        ts_stat[:] = [truncate_stats_with_mask(x, result) for x in ts_stat]

    return result


def aggregate_stats_timeline(aggr_name, aggr_data, result=None):
    if result is None:
        result = {}

    result.setdefault(ST_SKEY_TIMELINE, {})[aggr_name] = aggr_data
    result.setdefault(ST_SKEY_TOTALS, {})[aggr_name] = aggr_data[-2].count
    result[ST_SKEY_CNT_EVENTS] = aggr_data[-1].count
    statistics = result.setdefault(aggr_name, OrderedDict())

    stats = []
    for n, res in enumerate(reversed(aggr_data)):
        if not hasattr(res, "set") or (res.bucket is not None):
            break
        if res.set is None and n < 2:
            continue  # skip the total event and total counts
        stats.append(res)

    for res in reversed(stats):
        statistics[str(res.set) or KEY_UNKNOWN] = res.count

    return result


# -------------------------------------------------------------------------------


def group_events(events):
    """
    Group events according to the presence of the ``_Mentat.ResolvedAbuses`` key.
    Each event will be added to group ``overall`` and then to either ``internal``,
    or ``external`` based on the presence of the key mentioned above.

    :param list events: List of IDEA events to be grouped.
    :return: Structure containing event groups ``stats_overall``, ``stats_internal`` and ``stats_external``.
    :rtype: dict
    """
    result = {ST_OVERALL: [], ST_INTERNAL: [], ST_EXTERNAL: []}
    for msg in events:
        result[ST_OVERALL].append(msg)
        values = get_values(msg, "_Mentat.ResolvedAbuses")
        if values:
            result[ST_INTERNAL].append(msg)
        else:
            result[ST_EXTERNAL].append(msg)
    return result


def evaluate_event_groups(events, stats=None):
    """
    Evaluate full statistics for given list of IDEA events. Events will be
    grouped using :py:func:`group_events` first and the statistics will be
    evaluated separatelly for each of message groups ``stats_overall``,
    ``stats_internal`` and ``external``.

    :param list events: List of IDEA events to be evaluated.
    :param dict stats: Optional dictionary structure to populate with statistics.
    :return: Structure containing evaluated event statistics.
    :rtype: dict
    """
    if stats is None:
        stats = {}
    stats[ST_SKEY_COUNT] = len(events)

    msg_groups = group_events(events)

    for grp_key in LIST_STAT_GROUPS:
        stats[grp_key] = evaluate_events(msg_groups.get(grp_key, []))
    return stats


def aggregate_stat_groups(stats_list, result=None):
    """
    Aggregate multiple full statistical records produced by the
    :py:func:`mentat.stats.idea.evaluate_event_groups` function into single statistical
    record.

    :param list stats_list: List of full statistical records to be aggregated.
    :return: Single statistical record structure.
    :rtype: dict
    """
    if result is None:
        result = {}
    result[ST_SKEY_COUNT] = 0

    for stat in stats_list:
        result[ST_SKEY_COUNT] += stat.count

        if ST_SKEY_DT_FROM in result:
            result[ST_SKEY_DT_FROM] = min(result[ST_SKEY_DT_FROM], stat.dt_from)
        else:
            result[ST_SKEY_DT_FROM] = stat.dt_from
        if ST_SKEY_DT_TO in result:
            result[ST_SKEY_DT_TO] = max(result[ST_SKEY_DT_TO], stat.dt_to)
        else:
            result[ST_SKEY_DT_TO] = stat.dt_to

        if not stat.count:
            continue

        for grp_key in LIST_STAT_GROUPS:
            result[grp_key] = _merge_stats(getattr(stat, grp_key), result.setdefault(grp_key, {}))

    for grp_key in LIST_STAT_GROUPS:
        result[grp_key] = _calculate_secondary_stats(result.setdefault(grp_key, {}))

    return result


def aggregate_timeline_groups(stats_list, timeline_cfg, result=None):
    """
    Aggregate multiple full statistical records produced by the
    :py:func:`mentat.stats.idea.evaluate_event_groups` function and later retrieved
    from database as :py:class:`mentat.datatype.sqldb.EventStatisticsModel` into
    single statistical record. Given requested timeline time interval boundaries
    will be adjusted as necessary to provide best result.

    :param list stats_list: List of full statistical records to be aggregated.
    :param dict timeline_cfg: Timeline configuration
    :param dict result: Optional dictionary structure to contain the result.
    :return: Single statistical record structure.
    :rtype: dict
    """
    if result is None:
        result = {}
    result[ST_SKEY_COUNT] = 0

    # Do not calculate anything for empty statistical list.
    if not stats_list:
        return result

    # Calculate some overall dataset statistics.
    result[ST_SKEY_COUNT] = sum(x.count for x in stats_list)
    result[ST_SKEY_DT_FROM] = min(x.dt_from for x in stats_list)
    result[ST_SKEY_DT_TO] = max(x.dt_to for x in stats_list)

    # Process each statistical group separatelly.
    for grp_key in LIST_STAT_GROUPS:
        tmpres = result.setdefault(grp_key, {})

        # Prepare data structure for storing timeline statistics.
        if ST_SKEY_TIMELINE not in result:
            tmpres[ST_SKEY_TIMELINE] = _init_timeline(timeline_cfg)
            result[ST_SKEY_TLCFG] = timeline_cfg

        # Precalculate list of timeline keys for subsequent bisection search.
        tl_keys = [x[0] for x in tmpres[ST_SKEY_TIMELINE]]

        for stat in stats_list:
            # Merge this statistical record with overall result.
            _merge_stats(getattr(stat, grp_key), tmpres)

            # Merge this statistical record into appropriate timeline window.
            stat_dt = stat.dt_from
            tl_key_idx = bisect.bisect_right(tl_keys, stat_dt) - 1
            if tl_key_idx < 0:
                raise ValueError(
                    f"Statistical record with start time {stat_dt!s} does not fit into timeline with start time {tl_keys[0]!s} ({tl_key_idx})"
                )
            _merge_stats(getattr(stat, grp_key), tmpres[ST_SKEY_TIMELINE][tl_key_idx][1])

        # Calculate secondary statistics and truncate result to toplist of given size.
        result[grp_key] = _calculate_secondary_stats(result[grp_key])
        result[grp_key] = truncate_stats(result[grp_key])

        # Mask the result to toplist of given size for all timeline time windows.
        for tl_stat in tmpres[ST_SKEY_TIMELINE]:
            tl_stat[1] = truncate_stats_with_mask(tl_stat[1], result[grp_key])

    return result


# -------------------------------------------------------------------------------


def _counter_inc(stats, stat, key, increment=1):
    """
    Helper for incrementing given statistical parameter within given statistical
    bundle.

    :param dict stats: Structure containing all statistics.
    :param str stat: Name of the statistical category.
    :param str key: Name of the statistical key.
    :param int increment: Counter increment.
    :return: Updated structure containing statistics.
    :rtype: dict
    """

    # I have considered using setdefault() method, but the performance is worse
    # in comparison with using if (measured with cProfile module).
    if stat not in stats:
        stats[stat] = {}
    stats[stat][str(key)] = stats[stat].get(str(key), 0) + increment
    return stats


def _counter_inc_all(stats, stat, key_list, increment=1):
    """
    Helper for incrementing multiple statistical parameters within given statistical
    bundle.

    :param dict stats: Structure containing all statistics.
    :param str stat: Name of the statistic category.
    :param str key_list: List of the names of the statistical keys.
    :param int increment: Counter increment.
    :return: Updated structure containing statistics.
    :rtype: dict
    """
    if key_list:
        for key in key_list:
            _counter_inc(stats, stat, key, increment)
    return stats


def _counter_inc_one(stats, stat, increment=1):
    """
    Helper for incrementing given statistical parameter within given statistical
    bundle.

    :param dict stats: Structure containing all statistics.
    :param str stat: Name of the statistical category.
    :param str key: Name of the statistical key.
    :param int increment: Counter increment.
    :return: Updated structure containing statistics.
    :rtype: dict
    """

    # I have considered using setdefault() method, but the performance is worse
    # in comparison with using if (measured with cProfile module).
    if stat not in stats:
        stats[stat] = 0
    stats[stat] += increment
    return stats


def _include_event_to_stats(stats, event, is_target=False, recurring=False, skip=None):
    """
    Include given IDEA event into given statistical record.
    """
    stats[ST_SKEY_CNT_EVENTS] = stats.get(ST_SKEY_CNT_EVENTS, 0) + 1

    # Mark recurring events.
    if recurring:
        stats[ST_SKEY_CNT_RECURR] = stats.get(ST_SKEY_CNT_RECURR, 0) + 1

    # Evaluate event according to given list of aggregation rules.
    reg = {}
    for rule in get_list_aggregations(is_target):
        if skip and rule[0] in skip:
            continue

        # Special case for analyzers and detectors. Pynspect, the library used in the past,
        # allowed specifying the last element of the list-like like object using [#]. Ransack,
        # the new library, doesn't have this functionality, so getting the last element in the
        # list-like object must be handled differently.
        if rule[0] in (ST_SKEY_ANALYZERS, ST_SKEY_DETECTORS):
            node = get_values(event, "Node")[-1]
            values = get_values(node, rule[1])
        else:
            values = []
            for jpath in rule[1]:
                values = values + get_values(event, jpath)
        reg[rule[0]] = values

        if not values:
            _counter_inc(stats, rule[0], rule[2])
            continue

        for val in values:
            _counter_inc(stats, rule[0], val)

    # Calculate additional statistics based on the values of existing aggregation
    # rules.
    if reg.get(ST_SKEY_CATEGORIES):
        key = "/".join(reg[ST_SKEY_CATEGORIES])
        _counter_inc(stats, ST_SKEY_CATEGSETS, key)

    if ST_SKEY_DETECTORS in reg and reg[ST_SKEY_DETECTORS] and ST_SKEY_ANALYZERS in reg and reg[ST_SKEY_ANALYZERS]:
        for det in reg[ST_SKEY_DETECTORS]:
            for anl in reg[ST_SKEY_ANALYZERS]:
                key = f"{det}/{anl}"
                _counter_inc(stats, ST_SKEY_DETECTORSWS, key)
    elif reg.get(ST_SKEY_DETECTORS):
        for det in reg[ST_SKEY_DETECTORS]:
            key = det
            _counter_inc(stats, ST_SKEY_DETECTORSWS, key)


def _merge_stats(stats, result=None):
    """
    Merge given statistical record into given result record.

    :param dict stats: Statistical record to be merged.
    :param dict result: Optional data structure for merged result.
    :return: Structure containing merged event statistics.
    :rtype: dict
    """
    if result is None:
        result = {}

    result[ST_SKEY_CNT_ALERTS] = result.get(ST_SKEY_CNT_ALERTS, 0) + stats.get(ST_SKEY_CNT_ALERTS, 0)
    result[ST_SKEY_CNT_EVENTS] = result[ST_SKEY_CNT_ALERTS]

    for key in LIST_CALCSTAT_KEYS:
        if key in stats:
            for subkey, subval in stats[key].items():
                _counter_inc(result, key, subkey, subval)

    return result


def _include_report_to_stats(stats, report):
    """
    Merge given report statistical record into given result record.

    :param dict stats: Data structure for merged result.
    :param dict stats: Report statistical record to be merged.
    :return: Structure containing merged event statistics.
    :rtype: dict
    """
    stats[ST_SKEY_CNT_REPORTS] = stats.get(ST_SKEY_CNT_REPORTS, 0) + 1
    stats[ST_SKEY_CNT_EMAILS] = stats.get(ST_SKEY_CNT_EMAILS, 0) + len(report.mail_to or [])

    # Include the 'summary' report into the overall statistics in full.
    if report.type in [REPORT_TYPE_SUMMARY, REPORT_TYPE_TARGET]:
        if report.type == REPORT_TYPE_SUMMARY:
            stats[ST_SKEY_CNT_REPS_S] = stats.get(ST_SKEY_CNT_REPS_S, 0) + 1
        elif report.type == REPORT_TYPE_TARGET:
            stats[ST_SKEY_CNT_REPS_T] = stats.get(ST_SKEY_CNT_REPS_T, 0) + 1
        stats[ST_SKEY_CNT_REPS_S] = stats.get(ST_SKEY_CNT_REPS_S, 0) + 1
        stats[ST_SKEY_CNT_EVENTS] = stats.get(ST_SKEY_CNT_EVENTS, 0) + report.evcount_rep  # Number of reported events.
        stats[ST_SKEY_CNT_EVTS_A] = (
            stats.get(ST_SKEY_CNT_EVTS_A, 0) + report.evcount_all
        )  # Total number of all matched events.
        stats[ST_SKEY_CNT_EVTS_F] = (
            stats.get(ST_SKEY_CNT_EVTS_F, 0) + report.evcount_flt_blk
        )  # Number of filtered out events.
        stats[ST_SKEY_CNT_EVTS_T] = (
            stats.get(ST_SKEY_CNT_EVTS_T, 0) + report.evcount_thr_blk
        )  # Number of thresholded out events.
        stats[ST_SKEY_CNT_EVTS_N] = stats.get(ST_SKEY_CNT_EVTS_N, 0) + report.evcount_new  # Number of new events.
        stats[ST_SKEY_CNT_EVTS_R] = stats.get(ST_SKEY_CNT_EVTS_R, 0) + report.evcount_rlp  # Number of relapsed events.

        stats[ST_SKEY_DT_FROM] = min(report.dt_from, stats.get(ST_SKEY_DT_FROM, report.dt_from))
        stats[ST_SKEY_DT_TO] = max(report.dt_to, stats.get(ST_SKEY_DT_TO, report.dt_to))

        for key in LIST_CALCSTAT_KEYS:
            if key in report.statistics and key not in (ST_SKEY_ABUSES,):
                for subkey, subval in report.statistics[key].items():
                    _counter_inc(stats, key, subkey, subval)

        _counter_inc_all(stats, ST_SKEY_EMAILS, report.mail_to)

        # This fixes the bug with missing part of the timeline chart where some
        # data was not yet being generated.
        for group in report.groups:
            _counter_inc(stats, ST_SKEY_ABUSES, group.name, report.evcount_all)

    # Include the 'extra' report into the overall statistic
    else:
        _counter_inc_all(stats, ST_SKEY_EMAILS, report.mail_to)
        stats[ST_SKEY_CNT_REPS_E] = stats.get(ST_SKEY_CNT_REPS_E, 0) + 1
    return stats


def _calculate_secondary_stats(stats):
    """
    Calculate common secondary statistics.

    :param dict stats: Structure containing single statistic category.
    :return: Updated structure containing statistics.
    :rtype: dict
    """
    # Calculate unique and recurring events.
    if ST_SKEY_CNT_EVENTS in stats:
        if ST_SKEY_CNT_RECURR in stats:
            stats[ST_SKEY_CNT_UNIQUE] = stats[ST_SKEY_CNT_EVENTS] - stats[ST_SKEY_CNT_RECURR]
        else:
            stats[ST_SKEY_CNT_UNIQUE] = stats[ST_SKEY_CNT_EVENTS]
            stats[ST_SKEY_CNT_RECURR] = 0

    return stats


def _make_toplist(stats, dict_key, top_threshold, force=False):
    """
    Produce only toplist of given statistical keys.

    :param dict stats: Calculated statistics.
    :param str dict_key: Name of the dictionary key within statistics containing values.
    :param int top_threshold: Number of desired items in toplist.
    :param bool force: Force the toplist threshold even to whitelisted keys.
    :return: Updated statistics structure.
    :rtype: dict
    """
    if dict_key in TRUNCATION_WHITELIST and not force:
        top_threshold = TRUNCATION_WHITELIST_THRESHOLD

    # Convert threshold to list index.
    top_threshold -= 1

    # Store current value of __REST__ subkey to temporary variable.
    rest = None
    if ST_SKEY_REST in stats[dict_key]:
        rest = stats[dict_key][ST_SKEY_REST]
        del stats[dict_key][ST_SKEY_REST]

    # Produce list of dictionary keys sorted in reverse order by their values.
    sorted_key_list = sorted(sorted(stats[dict_key].keys()), key=lambda x: stats[dict_key][x], reverse=True)
    sorted_key_list_keep = sorted_key_list[:top_threshold]
    sorted_key_list_throw = sorted_key_list[top_threshold:]

    # Create truncated result into temporary data structure.
    tmp = {}
    tmp = {key: stats[dict_key][key] for key in sorted_key_list_keep}

    # Calculate and store the total for what was omitted into the __REST__ subkey.
    if sorted_key_list_throw:
        tmp[ST_SKEY_REST] = sum(stats[dict_key][key] for key in sorted_key_list_throw)

    # Add previous value of the __REST__ subkey.
    if rest:
        tmp[ST_SKEY_REST] = tmp.get(ST_SKEY_REST, 0) + rest

    # Put everything back into original statistics.
    stats[dict_key] = tmp

    return stats


def _mask_toplist(stats, mask, dict_key, top_threshold, force=False):
    """
    Produce only toplist of given statistical keys. Use global statistics as mask
    to determine which items to hide.

    :param dict stats: Calculated statistics.
    :param dict mask: Calculated overall statistics for masking.
    :param str dict_key: Name of the dictionary key within statistics containing values.
    :param int top_threshold: Number of desired items in toplist.
    :param bool force: Force the toplist threshold even to whitelisted keys.
    :return: Updated statistics structure.
    :rtype: dict
    """
    if dict_key in TRUNCATION_WHITELIST and not force:
        top_threshold = TRUNCATION_WHITELIST_THRESHOLD

    # Convert threshold to list index.
    top_threshold -= 1

    # Store current value of __REST__ subkey to temporary variable.
    rest = None
    if ST_SKEY_REST in stats[dict_key]:
        rest = stats[dict_key][ST_SKEY_REST]
        del stats[dict_key][ST_SKEY_REST]

    # Produce list of desired dictionary keys by calculating list intersection
    # with given mask.
    wanted_keys = mask[dict_key].keys()
    stat_key_list = [x for x in wanted_keys if x in stats[dict_key]]
    stat_key_list_keep = stat_key_list[:top_threshold]
    stat_key_list_throw = [x for x in stats[dict_key] if x not in stat_key_list_keep]

    # Create truncated result into temporary data structure.
    tmp = {}
    tmp = {key: stats[dict_key][key] for key in stat_key_list_keep}

    # Calculate and store the total for what was omitted.
    if stat_key_list_throw:
        tmp[ST_SKEY_REST] = sum(stats[dict_key][key] for key in stat_key_list_throw)

    # Add previous value of the __REST__ subkey.
    if rest:
        tmp[ST_SKEY_REST] = tmp.get(ST_SKEY_REST, 0) + rest

    # Put everything back into original statistics.
    stats[dict_key] = tmp

    return stats


def _init_time_scatter():
    """
    Init structure for time scatter chart dataset.
    """
    return [[{} for y in range(24)] for x in range(7)]


def _init_timeline(timeline_cfg: "TimelineCFG") -> DataWideType:
    """
    Init structure for timeline chart dataset.
    """
    return [cast(tuple[datetime.datetime, StatisticsDataType], [s, {}]) for s in timeline_cfg.iter_buckets()]


class TimelineCFG:
    """Timeline configuration."""

    t_from: datetime.datetime
    """Start of timeline (inclusive)"""

    t_to: datetime.datetime
    """End of timeline (exclusive)"""

    step: datetime.timedelta
    """The size of buckets"""

    count: int
    """The number of steps"""

    first_step: datetime.datetime
    """The first step larger or equal to `t_from` to which buckets are aligned to"""

    time_type: TimeBoundType
    """The type of timeline configuration (default DETECTION_TIME)"""

    def __init__(
        self,
        t_from: datetime.datetime,
        t_to: datetime.datetime,
        step: datetime.timedelta,
        count: Optional[int] = None,
        first_step: Optional[datetime.datetime] = None,
        time_type: TimeBoundType = TimeBoundType.DETECTION_TIME,
    ) -> None:
        self.t_from = t_from
        self.t_to = t_to
        self.step = step
        self.count = count or self._get_step_count(t_from, t_to, step, first_step or t_from)
        self.first_step = first_step or t_from
        self.time_type = time_type

    def to_dict(self) -> dict[str, datetime.datetime | datetime.timedelta | int]:
        return {
            self.time_type.value.t_from: self.t_from,
            self.time_type.value.t_to: self.t_to,
            "step": self.step,
            "count": self.count,
            "first_step": self.first_step,
        }

    def iter_buckets(self) -> Iterator[datetime.datetime]:
        yield self.t_from
        count = self.count - 1

        if self.first_step > self.t_from:
            yield self.first_step
            count -= 1

        current_bucket = self.first_step
        for _ in range(count):
            current_bucket += self.step
            yield current_bucket

    @staticmethod
    def _get_step_count(
        t_from: datetime.datetime,
        t_to: datetime.datetime,
        step: datetime.timedelta,
        first_step: datetime.datetime,
    ) -> int:
        cnt = math.ceil((t_to - first_step) / step)
        if first_step > t_from:
            cnt += 1
        return cnt

    @staticmethod
    def _round_datetime_up(
        datetime_: datetime.datetime,
        round_to: datetime.timedelta,
        timezone: Optional[datetime.tzinfo] = None,
    ) -> datetime.datetime:
        if timezone is None or not hasattr(timezone, "localize"):
            epoch = datetime.datetime(1970, 1, 1, tzinfo=timezone or datetime.UTC)
        else:
            epoch = timezone.localize(datetime.datetime(1970, 1, 1))

        mod = (datetime_.replace(tzinfo=datetime.UTC) - epoch) % round_to

        if not mod:
            return datetime_
        return datetime_ - mod + round_to

    @staticmethod
    def _round_timedelta_up(delta: datetime.timedelta, round_to: datetime.timedelta) -> datetime.timedelta:
        round_to_seconds = round_to.total_seconds()
        return datetime.timedelta(seconds=round_to_seconds * math.ceil(delta.total_seconds() / round_to_seconds))

    @staticmethod
    def _optimize_step(step: datetime.timedelta) -> datetime.timedelta:
        if step < LIST_OPTIMAL_STEPS[0]:
            # Set the step size to lowest larger than step 1, 2, 5 or 10 times
            # the largest smaller or equal than step negative power of 10
            lower_bound = datetime.timedelta(seconds=10 ** math.floor(math.log10(step.total_seconds())))
            return lower_bound * next(
                filter(lambda x: x * lower_bound >= step, (1, 2, 5, 10)),
                10,  # This value should not be reachable
            )

        if step <= LIST_OPTIMAL_STEPS[-1]:
            # Set the step size to the nearest larger or equal size from LIST_OPTIMAL_STEPS
            idx = bisect.bisect_left(LIST_OPTIMAL_STEPS, step)
            return LIST_OPTIMAL_STEPS[idx]

        # Otherwise round the step to whole days
        delta_day = datetime.timedelta(days=1)
        return TimelineCFG._round_timedelta_up(step, delta_day)

    @staticmethod
    def _calculate_timeline_steps(
        time_from: datetime.datetime,
        time_to: datetime.datetime,
        max_count: int,
        min_step_secs: Optional[int] = None,
        timezone: Optional[datetime.tzinfo] = None,
    ) -> tuple[datetime.datetime, datetime.timedelta, int]:
        delta = time_to - time_from

        if not min_step_secs:
            min_step_delta = datetime.timedelta(microseconds=1)
        else:
            min_step_delta = datetime.timedelta(seconds=min_step_secs)

        if delta <= datetime.timedelta(0):
            return time_from, min_step_delta, 0

        step = max(delta / max_count, min_step_delta)
        step = TimelineCFG._optimize_step(step)

        first_step = TimelineCFG._round_datetime_up(time_from, step, timezone=timezone)

        # Calculate actual step count, that will cover the requested timeline.
        step_count = TimelineCFG._get_step_count(time_from, time_to, step, first_step)

        if step_count > max_count:
            # In case the step count would be higher than the max_count
            # due to the shift of the first step, recalculate
            step = max(delta / (max_count - 1), min_step_delta)
            step = TimelineCFG._optimize_step(step)
            first_step = TimelineCFG._round_datetime_up(time_from, step, timezone=timezone)
            step_count = TimelineCFG._get_step_count(time_from, time_to, step, first_step)

        return first_step, step, step_count

    @classmethod
    def get_daily(
        cls: type[Self],
        time_from: datetime.datetime,
        time_to: datetime.datetime,
        time_type: TimeBoundType = TimeBoundType.DETECTION_TIME,
    ) -> Self:
        """Return optimal timeline configuration for timeline chart with step forced to 1 day."""
        step = datetime.timedelta(days=1)
        time_from = time_from.replace(hour=0, minute=0, second=0, microsecond=0)
        time_to = time_to.replace(hour=0, minute=0, second=0, microsecond=0) + step

        step_count = int((time_to - time_from) / step)

        return cls(time_from, time_to, step, step_count, time_type=time_type)

    @classmethod
    def get_with_step(
        cls: type[Self],
        time_from: datetime.datetime,
        time_to: datetime.datetime,
        step: datetime.timedelta,
        user_timezone: Optional[datetime.tzinfo] = None,
        time_type: TimeBoundType = TimeBoundType.DETECTION_TIME,
    ) -> Self:
        """Return timeline configuration for timeline chart with given step."""
        first_step = cls._round_datetime_up(time_from, step, user_timezone)
        step_count = cls._get_step_count(time_from, time_to, step, first_step)
        return cls(time_from, time_to, step, step_count, first_step, time_type=time_type)

    @classmethod
    def get_optimized(
        cls: type[Self],
        time_from: datetime.datetime,
        time_to: datetime.datetime,
        max_count: int,
        min_step_seconds: Optional[int] = None,
        user_timezone: Optional[datetime.tzinfo] = None,
        time_type: TimeBoundType = TimeBoundType.DETECTION_TIME,
    ) -> Self:
        """
        Finds optimal first step, step size and step count for provided constraints.

        Example for calculated step size of 5s where:
        ```txt
            t_from = YYYY-MM-DDThh:mm:02,
            t_to   = YYYY-MM-DDThh:mm:52,
            max_count = 12

        |---|-----|-----|-----|-----|-----|-----|-----|-----|-----|--|
        │   ╰───────╮                                 ╰──┬──╯        │
        time_from  first_step (rounded up to nearest 5s) step=5s  time_to

        step_count = 11
        ```
        """
        first_step, step, step_count = cls._calculate_timeline_steps(
            time_from, time_to, max_count, min_step_seconds, user_timezone
        )
        return cls(time_from, time_to, step, step_count, first_step, time_type=time_type)
