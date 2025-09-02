#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains base implementation of generic reporting class. It provides
common methods and utilities usefull for all kinds of reporters like:

* Jinja2 template rendering
* report localization
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import gettext
import os
import time
import urllib.parse

import jinja2
from babel.dates import UTC, format_datetime, format_timedelta, get_timezone
from babel.numbers import format_decimal

BABEL_RFC3339_FORMAT = "yyyy-MM-ddTHH:mm:ssZZZ"
"""
RFC3339 compliant time format specifier for Babel format_datetime function.

Resources: http://babel.pocoo.org/en/latest/dates.html#date-fields
"""


class BaseReporter:
    """
    Implementation of base reporting class providing following features and
    services:

    * ``self.renderer`` - Jinja2 template rendering
    * ``self.translator`` - report localization
    """

    def __init__(
        self,
        logger,
        reports_dir,
        templates_dir,
        locale="en",
        timezone="UTC",
        translations_dir=None,
    ):
        """
        :param str reports_dir: Name of the directory containing generated report files.
        :param str templates_dir: Name of the directory containing report template files.
        :param str locale: Locale for report rendering.
        :param str timezone: Timezone for report rendering.
        """
        self.logger = logger
        self.reports_dir = reports_dir
        self.templates_dir = templates_dir
        self.translations_dir = (
            translations_dir
            if translations_dir is not None
            else ";".join(os.path.join(directory, "translations") for directory in templates_dir.split(";"))
        )

        self.locale = None
        self.timezone = None
        self.tzinfo = None
        self.local_tz_name = time.localtime().tm_zone
        self.local_tz_offset = datetime.timedelta(seconds=time.localtime().tm_gmtoff)

        self.set_locale(locale)
        self.set_timezone(timezone)

        self.translations = {}
        self.renderer = self._setup_renderer(self.templates_dir)

    def _setup_renderer(self, templates_dir):
        """
        Setup Jinja2 template renderer.

        :param str templates_dir: Directory containing Jinja2 templates.
        :return: Renderer as Jinja2 environment object.
        :rtype: jinja2.Environment
        """
        templates_dirs = self.templates_dir.split(";")
        if len(templates_dirs) == 1:
            renderer = jinja2.Environment(
                loader=jinja2.FileSystemLoader(self.templates_dir),
                extensions=["jinja2.ext.i18n"],
            )
        else:
            renderer = jinja2.Environment(
                loader=jinja2.ChoiceLoader([jinja2.FileSystemLoader(x) for x in templates_dirs]),
                extensions=["jinja2.ext.i18n"],
            )

        #
        # Ignore Pylint warnings, we need lambdas to create closures. Otherwise
        # set_locale() does not have any effect.
        renderer.install_gettext_callables(
            lambda x: self.translator.gettext(x),  # pylint: disable=locally-disabled,unnecessary-lambda
            lambda s, p, n: self.translator.ngettext(s, p, n),  # pylint: disable=locally-disabled,unnecessary-lambda
            newstyle=True,
        )

        renderer.globals["logger"] = self.logger

        renderer.globals["get_locale"] = lambda: self.locale
        renderer.globals["get_timezone"] = lambda: self.timezone
        renderer.globals["get_timezone_local"] = lambda: self.local_tz_name

        renderer.globals["format_decimal"] = self.format_decimal
        renderer.globals["format_datetime"] = self.format_datetime
        renderer.globals["format_localdatetime"] = self.format_localdatetime
        renderer.globals["format_tzdatetime"] = self.format_tzdatetime
        renderer.globals["format_rfctzdatetime"] = self.format_rfctzdatetime
        renderer.globals["format_custom_datetime"] = self.format_custom_datetime
        renderer.globals["format_timedelta"] = self.format_timedelta
        renderer.globals["format_url"] = self.format_url

        renderer.globals["sum_list"] = sum
        renderer.globals["sum_dict"] = lambda x: sum(x.values())

        renderer.globals["sort_keys_desc"] = lambda x: sorted(sorted(x.keys()), key=lambda y: x[y], reverse=True)

        return renderer

    # ---------------------------------------------------------------------------

    def set_locale(self, locale):
        """
        Change internal locale to different value.

        :param str locale: New locale as string.
        """
        self.locale = locale

    def set_timezone(self, timezone):
        """
        Change internal timezone to different value.

        :param str timezone: New timezone as string.
        """
        self.timezone = timezone
        if self.timezone != "UTC":
            self.tzinfo = get_timezone(self.timezone)
        else:
            self.tzinfo = UTC

    @property
    def translator(self):
        """
        Return translator for currently active locale.
        """
        if self.locale not in self.translations:
            self.translations[self.locale] = gettext.NullTranslations()
            for tdir in self.translations_dir.split(";"):
                try:
                    translation = gettext.translation("messages", tdir, [self.locale])
                    translation.add_fallback(self.translations[self.locale])
                    self.translations[self.locale] = translation
                except OSError:
                    continue
        return self.translations[self.locale]

    # ---------------------------------------------------------------------------

    def format_decimal(self, val):
        """
        Simple wrapper around :py:func:babel.numbers.format_decimal` function
        that takes care of figuring out the appropriate locale.
        """
        return format_decimal(val, locale=self.locale)

    def get_datetime(self, val):
        """
        Method tries parse datetime if provided with string, otherwise return val directly.
        """
        if isinstance(val, str):
            try:
                return datetime.datetime.fromisoformat(val)
            except Exception:
                pass
        return val

    def format_datetime(self, val):
        """
        Simple wrapper around :py:func:babel.dates.format_datetime` function
        that takes care of figuring out the appropriate locale.
        """
        val = self.get_datetime(val)
        return format_datetime(val, locale=self.locale)

    def format_localdatetime(self, val):
        """
        Simple wrapper around :py:func:babel.dates.format_datetime` function
        that takes care of figuring out the appropriate locale and prints the
        datetime in local timezone (local to the server).
        """
        val = self.get_datetime(val)
        epoch = time.mktime(val.timetuple())
        offset = datetime.datetime.fromtimestamp(epoch) - datetime.datetime.utcfromtimestamp(epoch)
        return format_datetime(val + offset, locale=self.locale)

    def format_tzdatetime(self, val):
        """
        Simple wrapper around :py:func:babel.dates.format_datetime` function
        that takes care of figuring out the appropriate locale and prints the
        datetime in configured timezone.
        """
        val = self.get_datetime(val)
        if self.timezone != "UTC":
            return format_datetime(val, tzinfo=self.tzinfo, locale=self.locale)
        return format_datetime(val, locale=self.locale)

    def format_rfctzdatetime(self, val):
        """
        Simple wrapper around :py:func:babel.dates.format_datetime` function
        that prints the datetime in configured timezone and enforced RFC 3339
        format.
        """
        val = self.get_datetime(val)
        if self.timezone != "UTC":
            return format_datetime(val, BABEL_RFC3339_FORMAT, tzinfo=self.tzinfo, locale=self.locale)
        return format_datetime(val, BABEL_RFC3339_FORMAT, locale=self.locale)

    def format_custom_datetime(self, val, custom_format):
        """
        Simple wrapper around :py:func:babel.dates.format_datetime` function
        that prints the datetime in custom format.
        If the timezone is not UTC, print time in UTC in brackets.
        """
        val = self.get_datetime(val)
        if self.timezone == "UTC":
            return format_datetime(val, custom_format, locale=self.locale)
        if self.timezone != "UTC":
            return (
                f"{format_datetime(val, custom_format, tzinfo=self.tzinfo, locale=self.locale)}"
                f" ({format_datetime(val, custom_format, tzinfo=datetime.UTC, locale=self.locale)})"
            )
        return None

    def format_timedelta(self, val):
        """
        Simple wrapper around :py:func:babel.dates.format_timedelta` function
        that takes care of figuring out the appropriate locale.
        """
        return format_timedelta(val, locale=self.locale)

    def format_url(self, base_url, query_params=None):
        """
        Format given base URL and optional query parameters into valid URL.
        """
        result = base_url
        if query_params:
            result = "?".join(
                [
                    result,
                    "&".join(
                        [
                            f"{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(query_params[key])}"
                            for key in sorted(query_params.keys())
                        ]
                    ),
                ]
            )
        return result
