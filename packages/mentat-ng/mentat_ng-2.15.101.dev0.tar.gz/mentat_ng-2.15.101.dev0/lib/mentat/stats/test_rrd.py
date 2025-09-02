#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


import os
import random
import shutil
import time
import unittest

from pyzenkit.utils import get_resource_path_fr

import mentat.stats.rrd

RRD_STATS_DIR = get_resource_path_fr("/var/tmp/utest_rrdstats")
RRD_REPORTS_DIR = get_resource_path_fr("/var/tmp")
TEST_DATA_SIZE = 5000
TIME_START = int(time.time())
TIME_START = TIME_START - (TIME_START % mentat.stats.rrd.DFLT_STEP) - (TEST_DATA_SIZE * mentat.stats.rrd.DFLT_STEP)


class TestMentatStatsRrd(unittest.TestCase):
    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    def setUp(self):
        os.makedirs(RRD_STATS_DIR)
        self.stats = mentat.stats.rrd.RrdStats(RRD_STATS_DIR, RRD_REPORTS_DIR)

    def tearDown(self):
        shutil.rmtree(RRD_STATS_DIR)

    def test_01_internals(self):
        """
        Perform the basic operativity tests of internal and helper methods.
        """
        self.assertEqual(self.stats.clean("abcDEF123-_"), "abcDEF123-_")
        self.assertEqual(
            self.stats.clean('abcDEF123-_<,>./?;:"[]{}()=+*!@#$%^&*'),
            "abcDEF123-___________________________",
        )

        self.assertEqual(self.stats._color_for_ds("typea", "testa"), "FF0000")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typea", "testb"), "FFFF00")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typea", "testc"), "0000FF")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typea", "testa"), "FF0000")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typea", "testb"), "FFFF00")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typea", "testc"), "0000FF")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testa"), "FF0000")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testb"), "FFFF00")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testc"), "0000FF")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testa"), "FF0000")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testb"), "FFFF00")  # pylint: disable=locally-disabled,protected-access
        self.assertEqual(self.stats._color_for_ds("typeb", "testc"), "0000FF")  # pylint: disable=locally-disabled,protected-access

    def test_02_prepare_db(self):
        """
        Test creation of RRD database files.
        """
        self.maxDiff = None

        tst = TIME_START - mentat.stats.rrd.DFLT_STEP

        #
        # Create RRD databases for three different datasets of two different types.
        #
        self.assertEqual(
            self.stats.prepare_db(f"typea.{mentat.stats.rrd.DB_TOTALS_NAME}", tst),
            (f"{RRD_STATS_DIR}/typea._totals.rrd", True),
        )
        self.assertEqual(
            self.stats.prepare_db(f"typeb.{mentat.stats.rrd.DB_TOTALS_NAME}", tst),
            (f"{RRD_STATS_DIR}/typeb._totals.rrd", True),
        )

        self.assertEqual(
            self.stats.prepare_db("typea.testa", tst),
            (f"{RRD_STATS_DIR}/typea.testa.rrd", True),
        )
        self.assertEqual(
            self.stats.prepare_db("typea.testb", tst),
            (f"{RRD_STATS_DIR}/typea.testb.rrd", True),
        )
        self.assertEqual(
            self.stats.prepare_db("typea.testc", tst),
            (f"{RRD_STATS_DIR}/typea.testc.rrd", True),
        )

        self.assertEqual(
            self.stats.prepare_db("typeb.testa", tst),
            (f"{RRD_STATS_DIR}/typeb.testa.rrd", True),
        )
        self.assertEqual(
            self.stats.prepare_db("typeb.testb", tst),
            (f"{RRD_STATS_DIR}/typeb.testb.rrd", True),
        )
        self.assertEqual(
            self.stats.prepare_db("typeb.testc", tst),
            (f"{RRD_STATS_DIR}/typeb.testc.rrd", True),
        )

        #
        # Create same RRD databases again, but the files already exist, and will not be created.
        #
        self.assertEqual(
            self.stats.prepare_db(f"typea.{mentat.stats.rrd.DB_TOTALS_NAME}", tst),
            (f"{RRD_STATS_DIR}/typea._totals.rrd", False),
        )
        self.assertEqual(
            self.stats.prepare_db(f"typeb.{mentat.stats.rrd.DB_TOTALS_NAME}", tst),
            (f"{RRD_STATS_DIR}/typeb._totals.rrd", False),
        )

        self.assertEqual(
            self.stats.prepare_db("typea.testa", tst),
            (f"{RRD_STATS_DIR}/typea.testa.rrd", False),
        )
        self.assertEqual(
            self.stats.prepare_db("typea.testb", tst),
            (f"{RRD_STATS_DIR}/typea.testb.rrd", False),
        )
        self.assertEqual(
            self.stats.prepare_db("typea.testc", tst),
            (f"{RRD_STATS_DIR}/typea.testc.rrd", False),
        )

        self.assertEqual(
            self.stats.prepare_db("typeb.testa", tst),
            (f"{RRD_STATS_DIR}/typeb.testa.rrd", False),
        )
        self.assertEqual(
            self.stats.prepare_db("typeb.testb", tst),
            (f"{RRD_STATS_DIR}/typeb.testb.rrd", False),
        )
        self.assertEqual(
            self.stats.prepare_db("typeb.testc", tst),
            (f"{RRD_STATS_DIR}/typeb.testc.rrd", False),
        )

        #
        # Check the existence of database files.
        #
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, f"typea.{mentat.stats.rrd.DB_TOTALS_NAME}.rrd")))
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, f"typeb.{mentat.stats.rrd.DB_TOTALS_NAME}.rrd")))

        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typea.testa.rrd")))
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typea.testb.rrd")))
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typea.testc.rrd")))

        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typeb.testa.rrd")))
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typeb.testb.rrd")))
        self.assertTrue(os.path.isfile(os.path.join(RRD_STATS_DIR, "typeb.testc.rrd")))

    def test_03_find_dbs(self):
        """
        Test the lookup of RRD database files.
        """
        self.maxDiff = None

        self.test_02_prepare_db()

        self.assertEqual(
            self.stats.find_dbs(),
            {
                "typea": [
                    (
                        "typea._totals",
                        "typea",
                        "_totals",
                        f"{RRD_STATS_DIR}/typea._totals.rrd",
                        True,
                    ),
                    (
                        "typea.testa",
                        "typea",
                        "testa",
                        f"{RRD_STATS_DIR}/typea.testa.rrd",
                        False,
                    ),
                    (
                        "typea.testb",
                        "typea",
                        "testb",
                        f"{RRD_STATS_DIR}/typea.testb.rrd",
                        False,
                    ),
                    (
                        "typea.testc",
                        "typea",
                        "testc",
                        f"{RRD_STATS_DIR}/typea.testc.rrd",
                        False,
                    ),
                ],
                "typeb": [
                    (
                        "typeb._totals",
                        "typeb",
                        "_totals",
                        f"{RRD_STATS_DIR}/typeb._totals.rrd",
                        True,
                    ),
                    (
                        "typeb.testa",
                        "typeb",
                        "testa",
                        f"{RRD_STATS_DIR}/typeb.testa.rrd",
                        False,
                    ),
                    (
                        "typeb.testb",
                        "typeb",
                        "testb",
                        f"{RRD_STATS_DIR}/typeb.testb.rrd",
                        False,
                    ),
                    (
                        "typeb.testc",
                        "typeb",
                        "testc",
                        f"{RRD_STATS_DIR}/typeb.testc.rrd",
                        False,
                    ),
                ],
            },
        )

        self.assertEqual(
            self.stats.find_dbs("typea"),
            {
                "typea": [
                    (
                        "typea._totals",
                        "typea",
                        "_totals",
                        f"{RRD_STATS_DIR}/typea._totals.rrd",
                        True,
                    ),
                    (
                        "typea.testa",
                        "typea",
                        "testa",
                        f"{RRD_STATS_DIR}/typea.testa.rrd",
                        False,
                    ),
                    (
                        "typea.testb",
                        "typea",
                        "testb",
                        f"{RRD_STATS_DIR}/typea.testb.rrd",
                        False,
                    ),
                    (
                        "typea.testc",
                        "typea",
                        "testc",
                        f"{RRD_STATS_DIR}/typea.testc.rrd",
                        False,
                    ),
                ]
            },
        )

        self.assertEqual(
            self.stats.find_dbs("typeb"),
            {
                "typeb": [
                    (
                        "typeb._totals",
                        "typeb",
                        "_totals",
                        f"{RRD_STATS_DIR}/typeb._totals.rrd",
                        True,
                    ),
                    (
                        "typeb.testa",
                        "typeb",
                        "testa",
                        f"{RRD_STATS_DIR}/typeb.testa.rrd",
                        False,
                    ),
                    (
                        "typeb.testb",
                        "typeb",
                        "testb",
                        f"{RRD_STATS_DIR}/typeb.testb.rrd",
                        False,
                    ),
                    (
                        "typeb.testc",
                        "typeb",
                        "testc",
                        f"{RRD_STATS_DIR}/typeb.testc.rrd",
                        False,
                    ),
                ]
            },
        )

    def test_04_update(self):
        """
        Test update of RRD database files.
        """
        self.maxDiff = None

        self.test_02_prepare_db()

        rrd_dbs = self.stats.find_dbs()

        for idx in range(TEST_DATA_SIZE):
            tstamp = TIME_START + (idx * mentat.stats.rrd.DFLT_STEP)
            total = 0

            for rrddb_list in rrd_dbs.values():
                for rrddb in rrddb_list:
                    value = random.randint(0, 1000)
                    total += value
                    if not rrddb[4]:
                        self.assertEqual(
                            self.stats.update(rrddb[0], value, tst=tstamp),
                            (rrddb[3], False),
                        )

                # Store summaries into '_totals' database.
                for rrddb in rrddb_list:
                    if rrddb[4]:
                        self.assertEqual(
                            self.stats.update(rrddb[0], total, tst=tstamp),
                            (rrddb[3], False),
                        )

    def test_05_update_all(self):
        """
        Test global update of all RRD database files.
        """
        self.maxDiff = None

        self.test_02_prepare_db()

        for idx in range(TEST_DATA_SIZE):
            tstamp = TIME_START + (idx * mentat.stats.rrd.DFLT_STEP)
            self.assertEqual(
                self.stats.update_all(random.randint(0, 1000), tst=tstamp),
                [
                    (f"{RRD_STATS_DIR}/typea._totals.rrd", False),
                    (f"{RRD_STATS_DIR}/typea.testa.rrd", False),
                    (f"{RRD_STATS_DIR}/typea.testb.rrd", False),
                    (f"{RRD_STATS_DIR}/typea.testc.rrd", False),
                    (f"{RRD_STATS_DIR}/typeb._totals.rrd", False),
                    (f"{RRD_STATS_DIR}/typeb.testa.rrd", False),
                    (f"{RRD_STATS_DIR}/typeb.testb.rrd", False),
                    (f"{RRD_STATS_DIR}/typeb.testc.rrd", False),
                ],
            )

    def test_06_export(self):
        """
        Test exporting of RRD database files.
        """
        self.maxDiff = None

        self.test_04_update()

        rrd_dbs = self.stats.find_dbs()

        for rrddb_list in rrd_dbs.values():
            for rrddb in rrddb_list:
                (rrddbf, flag_new, result) = self.stats.export(rrddb[0])
                self.assertEqual(rrddbf, rrddb[3])
                self.assertFalse(flag_new)
                self.assertTrue(result)

    def test_07_lookup(self):
        """
        Test lookup of all RRD charts, spark charts and JSON export files.
        """
        self.test_04_update()

        result = self.stats.lookup()
        self.assertIsInstance(result, list)
        self.assertTrue(result)  # Not empty

    def test_08_generate(self):
        """
        Test generating all RRD charts, spark charts and JSON export files.
        """
        self.test_04_update()

        time_end = TIME_START + (mentat.stats.rrd.DFLT_STEP * TEST_DATA_SIZE)
        result = self.stats.generate(time_end)

        for res in result:
            self.assertTrue(os.path.isfile(res))

        self.assertEqual(
            result,
            [
                f"{RRD_REPORTS_DIR}/typea.l6hours.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l6hours.png",
                f"{RRD_REPORTS_DIR}/typea.l6hours.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l6hours.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l6hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l6hours-t.png",
                f"{RRD_REPORTS_DIR}/typea.l6hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l6hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l24hours.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l24hours.png",
                f"{RRD_REPORTS_DIR}/typea.l24hours.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l24hours.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l24hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l24hours-t.png",
                f"{RRD_REPORTS_DIR}/typea.l24hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l24hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l72hours.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l72hours.png",
                f"{RRD_REPORTS_DIR}/typea.l72hours.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l72hours.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l72hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l72hours-t.png",
                f"{RRD_REPORTS_DIR}/typea.l72hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l72hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.lweek.meta.json",
                f"{RRD_REPORTS_DIR}/typea.lweek.png",
                f"{RRD_REPORTS_DIR}/typea.lweek.spark.png",
                f"{RRD_REPORTS_DIR}/typea.lweek.xport.json",
                f"{RRD_REPORTS_DIR}/typea.lweek-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.lweek-t.png",
                f"{RRD_REPORTS_DIR}/typea.lweek-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.lweek-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l2weeks.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l2weeks.png",
                f"{RRD_REPORTS_DIR}/typea.l2weeks.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l2weeks.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l2weeks-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l2weeks-t.png",
                f"{RRD_REPORTS_DIR}/typea.l2weeks-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l2weeks-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l4weeks.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l4weeks.png",
                f"{RRD_REPORTS_DIR}/typea.l4weeks.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l4weeks.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l4weeks-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l4weeks-t.png",
                f"{RRD_REPORTS_DIR}/typea.l4weeks-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l4weeks-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l3months.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l3months.png",
                f"{RRD_REPORTS_DIR}/typea.l3months.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l3months.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l3months-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l3months-t.png",
                f"{RRD_REPORTS_DIR}/typea.l3months-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l3months-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l6months.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l6months.png",
                f"{RRD_REPORTS_DIR}/typea.l6months.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l6months.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l6months-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l6months-t.png",
                f"{RRD_REPORTS_DIR}/typea.l6months-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l6months-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.lyear.meta.json",
                f"{RRD_REPORTS_DIR}/typea.lyear.png",
                f"{RRD_REPORTS_DIR}/typea.lyear.spark.png",
                f"{RRD_REPORTS_DIR}/typea.lyear.xport.json",
                f"{RRD_REPORTS_DIR}/typea.lyear-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.lyear-t.png",
                f"{RRD_REPORTS_DIR}/typea.lyear-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.lyear-t.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l2years.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l2years.png",
                f"{RRD_REPORTS_DIR}/typea.l2years.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l2years.xport.json",
                f"{RRD_REPORTS_DIR}/typea.l2years-t.meta.json",
                f"{RRD_REPORTS_DIR}/typea.l2years-t.png",
                f"{RRD_REPORTS_DIR}/typea.l2years-t.spark.png",
                f"{RRD_REPORTS_DIR}/typea.l2years-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l6hours.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l6hours.png",
                f"{RRD_REPORTS_DIR}/typeb.l6hours.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l6hours.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l6hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l6hours-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l6hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l6hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l24hours.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l24hours.png",
                f"{RRD_REPORTS_DIR}/typeb.l24hours.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l24hours.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l24hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l24hours-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l24hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l24hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l72hours.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l72hours.png",
                f"{RRD_REPORTS_DIR}/typeb.l72hours.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l72hours.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l72hours-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l72hours-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l72hours-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l72hours-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.lweek.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.lweek.png",
                f"{RRD_REPORTS_DIR}/typeb.lweek.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.lweek.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.lweek-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.lweek-t.png",
                f"{RRD_REPORTS_DIR}/typeb.lweek-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.lweek-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks.png",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l2weeks-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks.png",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l4weeks-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l3months.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l3months.png",
                f"{RRD_REPORTS_DIR}/typeb.l3months.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l3months.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l3months-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l3months-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l3months-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l3months-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l6months.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l6months.png",
                f"{RRD_REPORTS_DIR}/typeb.l6months.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l6months.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l6months-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l6months-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l6months-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l6months-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.lyear.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.lyear.png",
                f"{RRD_REPORTS_DIR}/typeb.lyear.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.lyear.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.lyear-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.lyear-t.png",
                f"{RRD_REPORTS_DIR}/typeb.lyear-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.lyear-t.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l2years.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l2years.png",
                f"{RRD_REPORTS_DIR}/typeb.l2years.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l2years.xport.json",
                f"{RRD_REPORTS_DIR}/typeb.l2years-t.meta.json",
                f"{RRD_REPORTS_DIR}/typeb.l2years-t.png",
                f"{RRD_REPORTS_DIR}/typeb.l2years-t.spark.png",
                f"{RRD_REPORTS_DIR}/typeb.l2years-t.xport.json",
            ],
        )


if __name__ == "__main__":
    unittest.main()
