#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Event database storage abstraction layer. The current implementation requires
the `PostgreSQL <https://www.postgresql.org/>`__ database and is based directly
on the `Psycopg2 <http://initd.org/psycopg/docs/>`__ library for performance reasons.

.. warning::

    Current implementation is for optimalization purposes using some advanced
    schema features provided by the `PostgreSQL <https://www.postgresql.org/>`__
    database and thus no other engines are currently supported.

.. warning::

    The PostgreSQL extension `ip4r <https://github.com/RhodiumToad/ip4r>`__ must be installed.

References
^^^^^^^^^^

* https://github.com/RhodiumToad/ip4r
* https://www.gab.lc/articles/manage_ip_postgresql_with_ip4r
* http://initd.org/psycopg/docs/usage.html
* http://initd.org/psycopg/docs/sql.html
* http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax


"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>, Radko Krkoš <radko.krkos@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import contextlib
import copy
import re
from collections.abc import Callable
from typing import Any, TypeVar, cast

import psycopg2
import psycopg2.extras
import psycopg2.sql

import ipranges

import mentat.idea.internal
import mentat.idea.sqldb
import mentat.stats
from mentat.const import CKEY_CORE_DATABASE, CKEY_CORE_DATABASE_EVENTSTORAGE, random_str
from mentat.stats.idea import KEY_UNKNOWN, ST_SKEY_REST, ST_SKEY_TLCFG, TimeBoundType

_MANAGER = None

QTYPE_SELECT = "select"
QTYPE_SELECT_GHOST = "select_ghost"
QTYPE_COUNT = "count"
QTYPE_DELETE = "delete"
QTYPE_AGGREGATE = "aggregate"
QTYPE_TIMELINE = "timeline"
QTYPE_PIVOT = "pivot"

ENUM_TABLES = (
    "category",
    "protocol",
    "node_name",
    "node_type",
    "source_type",
    "target_type",
    "resolvedabuses",
    "targetabuses",
    "eventclass",
    "targetclass",
    "eventseverity",
    "targetseverity",
    "inspectionerrors",
    "tlp",
)

EVENTS_COLUMNS = (
    "id",
    "detecttime",
    "category",
    "description",
    "source_ip",
    "target_ip",
    "source_ip_aggr_ip4",
    "source_ip_aggr_ip6",
    "target_ip_aggr_ip4",
    "target_ip_aggr_ip6",
    "source_port",
    "target_port",
    "source_type",
    "target_type",
    "protocol",
    "node_name",
    "node_type",
    "resolvedabuses",
    "targetabuses",
    "storagetime",
    "eventclass",
    "targetclass",
    "eventseverity",
    "targetseverity",
    "inspectionerrors",
    "tlp",
    "shadow_reporting",
    "shadow_reporting_target",
)

EVENTS_COLUMNS_ARRAY = (
    "category",
    "source_ip",
    "target_ip",
    "source_port",
    "target_port",
    "source_type",
    "target_type",
    "protocol",
    "node_name",
    "node_type",
    "resolvedabuses",
    "targetabuses",
    "inspectionerrors",
)

EVENTS_COLUMNS_TOPLISTED = (
    "source_ip",
    "target_ip",
    "source_port",
    "target_port",
    "resolvedabuses",
    "targetabuses",
    "description",
)

# First item is the name of the index, the second is the definition.
INDEXES = {
    ("events_detecttime_idx", "ON events USING BTREE (detecttime)"),
    ("events_storagetime_idx", "ON events USING BTREE (storagetime)"),
    ("events_eventseverity_idx", "ON events USING BTREE (eventseverity) WHERE eventseverity IS NOT NULL"),
    ("events_targetseverity_idx", "ON events USING BTREE (targetseverity) WHERE targetseverity IS NOT NULL"),
    ("events_tlp_idx", "ON events USING BTREE(tlp)"),
    (
        "events_combined_idx",
        "ON events USING GIN (category, node_name, protocol, source_port, target_port, source_type, target_type, node_type, resolvedabuses, targetabuses, inspectionerrors)",
    ),
    (
        "events_ip_aggr_idx",
        "ON events USING GIST (source_ip_aggr_ip4, target_ip_aggr_ip4, source_ip_aggr_ip6, target_ip_aggr_ip6)",
    ),
    ("events_description_idx", "ON events USING GIN (description gin_trgm_ops)"),
    ("event_shadow_reporting_idx", "ON events USING BTREE(shadow_reporting)"),
    ("event_shadow_reporting_target_idx", "ON events USING BTREE(shadow_reporting_target)"),
    ("thresholds_thresholdtime_idx", "ON thresholds USING BTREE (thresholdtime)"),
    ("thresholds_relapsetime_idx", "ON thresholds USING BTREE (relapsetime)"),
    ("thresholds_ttltime_idx ON", "thresholds USING BTREE (ttltime)"),
    ("events_thresholded_combined_idx", "ON events_thresholded USING BTREE (groupname, eventseverity)"),
    ("events_thresholded_createtime_idx", "ON events_thresholded USING BTREE (createtime)"),
}

RE_QNAME = ' AS "_mentatq\\(([^)]+)\\)_"'
RE_QNAME_CMPL = re.compile(RE_QNAME)

F = TypeVar("F", bound=Callable[..., Any])


class EventStorageException(Exception):
    """
    Class for custom event storage exceptions.
    """


class StorageIntegrityError(EventStorageException):
    """
    Class for custom event storage exceptions related to integrity errors.
    """


class StorageConnectionException(EventStorageException):
    """
    Class for custom event storage exceptions related to database connection errors.
    """


class DataError(EventStorageException):
    """
    Class for custom event storage exceptions related to data errors.
    """


class QueryCanceledException(EventStorageException):
    """
    Class for custom event storage exceptions related to canceled queries.
    """


def _bq_param_multi_to_array(chunks, params, identifier, parameter, negate=False):
    """
    SQL query builder helper. Build part of the query for multi to array parameter.
    """
    if "__EMPTY__" in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL("{} = '{{}}'").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT ({} = '{{}}')").format(psycopg2.sql.Identifier(identifier)))
    elif "__ANY__" in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL("{} != '{{}}'").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT ({} != '{{}}')").format(psycopg2.sql.Identifier(identifier)))
    else:
        if not negate:
            chunks.append(psycopg2.sql.SQL("{} && %s").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT ({} && %s)").format(psycopg2.sql.Identifier(identifier)))
        params.append(parameter)


def _bq_param_multi_to_scalar(chunks, params, identifier, parameter, negate=False):
    """
    SQL query builder helper. Build part of the query for multi to scalar parameter.
    """
    if "__EMPTY__" in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL("COALESCE({},'') = ''").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT (COALESCE({},'') = '')").format(psycopg2.sql.Identifier(identifier)))
    elif "__ANY__" in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL("COALESCE({},'') != ''").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT (COALESCE({},'') != '')").format(psycopg2.sql.Identifier(identifier)))
    else:
        if not negate:
            chunks.append(psycopg2.sql.SQL("{} = ANY(%s)").format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL("NOT ({} = ANY(%s))").format(psycopg2.sql.Identifier(identifier)))
        params.append(parameter)


def _bq_gen_aggr_ident(ident, value):
    if ":" in str(value):
        return f"{ident}_aggr_ip6"
    return f"{ident}_aggr_ip4"


def _bq_searchby_addr(chunks, params, idents, items):
    items_exp = []
    chunks.append(
        psycopg2.sql.SQL("({})" if len(items) > 1 or len(idents) > 1 else "{}").format(
            psycopg2.sql.SQL(" OR ").join(
                [
                    psycopg2.sql.SQL("({} && %s AND %s && ANY({}))").format(
                        psycopg2.sql.Identifier(_bq_gen_aggr_ident(ident, itm)),
                        psycopg2.sql.Identifier(ident),
                    )
                    for ident in idents
                    for itm in items
                ]
            )
        )
    )
    for _ident in idents:
        for i in items:
            items_exp.append(i)
            items_exp.append(i)
    params.extend(items_exp)


def _bq_qpart_select_sorting(parameters, query, params):
    """Process and append query sorting and limiting parameters for select queries."""

    if not parameters:
        return query, params

    if parameters.get("sortby", None):
        field, direction = parameters["sortby"].split(".")
        if field not in ["detecttime", "storagetime"]:
            if parameters.get("st_from", None) or parameters.get("st_to", None):
                field = "storagetime"
            else:
                field = "detecttime"

        if direction in ("asc",):
            query += psycopg2.sql.SQL(" ORDER BY {} ASC").format(psycopg2.sql.Identifier(field))
        else:
            query += psycopg2.sql.SQL(" ORDER BY {} DESC").format(psycopg2.sql.Identifier(field))

    if parameters.get("limit", None):
        query += psycopg2.sql.SQL(" LIMIT %s")
        params.append(int(parameters["limit"]))
        if "page" in parameters and parameters["page"] and int(parameters["page"]) > 1:
            query += psycopg2.sql.SQL(" OFFSET %s")
            params.append((int(parameters["page"]) - 1) * int(parameters["limit"]))

    return query, params


def _bq_qbase_select(parameters, qname=None):
    query = psycopg2.sql.SQL("SELECT * FROM events")
    if qname:
        query += psycopg2.sql.SQL(" AS {}").format(psycopg2.sql.Identifier(qname))
    return query, []


def _bq_select_full(parameters, qname=None, dbtoplist=False):
    query, params = _bq_qbase_select(parameters, qname)
    query += psycopg2.sql.SQL(" INNER JOIN events_json USING(id)")
    query, params = _bq_where(parameters, query, params)
    query, params = _bq_qpart_select_sorting(parameters, query, params)
    return query, params


def _bq_select_ghost(parameters, qname=None, dbtoplist=False):
    query, params = _bq_qbase_select(parameters, qname)
    query, params = _bq_where(parameters, query, params)
    query, params = _bq_qpart_select_sorting(parameters, query, params)
    return query, params


def _bq_count(parameters, qname=None, dbtoplist=False):
    query = psycopg2.sql.SQL("SELECT count(id) FROM events")
    if qname:
        query += psycopg2.sql.SQL(" AS {}").format(psycopg2.sql.Identifier(qname))
    query, params = _bq_where(parameters, query, [])
    return query, params


def _bq_delete(parameters, qname=None, dbtoplist=False):
    query = psycopg2.sql.SQL("DELETE FROM events")
    if qname:
        query += psycopg2.sql.SQL(" AS {}").format(psycopg2.sql.Identifier(qname))
    query, params = _bq_where(parameters, query, [])
    return query, params


def _bq_get_unnested_set(parameters):
    if parameters["aggr_set"] in EVENTS_COLUMNS_ARRAY:
        return psycopg2.sql.SQL("unnest({})").format(psycopg2.sql.Identifier(parameters["aggr_set"]))
    return psycopg2.sql.SQL("COALESCE({}, {})").format(
        psycopg2.sql.Identifier(parameters["aggr_set"]),
        psycopg2.sql.Literal(KEY_UNKNOWN),
    )


def _bq_aggregate(parameters, qname=None, dbtoplist=False):
    query = psycopg2.sql.SQL("SELECT")
    params = []
    if parameters.get("aggr_set", None):
        query += psycopg2.sql.SQL(" {} AS set, COUNT(*) FROM events").format(_bq_get_unnested_set(parameters))
    else:
        query += psycopg2.sql.SQL(" COUNT(*) FROM events")
    if qname:
        query += psycopg2.sql.SQL(" AS {}").format(psycopg2.sql.Identifier(qname))
    query, params = _bq_where(parameters, query, params)
    if parameters.get("aggr_set", None):
        query += psycopg2.sql.SQL(" GROUP BY set")
        if parameters.get("limit", None) and parameters["aggr_set"] in EVENTS_COLUMNS_TOPLISTED:
            query += psycopg2.sql.SQL(" ORDER BY COUNT(*) DESC LIMIT %s")
            params.append(int(parameters["limit"]))
    return query, params


def _bq_timeline(parameters, qname, dbtoplist=None):
    is_count = not parameters.get("aggr_set", None)
    is_toplist = (
        dbtoplist and not is_count and "limit" in parameters and parameters["aggr_set"] in EVENTS_COLUMNS_TOPLISTED
    )
    timeline_cfg = parameters[ST_SKEY_TLCFG]

    if timeline_cfg.time_type == TimeBoundType.STORAGE_TIME:
        time_column = psycopg2.sql.Identifier("storagetime")
    else:
        time_column = psycopg2.sql.Identifier("detecttime")

    params = []
    subqueries = [
        psycopg2.sql.SQL(
            "timeline AS (SELECT * FROM (SELECT %s AS bucket UNION SELECT generate_series(%s, %s - INTERVAL '1 microsecond', %s) AS bucket) AS t ORDER BY bucket)"
        )
    ]
    params.append(timeline_cfg.t_from)
    params.append(timeline_cfg.first_step)
    params.append(timeline_cfg.t_to)
    params.append(timeline_cfg.step)

    if not is_count:
        if parameters["aggr_set"] in EVENTS_COLUMNS_ARRAY:
            subquery = psycopg2.sql.SQL(
                "total AS (SELECT COALESCE(SUM(CARDINALITY({})), 0) AS total FROM events"
            ).format(psycopg2.sql.Identifier(parameters["aggr_set"]))
            subquery, params = _bq_where(parameters, subquery, params, end_inclusive=False)
            subquery += psycopg2.sql.SQL(")")
            subqueries.append(subquery)

        subquery = psycopg2.sql.SQL("total_events AS (SELECT COUNT(*) AS total FROM events")
        subquery, params = _bq_where(parameters, subquery, params, end_inclusive=False)
        subquery += psycopg2.sql.SQL(")")
        subqueries.append(subquery)

    if is_toplist:
        subquery = psycopg2.sql.SQL("toplist AS (SELECT {} AS set, COUNT(*) AS sum FROM events").format(
            _bq_get_unnested_set(parameters)
        )
        subquery, params = _bq_where(parameters, subquery, params, end_inclusive=False)
        subquery += psycopg2.sql.SQL(" GROUP BY set ORDER BY sum DESC LIMIT %s)")
        params.append(parameters["limit"])
        subqueries.append(subquery)

        subquery = psycopg2.sql.SQL(
            "toplist_with_rest AS (SELECT set::text, sum FROM toplist UNION (SELECT {} as set, total - SUM(sum)::bigint as sum FROM {}, toplist GROUP BY total HAVING total - SUM(sum)::bigint > 0) ORDER BY sum DESC)"
        ).format(
            psycopg2.sql.Literal(ST_SKEY_REST),
            psycopg2.sql.Identifier("total")
            if parameters["aggr_set"] in EVENTS_COLUMNS_ARRAY
            else psycopg2.sql.Identifier(
                "total_events"
            ),  # in case the set is not array, just use total event count as total
        )
        subqueries.append(subquery)

    subquery = psycopg2.sql.SQL(
        "raw AS (SELECT GREATEST(%s, %s + %s * (width_bucket({}, (SELECT array_agg(bucket) FROM generate_series(%s, %s - INTERVAL '1 microsecond', %s) AS bucket)) - 1)) AS bucket{}, COUNT(*) AS count FROM {}"
    ).format(
        time_column,
        psycopg2.sql.SQL("")
        if is_count
        else psycopg2.sql.SQL(", {} AS set").format(_bq_get_unnested_set(parameters))
        if not is_toplist
        else psycopg2.sql.SQL(", set"),
        psycopg2.sql.Identifier("events")
        if not is_toplist
        else psycopg2.sql.SQL("(SELECT {}, {} AS set FROM events").format(
            time_column, _bq_get_unnested_set(parameters)
        ),
    )
    params.append(timeline_cfg.t_from)
    params.append(timeline_cfg.first_step)
    params.append(timeline_cfg.step)
    params.append(timeline_cfg.first_step)
    params.append(timeline_cfg.t_to)
    params.append(timeline_cfg.step)

    subquery, params = _bq_where(parameters, subquery, params, end_inclusive=False)

    if is_toplist:
        subquery += psycopg2.sql.SQL(") top_events INNER JOIN toplist USING (set)")

    subquery += psycopg2.sql.SQL(" GROUP BY bucket{})").format(
        psycopg2.sql.SQL("") if is_count else psycopg2.sql.SQL(", set")
    )
    subqueries.append(subquery)

    if is_toplist:
        subquery = psycopg2.sql.SQL(
            "raw_with_rest AS (SELECT bucket, set::text, count FROM raw UNION ALL SELECT bucket, {} AS set, raw_totals.count - raw_sums.count AS count FROM (SELECT GREATEST(%s, %s + %s * (width_bucket({}, (SELECT array_agg(bucket) FROM generate_series(%s, %s - INTERVAL '1 microsecond', %s) AS bucket)) - 1)) AS bucket, {} AS count FROM events"
        ).format(
            psycopg2.sql.Literal(ST_SKEY_REST),
            time_column,
            psycopg2.sql.SQL("SUM(CARDINALITY({}))").format(psycopg2.sql.Identifier(parameters["aggr_set"]))
            if parameters["aggr_set"] in EVENTS_COLUMNS_ARRAY
            else psycopg2.sql.SQL("COUNT(*)"),
        )
        params.append(timeline_cfg.t_from)
        params.append(timeline_cfg.first_step)
        params.append(timeline_cfg.step)
        params.append(timeline_cfg.first_step)
        params.append(timeline_cfg.t_to)
        params.append(timeline_cfg.step)

        subquery, params = _bq_where(parameters, subquery, params, end_inclusive=False)
        subquery += psycopg2.sql.SQL(
            " GROUP BY bucket) raw_totals FULL JOIN (SELECT bucket, SUM(count)::bigint AS count FROM raw GROUP BY bucket) raw_sums USING (bucket))"
        )
        subqueries.append(subquery)

    elif not is_count:
        subquery = psycopg2.sql.SQL(
            "sums AS (SELECT raw.set::text AS set, SUM(raw.count)::bigint AS sum FROM raw GROUP BY raw.set ORDER BY sum DESC)"
        )
        subqueries.append(subquery)

    main_query = psycopg2.sql.SQL(
        " (SELECT timeline.bucket{}, COALESCE(count, 0) AS count FROM {} LEFT JOIN {} ON {} ORDER BY bucket ASC{}) UNION ALL SELECT NULL, {} FROM {}"
    )
    if is_count:
        main_query = main_query.format(
            psycopg2.sql.SQL(""),
            psycopg2.sql.Identifier("timeline"),
            psycopg2.sql.Identifier("raw"),
            psycopg2.sql.SQL("timeline.bucket = raw.bucket"),
            psycopg2.sql.SQL(""),
            psycopg2.sql.SQL("SUM(count)::bigint"),
            psycopg2.sql.Identifier("raw"),
        )
    else:
        toplist_or_sums = psycopg2.sql.Identifier("toplist_with_rest" if is_toplist else "sums")
        with_or_without_rest = psycopg2.sql.Identifier("raw_with_rest" if is_toplist else "raw")

        main_query = main_query.format(
            psycopg2.sql.SQL(", {}.set").format(toplist_or_sums),
            psycopg2.sql.SQL('("timeline" FULL JOIN {} ON TRUE)').format(toplist_or_sums),
            with_or_without_rest,
            psycopg2.sql.SQL('"timeline".bucket = {}.bucket AND {}.set IS NOT DISTINCT FROM {}.set').format(
                with_or_without_rest, toplist_or_sums, with_or_without_rest
            ),
            psycopg2.sql.SQL(", {}.sum DESC").format(toplist_or_sums),
            psycopg2.sql.SQL("{}.set, {}.sum").format(*((toplist_or_sums,) * 2)),
            psycopg2.sql.SQL(
                "{} UNION ALL SELECT NULL, NULL, total FROM {} UNION ALL SELECT NULL, NULL, total FROM total_events"
            ).format(
                toplist_or_sums,
                psycopg2.sql.Identifier("total")
                if parameters["aggr_set"] in EVENTS_COLUMNS_ARRAY
                else psycopg2.sql.Identifier(
                    "total_events"
                ),  # in case the set is not array, just use total event count as total
            ),
        )

    query = psycopg2.sql.SQL("WITH ") + psycopg2.sql.SQL(", ").join(subqueries) + main_query

    if qname:
        query += psycopg2.sql.SQL(" AS {}").format(psycopg2.sql.Identifier(qname))

    return query, params


def _get_select_and_join_query_parts(
    agg_column: psycopg2.sql.Identifier, as_: psycopg2.sql.Identifier
) -> tuple[psycopg2.sql.Composable, psycopg2.sql.Composable]:
    if agg_column.string in EVENTS_COLUMNS_ARRAY:
        return (
            psycopg2.sql.SQL("{}").format(as_),
            psycopg2.sql.SQL(" CROSS JOIN LATERAL unnest({}) AS {}").format(agg_column, as_),
        )
    return (
        psycopg2.sql.SQL("COALESCE({}, {}) AS {}").format(agg_column, psycopg2.sql.Literal(KEY_UNKNOWN), as_),
        psycopg2.sql.SQL(""),
    )


def _bq_observed_counts(
    parameters: dict[str, Any], qname: str | None = None, dbtoplist: bool = False
) -> tuple[psycopg2.sql.Composable, list[Any]]:
    row_agg = psycopg2.sql.Identifier(parameters["row_agg"])
    col_agg = psycopg2.sql.Identifier(parameters["col_agg"])

    params: list[Any] = []

    row_select, row_join = _get_select_and_join_query_parts(
        row_agg,
        psycopg2.sql.Identifier("row_category"),
    )
    column_select, column_join = _get_select_and_join_query_parts(
        col_agg,
        psycopg2.sql.Identifier("col_category"),
    )

    query = psycopg2.sql.SQL("SELECT {}, {}, COUNT(*) AS observed FROM events{}{}").format(
        row_select,
        column_select,
        row_join,
        column_join,
    )

    query, params = _bq_where(parameters, query, params, end_inclusive=False)

    query += psycopg2.sql.SQL(" GROUP BY row_category, col_category")

    return query, params


def _bq_pivot(
    parameters: dict[str, Any], qname: str | None = None, dbtoplist: bool = False
) -> tuple[psycopg2.sql.Composable, list[Any]]:
    include_residuals = parameters["include_residuals"]

    params: list[Any] = []
    observed_counts_query, observed_params = _bq_observed_counts(parameters, qname, dbtoplist)

    subqueries: list[psycopg2.sql.Composable] = [
        psycopg2.sql.SQL("observed_counts AS ({})").format(observed_counts_query),
        psycopg2.sql.SQL("distinct_rows AS (SELECT DISTINCT row_category FROM observed_counts)"),
        psycopg2.sql.SQL("distinct_cols AS (SELECT DISTINCT col_category FROM observed_counts)"),
        psycopg2.sql.SQL(
            "all_pairs AS (SELECT dr.row_category, dc.col_category FROM distinct_rows dr CROSS JOIN distinct_cols dc)"
        ),
        psycopg2.sql.SQL(
            "pivot AS (SELECT ap.row_category, ap.col_category, COALESCE(oc.observed, 0) AS observed FROM all_pairs ap LEFT JOIN observed_counts oc ON ap.row_category = oc.row_category AND ap.col_category = oc.col_category)"
        ),
    ]
    params.extend(observed_params)

    if include_residuals:
        residuals_subqueries: list[psycopg2.sql.Composable] = [
            psycopg2.sql.SQL(
                "row_totals AS (SELECT row_category, SUM(observed) AS row_total FROM pivot GROUP BY row_category)"
            ),
            psycopg2.sql.SQL(
                "column_totals AS (SELECT col_category, SUM(observed) AS col_total FROM pivot GROUP BY col_category)"
            ),
            psycopg2.sql.SQL("total AS (SELECT SUM(observed) AS total FROM pivot)"),
            psycopg2.sql.SQL(
                "expected AS (SELECT p.row_category, p.col_category, p.observed, (rt.row_total * ct.col_total)::NUMERIC / t.total AS expected, rt.row_total, ct.col_total, t.total FROM pivot p JOIN row_totals rt ON p.row_category = rt.row_category JOIN column_totals ct ON p.col_category = ct.col_category CROSS JOIN total t)"
            ),
            psycopg2.sql.SQL(
                "residuals AS (SELECT row_category, col_category, observed, expected, CASE WHEN (1 - row_total::NUMERIC / total) > 0 AND (1 - col_total::NUMERIC / total) > 0 THEN (observed - expected) / SQRT(expected * (1 - row_total::NUMERIC / total) * (1 - col_total::NUMERIC / total)) ELSE NULL END AS standardized_residual FROM expected)"
            ),
        ]
        subqueries.extend(residuals_subqueries)

    main_query = psycopg2.sql.SQL(
        "SELECT row_category, col_category, observed, {} FROM {} AS {} ORDER BY row_category, col_category"
    ).format(
        psycopg2.sql.Identifier("standardized_residual") if include_residuals else psycopg2.sql.Literal(None),
        psycopg2.sql.Identifier("residuals") if include_residuals else psycopg2.sql.Identifier("pivot"),
        psycopg2.sql.Identifier(qname) if qname else psycopg2.sql.Identifier("res"),
    )

    query = psycopg2.sql.SQL("WITH ") + psycopg2.sql.SQL(", ").join(subqueries) + main_query

    return query, params


def _bq_where(parameters, query, params, end_inclusive=True):
    chunks = []

    inclusive = psycopg2.sql.SQL("=" if end_inclusive else "")

    if parameters:
        if parameters.get("dt_from", None):
            chunks.append(psycopg2.sql.SQL("{} >= %s").format(psycopg2.sql.Identifier("detecttime")))
            params.append(parameters["dt_from"].replace(tzinfo=None))
        if parameters.get("dt_to", None):
            chunks.append(psycopg2.sql.SQL("{} <{} %s").format(psycopg2.sql.Identifier("detecttime"), inclusive))
            params.append(parameters["dt_to"].replace(tzinfo=None))
        if parameters.get("st_from", None):
            chunks.append(psycopg2.sql.SQL("{} >= %s").format(psycopg2.sql.Identifier("storagetime")))
            params.append(parameters["st_from"].replace(tzinfo=None))
        if parameters.get("st_to", None):
            chunks.append(psycopg2.sql.SQL("{} <{} %s").format(psycopg2.sql.Identifier("storagetime"), inclusive))
            params.append(parameters["st_to"].replace(tzinfo=None))

        if parameters.get("shadow_reporting", None) is not None:
            val = str(parameters["shadow_reporting"]).strip().upper()
            if val in ["TRUE", "FALSE"]:
                chunks.append(
                    psycopg2.sql.SQL("{} IS {}").format(
                        psycopg2.sql.Identifier("shadow_reporting"),
                        psycopg2.sql.SQL(val),
                    )
                )
        if parameters.get("shadow_reporting_target", None) is not None:
            val = str(parameters["shadow_reporting_target"]).strip().upper()
            if val in ["TRUE", "FALSE"]:
                chunks.append(
                    psycopg2.sql.SQL("{} IS {}").format(
                        psycopg2.sql.Identifier("shadow_reporting_target"),
                        psycopg2.sql.SQL(val),
                    )
                )

        if parameters.get("host_addrs", None):
            _bq_searchby_addr(chunks, params, ["source_ip", "target_ip"], parameters["host_addrs"])
        else:
            if parameters.get("source_addrs", None):
                _bq_searchby_addr(chunks, params, ["source_ip"], parameters["source_addrs"])
            if parameters.get("target_addrs", None):
                _bq_searchby_addr(chunks, params, ["target_ip"], parameters["target_addrs"])

        if parameters.get("host_ports", None):
            chunks.append(
                psycopg2.sql.SQL("({} && %s OR {} && %s)").format(
                    psycopg2.sql.Identifier("source_port"),
                    psycopg2.sql.Identifier("target_port"),
                )
            )
            params.extend(
                [
                    [int(x) for x in parameters["host_ports"]],
                    [int(x) for x in parameters["host_ports"]],
                ]
            )
        else:
            if parameters.get("source_ports", None):
                chunks.append(psycopg2.sql.SQL("{} && %s").format(psycopg2.sql.Identifier("source_port")))
                params.append([int(x) for x in parameters["source_ports"]])
            if parameters.get("target_ports", None):
                chunks.append(psycopg2.sql.SQL("{} && %s").format(psycopg2.sql.Identifier("target_port")))
                params.append([int(x) for x in parameters["target_ports"]])

        if parameters.get("host_types", None):
            chunks.append(
                psycopg2.sql.SQL("({} && %s OR {} && %s)").format(
                    psycopg2.sql.Identifier("source_type"),
                    psycopg2.sql.Identifier("target_type"),
                )
            )
            params.extend([parameters["host_types"], parameters["host_types"]])
        else:
            if parameters.get("source_types", None):
                chunks.append(psycopg2.sql.SQL("{} && %s").format(psycopg2.sql.Identifier("source_type")))
                params.append(parameters["source_types"])
            if parameters.get("target_types", None):
                chunks.append(psycopg2.sql.SQL("{} && %s").format(psycopg2.sql.Identifier("target_type")))
                params.append(parameters["target_types"])

        for item in (
            ("protocols", "protocol", _bq_param_multi_to_array),
            ("categories", "category", _bq_param_multi_to_array),
            ("classes", "eventclass", _bq_param_multi_to_scalar),
            ("target_classes", "targetclass", _bq_param_multi_to_scalar),
            ("severities", "eventseverity", _bq_param_multi_to_scalar),
            ("target_severities", "targetseverity", _bq_param_multi_to_scalar),
            ("detectors", "node_name", _bq_param_multi_to_array),
            ("detector_types", "node_type", _bq_param_multi_to_array),
            ("groups", "resolvedabuses", _bq_param_multi_to_array),
            ("target_groups", "targetabuses", _bq_param_multi_to_array),
            ("inspection_errs", "inspectionerrors", _bq_param_multi_to_array),
            ("tlps", "tlp", _bq_param_multi_to_scalar),
        ):
            if parameters.get(item[0], None):
                item[2](
                    chunks,
                    params,
                    item[1],
                    parameters.get(item[0]),
                    parameters.get(f"not_{item[0]}", "False")
                    in ["True", "true", "TRUE", "y", "Y", "yes", "YES", "1", True],
                )

        if parameters.get("description", None):
            chunks.append(
                psycopg2.sql.SQL("{} ILIKE '%%' || %s || '%%' ESCAPE '&'").format(
                    psycopg2.sql.Identifier("description")
                )
            )
            params.append(re.sub("([%_&])", r"&\1", parameters["description"]))  # Escape _ and % characters

        # Authorization based on TLP.
        if "_TLP_restriction_groups" in parameters:
            groups = parameters.get("_TLP_restriction_groups")
            chunks.append(
                psycopg2.sql.SQL(
                    "({} IS NULL OR {} NOT IN ('AMBER-STRICT', 'AMBER', 'RED') OR {} && %s OR {} && %s)"
                ).format(
                    psycopg2.sql.Identifier("tlp"),
                    psycopg2.sql.Identifier("tlp"),
                    psycopg2.sql.Identifier("resolvedabuses"),
                    psycopg2.sql.Identifier("targetabuses"),
                )
            )
            params.append(groups)  # resolvedabuses
            params.append(groups)  # targetabuses

    if chunks:
        query += psycopg2.sql.SQL(" WHERE ")
        query += psycopg2.sql.SQL(" AND ").join(chunks)

    return query, params


_BQ_MAP = {
    QTYPE_SELECT: _bq_select_full,
    QTYPE_SELECT_GHOST: _bq_select_ghost,
    QTYPE_COUNT: _bq_count,
    QTYPE_DELETE: _bq_delete,
    QTYPE_AGGREGATE: _bq_aggregate,
    QTYPE_TIMELINE: _bq_timeline,
    QTYPE_PIVOT: _bq_pivot,
}


def build_query(parameters=None, qtype=QTYPE_SELECT, qname=None, dbtoplist=False, user=None):
    """
    Build SQL database query according to given parameters.

    :param dict parameters: Query parameters complex dictionary structure.
    :param str qtype: Type of the generated query ('select','count','delete').
    :param str qname: Unique name for the generated query.
    :param bool dbtoplist: Build aggregation or timeline SQL queries with toplisting within the database.
    :param UserModel user: user running the query (optional).
    :return: Generated query as ``psycopg2.sql.SQL`` and appropriate arguments.
    :rtype: tuple
    """
    if qname:
        qname = f"_mentatq({qname})_"
    if parameters is None:
        parameters = {}
    if user:
        parameters["_TLP_restriction_groups"] = user.get_all_group_names()

    try:
        return _BQ_MAP[str(qtype)](parameters, qname, dbtoplist)
    except KeyError as error:
        if isinstance(qtype, psycopg2.sql.Composed):
            return _bq_where(parameters, qtype, [])
        raise ValueError(f"Received invalid value '{qtype}' for SQL query type.") from error


class IPListAdapter:
    """
    Adapt a :py:class:`mentat.idea.sqldb.IPList` to an SQL quotable object.

    Resources: http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax
    """

    def __init__(self, seq):
        self._seq = seq

    def prepare(self, conn):
        """
        Implementation of ``psycopg2`` adapter interface.
        """

    def getquoted(self):
        """
        Implementation of ``psycopg2`` adapter interface.
        """
        qobjs = [str(o) for o in self._seq]
        return "'{" + ", ".join(qobjs) + "}'"

    __str__ = getquoted


class IPBaseAdapter:
    """
    Adapt a :py:class:`ipranges.IPBase` to an SQL quotable object.

    Resources: http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax
    """

    def __init__(self, rng):
        self._rng = rng

    def prepare(self, conn):
        """
        Implementation of ``psycopg2`` adapter interface.
        """

    def getquoted(self):
        """
        Implementation of ``psycopg2`` adapter interface.
        """
        return f"'{self._rng!s}'"

    __str__ = getquoted


def record_to_idea(val):
    """
    Convert given SQL record object, as fetched from PostgreSQL database, directly
    into :py:class:`mentat.idea.internal.Idea` object.
    """
    return mentat.idea.internal.Idea.from_json(val.event.tobytes().decode("utf-8"))


def record_to_idea_ghost(val):
    """
    Convert given SQL record object, as fetched from PostgreSQL database, directly
    into :py:class:`mentat.idea.internal.IdeaGhost` object.
    """
    return mentat.idea.internal.IdeaGhost.from_record(val)


_OBJECT_TYPES = {QTYPE_SELECT: record_to_idea, QTYPE_SELECT_GHOST: record_to_idea_ghost}


class EventStorageCursor:
    """
    Encapsulation of :py:class:`psycopg2.cursor` class.
    """

    def __init__(self, cursor):
        self.cursor = cursor
        self.lastquery = None

    def __del__(self):
        self.close()

    def __getattr__(self, name):
        return getattr(self.cursor, name)

    def close(self):
        """
        Close current database connection.
        """
        with contextlib.suppress(Exception):
            self.cursor.close()
        self.cursor = None

    # ---------------------------------------------------------------------------

    def insert_event(self, idea_event):
        """
        Insert given IDEA event into database.

        :param mentat.idea.internal idea_event: Instance of IDEA event.
        """
        idea_pgsql = mentat.idea.sqldb.Idea(idea_event)
        record = idea_pgsql.get_record()

        self.cursor.execute(
            "INSERT INTO events (id, tlp, detecttime, category, description, source_ip, target_ip, source_ip_aggr_ip4, source_ip_aggr_ip6, target_ip_aggr_ip4, target_ip_aggr_ip6, source_port, target_port, source_type, target_type, protocol, node_name, node_type, resolvedabuses, targetabuses, storagetime, eventclass, targetclass, eventseverity, targetseverity, inspectionerrors, shadow_reporting, shadow_reporting_target) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            record[0:-1],
        )
        self.cursor.execute(
            "INSERT INTO events_json (id, event) VALUES (%s, %s)",
            (record[0], record[-1]),
        )

    def fetch_event(self, eventid):
        """
        Fetch IDEA event with given primary identifier from database.

        :param str eventid: Primary identifier of the message to fetch.
        :return: Instance of IDEA event.
        :rtype: mentat.idea.internal
        """
        self.cursor.execute("SELECT id, event FROM events_json WHERE id = %s", (eventid,))
        record = self.cursor.fetchone()
        if record:
            return record_to_idea(record)
        return None

    def delete_event(self, eventid):
        """
        Delete IDEA event with given primary identifier from database.

        :param str eventid: Primary identifier of the message to fetch.
        """
        self.cursor.execute("DELETE FROM events WHERE id = %s", (eventid,))

    # ---------------------------------------------------------------------------

    def query_direct(self, raw_query, idents=None, params=None):
        """
        Perform direct database query.

        :param str raw_query: Raw SQL query. Will be converted to :py:class:`psycopg2.sql.SQL`.
        :param list idents: Optional list of SQL identifiers, will be converted to :py:class:`psycopg2.sql.Identifier` and formatted into ``raw_query`` above.
        :param list params: Optional list of SQL parameters, will be formatted into ``raw_query`` above.
        """
        query = psycopg2.sql.SQL(raw_query)
        if idents:
            idents = [psycopg2.sql.Identifier(i) for i in idents]
            query = query.format(*idents)

        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def count_events(self, parameters=None, qname=None):
        """
        Count the number of IDEA events in database. There is an option to assign given
        unique name to the count query, so that it can be identified within the
        ``pg_stat_activity`` table.

        :param dict parameters: Count query parameters.
        :param str qname: Optional unique name for the generated query.
        :return: Number of IDEA events in database.
        :rtype: int
        """
        query, params = build_query(parameters, qtype="count", qname=qname)
        self.lastquery = self.cursor.mogrify(query, params)
        self.cursor.execute(query, params)

        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def search_events(self, parameters=None, qtype=QTYPE_SELECT, qname=None, user=None):
        """
        Search IDEA events in database according to given parameters. The
        parameters will be passed down to the :py:func:`mentat.services.eventstorage.build_query`
        function to generate proper SQL query. There is an option to assign given
        unique name to the select query, so that it can be identified within the
        ``pg_stat_activity`` table.

        :param dict parameters: Search query parameters, see :py:func:`mentat.services.eventstorage.build_query` for details.
        :param string qtype: Type of the select query.
        :param str qname: Optional unique name for the generated query.
        :param UserModel user: User object for authorization using TLP.
        :return: Number of IDEA events in the result and list of events.
        :rtype: tuple
        """
        event_factory = _OBJECT_TYPES.get(qtype, lambda x: x)

        query, params = build_query(parameters, qtype=qtype, qname=qname, user=user)
        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        event_count = self.cursor.rowcount
        events_raw = self.cursor.fetchall()
        return event_count, [event_factory(event) for event in events_raw]

    def search_events_aggr(self, parameters=None, qtype=QTYPE_AGGREGATE, qname=None, dbtoplist=False, user=None):
        """
        Search IDEA events in database according to given parameters and perform selected aggregations. The
        parameters will be passed down to the :py:func:`mentat.services.eventstorage.build_query`
        function to generate proper SQL query. There is an option to assign given
        unique name to the select query, so that it can be identified within the
        ``pg_stat_activity`` table.

        :param dict parameters: Search query parameters, see :py:func:`mentat.services.eventstorage.build_query` for details.
        :param string qtype: Type of the select query.
        :param str qname: Optional unique name for the generated query.
        :param UserModel user: User object for authorization using TLP.
        :return: Number of IDEA events in the result and list of events.
        :rtype: tuple
        """
        query, params = build_query(parameters, qtype=qtype, qname=qname, dbtoplist=dbtoplist, user=user)
        self.lastquery = self.cursor.mogrify(query, params)
        print(self.lastquery)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def delete_events(self, parameters=None, qname=None):
        """
        Delete IDEA events in database according to given parameters. There is
        an option to assign given unique name to the query, so that it can be
        identified within the ``pg_stat_activity`` table.

        :param dict parameters: Delete query parameters.
        :param str qname: Optional unique name for the generated query.
        :return: Number of deleted events.
        :rtype: int
        """
        query, params = build_query(parameters, qtype="delete", qname=qname)
        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        return self.cursor.rowcount

    # ---------------------------------------------------------------------------

    def search_column_with(self, column, function="min"):
        """
        Search given column with given aggregation function. This method is intended
        to produce single min or max values for given column name.
        """
        if function not in ("min", "max"):
            raise ValueError("Invalid function for column search")
        sql_raw = f"SELECT {function}({{}}) FROM events"

        query = psycopg2.sql.SQL(sql_raw).format(psycopg2.sql.Identifier(column))
        self.lastquery = self.cursor.mogrify(query)

        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    # ---------------------------------------------------------------------------

    def table_cleanup(self, table, column, ttl):
        """
        Clean expired table records according to given TTL.

        :param str table: Name of the table to cleanup.
        :param str column: Name of the column holding the time information.
        :param datetime.datetime ttl: Maximal valid TTL.
        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute(
            psycopg2.sql.SQL("DELETE FROM {} WHERE {} < %s").format(
                psycopg2.sql.Identifier(table), psycopg2.sql.Identifier(column)
            ),
            (ttl,),
        )
        return self.cursor.rowcount

    # ---------------------------------------------------------------------------

    def threshold_set(self, key, thresholdtime, relapsetime, ttl, report_label):
        """
        Insert new threshold record into the thresholding cache.

        :param str key: Record key to the thresholding cache.
        :param datetime.datetime thresholdtime: Threshold window start time.
        :param datetime.datetime relapsetime: Relapse window start time.
        :param datetime.datetime ttl: Record TTL.
        :param str report_label: Label of the report in which source address was reported.
        """
        self.cursor.execute(
            "INSERT INTO thresholds (id, thresholdtime, relapsetime, ttltime, report_label) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET thresholdtime = EXCLUDED.thresholdtime, relapsetime = EXCLUDED.relapsetime, ttltime = EXCLUDED.ttltime, report_label = EXCLUDED.report_label",
            (key, thresholdtime, relapsetime, ttl, report_label),
        )

    def threshold_check(self, key, ttl):
        """
        Check thresholding cache for record with given key.

        :param str key: Record key to the thresholding cache.
        :param datetime.datetime ttl: Upper TTL boundary for valid record.
        :return: Full cache record as tuple.
        :rtype: tuple
        """
        self.cursor.execute("SELECT * FROM thresholds WHERE id = %s AND ttltime >= %s", (key, ttl))
        return self.cursor.fetchall()

    def threshold_save(self, eventid, keyid, group_name, severity, createtime, is_target, is_shadow):
        """
        Save given event to the list of thresholded events.

        :param str eventid: Unique event identifier.
        :param str keyid: Record key to the thresholding cache.
        :param str group_name: Name of the abuse group.
        :param str severity: Event severity.
        :param datetime.datetime createtime: Record creation time.
        :param bool is_target: is it a target-based event? (or source-based if False).
        :param bool is_shadow: If it is shadow reporting, or normal reporting.
        """
        self.cursor.execute(
            "INSERT INTO events_thresholded (eventid, keyid, groupname, eventseverity, createtime, istarget, isshadow) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (eventid, keyid, group_name, severity, createtime, is_target, is_shadow),
        )

    def thresholds_count(self):
        """
        Count threshold records in thresholding cache.

        :return: Number of records in thresholding cache.
        :rtype: int
        """
        self.cursor.execute(
            "SELECT count(*) FROM thresholds",
        )
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def thresholds_clean(self, ttl):
        """
        Clean no longer valid threshold records from thresholding cache.

        :param datetime.datetime ttl: Maximal valid TTL.
        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute("DELETE FROM thresholds WHERE ttltime < %s", (ttl,))
        return self.cursor.rowcount

    def fetch_thresholds(self):
        """
        Fetches list of tuples containing id and report_label from the thresholds table.

        :return: List of tuples (id, report_label)
        :rtype: list
        """

        self.cursor.execute("SELECT id, report_label FROM thresholds")
        return self.cursor.fetchall()

    def search_relapsed_events(self, group_name, severity, ttl, is_target, is_shadow):
        """
        Search for list of relapsed events for given group, severity and TTL.
        An event is considered relapsed if the following conditions are met:

        * there is a record in ``thresholds`` table with ``thresholds.ttltime <= $ttl``
          (this means that the thresholding window expired)
        * there is a record in ``events_thresholded`` table with ``events_thresholded.createtime >= thresholds.relapsetime``
          (this means that the event was thresholded in the relapse period)

        :param str group_name: Name of the abuse group.
        :param str severity: Event severity.
        :param datetime.datetime ttl: Record TTL time.
        :param bool is_target: Find only target-based events (or source-based if False).
        :param bool is_shadow: Is it shadow reporting (True) or normal reporting (False).
        :return: List of relapsed events as tuple of id, json of event data and list of threshold keys.
        :rtype: list
        """
        # First check that any event was recorded during the relapse period.
        # Last line is there to not report relapsed events with relapse period "none".
        self.cursor.execute(
            f"""
            SELECT DISTINCT events_thresholded.keyid
              FROM events_thresholded
              INNER JOIN thresholds ON events_thresholded.keyid = thresholds.id
              WHERE events_thresholded.groupname = %s
                AND events_thresholded.eventseverity = %s
                AND events_thresholded.createtime >= thresholds.relapsetime
                AND events_thresholded.istarget IS {"TRUE" if is_target else "NOT TRUE"}
                AND events_thresholded.isshadow IS {"TRUE" if is_shadow else "FALSE"}
                AND thresholds.ttltime <= %s
                AND thresholds.relapsetime != thresholds.ttltime
            """,
            (group_name, severity, ttl),
        )
        recorded_during_relapse = self.cursor.fetchall()
        # Extract the key IDs from the result
        key_ids = [record[0] for record in recorded_during_relapse]
        if not key_ids:
            return []

        # Fetch all thresholded events as there is an event recorded during the relapse
        self.cursor.execute(
            f"""
            SELECT events_json.id, events_json.event, ARRAY_AGG(events_thresholded.keyid) AS keyids
            FROM events_json
            INNER JOIN events_thresholded ON events_json.id = events_thresholded.eventid
            INNER JOIN thresholds ON events_thresholded.keyid = thresholds.id
            WHERE events_thresholded.groupname = %s
              AND events_thresholded.eventseverity = %s
              AND events_thresholded.createtime >= thresholds.thresholdtime
              AND events_thresholded.istarget IS {"TRUE" if is_target else "NOT TRUE"}
              AND events_thresholded.isshadow IS {"TRUE" if is_shadow else "FALSE"}
              AND thresholds.ttltime <= %s
              AND thresholds.relapsetime != thresholds.ttltime
              AND events_thresholded.keyid = ANY(%s)
            GROUP BY events_json.id
            """,
            (group_name, severity, ttl, key_ids),
        )
        return self.cursor.fetchall()

    def thresholded_events_count(self):
        """
        Count number of records in list of thresholded events.

        :return: Number of records in list of thresholded events.
        :rtype: int
        """
        self.cursor.execute(
            "SELECT count(*) FROM events_thresholded",
        )
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def thresholded_events_clean(self):
        """
        Clean no longer valid records from list of thresholded events. Record is
        no longer valid in the following case:

        * there is no appropriate record in ``thresholds`` table
          (there is no longer an active thresholding window)

        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute(
            """
            DELETE FROM events_thresholded
            WHERE NOT EXISTS (
                SELECT * FROM thresholds
                WHERE thresholds.id = events_thresholded.keyid
                      AND events_thresholded.createtime > thresholds.thresholdtime
            )
            """
        )
        return self.cursor.rowcount


class incstats_decorator:  # pylint: disable=locally-disabled,too-few-public-methods,invalid-name
    """
    Decorator for calculating usage statistics.
    """

    def __init__(self, stat_name: str, increment: int = 1):
        self.stat_name = stat_name
        self.increment = increment

    def __call__(self, func: F) -> F:
        def wrapped_f(other_self: Any, *args: Any, **kwargs: Any) -> Any:
            other_self.statistics[self.stat_name] = other_self.statistics.get(self.stat_name, 0) + self.increment
            return func(other_self, *args, **kwargs)

        return cast(F, wrapped_f)


class EventStorageService:
    """
    Proxy object for working with persistent SQL based event storages. Maintains
    and provides access to database connection.
    """

    def __init__(self, **conncfg):
        """
        Open and cache connection to event storage. The connection arguments for
        database engine are passed directly to :py:func:`psycopg2.connect`method.

        :param conncfg: Connection arguments.
        """
        conncfg["cursor_factory"] = psycopg2.extras.NamedTupleCursor
        if not hasattr(self, "dsn"):
            self.dsn = conncfg
        self.connection = psycopg2.connect(**self.dsn)
        self.cursor = None
        self.savepoint = None
        self.statistics = {}
        self.cursor_new()

    def __del__(self):
        self.close()

    @staticmethod
    def handle_db_exceptions(func: F) -> F:  # pylint: disable=locally-disabled,no-self-argument
        """
        Handle exceptions raised during database interfacing operations.
        """

        def exc_handle_wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            exc_store = None
            for _ in range(2):
                try:
                    return func(self, *args, **kwargs)  # pylint: disable=locally-disabled,not-callable

                except psycopg2.errors.QueryCanceled as exc:
                    self.rollback()
                    raise QueryCanceledException from exc

                except psycopg2.DataError as err:
                    self.rollback()
                    raise DataError(str(err)) from err

                except (psycopg2.OperationalError, psycopg2.InterfaceError) as err:
                    self.__init__()  # pylint: disable=locally-disabled,unnecessary-dunder-call
                    exc_store = err
                    continue

                except psycopg2.IntegrityError as err:
                    self.rollback()
                    raise StorageIntegrityError(str(err)) from err

                except psycopg2.DatabaseError as err:
                    self.rollback()
                    raise EventStorageException(str(err)) from err

            raise EventStorageException("DB connection error during data access") from exc_store

        return cast(F, exc_handle_wrapper)

    def close(self):
        """
        Close current database connection.
        """
        try:
            self.cursor.close()
            self.connection.close()
        except:  # pylint: disable=locally-disabled,bare-except
            pass
        self.cursor = None
        self.connection = None

    @incstats_decorator("commit")
    def commit(self):
        """
        Commit currently pending changes into persistent storage.
        """
        self.connection.commit()

    @incstats_decorator("commit_bulk")
    def commit_bulk(self):
        """
        Release and commit currently pending savepoint changes.
        """
        self.savepoint_release()
        self.commit()

    @incstats_decorator("rollback")
    def rollback(self):
        """
        Rollback currently pending changes into persistent storage.
        """
        self.connection.rollback()

    @incstats_decorator("savepoint_create")
    def savepoint_create(self):
        """
        Create new savepoint within transaction.
        """
        if not self.savepoint:
            self.savepoint = random_str(10)

        self.cursor.execute(psycopg2.sql.SQL("SAVEPOINT {}").format(psycopg2.sql.Identifier(self.savepoint)))

    @incstats_decorator("savepoint_release")
    def savepoint_release(self):
        """
        Release savepoint within transaction.
        """
        if not self.savepoint:
            raise EventStorageException("Savepoint does not exist in transaction.")

        self.cursor.execute(psycopg2.sql.SQL("RELEASE SAVEPOINT {}").format(psycopg2.sql.Identifier(self.savepoint)))
        self.savepoint = None

    @incstats_decorator("savepoint_rollback")
    def savepoint_rollback(self):
        """
        Rollback to savepoint within transaction.
        """
        if not self.savepoint:
            raise EventStorageException("Savepoint does not exist in transaction.")

        self.cursor.execute(
            psycopg2.sql.SQL("ROLLBACK TO SAVEPOINT {}").format(psycopg2.sql.Identifier(self.savepoint))
        )

    @incstats_decorator("mogrify")
    def mogrify(self, query, parameters):
        """
        Format given SQL query, replace placeholders with given parameters and
        return resulting SQL query as string.
        """
        return self.cursor.mogrify(query, parameters)

    @incstats_decorator("cursor_new")
    def cursor_new(self):
        """
        Create new database cursor.
        """
        if self.cursor:
            self.cursor.close()
        self.cursor = EventStorageCursor(self.connection.cursor())
        return self.cursor

    @handle_db_exceptions
    def database_create(self):
        """
        Create database SQL schema.
        """
        # Base list of CREATE TABLE SQLs.
        create_table_sqls = [
            "CREATE TABLE IF NOT EXISTS events(id text PRIMARY KEY, tlp text, detecttime timestamp NOT NULL, category text[] NOT NULL, description text, source_ip iprange[], target_ip iprange[], source_ip_aggr_ip4 ip4r, source_ip_aggr_ip6 ip6r, target_ip_aggr_ip4 ip4r, target_ip_aggr_ip6 ip6r, source_port integer[], target_port integer[], source_type text[], target_type text[], protocol text[], node_name text[] NOT NULL, node_type text[], storagetime timestamp NOT NULL, resolvedabuses text[], targetabuses text[], eventclass text, targetclass text, eventseverity text, targetseverity text, inspectionerrors text[], shadow_reporting boolean NOT NULL DEFAULT FALSE, shadow_reporting_target boolean NOT NULL DEFAULT FALSE)",
            "CREATE TABLE IF NOT EXISTS events_json(id text PRIMARY KEY REFERENCES events(id) ON DELETE CASCADE, event bytea NOT NULL)",
            "CREATE TABLE IF NOT EXISTS thresholds(id text PRIMARY KEY, thresholdtime timestamp NOT NULL, relapsetime timestamp NOT NULL, ttltime timestamp NOT NULL, report_label VARCHAR)",
            "CREATE TABLE IF NOT EXISTS events_thresholded(eventid text NOT NULL, keyid text NOT NULL, groupname text NOT NULL, eventseverity text NOT NULL, createtime timestamp NOT NULL, istarget boolean NOT NULL, isshadow boolean NOT NULL, PRIMARY KEY(eventid, keyid))",
        ]

        # Generate list of CREATE TABLE SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            create_table_sqls.append(
                psycopg2.sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} (data text UNIQUE NOT NULL, last_seen TIMESTAMP WITHOUT TIME ZONE NOT NULL)"
                ).format(psycopg2.sql.Identifier(f"enum_{column_name}"))
            )

        for query in create_table_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def index_create(self):
        """
        Create default set of table indices.
        """
        # Base list of CREATE INDEX SQLs.
        create_index_sqls = []
        for index_name, index_definition in INDEXES:
            create_index_sqls.append(f"CREATE INDEX IF NOT EXISTS {index_name} {index_definition}")

        # Generate list of CREATE INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            create_index_sqls.append(
                psycopg2.sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} USING BTREE (last_seen)").format(
                    psycopg2.sql.Identifier(f"enum_{column_name}_lastseen_idx"),
                    psycopg2.sql.Identifier(f"enum_{column_name}"),
                )
            )

        for query in create_index_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def database_drop(self):
        """
        Drop database SQL schema.
        """
        # Base list of DROP TABLE SQLs.
        drop_table_sqls = [
            "DROP TABLE IF EXISTS events_json CASCADE",
            "DROP TABLE IF EXISTS events CASCADE",
            "DROP TABLE IF EXISTS thresholds CASCADE",
            "DROP TABLE IF EXISTS events_thresholded CASCADE",
        ]

        # Generate list of CREATE INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            drop_table_sqls.append(
                psycopg2.sql.SQL("DROP TABLE IF EXISTS {}").format(psycopg2.sql.Identifier(f"enum_{column_name}"))
            )

        for query in drop_table_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def index_drop(self):
        """
        Drop default set of table indices.
        """
        # Base list of DROP INDEX SQLs.
        drop_index_sqls = []
        for index_name, _ in INDEXES:
            drop_index_sqls.append(f"DROP INDEX IF EXISTS {index_name}")

        # Generate list of DROP INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            drop_index_sqls.append(
                psycopg2.sql.SQL("DROP INDEX IF EXISTS {} ").format(
                    psycopg2.sql.Identifier(f"enum_{column_name}_lastseen_idx")
                )
            )
        for query in drop_index_sqls:
            self.cursor.execute(query)
            self.commit()

    # ---------------------------------------------------------------------------

    @incstats_decorator("insert_event")
    @handle_db_exceptions
    def insert_event(self, idea_event):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.insert_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.insert_event(idea_event)
        self.commit()

    @incstats_decorator("insert_event_bulkci")
    def insert_event_bulkci(self, idea_event):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.insert_event`
        method.

        This method will NOT automatically commit the insert operation.
        """
        exc_store = None
        for _ in range(2):
            try:
                self.savepoint_create()
                self.cursor.insert_event(idea_event)
                self.savepoint_create()
                return

            except psycopg2.DataError as err:
                self.savepoint_rollback()
                raise DataError(str(err)) from err

            except (psycopg2.OperationalError, psycopg2.InterfaceError) as err:
                self.__init__()  # pylint: disable=locally-disabled,unnecessary-dunder-call
                exc_store = err
                continue

            except psycopg2.IntegrityError as err:
                self.savepoint_rollback()
                raise StorageIntegrityError(str(err)) from err

            except psycopg2.DatabaseError as err:
                self.savepoint_rollback()
                raise EventStorageException(str(err)) from err

        raise EventStorageException("DB connection error during data access") from exc_store

    @incstats_decorator("fetch_event")
    @handle_db_exceptions
    def fetch_event(self, eventid):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.fetch_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.fetch_event(eventid)
        self.commit()
        return result

    @incstats_decorator("delete_event")
    @handle_db_exceptions
    def delete_event(self, eventid):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.delete_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.delete_event(eventid)
        self.commit()

    @incstats_decorator("query_direct")
    @handle_db_exceptions
    def query_direct(self, raw_query, idents=None, params=None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.query_direct`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.query_direct(raw_query, idents, params)
        self.commit()
        return result

    @incstats_decorator("count_events")
    @handle_db_exceptions
    def count_events(self, parameters=None, qname=None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.count_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.count_events(parameters, qname=qname)
        self.commit()
        return result

    @incstats_decorator("search_events")
    @handle_db_exceptions
    def search_events(self, parameters=None, qtype=QTYPE_SELECT, qname=None, user=None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count, result = self.cursor.search_events(parameters, qtype=qtype, qname=qname, user=user)
        self.commit()
        return count, result

    @incstats_decorator("search_events_aggr")
    @handle_db_exceptions
    def search_events_aggr(self, parameters=None, qtype=QTYPE_AGGREGATE, qname=None, dbtoplist=False, user=None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_events_aggr`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.search_events_aggr(parameters, qtype=qtype, qname=qname, dbtoplist=dbtoplist, user=user)
        self.commit()
        return result

    @incstats_decorator("search_column_with")
    @handle_db_exceptions
    def search_column_with(self, column, function="min"):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_column_with`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.search_column_with(column, function)
        self.commit()
        return result

    @incstats_decorator("delete_events")
    @handle_db_exceptions
    def delete_events(self, parameters=None, qname=None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.delete_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.delete_events(parameters, qname=qname)
        self.commit()
        return count

    @incstats_decorator("fetch_enum_values")
    @handle_db_exceptions
    def fetch_enum_values(self, column: str) -> list[str]:
        """
        Fetch and return distinct precomputed values of the specified table column
        from the corresponding enum table.

        This method retrieves the distinct values from a precomputed enum table
        (e.g., `enum_column_name`) associated with the provided column. The table
        is assumed to be updated separately to maintain performance during fetch
        operations.

        Transactions are automatically committed for successful database operations
        and rolled back in case of exceptions.

        :param str column: Name of the column to query for distinct values.
        :return: List of distinct values.
        :rtype: list
        """
        enum_table = f"enum_{column}"
        self.cursor.execute(
            psycopg2.sql.SQL("SELECT data FROM {} ORDER BY data").format(psycopg2.sql.Identifier(enum_table))
        )
        result_raw = self.cursor.fetchall()
        self.commit()
        return [item[0] for item in result_raw if item[0] is not None]

    @incstats_decorator("distinct_values")
    @handle_db_exceptions
    def distinct_values(self, column: str, last_run_ts: str | None = None) -> list[str]:
        """
        Return distinct values of given table column.

        It will automatically commit transaction for successful database operation
        and rollback the invalid one.

        :param str column: Name of the column to query for distinct values.
        :param str last_run_ts: Timestamp of the last run to filter new values.
        :return: List of distinct values.
        :rtype: list
        """
        enum_table = f"enum_{column}"

        # Get last_seen first.
        self.cursor.execute(
            psycopg2.sql.SQL("SELECT max(last_seen) FROM {}").format(psycopg2.sql.Identifier(enum_table))
        )
        last_seen = self.cursor.fetchone()[0]
        self.commit()

        # Build and execute query for updating enumeration table.
        enum_query = psycopg2.sql.SQL("INSERT INTO {} (SELECT * FROM (").format(psycopg2.sql.Identifier(enum_table))
        if column not in (
            "eventclass",
            "targetclass",
            "eventseverity",
            "targetseverity",
            "tlp",
        ):
            enum_query += psycopg2.sql.SQL("SELECT unnest({})").format(psycopg2.sql.Identifier(column))
        else:
            enum_query += psycopg2.sql.SQL("SELECT {}").format(psycopg2.sql.Identifier(column))
        enum_query += psycopg2.sql.SQL(
            " AS data, max(storagetime) AS last_seen FROM events "
            "WHERE storagetime >= COALESCE(%s, %s, (SELECT min(storagetime) FROM events)) "
            "GROUP BY data) AS enum WHERE data IS NOT NULL) ON CONFLICT (data) DO UPDATE SET last_seen = excluded.last_seen"
        )
        # Use the time of the last run before the value of last_seen from the database.
        # Some values may be quite rare and it doesn't make sense to always search all events
        # since the time when this rare value appeared the last time.
        self.cursor.execute(
            enum_query,
            (
                last_run_ts,
                last_seen,
            ),
        )
        self.commit()

        # Return all entries from recently updated enumeration table.
        return self.fetch_enum_values(column)

    @handle_db_exceptions
    def table_cleanup(self, table, column, ttl):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.table_cleanup`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.table_cleanup(table, column, ttl)
        self.commit()
        return count

    @handle_db_exceptions
    def threshold_set(self, key, thresholdtime, relapsetime, ttl, report_label):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_set`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.threshold_set(key, thresholdtime, relapsetime, ttl, report_label)
        self.commit()

    @handle_db_exceptions
    def threshold_check(self, key, threshold):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_check`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.threshold_check(key, threshold)
        self.commit()
        return result

    @handle_db_exceptions
    def threshold_save(self, eventid, keyid, group_name, severity, createtime, is_target, is_shadow):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_save`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.threshold_save(eventid, keyid, group_name, severity, createtime, is_target, is_shadow)
        self.commit()

    @handle_db_exceptions
    def thresholds_count(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholds_count`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.thresholds_count()
        self.commit()
        return result

    @handle_db_exceptions
    def thresholds_clean(self, threshold):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholds_clean`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.thresholds_clean(threshold)
        self.commit()
        return count

    @handle_db_exceptions
    def fetch_thresholds(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.fetch_thresholds`
        method.

        It will automatically commit transaction for successful database operation
        and rollback the invalid one.
        """
        thresholds = self.cursor.fetch_thresholds()
        self.commit()
        return thresholds

    @handle_db_exceptions
    def search_relapsed_events(self, group_name, severity, ttl, is_target, is_shadow):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_relapsed_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        events = self.cursor.search_relapsed_events(group_name, severity, ttl, is_target, is_shadow)
        self.commit()
        return events

    @handle_db_exceptions
    def thresholded_events_count(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholded_events_count`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.thresholded_events_count()
        self.commit()
        return result

    @handle_db_exceptions
    def thresholded_events_clean(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholded_events_clean`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.thresholded_events_clean()
        self.commit()
        return count

    # ---------------------------------------------------------------------------

    def table_status(self, table_name, time_column):
        """
        Determine status of given table within current database.
        """
        result = {}

        self.cursor.execute(
            psycopg2.sql.SQL(
                "SELECT *, pg_size_pretty(total_bytes) AS total\
                    , pg_size_pretty(index_bytes) AS INDEX\
                    , pg_size_pretty(toast_bytes) AS toast\
                    , pg_size_pretty(table_bytes) AS TABLE\
                FROM (\
                    SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (\
                        SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME\
                            , c.reltuples AS row_estimate\
                            , pg_total_relation_size(c.oid) AS total_bytes\
                            , pg_indexes_size(c.oid) AS index_bytes\
                            , pg_total_relation_size(reltoastrelid) AS toast_bytes\
                        FROM pg_class c\
                        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace\
                        WHERE relkind = 'r' AND relname = %s\
                    ) a\
                ) a;"
            ),
            [table_name],
        )
        data_raw = self.cursor.fetchone()
        self.commit()
        result.update(
            table_name=data_raw.table_name,
            row_estimate=data_raw.row_estimate,
            total_bytes=data_raw.total_bytes,
            index_bytes=data_raw.index_bytes,
            toast_bytes=data_raw.toast_bytes,
            table_bytes=data_raw.table_bytes,
            total_bytes_str=data_raw.total,
            index_bytes_str=data_raw.index,
            toast_bytes_str=data_raw.toast,
            table_bytes_str=data_raw.table,
        )

        if time_column:
            self.cursor.execute(
                psycopg2.sql.SQL("SELECT MIN({}) as minvalue FROM {}").format(
                    psycopg2.sql.Identifier(time_column),
                    psycopg2.sql.Identifier(table_name),
                )
            )
            record = self.cursor.fetchone()
            self.commit()
            if record:
                result["dt_oldest"] = record.minvalue

            self.cursor.execute(
                psycopg2.sql.SQL("SELECT MAX({}) as maxvalue FROM {}").format(
                    psycopg2.sql.Identifier(time_column),
                    psycopg2.sql.Identifier(table_name),
                )
            )
            record = self.cursor.fetchone()
            self.commit()
            if record:
                result["dt_newest"] = record.maxvalue

        return result

    def database_status(self, brief=False):
        """
        Determine status of all tables within current database and general
        PostgreSQL configuration.
        """
        result = {"tables": {}}

        # ---

        if not brief:
            self.cursor.execute("SELECT * FROM pg_settings")
            records = self.cursor.fetchall()
            self.commit()
            result["pg_settings"] = {rec.name: rec for rec in records}

        # ---

        table_wanted_list = [
            ("events", "storagetime"),
            ("events_json", None),
            ("events_thresholded", "createtime"),
            ("thresholds", "ttltime"),
        ]
        for column_name in ENUM_TABLES:
            table_wanted_list.append((f"enum_{column_name}", "last_seen"))

        for table_name in table_wanted_list:
            result["tables"][table_name[0]] = self.table_status(*table_name)

        return result

    def queries_status(self, qpattern=None, discard_parallel_workers=True):
        """
        Determine status of all currently running queries.
        """
        result = []

        # ---

        if not qpattern:
            self.cursor.execute(
                "SELECT *, now() - pg_stat_activity.query_start AS query_duration FROM pg_stat_activity WHERE datname = (SELECT current_database())"
            )
        else:
            self.cursor.execute(
                f"SELECT *, now() - pg_stat_activity.query_start AS query_duration FROM pg_stat_activity WHERE datname = (SELECT current_database()) AND query ~ '{qpattern}'"
            )
        records = self.cursor.fetchall()
        self.commit()
        for data_raw in records:
            subres = {
                "datid": data_raw.datid,
                "datname": data_raw.datname,
                "pid": data_raw.pid,
                "usesysid": data_raw.usesysid,
                "usename": data_raw.usename,
                "application_name": data_raw.application_name,
                "client_addr": data_raw.client_addr,
                "client_hostname": data_raw.client_hostname,
                "client_port": data_raw.client_port,
                "backend_start": data_raw.backend_start,
                "xact_start": data_raw.xact_start,
                "query_start": data_raw.query_start,
                "state_change": data_raw.state_change,
                "wait_event_type": data_raw.wait_event_type,
                "wait_event": data_raw.wait_event,
                "state": data_raw.state,
                "backend_xid": data_raw.backend_xid,
                "backend_xmin": data_raw.backend_xmin,
                "query": data_raw.query,
                "query_duration": data_raw.query_duration,
                "backend_type": data_raw.backend_type,
            }
            if discard_parallel_workers and subres["backend_type"] == "parallel worker":
                continue
            re_match = RE_QNAME_CMPL.search(subres["query"])
            if re_match is not None:
                subres["query_name"] = re_match.group(1)
            result.append(subres)

        return result

    def query_status(self, qname):
        """
        Determine status of given query.
        """
        qname = rf"_mentatq\({qname}\)_"

        self.cursor.execute(
            f"SELECT *, now() - pg_stat_activity.query_start AS query_duration FROM pg_stat_activity WHERE datname = (SELECT current_database()) AND query ~ '{qname}'"
        )
        data_raw = self.cursor.fetchone()
        self.commit()
        if not data_raw:
            return {}

        result = {
            "datid": data_raw.datid,
            "datname": data_raw.datname,
            "pid": data_raw.pid,
            "usesysid": data_raw.usesysid,
            "usename": data_raw.usename,
            "application_name": data_raw.application_name,
            "client_addr": data_raw.client_addr,
            "client_hostname": data_raw.client_hostname,
            "client_port": data_raw.client_port,
            "backend_start": data_raw.backend_start,
            "xact_start": data_raw.xact_start,
            "query_start": data_raw.query_start,
            "state_change": data_raw.state_change,
            "wait_event_type": data_raw.wait_event_type,
            "wait_event": data_raw.wait_event,
            "state": data_raw.state,
            "backend_xid": data_raw.backend_xid,
            "backend_xmin": data_raw.backend_xmin,
            "query": data_raw.query,
            "query_duration": data_raw.query_duration,
            "backend_type": data_raw.backend_type,
        }
        re_match = RE_QNAME_CMPL.search(result["query"])
        if re_match is not None:
            result["query_name"] = re_match.group(1)

        return result

    def query_cancel(self, qname):
        """
        Cancel given query.
        """
        qname = rf"_mentatq\({qname}\)_"

        self.cursor.execute(
            f"SELECT pg_cancel_backend(pid) AS opresult FROM pg_stat_activity WHERE datname = (SELECT current_database()) AND query ~ '{qname}' AND backend_type = 'client backend'"
        )
        data_raw = self.cursor.fetchone()
        self.commit()
        if data_raw:
            return data_raw.opresult
        return None


class EventStorageServiceManager:
    """
    Class representing a custom _EventStorageServiceManager_ capable of understanding
    and parsing Mentat system core configurations.
    """

    def __init__(self, core_config, updates=None):
        """
        Initialize a _EventStorageServiceManager_ proxy object with full core configuration
        tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = {}
        self._storage = None
        self._configure_dbconfig(core_config, updates)

    def _configure_dbconfig(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = copy.deepcopy(core_config[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_EVENTSTORAGE])

        if updates and CKEY_CORE_DATABASE in updates and CKEY_CORE_DATABASE_EVENTSTORAGE in updates[CKEY_CORE_DATABASE]:
            self._dbconfig.update(updates[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_EVENTSTORAGE])

    # ---------------------------------------------------------------------------

    def close(self):
        """
        Close internal storage connection.
        """
        if self._storage:
            self._storage.close()
            self._storage = None

    def service(self):
        """
        Return handle to storage connection service according to internal configurations.

        :return: Reference to storage service.
        :rtype: mentat.services.eventstorage.EventStorageService
        """
        if not self._storage:
            self._storage = EventStorageService(**self._dbconfig)
        return self._storage


# -------------------------------------------------------------------------------


def init(core_config, updates=None):
    """
    (Re-)Initialize :py:class:`mentat.services.eventstorage.EventStorageServiceManager`
    instance at module level and store the refence within module.

    :param dict core_config: Mentat core configuration structure.
    :param dict updates: Optional configuration updates (same structure as ``core_config``).
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = EventStorageServiceManager(core_config, updates)


def set_manager(man):
    """
    Set manager from outside of the module. This should be used only when you know
    exactly what you are doing.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = man


def manager():
    """
    Obtain reference to :py:class:`mentat.services.eventstorage.EventStorageServiceManager`
    instance stored at module level.

    :return: Storage service manager reference.
    :rtype: mentat.services.eventstorage.EventStorageServiceManager
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`mentat.services.eventstorage.EventStorageService`
    instance from module level manager.

    :return: Storage service reference.
    :rtype: mentat.services.eventstorage.EventStorageService
    """
    return manager().service()


def close():
    """
    Close database connection on :py:class:`mentat.services.eventstorage.EventStorageService`
    instance from module level manager.
    """
    return manager().close()


#
# Register custom psycopg2 adapter for adapting lists of IP addressess into SQL
# query.
#
psycopg2.extensions.register_adapter(mentat.idea.sqldb.IPList, IPListAdapter)
psycopg2.extensions.register_adapter(ipranges.IPBase, IPBaseAdapter)
