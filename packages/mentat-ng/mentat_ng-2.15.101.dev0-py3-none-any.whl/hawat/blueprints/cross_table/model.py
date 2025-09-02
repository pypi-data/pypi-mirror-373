from typing import NamedTuple

from flask_babel.speaklater import LazyString


class AggColumn(NamedTuple):
    key: str
    display_name: str | LazyString
    """
    The rendered name of the aggregation column.
    """

    column_name: str
    """
    The name of the column in the database that corresponds to this aggregation column.
    """
