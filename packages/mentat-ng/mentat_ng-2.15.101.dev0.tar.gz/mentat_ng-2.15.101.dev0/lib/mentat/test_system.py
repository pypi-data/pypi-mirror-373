#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.system` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import unittest
from pprint import pprint

import mentat.system

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------


class TestMentatStorage(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.system` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    def test_01_analyze_process_ps(self):
        """
        Perform basic tests of single process analysis.
        """
        self.maxDiff = None

        tests = [
            (
                "2744 sudo            sudo PYTHONPATH=./lib/ python3 bin/mentat-hawat.py",
                None,
            ),
            (
                "2745 python3         python3 bin/mentat-hawat.py",
                {
                    "args": None,
                    "exec": "mentat-hawat.py",
                    "name": "mentat-hawat.py",
                    "paralel": False,
                    "pid": 2745,
                    "psline": "2745 python3         python3 bin/mentat-hawat.py",
                    "process": "python3",
                },
            ),
            (
                "2747 postgres        postgres: 10/main: mentat mentat_events 127.0.0.1(48086) idle",
                None,
            ),
            (
                "4859 postgres        postgres: 10/main: mentat mentat_events 127.0.0.1(48168) idle",
                None,
            ),
            (
                "4861 python3         python3 /usr/local/bin/mentat-storage.py",
                {
                    "args": None,
                    "exec": "mentat-storage.py",
                    "name": "mentat-storage.py",
                    "paralel": False,
                    "pid": 4861,
                    "process": "python3",
                    "psline": "4861 python3         python3 /usr/local/bin/mentat-storage.py",
                },
            ),
            (
                "4866 postgres        postgres: 10/main: mentat mentat_main 127.0.0.1(48170) idle in transaction",
                None,
            ),
            (
                "4868 python3         python3 /usr/local/bin/mentat-enricher.py",
                {
                    "args": None,
                    "exec": "mentat-enricher.py",
                    "name": "mentat-enricher.py",
                    "paralel": False,
                    "pid": 4868,
                    "process": "python3",
                    "psline": "4868 python3         python3 /usr/local/bin/mentat-enricher.py",
                },
            ),
            (
                "4874 python3         python3 /usr/local/bin/mentat-inspector.py",
                {
                    "args": None,
                    "exec": "mentat-inspector.py",
                    "name": "mentat-inspector.py",
                    "paralel": False,
                    "pid": 4874,
                    "process": "python3",
                    "psline": "4874 python3         python3 /usr/local/bin/mentat-inspector.py",
                },
            ),
            (
                "4953 postgres        postgres: 10/main: mentat mentat_events 127.0.0.1(48172) idle",
                None,
            ),
            ("5401 python3         python3 lib/mentat/test_system.py", None),
        ]
        for test in tests:
            self.assertEqual(mentat.system.analyze_process_ps(test[0]), test[1])

    def test_02_analyze_process_list_ps(self):
        """
        Perform basic tests of process list analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("All Mentat processes:")
            pprint(mentat.system.analyze_process_list_ps())

    def test_03_analyze_pid_file(self):
        """
        Perform basic tests of single PID file analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("Single PID file:")
            pprint(mentat.system.analyze_pid_file("mentat-storage.py.pid", "/var/mentat/run/mentat-storage.py.pid"))

    def test_04_analyze_pid_files(self):
        """
        Perform basic tests of PID files analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("All PID files:")
            pprint(mentat.system.analyze_pid_files("/var/mentat/run"))

    def test_05_analyze_cron_file(self):
        """
        Perform basic tests of single cron file analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("Single cron file:")
            pprint(
                mentat.system.analyze_cron_file(
                    "mentat-statistician-py.cron",
                    "/etc/mentat/cron/mentat-statistician-py.cron",
                    {},
                )
            )

    def test_06_analyze_cron_files(self):
        """
        Perform basic tests of cron files analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("All cron files:")
            pprint(mentat.system.analyze_cron_files("/etc/mentat/cron", "/etc/cron.d"))

    def test_07_analyze_log_file(self):
        """
        Perform basic tests of single log file analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("Single log file:")
            pprint(mentat.system.analyze_log_file("mentat-storage.py.log", "/var/mentat/log/mentat-storage.py.log"))

    def test_08_analyze_log_files(self):
        """
        Perform basic tests of log files analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("All log files:")
            pprint(mentat.system.analyze_log_files("/var/mentat/log"))

    def test_09_analyze_runlog_file(self):
        """
        Perform basic tests of single runlog file analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("Single runlog file:")
            # pprint(mentat.system.analyze_runlog_file('201801221611.runlog', '/var/mentat/run/mentat-storage.py/201801221611.runlog'))

    def test_10_analyze_runlog_files(self):
        """
        Perform basic tests of runlog files analysis.
        """
        self.maxDiff = None

        if self.verbose:
            print("All runlog files:")
            # pprint(mentat.system.analyze_runlog_files('/var/mentat/run'))

    def test_11_module_status(self):
        """
        Perform the basic Mentat system tests.
        """
        self.maxDiff = None

        modules = mentat.system.make_module_list(
            [
                {"exec": "mentat-storage.py", "args": []},
                {"exec": "mentat-enricher.py", "args": []},
                {"exec": "mentat-inspector.py", "args": []},
            ]
        )
        cronjobs = mentat.system.make_cronjob_list(
            [
                {"name": "geoipupdate"},
                {"name": "mentat-cleanup-py"},
                {"name": "mentat-precache-py"},
                {"name": "mentat-statistician-py"},
            ]
        )

        if self.verbose:
            print("System status:")
            pprint(
                mentat.system.system_status(
                    modules,
                    cronjobs,
                    "/etc/mentat",
                    "/etc/cron.d",
                    "/var/mentat/log",
                    "/var/mentat/run",
                )
            )

        # self.assertTrue(
        #    mentat.system.system_status(
        #        modules,
        #        cronjobs,
        #        '/etc/mentat',
        #        '/etc/cron.d',
        #        '/var/mentat/log',
        #        '/var/mentat/run'
        #    )
        # )


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
