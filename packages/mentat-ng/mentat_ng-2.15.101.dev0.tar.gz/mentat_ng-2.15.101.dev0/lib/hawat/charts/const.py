"""
This file contains necessary classes and constants for the use of the charts module.
"""

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Literal, NamedTuple, NewType

from flask_babel import format_decimal, lazy_gettext
from flask_babel.speaklater import LazyString

import hawat.utils

KEY_SUM = "__SUM__"
KEY_SHARE = "__SHARE__"

# Colors taken from d3.scale.category20()
CATEGORY20_COLORS = [
    "#1f77b4",
    "#aec7e8",
    "#ff7f0e",
    "#ffbb78",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
    "#8c564b",
    "#c49c94",
    "#e377c2",
    "#f7b6d2",
    "#7f7f7f",
    "#c7c7c7",
    "#bcbd22",
    "#dbdb8d",
    "#17becf",
    "#9edae5",
]

COLOR_LIST = CATEGORY20_COLORS
"""Used colors for the charts and tables."""

AXIS_LINE_COLOR = "black"
GRID_COLOR = "lightgray"
TRANSPARENT = "rgb(255, 255, 255, 0)"

MAX_VALUE_COUNT = 20
NUMBER_OF_LABELED_TICKS = 12
PIE_CHART_SHOW_PERCENTAGE_CUTOFF = 0.01

ChartJSONType = NewType("ChartJSONType", dict[str, Any])


class InputDataFormat(StrEnum):
    """
    There are several data formats used in mentat, and each enum is assigned to a
    data format which is then unified to a single-format pandas dataframes for generating charts
    and rendering tables.
    """

    WIDE_SIMPLE = "wide_simple"
    """
        Provided keys should be a list of tuples, where the first element is the key and second
        element is the translation string, which will appear in the charts and tables.
        Under each key in the provided data is only a single number expected.
        example:
            key: [
                ('cnt_events', 'reported'),
                ('cnt_events_filtered', 'filtered'),
                ('cnt_events_thresholded', 'thresholded')
            ]
            data: [
                [datetime(1970, 1, 1, 0, 0), {
                    'cnt_events': 42,
                    'cnt_events_filtered': 4,
                    'cnt_events_thresholded': 2,
                    **other_aggregations
                }],
                [datetime(1970, 1, 2, 0, 0), {
                    'cnt_events': 40,
                    'cnt_events_filtered': 4,
                    'cnt_events_thresholded': 0,
                    **other_aggregations
                }],
                *rest_of_the_timeline
            ]
    """

    WIDE_COMPLEX = "wide_complex"
    """
    Keys of dictionary stored under the provided key are used as columns in the dataframe.
    example:
        key: 'sources'
        data: [
            [datetime(1970, 1, 1, 0, 0), {
                'sources': {
                    '192.168.0.4': 21,
                    '2001:718:1:a200::11:3': 24,
                    **other_ip_counts,
                }
                **other_aggregations
            }],
            *rest_of_the_timeline
        ]
    """

    LONG_SIMPLE = "long_simple"
    """
    Key is only used to obtain the correct translation if the chart section named tuple is not
    provided.

    The only difference from the complex variant is that it does not have the 'set' column and
    therefore, each bucket timestamp occurs only once in the data.
    This means it is impossible to support other data complexity than NONE.

    example:
        key: 'sources',
        data: [
            {'bucket': datetime(1970, 1, 1, 0, 0), 'count': 123},
            {'bucket': datetime(1970, 1, 2, 0, 0), 'count': 0},
            *rest_of_the_timeline
        ]
    """

    LONG_COMPLEX = "long_complex"
    """
    Key is only used to obtain the correct translation if the chart section named tuple is not
    provided. And each value name is in the column 'set'. The rows are sorted by buckets, and
    rows with the same bucket are also sorted by the count values.

    example:
        key: 'sources',
        data: [
            {'bucket': datetime(1970, 1, 1, 0, 0), 'set': '192.168.0.4', 'count': 123},
            {'bucket': datetime(1970, 1, 1, 0, 0), 'set': '2001:718:1:a200::11:3', 'count': 23},
            {'bucket': datetime(1970, 1, 2, 0, 0), 'set': '192.168.0.4', 'count': 234},
            {'bucket': datetime(1970, 1, 2, 0, 0), 'set': '2001:718:1:a200::11:3', 'count': 0},
            *rest_of_the_timeline
        ]
    """


class ChartRenderer(StrEnum):
    """
    Supported chart renderers.
    """

    PLOTLY = "plotly"
    HTML_TABLE = "html_table"


class ChartType(StrEnum):
    """
    Supported chart types.
    """

    TIMELINE = "timeline"
    SECONDARY = "secondary"
    PIVOT_TABLE = "pivot_table"


class TableType(StrEnum):
    """
    Type of the table to generate for the chart.
    """

    TOGGLEABLE = "toggleable"
    """Table can be shown or hidden by clicking on the button next to the chart."""

    COLUMNS = "columns"
    """Table is shown as a separate column next to the chart."""

    NONE = "none"
    """No table is shown."""


InputDataFormatLong = Literal[InputDataFormat.LONG_SIMPLE, InputDataFormat.LONG_COMPLEX]
InputDataFormatWide = Literal[InputDataFormat.WIDE_SIMPLE, InputDataFormat.WIDE_COMPLEX]


class DataComplexity(StrEnum):
    NONE = "none"
    """Only a single number per each timeline bucket. Does not generate a secondary chart"""

    SINGLE = "single"
    """Each datapoint has at most 1 possible value assigned to it. Generates a pie chart"""

    MULTI = "multi"
    """Each datapoint has a list of values assigned to it. Generates a bar chart"""


class TableRecord(NamedTuple):
    """
    A record representing a row in the pivot table.
    """

    row_category: str
    col_category: str
    observed: int
    standardized_residual: float | None = None


PivotItems = list[TableRecord]


class TableColoring(StrEnum):
    """
    Enum representing the available table coloring options.
    """

    NONE = "none"
    """No coloring applied to the table."""

    NUMBER_LOG = "number_log"
    """
    Coloring based on the logarithm of the numerical values in the table.
    Higher values are represented with darker color.
    """

    NUMBER = "number"
    """
    Coloring based solely on the numerical values in the table.
    Higher values are represented with darker color.
    """

    RESIDUAL_DIVERGING = "residual_diverging"
    """
    Coloring based on the Pearson residuals of the values in the table.
    Values higher than the expected value are represented with darker blue,
    while values lower than the expected value are represented with darker red.
    """

    RESIDUAL = "residual"
    """
    Coloring based on the Pearson residuals of the values in the table.
    Values higher than the expected value are represented with darker color.
    Values lower than the expected value are represented with lighter color.
    """


class TableAggregation(NamedTuple):
    func: Callable | str  # function to be used for aggregation, or its name in pandas,
    icon_name: str
    name: LazyString | str
    tooltip: LazyString | str
    format_func: Callable = hawat.utils.fallback_formatter(format_decimal)


TABLE_AGGREGATIONS = [
    TableAggregation("sum", "sum", lazy_gettext("Sum"), lazy_gettext("Sum of all values")),
    TableAggregation("min", "min", lazy_gettext("Minimum"), lazy_gettext("Minimal value")),
    TableAggregation("max", "max", lazy_gettext("Maximum"), lazy_gettext("Maximal value")),
    TableAggregation("mean", "avg", lazy_gettext("Average"), lazy_gettext("Average value")),
    TableAggregation("median", "med", lazy_gettext("Median"), lazy_gettext("Median value")),
    TableAggregation("count", "cnt", lazy_gettext("Count"), lazy_gettext("Count of all values")),
]
