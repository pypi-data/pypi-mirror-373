#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains object encapsulation of `RRDTOOL <http://oss.oetiker.ch/rrdtool/>`__
for easier usage in Mentat project.

Overview
^^^^^^^^

In Mentat RRD databases are used to store quick periodical performance statistics.
Each database file is configured to store only single dataset and when generating
charts multiple RRD files must be combined when necessary to create more complex
charts. This approach has the benefit of very easy way of deleting datasets, that
are not required anymore, or obsolete and not appearing in life data anymore.

Every RRD database file is configured in following way:

* **internal dataset name:** ``eventcnt``
* **default step:** 300 seconds (5 minutes)
* **raw storage size:** 3 months
* **aggregated storage size:** 1 year (min, max, avg)

The whole RRD handling functionality is implemented in :py:class:`RrdStats`, which
receives certain parameters (like locations of database and chart files) upon
instantination and those can be then omitted from calls to all other methods. See
the documentation below for more details.

There is a definition of color palette in ``COLOR_PALETTE`` constant value, which
contains all possible colors usable in RRD charts.

The implementation is based on Python library :py:mod:`rrdtool` (`PyPI <https://pypi.python.org/pypi/rrdtool/0.1.11>`__,
`documentation <http://pythonhosted.org/rrdtool/>`__).

RRD database identifier naming convention
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Names of RRD database files are constructed as follows:

    type.snake_case_name.rrd

When being processed, each RRD database file name is split at ``.`` character,
which yields three tokens:

* **type:** type, category, or group of the dataset
* **snake_case_name:** escaped name of the dataset, anything ``[^-_a-zA-Z0-9]`` is
  replaced with ``_``
* **file suffix**

The idea behind the naming scheme is, that statistics are being calculated
separatelly for multiple message groups, for example according to the name of the
detector, categories, etc. The ``type`` token should uniquelly indentify each of
these groups. The ``snake_case_name`` then contains underscore-escaped name of
the detector/category/etc.

The ``type.snake_case_name`` pair is called ``db_id`` in further documentation
and it is unique identifier of the dataset.

Example usage
^^^^^^^^^^^^^

.. code-block:: python

    >>> rrd_stats = mentat.stats.rrd.RrdStats('/var/tmp', '/var/tmp')
    >>> stats.find_dbs()
    defaultdict(<class 'list'>, {})

    >>> rrd_stats.prepare_db('typea.test_a')
    ('/var/tmp/utest_rrdstats/typea.testa.rrd', True)
    >>> rrd_stats.prepare_db('typea.test_b')
    ('/var/tmp/utest_rrdstats/typea.testb.rrd', True)
    >>> rrd_stats.prepare_db('typeb.test_a')
    ('/var/tmp/utest_rrdstats/typeb.testa.rrd', True)
    >>> rrd_stats.prepare_db('typeb.test_b')
    ('/var/tmp/utest_rrdstats/typeb.testb.rrd', True)
    >>> stats.find_dbs()
    defaultdict(<class 'list'>, {'typeb': [('typeb.test_a', 'typeb', 'test_a', '/var/tmp/typeb.test_a.rrd', False), ('typeb.test_b', 'typeb', 'test_b', '/var/tmp/typeb.test_b.rrd', False)], 'typea': [('typea.test_a', 'typea', 'test_a', '/var/tmp/typea.test_a.rrd', False), ('typea.test_b', 'typea', 'test_b', '/var/tmp/typea.test_b.rrd', False)]})

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import collections
import datetime
import json
import os
import re
import time

import rrdtool

from pyzenkit.utils import get_resource_path

DFLT_STEP = 300  # Default update step for database datasets.
DFLT_WIDTH = 800  # Default chart width in pixels.
DFLT_HEIGHT = 300  # Default chart height in pixels.
DFLT_SPARK_WIDTH = 75  # Default sparkchart width in pixels.
DFLT_SPARK_HEIGHT = 25  # Default sparkchart height in pixels.
DFLT_COLOR_TOTALS = "red"  # Default color for summary dataset (totals).
DS_NAME = "eventcnt"  # Dataset name within RRD database file.
DB_TOTALS_NAME = "_totals"  # Identifier for the summary dataset (totals).
FEED_ID = "datafeed"  # Identifier of the dataset in exported JSON.
FILE_CHARTLIST = "_chartlist.json"  # Name of the chart list file.


#
# Precompiled regular expression patterns for handling RRD database file names.
#
PTRN_RRDFILE = re.compile(r"(.+)\.rrd$")
PTRN_TOTALDB = re.compile(rf"{DB_TOTALS_NAME}$")
PTRN_NAMERPL = re.compile(r"\.")
PTRN_NAMECLN = re.compile(r"[^-_a-zA-Z0-9]")


#
# Color palette for generating RRD charts.
#
COLOR_PALETTE = {
    "aliceblue": "F0F8FF",
    "antiquewhite": "FAEBD7",
    "aqua": "00FFFF",
    "aquamarine": "7FFFD4",
    "azure": "F0FFFF",
    "beige": "F5F5DC",
    "bisque": "FFE4C4",
    "black": "000000",
    "blanchedalmond": "FFEBCD",
    "blue": "0000FF",
    "blueviolet": "8A2BE2",
    "brown": "A52A2A",
    "burlywood": "DEB887",
    "cadetblue": "5F9EA0",
    "chartreuse": "7FFF00",
    "chocolate": "D2691E",
    "coral": "FF7F50",
    "cornflowerblue": "6495ED",
    "cornsilk": "FFF8DC",
    "crimson": "DC143C",
    "cyan": "00FFFF",
    "darkblue": "00008B",
    "darkcyan": "008B8B",
    "darkgoldenrod": "B8860B",
    "darkgray": "A9A9A9",
    "darkgreen": "006400",
    "darkkhaki": "BDB76B",
    "darkmagenta": "8B008B",
    "darkolivegreen": "556B2F",
    "darkorange": "FF8C00",
    "darkorchid": "9932CC",
    "darkred": "8B0000",
    "darksalmon": "E9967A",
    "darkseagreen": "8FBC8F",
    "darkslateblue": "483D8B",
    "darkslategray": "2F4F4F",
    "darkturquoise": "00CED1",
    "darkviolet": "9400D3",
    "deeppink": "FF1493",
    "deepskyblue": "00BFFF",
    "dimgray": "696969",
    "dodgerblue": "1E90FF",
    "firebrick": "B22222",
    "floralwhite": "FFFAF0",
    "forestgreen": "228B22",
    "fuchsia": "FF00FF",
    "gainsboro": "DCDCDC",
    "ghostwhite": "F8F8FF",
    "gold": "FFD700",
    "goldenrod": "DAA520",
    "gray": "808080",
    "green": "008000",
    "greenyellow": "ADFF2F",
    "honeydew": "F0FFF0",
    "hotpink": "FF69B4",
    "indianred": "CD5C5C",
    "indigo": "4B0082",
    "ivory": "FFFFF0",
    "khaki": "F0E68C",
    "lavender": "E6E6FA",
    "lavenderblush": "FFF0F5",
    "lawngreen": "7CFC00",
    "lemonchiffon": "FFFACD",
    "lightblue": "ADD8E6",
    "lightcoral": "F08080",
    "lightcyan": "E0FFFF",
    "lightgoldenrodyellow": "FAFAD2",
    "lightgreen": "90EE90",
    "lightgrey": "D3D3D3",
    "lightpink": "FFB6C1",
    "lightsalmon": "FFA07A",
    "lightseagreen": "20B2AA",
    "lightskyblue": "87CEFA",
    "lightslategray": "778899",
    "lightsteelblue": "B0C4DE",
    "lightyellow": "FFFFE0",
    "lime": "00FF00",
    "limegreen": "32CD32",
    "linen": "FAF0E6",
    "magenta": "FF00FF",
    "maroon": "800000",
    "mediumauqamarine": "66CDAA",
    "mediumblue": "0000CD",
    "mediumorchid": "BA55D3",
    "mediumpurple": "9370D8",
    "mediumseagreen": "3CB371",
    "mediumslateblue": "7B68EE",
    "mediumspringgreen": "00FA9A",
    "mediumturquoise": "48D1CC",
    "mediumvioletred": "C71585",
    "midnightblue": "191970",
    "mintcream": "F5FFFA",
    "mistyrose": "FFE4E1",
    "moccasin": "FFE4B5",
    "navajowhite": "FFDEAD",
    "navy": "000080",
    "oldlace": "FDF5E6",
    "olive": "808000",
    "olivedrab": "688E23",
    "orange": "FFA500",
    "orangered": "FF4500",
    "orchid": "DA70D6",
    "palegoldenrod": "EEE8AA",
    "palegreen": "98FB98",
    "paleturquoise": "AFEEEE",
    "palevioletred": "D87093",
    "papayawhip": "FFEFD5",
    "peachpuff": "FFDAB9",
    "peru": "CD853F",
    "pink": "FFC0CB",
    "plum": "DDA0DD",
    "powderblue": "B0E0E6",
    "purple": "800080",
    "red": "FF0000",
    "rosybrown": "BC8F8F",
    "royalblue": "4169E1",
    "saddlebrown": "8B4513",
    "salmon": "FA8072",
    "sandybrown": "F4A460",
    "seagreen": "2E8B57",
    "seashell": "FFF5EE",
    "sienna": "A0522D",
    "silver": "C0C0C0",
    "skyblue": "87CEEB",
    "slateblue": "6A5ACD",
    "slategray": "708090",
    "snow": "FFFAFA",
    "springgreen": "00FF7F",
    "steelblue": "4682B4",
    "tan": "D2B48C",
    "teal": "008080",
    "thistle": "D8BFD8",
    "tomato": "FF6347",
    "turquoise": "40E0D0",
    "violet": "EE82EE",
    "wheat": "F5DEB3",
    "white": "FFFFFF",
    "whitesmoke": "F5F5F5",
    "yellow": "FFFF00",
    "yellowGreen": "9ACD32",
}

# Reversed color palette key: value => value: key.
COLOR_PALETTE_R = {v: k for k, v in COLOR_PALETTE.items()}

# List of color names.
COLORS_STR = list(COLOR_PALETTE.keys())

# List of color codes.
COLORS_HEX = list(COLOR_PALETTE_R.keys())

# Optimal color palette - optimized for best contrast within neigboring values.
# Work in progress, only colors to first blank line were ordered.
COLORS_OPT = (
    "red",
    "yellow",
    "blue",
    "green",
    "midnightblue",
    "salmon",
    "orange",
    "gray",
    "lightblue",
    "peachpuff",
    "indigo",
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgreen",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "greenyellow",
    "honeydew",
    "hotpink",
    "indianred",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lemonchiffon",
    "lightcoral",
    "lightcyan",
    "lightgoldenrodyellow",
    "lightgreen",
    "lightgrey",
    "lightpink",
    "lightsalmon",
    "lightseagreen",
    "lightskyblue",
    "lightslategray",
    "lightsteelblue",
    "lightyellow",
    "lime",
    "limegreen",
    "linen",
    "magenta",
    "maroon",
    "mediumauqamarine",
    "mediumblue",
    "mediumorchid",
    "mediumpurple",
    "mediumseagreen",
    "mediumslateblue",
    "mediumspringgreen",
    "mediumturquoise",
    "mediumvioletred",
    "mintcream",
    "mistyrose",
    "moccasin",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "paleturquoise",
    "palevioletred",
    "papayawhip",
    "peru",
    "pink",
    "plum",
    "powderblue",
    "purple",
    "rosybrown",
    "royalblue",
    "saddlebrown",
    "sandybrown",
    "seagreen",
    "seashell",
    "sienna",
    "silver",
    "skyblue",
    "slateblue",
    "slategray",
    "snow",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowGreen",
)


class RrdStatsException(Exception):
    """
    Base class for all RrdStats specific exceptions.

    The :py:mod:`rrdtool` module does not provide enough granularity with its
    exceptions and it is necessary to parse the exception string to determine
    the exact problem. This module provides custom set of exceptions to diferentiate
    between different problems.
    """

    def __init__(self, description):
        self.description = description

    def __str__(self):
        return repr(self.description)


class RrdsCreateException(RrdStatsException):
    """
    Exceptions occuring during creating of RRD database files.
    """


class RrdsUpdateException(RrdStatsException):
    """
    Exceptions occuring during updating of RRD database files.
    """


class RrdsExportException(RrdStatsException):
    """
    Exceptions occuring during exporting of RRD database files.
    """


class RrdsGraphException(RrdStatsException):
    """
    Exceptions occuring during generating of RRD charts.
    """


class RrdStats:
    """
    Class implementing RRD database file management and chart generation.
    """

    def __init__(self, rrds_dir, reports_dir, step=DFLT_STEP):
        """
        Initialize new RRD database manipulation object.

        :param str rrds_dir: Name of the directory containing RRD database files.
        :param str reports_dir: Name of the directory containing generated RRD charts and export files.
        :param int step: Update step for RRD database files in seconds.
        """
        self.rrds_dir = get_resource_path(rrds_dir)
        self.reports_dir = get_resource_path(reports_dir)
        self.step = step
        self.colors = collections.defaultdict(dict)
        self.colors_ptr = collections.defaultdict(int)

    @staticmethod
    def clean(name):
        """
        Cleanup given name so it can be used as RRD database file name.

        :param str name: Name to be cleaned.
        :return: Name with all forbidden characters escaped with ``_``.
        :rtype: str
        """
        return PTRN_NAMECLN.sub("_", name)

    @staticmethod
    def _json_dump(fname, data):
        """
        Store given data structure inti given JSON file.

        :param str fname: Name of the JSON file.
        :param dict data: Data to be stored.
        """
        with open(fname, "w", encoding="utf8") as expf:
            json.dump(data, expf, indent=4, sort_keys=True)

    def prepare_db(self, ds_id, time_start=None):
        """
        Ensure existence of appropriate RRD database file for storing single data set.

        :param str ds_id: Identifier of the dataset.
        :param int time_start: Name to be cleaned.
        :return: Absolute filesystem path to the prepared RRD database file as
                 string and boolean flag marking creation of new file.
        :rtype: tuple
        """

        # Unless given explicitly, calculate starting timestamp from current time,
        # then adjust it to whole step interval using modulo operation.
        if not time_start:
            time_start = int(time.time())
            time_start = time_start - (time_start % self.step)

        # Determine the name of the RRD database file based on dataset ID and
        # filesystem location of database files.
        rrddb = os.path.join(self.rrds_dir, f"{ds_id}.rrd")
        if os.path.isfile(rrddb):
            return (rrddb, False)

        # Calculate steps per hour, will be used later during initialization.
        sph = int(3600 / self.step)

        # Calculate the size for three month storage.
        rows = sph * 24 * 7 * 31 * 3

        try:
            rrdtool.create(
                # Path to RRD database file.
                rrddb,
                # Start time.
                "--start",
                f"{time_start - self.step}",
                # Update step.
                "--step",
                f"{self.step}",
                # Define data store.
                f"DS:{DS_NAME}:ABSOLUTE:{2 * self.step}:U:U",
                # 3 month raw storage (sph * 24 * 7 * 31 * 3).
                f"RRA:MAX:0.5:1:{rows}",
                # 1 year average storage (2 * 24 * 31 * 12).
                "RRA:AVERAGE:0.5:6:17856",
                # 1 year min storage (2 * 24 * 31 * 12).
                "RRA:MIN:0.5:6:17856",
                # 1 year max storage (2 * 24 * 31 * 12).
                "RRA:MAX:0.5:6:17856",
            )

        except rrdtool.OperationalError as exc:
            raise RrdsCreateException(f"Unable to create RRD database '{ds_id}' in file '{rrddb}': {exc!s}") from exc

        return (rrddb, True)

    def find_dbs(self, flt_type=None):
        """
        Find all currently available RRD database files.

        :param str flt_type: Dataset type filter to dump part of the full result.
        :return: Structured dictionary containing list of RRD database metadata structures for each type.
        :rtype: collections.defaultdict
        """
        rrds = collections.defaultdict(list)

        for fln in os.listdir(self.rrds_dir):
            # RRD database must be ordinary file.
            flp = os.path.join(self.rrds_dir, fln)
            if not os.path.isfile(flp):
                continue

            # And must match proper name pattern.
            match = PTRN_RRDFILE.match(fln)
            if not match:
                continue

            ds_id = str(match.group(1))
            (ds_type, ds_name) = ds_id.split(".")

            # Optional filtering based on dataset type.
            if flt_type and flt_type != ds_type:
                continue

            # Detection of summary dataset.
            ds_totals = False
            if PTRN_TOTALDB.search(ds_id):
                ds_totals = True

            rrds[ds_type].append((ds_id, ds_type, ds_name, flp, ds_totals))

        # Always return sorted result to be deterministic.
        for ds_type in rrds:
            rrds[ds_type] = sorted(rrds[ds_type], key=lambda x: x[0])

        return rrds

    def update(self, ds_id, value, tst=None):
        """
        Update given RRD database.

        :param str ds_id: Identifier of the dataset.
        :param int value: Value to be set.
        :param int tst: Update timestamp.
        :return: Absolute filesystem path to the prepared RRD database file as
                 string and boolean flag marking creation of new file.
        :rtype: tuple
        """
        if not tst:
            tst = int(time.time())

        (rrddb, flag_new) = self.prepare_db(ds_id, tst - (tst % self.step))

        try:
            rrdtool.update(
                # Path to RRD database file.
                rrddb,
                # 1500547120:558
                f"{tst}:{value}",
            )
            return (rrddb, flag_new)

        except rrdtool.OperationalError as exc:
            raise RrdsUpdateException(
                f"Unable to update RRD database '{ds_id}' in file '{rrddb}' with value '{value}' and timestamp '{tst!s}': {exc!s}"
            ) from exc

    def update_all(self, value, tst=None, flt_type=None):
        """
        Updade all RRD database files with given value.

        :param int value: Value to be set.
        :param int tst: Update timestamp.
        :param str flt_type: Dataset type filter to dump part of the full result.
        :return: List of updated RRD database files.
        :rtype: list of tuples
        """
        rrds = self.find_dbs(flt_type)

        rrddbs = []
        for rrd_type in sorted(rrds.keys()):
            for rrd in rrds[rrd_type]:
                rrddbs.append(self.update(rrd[0], value, tst))
        return rrddbs

    def export(self, ds_id):
        """
        Export whole RRD database into JSON structure.

        :param str ds_id: Identifier of the dataset.
        :return: Absolute filesystem path to the prepared RRD database file as
                 string, boolean flag marking creation of new fileand axported
                 dataset as JSON structure.
        :rtype: tuple
        """
        (rrddb, flag_new) = self.prepare_db(ds_id)

        try:
            result = rrdtool.xport(
                "--json",
                # 'DEF:eventcnt_proc_a01=./spool/proc.a01.rrd:eventcnt:MAX'
                f"DEF:{FEED_ID}={rrddb}:{DS_NAME}:MAX",
                # 'CDEF:eventcnt_proc_a01_r=eventcnt_proc_a01,300,*'
                f"CDEF:{FEED_ID}_r={FEED_ID},300,*",
                # 'XPORT:eventcnt_proc_a01_r:'
                "XPORT:{}_r:{}".format(FEED_ID, f"# of messages from {ds_id}"),
            )
            return (rrddb, flag_new, result)

        except rrdtool.OperationalError as exc:
            raise RrdsExportException(f"Unable to export RRD database '{ds_id}' in file '{rrddb}': {exc!s}") from exc

    def lookup(self, flt_type=None):
        """
        Lookup all available RRD charts, spark charts and JSON export files.

        :param str flt_type: Dataset type filter to dump part of the full result.
        :return: List of available charts.
        :rtype: list of dict
        """
        rrds = self.find_dbs(flt_type)
        chartlist = []
        counter = 0

        # Prepare RRD args for each dataset type (category).
        for rrd_t in sorted(rrds.keys()):
            maxstrlength = 0
            for rrd in rrds[rrd_t]:
                maxstrlength = max(maxstrlength, len(rrd[2]))

            rrd_args = {
                "dsets": [],
                "defs": [],
                "draws": [],
                "xports": [],
                "t_dsets": [],
                "t_defs": [],
                "t_draws": [],
                "t_xports": [],
            }
            for rrd in rrds[rrd_t]:
                counter = self._rrd_configure_args(rrd, rrd_args, counter, maxstrlength)

            # Get the list of charts to be generated for this dataset type (category).
            chlist = self._rrd_prepare_charts(rrd_t, rrd_args)

            chartlist += chlist

        return chartlist

    def generate(self, tst, flt_type=None):
        """
        Generate all available RRD charts, spark charts and JSON export files.

        :param int tst: Upper time boundary as unix timestamp.
        :param str flt_type: Dataset type filter to dump part of the full result.
        :return: List of generated files.
        :rtype: list of str
        """
        chartlist = self.lookup(flt_type)
        result = []

        # Generate the metadata files, charts, sparkline charts and export files.
        for chrt in chartlist:
            result.append(self._rrd_generate_meta(chrt, tst))
            result.append(self._rrd_generate_chart(chrt, tst))
            result.append(self._rrd_generate_sparkchart(chrt, tst))
            result.append(self._rrd_xport(chrt, tst))

        # Dump chart configurations alongside the generated charts.
        self._json_dump(os.path.join(self.reports_dir, FILE_CHARTLIST), chartlist)

        return result

    # ---------------------------------------------------------------------------

    def _color_for_ds(self, ds_type, ds_id):
        """
        Pick a color for given chart dataset.

        :param str ds_type: Name of the dataset type.
        :param str ds_id: Identifier of the dataset.
        :return: Color in RGB format.
        :rtype: str
        """

        # If the color for this dataset was specified explicitly, return it.
        if ds_type in self.colors and ds_id in self.colors[ds_type]:
            return self.colors[ds_type][ds_id]

        # Draw the totals in configured default, there is always only one line in chart.
        if PTRN_TOTALDB.search(ds_id):
            return COLOR_PALETTE[DFLT_COLOR_TOTALS]

        # Otherwise pick new random color and remember it for this dataset.
        color_index = self.colors_ptr[ds_type] % len(COLORS_OPT)
        color_hex = COLOR_PALETTE[COLORS_OPT[color_index]]
        self.colors[ds_type][ds_id] = color_hex
        self.colors_ptr[ds_type] += 1

        return color_hex

    def _title_for_ds_type(self, ds_type):
        """
        Get chart title for dataset type.

        .. todo::

            Currently this feature is not needed. However it was used in previous
            library version in Perl. It was kept, because it seems it will be needed
            again.

        :param str ds_type: Name of the dataset type.
        :return: Chart title.
        :rtype: str
        """
        # If the title for this dataset type was specified explicitly, return it
        # if ds_type in self.titles:
        #    return self.titles[ds_type]

        return "Events processed"

    def _rrd_configure_args(self, rrd, rrd_args, counter, lbl_length):
        """
        Configure arguments for generating all available RRD charts. RRDTOOL requires
        its arguments to be in certain format and they can be quite complex. This
        internal method will take care of just that.

        :param tuple rrd: RRD database metadata structure.
        :param dict rrd_args: Data structure in which rrdtool argument will be stored.
        :param int counter: Counter of datasets in chart (will turn on stacking for # > 1).
        :param int lbl_length: Length of chart legend labels (to make them all same width).
        :return: Dataset counter incremented by one.
        :rtype: int
        """

        # Define stack_flag based on number of datasets in chart.
        counter += 1
        stack_flag = ""
        if counter > 1:
            stack_flag = ":STACK"

        # Pick a color for dataset.
        color = self._color_for_ds(rrd[1], rrd[2])

        # Generate internal dataset ID and chart legend.
        idsid = "{}_{}".format(DS_NAME, PTRN_NAMERPL.sub("_", rrd[2]))
        legend = ("# of messages from {:" + str(lbl_length) + "s}").format(rrd[2])
        if rrd[4]:
            legend = "Total # of messages"

        # Generate metadata describing RRD dataset. Those may be used to interpret
        # the data using other tools.
        rrd_dataset = {
            "id": rrd[0],  # Full RRD database identifier.
            "ds_type": rrd[1],  # Dataset type.
            "ds_id": rrd[2],  # Dataset identifier.
            "ds_id_int": idsid,  # Internal dataset identifier (within RRD file).
            "path": rrd[3],  # Full filesystem path to RRD database file.
            "legend": legend,  # Dataset legend.
            "color": color,  # Dataset color.
            "total": rrd[4],  # Boolean flag indicating summary dataset.
        }

        # Generate RRD dataset definitions.
        defs = [
            # 'DEF:eventcnt_proc_a01=./spool/proc.a01.rrd:eventcnt:MIN'
            f"DEF:{idsid}={rrd[3]}:{DS_NAME}:MAX",
            # 'CDEF:eventcnt_proc_a01_r=eventcnt_proc_a01,300,*'
            f"CDEF:{idsid}_r={idsid},300,*",
            # Calculate current value.
            # 'VDEF:cur_eventcnt_proc_a01=eventcnt_proc_a01_r,LAST'
            f"VDEF:cur_{idsid}={idsid}_r,LAST",
            # Calculate overall average value.
            # 'VDEF:avg_eventcnt_proc_a01=eventcnt_proc_a01_r,AVERAGE'
            f"VDEF:avg_{idsid}={idsid}_r,AVERAGE",
            # Calculate overall maximum value.
            # 'VDEF:max_eventcnt_proc_a01=eventcnt_proc_a01_r,MAXIMUM'
            f"VDEF:max_{idsid}={idsid}_r,MAXIMUM",
            # Calculate overall minimum value.
            # 'VDEF:min_eventcnt_proc_a01=eventcnt_proc_a01_r,MINIMUM'
            f"VDEF:min_{idsid}={idsid}_r,MINIMUM",
        ]

        # Generate RRD drawing definitions.
        draws = [
            # Diplay the actual data as stacked area.
            # 'AREA:draw10#FFFF00:# of messages processed from a02:STACK'
            f"AREA:{idsid}_r#{color}:{legend}{stack_flag}",
            # Display current value in the labels.
            # 'GPRINT:cur_eventcnt_proc_a01:Cur [a01] = %lf'
            f"GPRINT:cur_{idsid}:Cur\\: %8.1lf",
            # Display overall average in the labels.
            # 'GPRINT:avg_eventcnt_proc_a01:Avg [a01] = %lf'
            f"GPRINT:avg_{idsid}:Avg\\: %8.1lf",
            # Display overall maximum in the labels.
            # 'GPRINT:max_eventcnt_proc_a01:Max [a01] = %lf'
            f"GPRINT:max_{idsid}:Max\\: %8.1lf",
            # Display overall minimum in the labels.
            # 'GPRINT:min_eventcnt_proc_a01:Min [a01] = %lf'
            f"GPRINT:min_{idsid}:Min\\: %8.1lf\\n",
        ]

        # Generate RRD exporting definitions.
        xports = [
            # Xport the actual data.
            f"XPORT:{idsid}_r:{legend}"
        ]

        # Append the RRDTOOL arguments to appropriate collections based on the fact,
        # that they belong to summary database, or not.
        if rrd[4]:
            rrd_args["t_dsets"].append(rrd_dataset)
            rrd_args["t_defs"] += defs
            rrd_args["t_draws"] += draws
            rrd_args["t_xports"] += xports
        else:
            rrd_args["dsets"].append(rrd_dataset)
            rrd_args["defs"] += defs
            rrd_args["draws"] += draws
            rrd_args["xports"] += xports

        return counter

    def _rrd_prepare_charts(self, ds_type, rrd_args):
        """
        Generate metadata for all RRD charts that should be generated.

        :param str ds_type: Name of the dataset type.
        :param dict rrd_args: Data structure with preconfigured RRD arguments (see :py:func:`_rrd_configure_args`).
        :return: List containing metadata of all available charts.
        :rtype: list
        """

        title = self._title_for_ds_type(ds_type)
        charts = []

        # Define chart meta-specifications
        chspecs = [
            # 0: filename chunk
            # 1: title chunk
            # 2: button link
            # 3: size
            ("l6hours", "in last 6 hours", "6 hours", 21600),
            ("l24hours", "in last 24 hours", "24 hours", 86400),
            ("l72hours", "in last 72 hours", "72 hours", 259200),
            ("lweek", "in last week", "week", 604800),
            ("l2weeks", "in last 2 weeks", "2 weeks", 1209600),
            ("l4weeks", "in last 4 weeks", "4 weeks", 2419200),
            ("l3months", "in last 3 months", "3 months", 7257600),
            ("l6months", "in last 6 months", "6 months", 14515200),
            ("lyear", "in last year", "year", 29030400),
            ("l2years", "in last 2 years", "2 years", 58060800),
        ]

        # Generate chart metadata from meta-specifications
        for chsp in chspecs:
            charts.append(
                {
                    "ds_type": ds_type,
                    "size": chsp[3],
                    "chid": f"{ds_type}-{chsp[0]}",
                    "fid": f"{ds_type}.{chsp[0]}",
                    "file_meta": f"{ds_type}.{chsp[0]}.meta.json",
                    "file_chart": f"{ds_type}.{chsp[0]}.png",
                    "file_schart": f"{ds_type}.{chsp[0]}.spark.png",
                    "file_xport": f"{ds_type}.{chsp[0]}.xport.json",
                    "path_meta": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}.meta.json"),
                    "path_chart": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}.png"),
                    "path_schart": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}.spark.png"),
                    "path_xport": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}.xport.json"),
                    "title": f"{title} {chsp[1]} - by {ds_type}",
                    "legend": f"Overview by {ds_type}",
                    "label": "[#]",
                    "link": chsp[2],
                    "totals": 0,
                    "datasets": rrd_args["dsets"],
                    "def_args": rrd_args["defs"],
                    "draw_args": rrd_args["draws"],
                    "xport_args": rrd_args["xports"],
                }
            )
            charts.append(
                {
                    "ds_type": ds_type,
                    "size": chsp[3],
                    "chid": f"{ds_type}-{chsp[0]}-t",
                    "fid": f"{ds_type}.{chsp[0]}-t",
                    "file_meta": f"{ds_type}.{chsp[0]}-t.meta.json",
                    "file_chart": f"{ds_type}.{chsp[0]}-t.png",
                    "file_schart": f"{ds_type}.{chsp[0]}-t.spark.png",
                    "file_xport": f"{ds_type}.{chsp[0]}-t.xport.json",
                    "path_meta": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}-t.meta.json"),
                    "path_chart": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}-t.png"),
                    "path_schart": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}-t.spark.png"),
                    "path_xport": os.path.join(self.reports_dir, f"{ds_type}.{chsp[0]}-t.xport.json"),
                    "title": f"{title} {chsp[1]} - by {ds_type} (TOTAL)",
                    "legend": f"Totals by {ds_type}",
                    "label": "[#]",
                    "link": chsp[2],
                    "totals": 1,
                    "datasets": rrd_args["dsets"],
                    "def_args": rrd_args["t_defs"],
                    "draw_args": rrd_args["t_draws"],
                    "xport_args": rrd_args["t_xports"],
                }
            )
        return charts

    # ---------------------------------------------------------------------------

    def _rrd_generate_meta(self, chspec, time_end):
        """
        Generate metadata JSON file for given chart.

        :param dict chspec: Chart specification dictionary. See the :py:func:`_rrd_prepare_charts` for details on the structure.
        :param int time_end: Timestamp of the high chart time boundary.
        :return: Full path to the file, that was written.
        :rtype: str
        """

        chspec["ts_start"] = time_end - chspec["size"]
        chspec["ts_end"] = time_end

        self._json_dump(chspec["path_meta"], chspec)

        return chspec["path_meta"]

    def _rrd_xport(self, chspec, time_end):
        """
        Perform actual export of given RRD database file into JSON file.

        :param dict chspec: Chart specification dictionary. See the :py:func:`_rrd_prepare_charts` for details on the structure.
        :param int time_end: Timestamp of the high chart time boundary.
        :return: Full path to the file, that was written.
        :rtype: str
        """

        try:
            rrdargs = chspec["def_args"] + chspec["xport_args"]
            result = rrdtool.xport(
                "--start",
                "{}".format(time_end - chspec["size"]),
                "--end",
                f"{time_end}",
                "--json",
                *rrdargs,
            )

            self._json_dump(chspec["path_xport"], result)

            return chspec["path_xport"]

        except rrdtool.OperationalError as exc:
            raise RrdsExportException(
                "Unable to export RRD chart data '{}:{}' into file '{}': {}".format(
                    chspec["fid"], chspec["title"], chspec["path_xport"], str(exc)
                )
            ) from exc

    def _rrd_generate_chart(self, chspec, time_end):
        """
        Actually generate given RRD chart.

        :param dict chspec: Chart specification dictionary. See the :py:func:`_rrd_prepare_charts` for details on the structure.
        :return: Full path to the file, that was written.
        :rtype: str
        """

        try:
            rrdargs = chspec["def_args"] + chspec["draw_args"]
            rrdtool.graph(
                chspec["path_chart"],
                "--width",
                f"{DFLT_WIDTH}",
                "--height",
                f"{DFLT_HEIGHT}",
                "--title",
                chspec["title"],
                "--watermark",
                f"Generated at {datetime.datetime.now()} by Mentat system, CESNET, z.s.p.o.",
                "--vertical-label",
                chspec["label"],
                "--right-axis-label",
                chspec["label"],
                "--start",
                "{}".format(time_end - chspec["size"]),
                "--end",
                f"{time_end}",
                "--slope-mode",
                *rrdargs,
            )

            return chspec["path_chart"]

        except rrdtool.OperationalError as exc:
            raise RrdsGraphException(
                "Unable to generate RRD chart '{}:{}' into file '{}': {}".format(
                    chspec["fid"], chspec["title"], chspec["path_chart"], str(exc)
                )
            ) from exc

    def _rrd_generate_sparkchart(self, chspec, time_end):
        """
        Actually generate given RRD spark chart.

        :param dict chspec: Chart specification dictionary. See the :py:func:`_rrd_prepare_charts` for details on the structure.
        :return: Full path to the file, that was written.
        :rtype: str
        """

        try:
            rrdargs = chspec["def_args"] + chspec["draw_args"]
            rrdtool.graph(
                chspec["path_schart"],
                "--width",
                f"{DFLT_SPARK_WIDTH}",
                "--height",
                f"{DFLT_SPARK_HEIGHT}",
                "--start",
                "{}".format(time_end - chspec["size"]),
                "--end",
                f"{time_end}",
                "--slope-mode",
                "--only-graph",
                "--no-legend",
                "--x-grid",
                "none",
                "--y-grid",
                "none",
                "--color",
                "BACK#FFFFFF",
                "--color",
                "ARROW#FFFFFF",
                "--color",
                "CANVAS#FFFFFF",
                "--color",
                "SHADEA#FFFFFF",
                "--color",
                "SHADEB#FFFFFF",
                "--color",
                "GRID#FFFFFF",
                "--color",
                "MGRID#FFFFFF",
                "--color",
                "FRAME#FFFFFF",
                "--color",
                "FONT#FFFFFF",
                *rrdargs,
            )

            return chspec["path_schart"]

        except rrdtool.OperationalError as exc:
            raise RrdsGraphException(
                "Unable to generate sparkline RRD chart '{}':'{}' into file '{}': {}".format(
                    chspec["fid"], chspec["title"], chspec["path_schart"], str(exc)
                )
            ) from exc
