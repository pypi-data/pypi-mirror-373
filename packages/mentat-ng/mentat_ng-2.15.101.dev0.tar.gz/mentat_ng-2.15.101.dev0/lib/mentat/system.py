#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Mentat system management and inspection library.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import collections
import datetime
import os
import re
import subprocess

import pyzenkit.jsonconf

#
# Real-time module status codes.
#
STATUS_RT_RUNNING_OK = 0  # Module is running or service is OK
STATUS_RT_RUNNING_PF_MISSING = 1  # Module is running, but pid file is missing
STATUS_RT_RUNNING_PID_MISSMATCH = 2  # Module is running, but pid file contains different PID
STATUS_RT_RUNNING_INCONSISTENT = 10  # Module is running, but pid files are inconsistent
STATUS_RT_RUNNING_FEWER = 11  # Module is running in fewer that required instances
STATUS_RT_RUNNING_MORE = 12  # Module is running in more that required instances
STATUS_RT_DEAD_PF_EXISTS = 3  # Module is dead and pid file exists
STATUS_RT_DEAD_LOCK_EXISTS = 4  # Module is dead and lock file exists
STATUS_RT_NOT_RUNNING = 5  # Module is not running
STATUS_RT_UNKNOWN = 6  # Module or service status is unknown

# Overall module status messages
OVERALL_MODULE_STATUS_MESSAGES = {
    STATUS_RT_RUNNING_OK: "All modules are running OK",
    STATUS_RT_RUNNING_PF_MISSING: "All modules are running, but all pid files are missing",
    STATUS_RT_RUNNING_PID_MISSMATCH: "All modules are running, but all pid files contain different PID",
    STATUS_RT_RUNNING_INCONSISTENT: "All modules are running, but all pid files are inconsistent",
    STATUS_RT_RUNNING_FEWER: "All modules are running in fewer that required instances",
    STATUS_RT_RUNNING_MORE: "All modules are running in more that required instances",
    STATUS_RT_DEAD_PF_EXISTS: "All modules are dead and all pid files exist",
    STATUS_RT_DEAD_LOCK_EXISTS: "All modules are dead and all lock files exist",
    STATUS_RT_NOT_RUNNING: "All modules are not running",
    STATUS_RT_UNKNOWN: "Some modules are in different state, overall system state is unknown",
}

#
# Cronjob module status codes.
#
STATUS_CJ_ENABLED = 0  # Cronjob is enabled
STATUS_CJ_DISABLED = 5  # Cronjob is not running
STATUS_CJ_UNKNOWN = 6  # Cronjob status is unknown

# Overall cronjob status messages
OVERALL_CRONJOB_STATUS_MESSAGES = {
    STATUS_CJ_ENABLED: "All cronjobs are enabled",
    STATUS_CJ_DISABLED: "All cronjobs are disabled",
    STATUS_CJ_UNKNOWN: "Some cronjobs are in different state, overall system state is unknown",
}

#
# Cronjob module status codes.
#
STATUS_ONLINE = 0  # The whole system is online
STATUS_OFFLINE = 5  # The whole system is offline
STATUS_UNKNOWN = 6  # System overall status is unknown

# Overall cronjob status messages
OVERALL_STATUS_MESSAGES = {
    STATUS_ONLINE: "All modules are running OK and all cronjobs are enabled",
    STATUS_OFFLINE: "All modules are NOT running and all cronjobs are disabled",
    STATUS_UNKNOWN: "Some modules and cronjobs are in different state, overall system state is unknown",
}


REGEXP_MENTAT_PS = re.compile(
    r"\s*(\d+)\s+([^\s]+)\s+([^\s]*(?:python(?:\d+(?:\.\d+)?)?))\s+[^\s]+(mentat-[^\s]+)(?:\s+(.*))?"
)
"""Regular expression for selecting Mentat related processes."""
REGEXP_MENTAT_PIDF = re.compile(r"(.+?)(?:\.([0-9a-fA-F]+))?\.pid$")
"""Regular expression for selecting Mentat related PID files."""
REGEXP_MENTAT_CRONF = re.compile(r"(.+)\.cron$")
"""Regular expression for selecting Mentat related log files."""
REGEXP_MENTAT_LOGF = re.compile(r"(.+)\.log$")
"""Regular expression for selecting Mentat related log files."""
REGEXP_MENTAT_RLOGF = re.compile(r"(.+)(?:\.([0-9a-fA-F]+))?\.runlog$")
"""Regular expression for selecting Mentat related runlog files."""


class MentatModule:
    """
    Class representing Mentat real-time module configuration for control utility.
    """

    def __init__(self, params):
        if "exec" not in params:
            # raise pyzenkit.baseapp.ZenAppSetupException
            raise Exception("Module definition in configuration file is missing mandatory attribute 'exec'.")

        self.executable = params["exec"]

        self.name = params.get("name", self.executable)
        self.args = params.get("args", [])
        self.paralel = params.get("paralel", False)
        self.count = int(params.get("count", 0))

        if self.paralel and self.count <= 1:
            # raise pyzenkit.baseapp.ZenAppSetupException
            raise Exception(
                f"Module '{self.name}' is configured to run in paralel and the 'count' attribute is missing or below '2'."
            )

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"MentatModule(name={self.name},executable={self.executable})"


class MentatCronjob:
    """
    Class representing Mentat cronjob module configuration for control utility.
    """

    def __init__(self, params):
        if "name" not in params:
            # raise pyzenkit.baseapp.ZenAppSetupException
            raise Exception("Cronjob definition in configuration file is missing mandatory attribute 'name'.")

        self.name = params["name"]

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"MentatCronjob(name={self.name})"


def make_module_list(modules):
    """
    *Helper function*
    """
    result = collections.OrderedDict()
    for mod in modules:
        record = MentatModule(mod)
        result[record.name] = record
    return result


def make_cronjob_list(cronjobs):
    """
    *Helper function*
    """
    result = collections.OrderedDict()
    for mod in cronjobs:
        record = MentatCronjob(mod)
        result[record.name] = record
    return result


# -------------------------------------------------------------------------------


def analyze_process_ps(cmdline):
    """
    Analyze given process command line received from ``ps`` utility.

    Example of returned structure::

        {
            'args': None,
            'exec': 'mentat-storage.py',
            'name': 'mentat-storage.py',
            'paralel': False,
            'pid': 9349,
            'process': 'python3',
            'psline': '9349 python3 python3 /usr/local/bin/mentat-storage.py'
        }

    :param str cmdline: Command line as received from ``ps`` utility).
    :return: Structure containing parsed process information.
    :rtype: dict
    """
    match = REGEXP_MENTAT_PS.match(cmdline)
    if not match:
        return None
    if match.group(4) in ["mentat-controller.py"]:
        return None

    record = {
        "process": match.group(2),
        "name": match.group(4),
        "exec": match.group(4),
        "args": match.group(5),
        "pid": int(match.group(1)),
        "psline": cmdline,
        "paralel": False,
    }

    # Attempt to parse command line arguments for selected data.
    if record["args"]:
        # Attempt to parse custom name.
        match = re.search(r"--name(?: |=)([^\s]+)", record["args"])
        if match:
            record["name"] = match.group(1)

        # Attempt to detect paralel mode switch.
        match = re.search("--paralel", record["args"])
        if match:
            record["paralel"] = True

    return record


def analyze_process_list_ps():
    """
    Analyze all running processes using Linux`s ``ps`` utility.

    Processes are listed with following exact command::

        /bin/ps axo pid,comm,args | grep mentat | grep -v grep

    Only processes that match the internal regular expression are selected.

    Example of returned structure::

        {
            'mentat-enricher.py': {9356: {'args': None,
                                   'exec': 'mentat-enricher.py',
                                   'name': 'mentat-enricher.py',
                                   'paralel': False,
                                   'pid': 9356,
                                   'process': 'python3',
                                   'psline': '9356 python3 python3 /usr/local/bin/mentat-enricher.py'}},
            'mentat-inspector.py': {9362: {'args': None,
                                    'exec': 'mentat-inspector.py',
                                    'name': 'mentat-inspector.py',
                                    'paralel': False,
                                    'pid': 9362,
                                    'process': 'python3',
                                    'psline': '9362 python3 python3 /usr/local/bin/mentat-inspector.py'}},
            'mentat-storage.py': {9349: {'args': None,
                                  'exec': 'mentat-storage.py',
                                  'name': 'mentat-storage.py',
                                  'paralel': False,
                                  'pid': 9349,
                                  'process': 'python3',
                                  'psline': '9349 python3 python3 /usr/local/bin/mentat-storage.py'}}
        }

    :return: Structured dictionary containing information about selected processess.
    :rtype: dict
    """
    processes = collections.defaultdict(dict)
    with subprocess.Popen(
        ["/bin/ps axo pid,comm,args | grep mentat | grep -v grep"],
        stdout=subprocess.PIPE,
        shell=True,
    ) as proc:
        for psline in proc.stdout:
            psline = psline.rstrip()
            psline = psline.decode("utf-8")

            record = analyze_process_ps(psline)
            if not record:
                continue

            processes[record["name"]][record["pid"]] = record
    return dict(processes)


def analyze_pid_file(pid_file, pid_file_path):
    """
    Analyze given PID file.

    Example of returned structure::

        {
            'atime': datetime.datetime(2018, 1, 23, 8, 25, 16, 439742),
            'file': 'mentat-storage.py.pid',
            'mtime': datetime.datetime(2018, 1, 23, 8, 25, 12, 943727),
            'name': 'mentat-storage.py',
            'paralel': False,
            'path': '/var/mentat/run/mentat-storage.py.pid',
            'pid': 9349,
            'size': 5
        }

    :param str pid_file: Basename of the PID file.
    :param str pid_file_path: Full path to the PID file.
    :return: Structure containing parsed PID file information.
    :rtype: dict
    """
    try:
        match = REGEXP_MENTAT_PIDF.match(pid_file)
        if not match:
            return None

        pid = None
        with open(pid_file_path, "r", encoding="utf8") as pidf:
            pid = pidf.read()
        pid = int(pid)

        fsstat = os.stat(pid_file_path)
        return {
            "name": match.group(1),
            "file": pid_file,
            "path": pid_file_path,
            "pid": int(pid),
            "paralel": bool(match.group(2)),
            "size": fsstat.st_size,
            "atime": datetime.datetime.utcfromtimestamp(fsstat.st_atime),
            "mtime": datetime.datetime.utcfromtimestamp(fsstat.st_mtime),
        }
    except Exception:
        return None


def analyze_pid_files(pid_dir_path):
    """
    Analyze all PID files in given run directory.

    Example of returned structure::

        {
            'mentat-enricher.py': {9356: {'atime': datetime.datetime(2018, 1, 23, 8, 25, 16, 439742),
                                          'file': 'mentat-enricher.py.pid',
                                          'mtime': datetime.datetime(2018, 1, 23, 8, 25, 14, 319733),
                                          'name': 'mentat-enricher.py',
                                          'paralel': False,
                                          'path': '/var/mentat/run/mentat-enricher.py.pid',
                                          'pid': 9356,
                                          'size': 5}},
            'mentat-inspector.py': {9362: {'atime': datetime.datetime(2018, 1, 23, 8, 25, 16, 439742),
                                           'file': 'mentat-inspector.py.pid',
                                           'mtime': datetime.datetime(2018, 1, 23, 8, 25, 14, 947736),
                                           'name': 'mentat-inspector.py',
                                           'paralel': False,
                                           'path': '/var/mentat/run/mentat-inspector.py.pid',
                                           'pid': 9362,
                                           'size': 5}},
            'mentat-storage.py': {9349: {'atime': datetime.datetime(2018, 1, 23, 8, 25, 16, 439742),
                                         'file': 'mentat-storage.py.pid',
                                         'mtime': datetime.datetime(2018, 1, 23, 8, 25, 12, 943727),
                                         'name': 'mentat-storage.py',
                                         'paralel': False,
                                         'path': '/var/mentat/run/mentat-storage.py.pid',
                                         'pid': 9349,
                                         'size': 5}}
        }

    :param str pid_dir_path: path to directory containing PID files.
    :return: Structure containing parsed information for all PID files.
    :rtype: dict
    """
    pid_files = collections.defaultdict(dict)

    all_files = os.listdir(pid_dir_path)
    for pid_file in all_files:
        pid_file_path = os.path.join(pid_dir_path, pid_file)
        if not os.path.isfile(pid_file_path):
            continue

        record = analyze_pid_file(pid_file, pid_file_path)
        if not record:
            continue

        pid_files[record["name"]][record["pid"]] = record
    return dict(pid_files)


def analyze_cron_file(cron_file, cron_file_path, cron_links):
    """
    Analyze given cron file.

    Example of returned structure::

        {
            'atime': datetime.datetime(2018, 1, 21, 9, 13, 48, 34648),
            'file': 'mentat-statistician-py.cron',
            'link': None,
            'mtime': datetime.datetime(2017, 7, 19, 10, 25, 30),
            'name': 'mentat-statistician-py',
            'path': '/etc/mentat/cron/mentat-statistician-py.cron',
            'size': 429
        }

    :param str cron_file: Basename of the cron file.
    :param str cron_file_path: Full path to the cron file.
    :param dict cron_links: Dictionary containing existing links in cron directory.
    :return: Structure containing parsed cron file information.
    :rtype: dict
    """
    try:
        match = REGEXP_MENTAT_CRONF.match(cron_file)
        if not match:
            return None

        fsstat = os.stat(cron_file_path)
        return {
            "name": match.group(1),
            "file": cron_file,
            "path": cron_file_path,
            "size": fsstat.st_size,
            "atime": datetime.datetime.utcfromtimestamp(fsstat.st_atime),
            "mtime": datetime.datetime.utcfromtimestamp(fsstat.st_mtime),
            "link": cron_links.get(cron_file_path, None),
        }
    except Exception:
        return None


def analyze_cron_files(cfg_dir_path, cron_dir_path):
    """
    Analyze all cron files in config and cron directory.

    Example of returned structure::

        {
            'mentat-precache-py': {'atime': datetime.datetime(2018, 1, 21, 9, 13, 45),
                                   'file': 'mentat-precache-py.cron',
                                   'link': None,
                                   'mtime': datetime.datetime(2017, 9, 1, 11, 10, 17),
                                   'name': 'mentat-precache-py',
                                   'path': '/etc/mentat/cron/mentat-precache-py.cron',
                                   'size': 417},
            'mentat-statistician-py': {'atime': datetime.datetime(2018, 1, 21, 9, 13, 48, 34648),
                                       'file': 'mentat-statistician-py.cron',
                                       'link': None,
                                       'mtime': datetime.datetime(2017, 7, 19, 10, 25, 30),
                                       'name': 'mentat-statistician-py.cron',
                                       'path': '/etc/mentat/cron/mentat-statistician-py.cron',
                                       'size': 429}
        }

    :param str cfg_dir_path: Path to configuration directory containing cron scripts.
    :param str cron_dir_path: Path to system cron directory.
    :return: Structure containing parsed cron file information.
    :rtype: dict
    """
    cron_files = {}
    cron_links = {}

    crn_all_files = os.listdir(cron_dir_path)
    for cron_file in crn_all_files:
        cron_file_path = os.path.join(cron_dir_path, cron_file)
        if not os.path.islink(cron_file_path):
            continue
        cron_links[os.readlink(cron_file_path)] = cron_file_path

    cfg_all_files = os.listdir(cfg_dir_path)
    for cron_file in cfg_all_files:
        cron_file_path = os.path.join(cfg_dir_path, cron_file)
        if not os.path.isfile(cron_file_path):
            continue

        record = analyze_cron_file(cron_file, cron_file_path, cron_links)
        if not record:
            continue

        cron_files[record["name"]] = record
    return cron_files


def analyze_log_file(log_file, log_file_path):
    """
    Analyze given log file.

    Example of returned structure::

        {
            'atime': datetime.datetime(2018, 1, 22, 15, 11, 15, 562358),
            'file': 'mentat-storage.py.log',
            'mtime': datetime.datetime(2018, 1, 23, 9, 8, 43, 403734),
            'name': 'mentat-storage.py',
            'path': '/var/mentat/log/mentat-storage.py.log',
            'size': 5831678
        }

    :param str log_file: Basename of the log file.
    :param str log_file_path: Full path to the log file.
    :return: Structure containing parsed log file information.
    :rtype: dict
    """
    try:
        match = REGEXP_MENTAT_LOGF.match(log_file)
        if not match:
            return None

        fsstat = os.stat(log_file_path)
        return {
            "name": match.group(1),
            "file": log_file,
            "path": log_file_path,
            "size": fsstat.st_size,
            "atime": datetime.datetime.utcfromtimestamp(fsstat.st_atime),
            "mtime": datetime.datetime.utcfromtimestamp(fsstat.st_mtime),
        }
    except Exception:
        return None


def analyze_log_files(log_dir_path):
    """
    Analyze all PID files in run directory.

    Example of returned structure::

        {
            'mentat-enricher.py': {'atime': datetime.datetime(2018, 1, 9, 12, 25, 26, 338720),
                                   'file': 'mentat-enricher.py.log',
                                   'mtime': datetime.datetime(2018, 1, 23, 9, 8, 38, 163710),
                                   'name': 'mentat-enricher.py',
                                   'path': '/var/mentat/log/mentat-enricher.py.log',
                                   'size': 6057586},
            'mentat-inspector.py': {'atime': datetime.datetime(2018, 1, 18, 17, 5, 22, 734164),
                                    'file': 'mentat-inspector.py.log',
                                    'mtime': datetime.datetime(2018, 1, 23, 9, 8, 35, 291697),
                                    'name': 'mentat-inspector.py',
                                    'path': '/var/mentat/log/mentat-inspector.py.log',
                                    'size': 8156449},
            'mentat-storage.py': {'atime': datetime.datetime(2018, 1, 22, 15, 11, 15, 562358),
                                  'file': 'mentat-storage.py.log',
                                  'mtime': datetime.datetime(2018, 1, 23, 9, 8, 43, 403734),
                                  'name': 'mentat-storage.py',
                                  'path': '/var/mentat/log/mentat-storage.py.log',
                                  'size': 5831678}
        }

    :param str log_dir_path: Path to directory containing log files.
    :return: Structure containing parsed log file information.
    :rtype: dict
    """
    log_files = {}

    all_files = os.listdir(log_dir_path)
    for log_file in all_files:
        log_file_path = os.path.join(log_dir_path, log_file)
        if not os.path.isfile(log_file_path):
            continue

        record = analyze_log_file(log_file, log_file_path)
        if not record:
            continue

        log_files[record["name"]] = record
    return log_files


def analyze_runlog_file(runlog_file, runlog_file_path):
    """
    Analyze given runlog file.

    Example of returned structure::

        {
            'atime': datetime.datetime(2018, 1, 22, 16, 33, 56, 766819),
            'data': {...},
            'file': '201801221611.runlog',
            'mtime': datetime.datetime(2018, 1, 22, 15, 30, 0, 427902),
            'name': '201801221611',
            'path': '/var/mentat/run/mentat-storage.py/201801221611.runlog',
            'size': 1209
        }

    :param str runlog_file: Basename of the runlog file.
    :param str runlog_file_path: Full path to the runlog file.
    :return: Structure containing parsed runlog file information.
    :rtype: dict
    """
    try:
        match = REGEXP_MENTAT_RLOGF.match(runlog_file)
        if not match:
            return None

        fsstat = os.stat(runlog_file_path)
        return {
            "name": match.group(1),
            "file": runlog_file,
            "path": runlog_file_path,
            "size": fsstat.st_size,
            "atime": datetime.datetime.utcfromtimestamp(fsstat.st_atime),
            "mtime": datetime.datetime.utcfromtimestamp(fsstat.st_mtime),
            "data": pyzenkit.jsonconf.json_load(runlog_file_path),
        }
    except Exception:
        return None


def analyze_runlog_files(run_dir_path, limit=None):
    """
    Analyze all runlog files in run directory.

    :param str run_dir_path: Path to directory containing run files.
    :return: Structure containing parsed runlog file information.
    :rtype: dict
    """
    runlog_files = collections.defaultdict(dict)

    all_files = os.listdir(run_dir_path)
    for runlog_dir in all_files:
        runlog_dir_path = os.path.join(run_dir_path, runlog_dir)
        if not os.path.isdir(runlog_dir_path):
            continue

        all_rl_files = sorted(os.listdir(runlog_dir_path), reverse=True)
        file_counter = 0
        for runlog_file in all_rl_files:
            runlog_file_path = os.path.join(runlog_dir_path, runlog_file)
            if not os.path.isfile(runlog_file_path):
                continue

            record = analyze_runlog_file(runlog_file, runlog_file_path)
            if not record:
                continue

            file_counter += 1
            if limit and file_counter > limit:
                break

            runlog_files[runlog_dir][record["name"]] = record
    return dict(runlog_files)


# -------------------------------------------------------------------------------


def module_status(mod_data, pidf_data, proc_data, overall_status):
    """
    Analyze status of given module.
    """
    # Check the consistency of running processes and pid files.
    consistent = True
    if pidf_data:
        for pid in pidf_data:
            if not proc_data or pid not in proc_data:
                overall_status["messages"]["error"].append(
                    (
                        "Process '{}' is dead, but pid file '{}' exists".format(pid, pidf_data[pid]["path"]),
                        "pidfile",
                        pidf_data[pid]["path"],
                    )
                )
                consistent = False
    if proc_data:
        for pid in proc_data:
            if not pidf_data or pid not in pidf_data:
                overall_status["messages"]["error"].append(
                    (
                        "Process '{}':'{}' is running, but  pid file is missing".format(pid, proc_data[pid]["name"]),
                        "process",
                        pid,
                    )
                )
                consistent = False

    # PID file exists and process is running.
    if pidf_data and proc_data:
        # Check the number of running processes
        if mod_data.paralel:
            if mod_data.count > len(proc_data.keys()):
                return (
                    STATUS_RT_RUNNING_FEWER,
                    f"There are fewer instances running than required ({mod_data.count}:{len(proc_data.keys())})",
                )
            if mod_data.count < len(proc_data.keys()):
                return (
                    STATUS_RT_RUNNING_MORE,
                    f"There are more instances running than required ({mod_data.count}:{len(proc_data.keys())})",
                )

        # Process is running or service is OK
        if consistent:
            return (
                STATUS_RT_RUNNING_OK,
                f"Process is running or service is OK ({len(proc_data.keys())})",
            )
        return (
            STATUS_RT_RUNNING_INCONSISTENT,
            "Process is running in inconsistent state",
        )

    # PID file(s) exist(s) and any process is not running
    if pidf_data:
        if mod_data.paralel:
            return (
                STATUS_RT_DEAD_PF_EXISTS,
                "Processes are dead, but some pid files exist",
            )
        return (STATUS_RT_DEAD_PF_EXISTS, "Process is dead, but pid file exist")

    # PID file(s) do(es) not exist, but some process is running
    if proc_data:
        if mod_data.paralel:
            return (
                STATUS_RT_RUNNING_PF_MISSING,
                "Processes are running, but pid files are missing",
            )
        return (
            STATUS_RT_RUNNING_PF_MISSING,
            "Process is running, but pid file is missing",
        )

    # Process is not running
    return (STATUS_RT_NOT_RUNNING, "Process is not running or service is stopped")


def cronjob_status(cronj_data, cronf_data, overall_status):
    """
    Analyze status of given cron module.
    """
    if cronf_data and cronf_data["link"]:
        return (STATUS_CJ_ENABLED, "Cronjob is enabled")
    return (STATUS_CJ_DISABLED, "Cronjob is disabled")


def system_status(modules, cronjobs, cfg_dir_path, cron_dir_path, log_dir_path, run_dir_path):
    """
    Analyze status of all modules and cronjobs and detect additional problems.
    """
    status = {}
    status["dt"] = datetime.datetime.utcnow()
    status["modules"] = {}
    status["cronjobs"] = {}
    status["messages"] = {"info": [], "notice": [], "warning": [], "error": []}
    status["processes"] = analyze_process_list_ps()
    status["pid_files"] = analyze_pid_files(run_dir_path)
    status["log_files"] = analyze_log_files(log_dir_path)
    status["runlog_files"] = analyze_runlog_files(run_dir_path, limit=1)
    status["cron_files"] = analyze_cron_files(os.path.join(cfg_dir_path, "cron"), cron_dir_path)
    status["resultm"] = None
    status["resultc"] = None
    status["result"] = None

    # A) Analyze status of configured modules.
    for mname, mdata in modules.items():
        status["modules"][mname] = module_status(
            mdata,
            status["pid_files"].get(mname, None),
            status["processes"].get(mname, None),
            status,
        )

    # B) Analyze status of configured cronjob modules.
    for mname, mdata in cronjobs.items():
        status["cronjobs"][mname] = cronjob_status(mdata, status["cron_files"].get(mname, None), status)

    # -----

    _analyze_unconfigured_pid_files(status, modules)
    _analyze_unconfigured_modules(status, modules)
    _analyze_unconfigured_cronjobs(status, cronjobs)

    # -----

    # Determine overall status of real-time processing modules.
    for mstatus in status["modules"].values():
        if not status["resultm"]:
            status["resultm"] = (mstatus[0], OVERALL_MODULE_STATUS_MESSAGES[mstatus[0]])
        elif status["resultm"][0] != mstatus[0]:
            status["resultm"] = (
                STATUS_RT_UNKNOWN,
                OVERALL_MODULE_STATUS_MESSAGES[STATUS_RT_UNKNOWN],
            )
    if not status["resultm"]:
        status["resultm"] = (
            STATUS_RT_NOT_RUNNING,
            OVERALL_MODULE_STATUS_MESSAGES[STATUS_RT_NOT_RUNNING],
        )

    # Determine overall status of cronjob modules.
    for mstatus in status["cronjobs"].values():
        if not status["resultc"]:
            status["resultc"] = (
                mstatus[0],
                OVERALL_CRONJOB_STATUS_MESSAGES[mstatus[0]],
            )
        elif status["resultc"][0] != mstatus[0]:
            status["resultc"] = (
                STATUS_CJ_UNKNOWN,
                OVERALL_CRONJOB_STATUS_MESSAGES[STATUS_CJ_UNKNOWN],
            )
    if not status["resultc"]:
        status["resultc"] = (
            STATUS_CJ_DISABLED,
            OVERALL_CRONJOB_STATUS_MESSAGES[STATUS_CJ_DISABLED],
        )

    # Determine overall status of the whole system.
    if status["resultm"][0] != status["resultc"][0]:
        status["result"] = (STATUS_UNKNOWN, OVERALL_STATUS_MESSAGES[STATUS_UNKNOWN])
    else:
        status["result"] = (
            status["resultm"][0],
            OVERALL_STATUS_MESSAGES[status["resultm"][0]],
        )

    return status


def analyze_versions():
    """
    Analyze versions of various relevant dependencies (like PostgreSQL, ...).
    """
    result = {}

    out = subprocess.check_output(["psql", "-V"])
    result["postgresql"] = out.decode("utf-8").strip()

    return result


# -------------------------------------------------------------------------------


def _analyze_unconfigured_pid_files(status, modules):
    """
    Analyze list of all PID files and find any that do not belong to known modules.
    """
    for mname in sorted(status["pid_files"].keys()):
        if mname in modules:
            continue
        for pid in sorted(status["pid_files"][mname].keys()):
            status["messages"]["info"].append(
                (
                    "Unknown pid file '{}' for PID '{}'".format(status["pid_files"][mname][pid]["path"], pid),
                    "pidfile",
                    status["pid_files"][mname][pid]["path"],
                )
            )


def _analyze_unconfigured_modules(status, modules):
    """
    Analyze list of all processes files and find any that do not belong to known modules.
    """
    for mname in sorted(status["processes"].keys()):
        if mname in modules:
            continue
        for pid in sorted(status["processes"][mname].keys()):
            status["messages"]["info"].append(
                (
                    "Unknown process '{}' with PID '{}'".format(status["processes"][mname][pid]["exec"], pid),
                    "pidfile",
                    pid,
                )
            )


def _analyze_unconfigured_cronjobs(status, cronjobs):
    """
    Analyze list of all cron files and find any that do not belong to known cronjob
    modules.
    """
    for mname in sorted(status["cron_files"].keys()):
        if mname in cronjobs:
            continue
        if status["cron_files"][mname]["link"]:
            status["messages"]["info"].append(
                (
                    "Unconfigured cron file '{}' for cron module '{}'".format(
                        status["cron_files"][mname]["link"],
                        status["cron_files"][mname]["path"],
                    ),
                    "cronfile",
                    status["cron_files"][mname]["path"],
                )
            )
