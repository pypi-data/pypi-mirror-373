#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains various usefull utilities for *Hawat* application.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import copy
import csv
import datetime
import functools
import json
import math
import os
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final, NamedTuple, Optional, Self, TypeVar, cast

if TYPE_CHECKING:
    from hawat.forms import HawatBaseForm


class UrlParamRule(NamedTuple):
    """
    Named tuple for URL parameter rule.
    """

    key: str
    func_update: Callable[[dict[str, Any], str, Any], None]
    """
    Callable for updating URL parameter dictionary with given key and value.
    """

    as_list: bool
    """
    Indication that the rule parameter can be a list of multiple values.
    """

    optional: bool


class _ExcludeFromParamsType:
    """
    Type for marking values that should be excluded from parameters.
    """

    def __bool__(self) -> bool:
        return False


class URLParamsBuilder:
    """
    Small utility class for building URL parameter dictionaries for various view
    endpoints.
    """

    EXCLUDE: Final = _ExcludeFromParamsType()
    """Value signifying that the parameter should be excluded from the URL parameters entirely"""

    rules: list[UrlParamRule]
    kwrules: list[UrlParamRule]
    _used_keys: set[str]
    _insignificant_keys: set[str]
    """Keys contained within this set will be ignored when checking for context relevance."""

    _skeleton: dict[str, Any]

    def __init__(self, skeleton: Optional[dict[str, Any]] = None) -> None:
        self.rules = []
        self.kwrules = []
        self._skeleton = skeleton or {}
        self._used_keys = set(self._skeleton.keys())
        self._insignificant_keys = set()

    @property
    def skeleton(self) -> dict[str, Any]:
        return {k: v for k, v in self._skeleton.items() if v is not self.EXCLUDE}

    @staticmethod
    def _add_scalar(dst: dict[str, Any], key: str, val: Any) -> None:
        if val is URLParamsBuilder.EXCLUDE:
            return
        if val is not None:
            dst[key] = val

    def _add_rule(self, rule: UrlParamRule) -> None:
        if rule.key in self._used_keys:
            raise ValueError(
                f"Key '{rule.key}' is already used. If using in combination with the `add_kwrule_from_form` method, use it last."
            )
        self.rules.append(rule)
        self._used_keys.add(rule.key)

    def _add_kwrule(self, rule: UrlParamRule, insignificant: bool) -> None:
        if rule.key in self._used_keys:
            raise ValueError(
                f"Key '{rule.key}' is already used. If using in combination with the `add_kwrule_from_form` method, use it last."
            )
        self.kwrules.append(rule)
        self._used_keys.add(rule.key)
        if insignificant:
            self._insignificant_keys.add(rule.key)

    @staticmethod
    def _add_vector(dst: dict[str, Any], key: str, val: list[Any] | Any) -> None:
        if val is URLParamsBuilder.EXCLUDE:
            return
        if isinstance(val, list):
            dst.setdefault(key, []).extend(val)
        elif val is not None:
            dst.setdefault(key, []).append(val)

    def add_rule(self, key: str, as_list: bool = False, optional: bool = False) -> Self:
        """
        Add new rule to URL parameter builder.

        :param str key: Name of the rule key.
        :param bool as_list: Indication that the rule parameter is a list of multiple values.
        :param bool optional: Indication that the rule parameter is optional.
        """
        rule = UrlParamRule(key, self._add_vector if as_list else self._add_scalar, as_list, optional)
        self._add_rule(rule)
        return self

    def add_kwrule(
        self,
        key: str,
        as_list: bool = False,
        optional: bool = False,
        insignificant: bool = False,
    ) -> Self:
        """
        Add new keyword rule to URL parameter builder.

        :param str key: Name of the rule key.
        :param bool as_list: Indication that the rule parameter is a list of multiple values.
        :param bool optional: Indication that the rule parameter is optional.
        :param bool insignificant: Indication that the rule parameter should be ignored in context relevance checks.
        """
        rule = UrlParamRule(key, self._add_vector if as_list else self._add_scalar, as_list, optional)
        self._add_kwrule(rule, insignificant)
        return self

    def add_kwrules_from_form(self, form: type["HawatBaseForm"]) -> Self:
        """
        Add keyword rules from given form.
        Will not override existing rules.

        :param BaseItemForm form: Form to extract keyword rules from.
        """
        for field_name in form.get_field_names():
            if field_name in self._used_keys or form.is_csag_context_excluded(field_name):
                continue  # Do not override existing rules
            as_list = form.is_multivalue(field_name)
            rule = UrlParamRule(
                field_name,
                self._add_vector if as_list else self._add_scalar,
                as_list,
                True,
            )
            self._add_kwrule(rule, form.is_csag_context_insignificant(field_name))

        return self

    def get_params(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Get URL parameters as dictionary with filled-in values.
        """
        tmp = self.skeleton
        for idx, rule in enumerate(self.rules):
            try:
                rule.func_update(tmp, rule.key, args[idx])
            except IndexError:
                if not rule.optional:
                    raise

        for rule in self.kwrules:
            if rule.key in kwargs:
                rule.func_update(tmp, rule.key, kwargs[rule.key])
            elif not rule.optional:
                raise ValueError(f"Missing keyword argument '{rule.key}'")
        return tmp

    def is_context_relevant(self, **kwargs: Any) -> bool:
        """
        Check if any of the given keyword arguments are relevant to the stored URL parameters.
        """
        return any(
            rule.key not in self._insignificant_keys
            and kwargs.get(rule.key)
            and (
                not isinstance(kwargs[rule.key], list)
                or any(kwargs[rule.key])  # Check if the list contains non-empty values
            )
            for rule in self.kwrules
        )


class LimitCounter:
    """
    Simple configurable limit counter with support for multiple keys.
    """

    def __init__(self, limit):
        self.counters = {}
        self.limit = limit

    def count_and_check(self, key, increment=1):
        """
        Increment key counter and check against internal limit.
        """
        self.counters[key] = self.counters.get(key, 0) + increment
        return self.counters[key] <= self.limit


# ------------------------------------------------------------------------------


def get_timedelta(tstamp):
    """
    Get timedelta from current UTC time and given datetime object.

    :param datetime.datetime: Datetime of the lower timedelta boundary.
    :return: Timedelta object.
    :rtype: datetime.timedelta
    """
    return datetime.datetime.utcnow() - tstamp


def get_datetime_utc(aware=False):
    """
    Get current UTC datetime.

    :return: Curent UTC datetime.
    :rtype: datetime.datetime
    """
    if aware:
        return datetime.datetime.now(datetime.UTC)
    return datetime.datetime.utcnow()


def parse_datetime(dtstring):
    """
    Parse given datetime string.

    :param str dtstring: Datetime string in ISON format to parse.
    :return: Curent UTC datetime.
    :rtype: datetime.datetime
    """
    return datetime.datetime.fromisoformat(dtstring)


def get_datetime_local():
    """
    Get current local timestamp.

    :return: Curent local timestamp.
    :rtype: datetime.datetime
    """
    return datetime.datetime.now()


def check_file_exists(filename):
    """
    Check, that given file exists in the filesystem.

    :param str filename: Name of the file to check.
    :return: Existence flag as ``True`` or ``False``.
    :rtype: bool
    """
    return os.path.isfile(filename)


def in_query_params(haystack, needles, on_true=True, on_false=False, on_empty=False):
    """
    Utility method for checking that any needle from given list of needles is
    present in given haystack.
    """
    if not haystack:
        return on_empty
    for needle in needles:
        if needle in haystack:
            return on_true
    return on_false


def generate_query_params(baseparams, updates):
    """
    Generate query parameters for GET method form.

    :param dict baseparams: Original query parameters.
    :param dict updates: Updates for query parameters.
    :return: Deep copy of original parameters modified with given updates.
    :rtype: dict
    """
    result = copy.deepcopy(baseparams)
    result.update(updates)
    return result


def parse_csv(content, delimiter):
    """
    Used to parse CSV from attachments in IDEA.
    If it is unable to parse as CSV, None is returned.

    :param str content: string from Attach.Content in IDEA message.
    :param str delimiter: delimiter used in the file (comma, tab...).
    :return Optional[List[List[str]]]: list of parsed lines, or None if unable to parse.
    """
    try:
        return list(csv.reader(content.splitlines(), delimiter=delimiter))
    except Exception:
        return None


def get_uuid4():
    """
    Generate random UUID identifier.
    """
    return uuid.uuid4()


def load_json_from_file(filename):
    """
    Load JSON from given file.
    """
    with open(filename, encoding="utf8") as fhnd:
        return json.load(fhnd)


def make_copy_deep(data):
    """
    Make a deep copy of given data structure.
    """
    return copy.deepcopy(data)


def get_format_byte_size_function(
    format_func: Callable[[float], str] = lambda x: f"{x:.4g}", base: int = 1024
) -> Callable[[int], str]:
    def format_byte_size(size: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]

        if size == 0:
            return f"{format_func(0.0)} B"

        exponent = min(int(math.log(abs(size), base)), len(units) - 1)
        val = size / (base**exponent)
        return f"{format_func(val)} {units[exponent]}"

    return format_byte_size


F = TypeVar("F", bound=Callable[..., str])


def fallback_formatter(formatter: F, fallback: str = "🗙") -> F:
    """
    Returns wrapped formatter function so that when the formatter function
    fails with an exception, fallback string is returned instead.
    """

    @functools.wraps(formatter)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return formatter(*args, **kwargs)
        except Exception:
            return fallback

    return cast(F, wrapper)
