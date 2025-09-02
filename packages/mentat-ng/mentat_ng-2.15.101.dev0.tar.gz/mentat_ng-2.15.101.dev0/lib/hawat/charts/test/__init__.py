#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# ------------------------------------------------------------------------------


"""
Tests for :py:mod:`hawat.charts`.
"""

import datetime
import json
import unittest

import pandas as pd
import plotly.io as pio

from hawat import charts
from hawat.charts import chart_configuration
from hawat.test import HawatTestCase
from hawat.test.runner import TestRunnerMixin
from mentat.stats.idea import TimelineCFG


class ChartsTestCase(TestRunnerMixin, HawatTestCase):
    """
    Class for testing :py:class:`hawat.charts`.
    """

    def test_get_datetime_format_function_utc_10min_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 10, 11),
                datetime.datetime(2020, 1, 1, 0, 20, 42),
            ],
            forced_timezone="UTC",
        )

        self.assertEqual(res, ["2020-01-01 00:00", "2020-01-01 00:10", "2020-01-01 00:20"])

    def test_get_datetime_format_function_utc_10sec_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 0, 10),
                datetime.datetime(2020, 1, 1, 0, 0, 20),
            ],
            forced_timezone="UTC",
        )

        self.assertEqual(res, ["2020-01-01 00:00:00", "2020-01-01 00:00:10", "2020-01-01 00:00:20"])

    def test_get_datetime_format_function_utc_05sec_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 0, 0, 500000),
                datetime.datetime(2020, 1, 1, 0, 0, 1),
            ],
            forced_timezone="UTC",
        )

        self.assertEqual(res, ["2020-01-01 00:00:00", "2020-01-01 00:00:00.5", "2020-01-01 00:00:01"])

    def test_get_datetime_format_function_utc_2day_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 3, 0, 0, 0),
                datetime.datetime(2020, 1, 5, 0, 0, 0),
            ],
            forced_timezone="UTC",
        )

        self.assertEqual(res, ["2020-01-01", "2020-01-03", "2020-01-05"])

    def test_get_datetime_format_function_npt_10min_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 10, 11),
                datetime.datetime(2020, 1, 1, 0, 20, 42),
            ],
            forced_timezone="Asia/Kathmandu",
        )
        self.assertEqual(res, ["2020-01-01 05:45", "2020-01-01 05:55", "2020-01-01 06:05"])

    def test_get_datetime_format_function_npt_10sec_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 0, 10),
                datetime.datetime(2020, 1, 1, 0, 0, 20),
            ],
            forced_timezone="Asia/Kathmandu",
        )

        self.assertEqual(res, ["2020-01-01 05:45:00", "2020-01-01 05:45:10", "2020-01-01 05:45:20"])

    def test_get_datetime_format_function_npt_05sec_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0, 0),
                datetime.datetime(2020, 1, 1, 0, 0, 0, 500000),
                datetime.datetime(2020, 1, 1, 0, 0, 1),
            ],
            forced_timezone="Asia/Kathmandu",
        )

        self.assertEqual(res, ["2020-01-01 05:45:00", "2020-01-01 05:45:00.5", "2020-01-01 05:45:01"])

    def test_get_datetime_format_function_npt_2day_step(self):
        """
        Test the function :py:func:`hawat.charts.chart_configuration._format_ticks`.
        """
        res = chart_configuration._format_ticks(  # pylint: disable=locally-disabled,protected-access
            [
                datetime.datetime(2020, 1, 1, 0, 0, 0),
                datetime.datetime(2020, 1, 3, 0, 0, 0),
                datetime.datetime(2020, 1, 5, 0, 0, 0),
            ],
            forced_timezone="Asia/Kathmandu",
        )

        self.assertEqual(res, ["2020-01-01", "2020-01-03", "2020-01-05"])

    def test_get_secondary_chart_and_table_dataframe(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {"test_chart": {"b": 2, "a": 1, "c": 3}},
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
            ),
            charts.InputDataFormat.WIDE_COMPLEX,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {"set": "b", "count": 2, "__SHARE__": 2 / 6},
                {"set": "a", "count": 1, "__SHARE__": 1 / 6},
                {"set": "c", "count": 3, "__SHARE__": 3 / 6},
            ]
        )
        self.assertTrue(
            (scd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nbut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_secondary_chart_and_table_dataframe_sort(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {"test_chart": {"b": 2, "a": 1, "c": 3}},
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
            ),
            charts.InputDataFormat.WIDE_COMPLEX,
            sort=True,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {"set": "c", "count": 3, "__SHARE__": 3 / 6},
                {"set": "b", "count": 2, "__SHARE__": 2 / 6},
                {"set": "a", "count": 1, "__SHARE__": 1 / 6},
            ]
        )
        self.assertTrue(
            (scd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nbut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_secondary_chart_and_table_dataframe_rest1(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {
                "test_chart": {
                    "b": 2,
                    "a": 1,
                    "c": 3,
                    "d": 4,
                    "e": 5,
                    "f": 6,
                    "g": 7,
                    "h": 8,
                    "i": 9,
                    "j": 10,
                    "k": 11,
                    "l": 12,
                    "m": 13,
                    "n": 14,
                    "o": 15,
                    "p": 16,
                    "q": 17,
                    "r": 18,
                    "s": 19,
                    "t": 20,
                }
            },
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
            ),
            charts.InputDataFormat.WIDE_COMPLEX,
            sort=True,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {"set": "t", "count": 20, "__SHARE__": 20 / 210},
                {"set": "s", "count": 19, "__SHARE__": 19 / 210},
                {"set": "r", "count": 18, "__SHARE__": 18 / 210},
                {"set": "q", "count": 17, "__SHARE__": 17 / 210},
                {"set": "p", "count": 16, "__SHARE__": 16 / 210},
                {"set": "o", "count": 15, "__SHARE__": 15 / 210},
                {"set": "n", "count": 14, "__SHARE__": 14 / 210},
                {"set": "m", "count": 13, "__SHARE__": 13 / 210},
                {"set": "l", "count": 12, "__SHARE__": 12 / 210},
                {"set": "k", "count": 11, "__SHARE__": 11 / 210},
                {"set": "j", "count": 10, "__SHARE__": 10 / 210},
                {"set": "i", "count": 9, "__SHARE__": 9 / 210},
                {"set": "h", "count": 8, "__SHARE__": 8 / 210},
                {"set": "g", "count": 7, "__SHARE__": 7 / 210},
                {"set": "f", "count": 6, "__SHARE__": 6 / 210},
                {"set": "e", "count": 5, "__SHARE__": 5 / 210},
                {"set": "d", "count": 4, "__SHARE__": 4 / 210},
                {"set": "c", "count": 3, "__SHARE__": 3 / 210},
                {"set": "b", "count": 2, "__SHARE__": 2 / 210},
                {"set": "a", "count": 1, "__SHARE__": 1 / 210},
            ]
        )
        self.assertTrue(
            (scd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nbut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_secondary_chart_and_table_dataframe_rest2(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {
                "test_chart": {
                    "b": 2,
                    "a": 1,
                    "c": 3,
                    "d": 4,
                    "e": 5,
                    "f": 6,
                    "g": 7,
                    "h": 8,
                    "i": 9,
                    "j": 10,
                    "k": 11,
                    "l": 12,
                    "m": 13,
                    "n": 14,
                    "o": 15,
                    "p": 16,
                    "q": 17,
                    "r": 18,
                    "s": 19,
                    "t": 20,
                    "u": 21,
                }
            },
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.SINGLE,
            ),
            charts.InputDataFormat.WIDE_COMPLEX,
            add_rest=True,
            sort=True,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {"set": "u", "count": 21, "__SHARE__": 21 / 231},
                {"set": "t", "count": 20, "__SHARE__": 20 / 231},
                {"set": "s", "count": 19, "__SHARE__": 19 / 231},
                {"set": "r", "count": 18, "__SHARE__": 18 / 231},
                {"set": "q", "count": 17, "__SHARE__": 17 / 231},
                {"set": "p", "count": 16, "__SHARE__": 16 / 231},
                {"set": "o", "count": 15, "__SHARE__": 15 / 231},
                {"set": "n", "count": 14, "__SHARE__": 14 / 231},
                {"set": "m", "count": 13, "__SHARE__": 13 / 231},
                {"set": "l", "count": 12, "__SHARE__": 12 / 231},
                {"set": "k", "count": 11, "__SHARE__": 11 / 231},
                {"set": "j", "count": 10, "__SHARE__": 10 / 231},
                {"set": "i", "count": 9, "__SHARE__": 9 / 231},
                {"set": "h", "count": 8, "__SHARE__": 8 / 231},
                {"set": "g", "count": 7, "__SHARE__": 7 / 231},
                {"set": "f", "count": 6, "__SHARE__": 6 / 231},
                {"set": "e", "count": 5, "__SHARE__": 5 / 231},
                {"set": "d", "count": 4, "__SHARE__": 4 / 231},
                {"set": "c", "count": 3, "__SHARE__": 3 / 231},
                {"set": "__REST__", "count": 3, "__SHARE__": 3 / 231},
            ]
        )
        self.assertTrue(
            (scd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nBut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_secondary_chart_and_table_dataframe_wide_simple(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {
                "b": 2,
                "a": 1,
                "c": 3,
                "d": 4,
                "e": 5,
                "f": 6,
                "g": 7,
                "h": 8,
                "i": 9,
                "j": 10,
                "k": 11,
                "l": 12,
                "m": 13,
                "n": 14,
                "o": 15,
                "p": 16,
                "q": 17,
                "r": 18,
                "s": 19,
                "t": 20,
                "u": 21,
            },
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
                data_keys=[
                    charts.DataKey("a", "Key A"),
                    charts.DataKey("u", "Key U"),
                ],
            ),
            charts.InputDataFormat.WIDE_SIMPLE,
            add_rest=True,
            sort=True,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {"set": "Key U", "count": 21, "__SHARE__": 21 / 22},
                {"set": "Key A", "count": 1, "__SHARE__": 1 / 22},
            ]
        )
        self.assertTrue(
            (scd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nBut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_secondary_chart_and_table_dataframe_wide_simple_datakey_empty(self):
        """
        Test the function :py:func:`hawat.charts.get_secondary_chart_and_table_dataframe`.
        """
        scd = charts.SecondaryChartData(
            {
                "b": 2,
                "a": 1,
                "c": 3,
                "d": 4,
                "e": 5,
                "f": 6,
                "g": 7,
                "h": 8,
                "i": 9,
                "j": 10,
                "k": 11,
                "l": 12,
                "m": 13,
                "n": 14,
                "o": 15,
                "p": 16,
                "q": 17,
                "r": 18,
                "s": 19,
                "t": 20,
                "u": 21,
            },
            charts.SecondaryChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
                data_keys=[],
            ),
            charts.InputDataFormat.WIDE_SIMPLE,
            add_rest=True,
            sort=True,
        )

        fig = pio.from_json(json.dumps(scd.chart))
        pio.to_json(fig)  # shouldn't raise

        self.assertTrue(
            scd.df.reset_index().empty,
            f"Expected:\nAn empty DataFrame\nBut found:\n{scd.df.reset_index()!r}",
        )

    def test_get_timeline_chart_and_table_data_frame_wide_simple(self):
        tcd = charts.TimelineChartData(
            [
                [
                    datetime.datetime(1970, 1, 1, 0, 0),
                    {
                        "cnt_events": 42,
                        "cnt_events_filtered": 4,
                        "cnt_events_thresholded": 2,
                    },
                ],
                [
                    datetime.datetime(1970, 1, 2, 0, 0),
                    {
                        "cnt_events": 40,
                        "cnt_events_filtered": 4,
                        "cnt_events_thresholded": 0,
                    },
                ],
                [
                    datetime.datetime(1970, 1, 3, 0, 0),
                    {
                        "cnt_events": 51,
                        "cnt_events_filtered": 1,
                        "cnt_events_thresholded": 0,
                    },
                ],
            ],
            config=charts.TimelineChartConfig(
                key="test_chart",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
                data_keys=[
                    charts.DataKey("cnt_events", "reported"),
                    charts.DataKey("cnt_events_filtered", "filtered"),
                    charts.DataKey("cnt_events_thresholded", "thresholded"),
                ],
            ),
            timeline_cfg=TimelineCFG.get_daily(
                datetime.datetime(1970, 1, 1, 0, 0),
                datetime.datetime(1970, 1, 4, 23, 59),
            ),
            data_format=charts.InputDataFormat.WIDE_SIMPLE,
            forced_timezone="UTC",
        )

        fig = pio.from_json(json.dumps(tcd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "reported": 42,
                    "filtered": 4,
                    "thresholded": 2,
                    "__SUM__": 48,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "reported": 40,
                    "filtered": 4,
                    "thresholded": 0,
                    "__SUM__": 44,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "reported": 51,
                    "filtered": 1,
                    "thresholded": 0,
                    "__SUM__": 52,
                },
            ]
        )
        self.assertTrue(
            (tcd.df.reset_index() == expected).all().all(),
            f"Expected:\nAn empty DataFrame\nBut found:\n{tcd.df.reset_index()!r}",
        )

    def test_get_timeline_chart_and_table_data_frame_wide_complex(self):
        tcd = charts.TimelineChartData(
            [
                [
                    datetime.datetime(1970, 1, 1, 0, 0),
                    {"sources": {"192.168.0.4": 21, "2001:718:1:a200::11:3": 24}},
                ],
                [
                    datetime.datetime(1970, 1, 2, 0, 0),
                    {"sources": {"192.168.0.4": 15, "2001:718:1:a200::11:3": 18}},
                ],
                [
                    datetime.datetime(1970, 1, 3, 0, 0),
                    {"sources": {"192.168.0.4": 10, "2001:718:1:a200::11:3": 12}},
                ],
            ],
            config=charts.TimelineChartConfig(
                key="sources",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.MULTI,
            ),
            timeline_cfg=TimelineCFG.get_daily(
                datetime.datetime(1970, 1, 1, 0, 0),
                datetime.datetime(1970, 1, 4, 23, 59),
            ),
            data_format=charts.InputDataFormat.WIDE_COMPLEX,
            forced_timezone="UTC",
        )

        fig = pio.from_json(json.dumps(tcd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "192.168.0.4": 21,
                    "2001:718:1:a200::11:3": 24,
                    "__SUM__": 45,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "192.168.0.4": 15,
                    "2001:718:1:a200::11:3": 18,
                    "__SUM__": 33,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "192.168.0.4": 10,
                    "2001:718:1:a200::11:3": 12,
                    "__SUM__": 22,
                },
            ]
        )
        self.assertTrue(
            (tcd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nBut found:\n{tcd.df.reset_index()!r}",
        )

    def test_get_timeline_chart_and_table_data_frame_long_simple(self):
        tcd = charts.TimelineChartData(
            [
                {"bucket": datetime.datetime(1970, 1, 1, 0, 0), "count": 123},
                {"bucket": datetime.datetime(1970, 1, 2, 0, 0), "count": 0},
                {"bucket": datetime.datetime(1970, 1, 3, 0, 0), "count": 456},
            ],
            config=charts.TimelineChartConfig(
                key="sources",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.NONE,
            ),
            timeline_cfg=TimelineCFG.get_daily(
                datetime.datetime(1970, 1, 1, 0, 0),
                datetime.datetime(1970, 1, 4, 23, 59),
            ),
            data_format=charts.InputDataFormat.LONG_SIMPLE,
            forced_timezone="UTC",
        )

        fig = pio.from_json(json.dumps(tcd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "Test chart column name": 123,
                    "__SUM__": 123,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "Test chart column name": 0,
                    "__SUM__": 0,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "Test chart column name": 456,
                    "__SUM__": 456,
                },
            ]
        )
        self.assertTrue(
            (tcd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nBut found:\n{tcd.df.reset_index()!r}",
        )

    def test_get_timeline_chart_and_table_data_frame_long_complex(self):
        tcd = charts.TimelineChartData(
            [
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "set": "192.168.0.4",
                    "count": 123,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "set": "2001:718:1:a200::11:3",
                    "count": 23,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "set": "192.168.0.4",
                    "count": 234,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "set": "2001:718:1:a200::11:3",
                    "count": 0,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "set": "192.168.0.4",
                    "count": 0,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "set": "2001:718:1:a200::11:3",
                    "count": 0,
                },
            ],
            config=charts.TimelineChartConfig(
                key="sources",
                column_name="Test chart column name",
                data_complexity=charts.DataComplexity.SINGLE,
            ),
            timeline_cfg=TimelineCFG.get_daily(
                datetime.datetime(1970, 1, 1, 0, 0),
                datetime.datetime(1970, 1, 4, 23, 59),
            ),
            data_format=charts.InputDataFormat.LONG_COMPLEX,
            forced_timezone="UTC",
        )

        fig = pio.from_json(json.dumps(tcd.chart))
        pio.to_json(fig)  # shouldn't raise

        expected = pd.DataFrame(
            [
                {
                    "bucket": datetime.datetime(1970, 1, 1, 0, 0),
                    "192.168.0.4": 123,
                    "2001:718:1:a200::11:3": 23,
                    "__SUM__": 146,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 2, 0, 0),
                    "192.168.0.4": 234,
                    "2001:718:1:a200::11:3": 0,
                    "__SUM__": 234,
                },
                {
                    "bucket": datetime.datetime(1970, 1, 3, 0, 0),
                    "192.168.0.4": 0,
                    "2001:718:1:a200::11:3": 0,
                    "__SUM__": 0,
                },
            ]
        )
        self.assertTrue(
            (tcd.df.reset_index() == expected).all().all(),
            f"Expected:\n{expected!r}\nBut found:\n{tcd.df.reset_index()!r}",
        )

    def test_get_pivot_table(self):
        ptcd = charts.PivotTableChartData(
            [
                charts.const.TableRecord("row_1", "col_1", 10),
                charts.const.TableRecord("row_1", "col_2", 20),
                charts.const.TableRecord("row_2", "col_1", 30),
                charts.const.TableRecord("row_2", "col_2", 40),
            ],
            charts.PivotTableChartConfig(
                column_name="Test chart column name", table_coloring=charts.TableColoring.NONE
            ),
        )

        expected_header = ["col_1", "col_2"]
        default_color = "rgb(250, 250, 250)"
        expected_rows = [
            charts.model.TableRow(
                cells=[
                    charts.model.TableCell(value=10, color=default_color),
                    charts.model.TableCell(value=20, color=default_color),
                ],
                header="row_1",
            ),
            charts.model.TableRow(
                cells=[
                    charts.model.TableCell(value=30, color=default_color),
                    charts.model.TableCell(value=40, color=default_color),
                ],
                header="row_2",
            ),
        ]

        self.assertEqual(list(ptcd.iter_header()), expected_header)
        self.assertEqual(list(ptcd.iter_rows()), expected_rows)


# ------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
