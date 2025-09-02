#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing PostgreSQL database backup functions
and features.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-backup.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-backup.py --debug

    # Run with increased logging level.
    mentat-backup.py --log-level debug


Available script commands
-------------------------

``backup`` (*default*)
    Perform backup of data of all configured collections within configured
    time interval thresholds.

``remote-mount``
    Mount the remote backup storage to local mount point and exit.

``remote-unmount``
    Unmount the remote backup storage from local mount point and exit.

``status``
    Determine the status of backup files on the remote storage.


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--no-upload``
    Do not upload the backup file to remote storage (*flag*).

    *Type:* ``boolean``, *default:* ``False``

``--mount-point dir-name``
    Name of the mount point directory.

    *Type:* ``string``, *default:* ``/media/du-store``

``--temp-dir dir-name``
    Name of the log file.

    *Type:* ``string``, *default:* ``/var/tmp``

``--backup-dir dir-name``
    Name of the log file.

    *Type:* ``string``, *default:* ``/var/mentat/backups``

``--remote-host user@host.domain.org``
    SSH connection string for the remote host to which to sychronize backups.

    *Type:* ``string``, *default:* ``None``

``--remote-dir dir-name``
    Directory path on the remote host to which to sychronize backups.

    *Type:* ``string``, *default:* ``None``


Backup script requirements
--------------------------

To enable backup synchronization to remote machine, SSH access without password
must be configured and accessible for the ``mentat`` system user. Additionally,
the ``sshfs`` package must be installed on local machine.


Backup structure
----------------

This script produces ``.tar.gz`` compressed archives for each run. Each archive
contains backups for following databases:

main database
    This database us backupped using native ``pg_dump`` command and may be restored
    with its ``pg_restore`` counterpart.

    Resources: https://www.postgresql.org/docs/current/static/backup-dump.html

event database
    This database is backupped only selectively using ``psql`` utility. This
    constraint is due to the possibly huge size of the whole database, to instead
    the incremental approach is used.

    Resources: https://www.postgresql.org/message-id/CAM6mie+8hZPyaXCGgHTwS3=ECzwkLyLn99R4LEtkXgUG7+yNnA@mail.gmail.com
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import glob
import math
import os
import pprint
import re
import subprocess
import time

import pyzenkit.zenscript

import mentat.const
import mentat.script.base


class MentatBackupScript(mentat.script.base.MentatBaseScript):
    """
    Implementation of Mentat module (script) providing database backup functions
    and features.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_NO_UPLOAD = "no_upload"
    CONFIG_MOUNT_POINT = "mount_point"
    CONFIG_TEMP_DIR = "temp_dir"
    CONFIG_BACKUP_DIR = "backup_dir"
    CONFIG_REMOTE_HOST = "remote_host"
    CONFIG_REMOTE_DIR = "remote_dir"

    def __init__(self):
        """
        Initialize backup script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        super().__init__(description="mentat-backup.py - PostgreSQL database backup script for Mentat system")

    def _init_argparser(self, **kwargs):
        """
        Initialize script command line argument parser. This method overrides the
        base implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this script object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for custom script arguments.
        #
        arggroup_script = argparser.add_argument_group("custom script arguments")

        arggroup_script.add_argument(
            "--no-upload",
            help="do not upload the backup file to remote storage (flag)",
            action="store_true",
            default=None,
        )
        arggroup_script.add_argument(
            "--mount-point",
            help="name of the local mount point directory for remote storage",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--temp-dir",
            help="name of the local temporary file directory",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--backup-dir",
            help="name of the local database backup directory",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--remote-host",
            help="SSH connection string for the remote host to which to sychronize backups",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--remote-dir",
            help="directory path on the remote host to which to sychronize backups",
            type=str,
            default=None,
        )

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default script configurations. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_NO_UPLOAD, False),
            (self.CONFIG_MOUNT_POINT, self.get_resource_path("media/ds-store")),
            (self.CONFIG_TEMP_DIR, self.paths[self.PATH_TMP]),
            (
                self.CONFIG_BACKUP_DIR,
                os.path.join(self.paths[self.PATH_VAR], "backups"),
            ),
            (self.CONFIG_REMOTE_HOST, None),
            (self.CONFIG_REMOTE_DIR, None),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _sub_stage_init(self, **kwargs):
        """
        **SUBCLASS HOOK**: Perform additional custom initialization actions.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from constructor.
        """
        # Override default 'interval' value.
        self.config[self.CONFIG_INTERVAL] = "daily"

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "backup"

    def cbk_command_backup(self):
        """
        Implementation of **backup** command (*default*).

        Perform backup of data of all configured collections within configured
        time interval thresholds.
        """
        # Change to the filesystem root.
        os.chdir("/")

        # First calculate thresholds for collection backups.
        (time_l, time_h) = self.calculate_interval_thresholds(
            time_high=self.c(self.CONFIG_TIME_HIGH),
            interval=self.c(self.CONFIG_INTERVAL),
            adjust=self.c(self.CONFIG_REGULAR),
        )
        self.logger.info(
            "Lower backup time interval threshold: %s (%s)",
            time_l.isoformat(),
            time_l.timestamp(),
        )
        self.logger.info(
            "Upper backup time interval threshold: %s (%s)",
            time_h.isoformat(),
            time_h.timestamp(),
        )

        # Generate backup identifier.
        date = time_h.strftime("%Y%m%d%H%M")
        backup_label = f"mentat_psqldb_{self.c(self.CONFIG_INTERVAL)}"
        backup_id = f"{backup_label}_{date}"

        # Generate appropriate file names.
        dir_tmp = os.path.join(self.c(self.CONFIG_TEMP_DIR), backup_id)
        backup_mask = os.path.join(self.c(self.CONFIG_BACKUP_DIR), f"{backup_label}*.tar.gz")
        backup_file = os.path.join(self.c(self.CONFIG_BACKUP_DIR), f"{backup_id}.tar.gz")
        backup_link = os.path.join(self.c(self.CONFIG_BACKUP_DIR), "mentat_psqldb_latest.tar.gz")
        self.logger.debug("Temporary directory for backup: '%s'", dir_tmp)
        self.logger.debug("Backup file mask: '%s'", backup_mask)
        self.logger.debug("Backup file name: '%s'", backup_file)

        # Perform actual backup.
        result = self._backup_database(dir_tmp, backup_file, backup_link, time_l, time_h)

        #        if False and not self.c(self.CONFIG_NO_UPLOAD):
        #            # Mount the remote directory to local directory.
        #            self._remote_mount(self.c(self.CONFIG_MOUNT_POINT))

        #            # Move the backup file to remote storage.
        #            self._copy_to_remote(backup_file, self.c(self.CONFIG_MOUNT_POINT), self.c(self.CONFIG_INTERVAL))

        #            # Trim the locally present backup files.
        #            self._clean_local_backups(backup_mask, backup_file)

        #            # Unmount the remote directory from local directory.
        #            self._remote_unmount(self.c(self.CONFIG_MOUNT_POINT))

        #            # Update persistent state.
        #            self.pstate['ts_last_' + self.c(self.CONFIG_INTERVAL)] = time.time()

        return result  # noqa: RET504

    def cbk_command_remote_mount(self):
        """
        Implementation of the **remote-mount** command.

        Mount the remote backup storage to local mount point and exit.
        """
        self._remote_mount(self.c(self.CONFIG_MOUNT_POINT))

        return self.RESULT_SUCCESS

    def cbk_command_remote_unmount(self):
        """
        Implementation of the **remote-unmount** command.

        Unmount the remote backup storage from local mount point and exit.
        """
        self._remote_unmount(self.c(self.CONFIG_MOUNT_POINT))

        return self.RESULT_SUCCESS

    def cbk_command_status(self):
        """
        Implementation of the **status** command.

        Determine the status of backup files on the remote storage.
        """
        # Mount the remote directory to local directory.
        self._remote_mount(self.c(self.CONFIG_MOUNT_POINT))

        # List the remote storage.
        result = self._analyze_remote(self.c(self.CONFIG_MOUNT_POINT), self.c(self.CONFIG_INTERVAL))

        if result["backups"]:
            self.logger.info("Found total of '{:,d}' backup files".format(len(result["backups"])))
            self.logger.info("Latest backup is from '%s'", result["backups"][0]["ts_str"])
            self.logger.info("Oldest backup is from '%s'", result["backups"][-1]["ts_str"])

            previous = {}
            for bkp in result["backups"]:
                if previous is not None and bkp["step"] > 86400:
                    self.logger.info(
                        "Missing '{:,d}' backup files between '{}' and '{}'".format(
                            math.floor((bkp["step"] / 86400) - 1),
                            previous["ts_str"],
                            bkp["ts_str"],
                        )
                    )
                previous = bkp
        else:
            self.logger.warning("There are no backup files")

        # Unmount the remote directory from local directory
        self._remote_unmount(self.c(self.CONFIG_MOUNT_POINT))

        return self.RESULT_SUCCESS

    # ---------------------------------------------------------------------------

    def _backup_database(self, dir_tmp, backup_file, backup_link, time_l, time_h):
        """
        Perform backup of all configured database collections.
        """
        if not os.path.isdir(dir_tmp):
            self.logger.info("Creating local temporary directory '%s' for backup files", dir_tmp)
            os.makedirs(dir_tmp)
        else:
            raise pyzenkit.zenscript.ZenScriptException(
                f"Local backup directory '{dir_tmp}' already exists, perhaps some previous backup failed. Cleanup manually and try again."
            )

        if os.path.isfile(backup_file):
            raise pyzenkit.zenscript.ZenScriptException(
                f"Backup file '{backup_file}' already exists. Cleanup manually and try again."
            )

        result = {"dump_commands": [], "dumped_databases": []}

        # Backup the 'main' database as a whole.
        try:
            dbname = self.config[mentat.const.CKEY_CORE_DATABASE][mentat.const.CKEY_CORE_DATABASE_SQLSTORAGE]["url"]
            self.logger.info("Performing backup of system database '%s'", dbname)
            cmd = r"pg_dump --clean --create --if-exists --format=d --jobs=3 --dbname={} --username=mentat --no-password --file={}".format(
                dbname, os.path.join(dir_tmp, "main")
            )
            result["dump_commands"].append(cmd)
            self.execute_command(cmd)
            cmd = r"chmod 755 {}".format(os.path.join(dir_tmp, "main"))
            result["dump_commands"].append(cmd)
            self.execute_command(cmd)
            result["dumped_databases"].append(dbname)
        except subprocess.CalledProcessError:
            self.logger.warning("Unable to backup database '%s'", dbname)

        # Backup the 'event' in incremental manner (by day).
        try:
            dbname = self._make_connection_string(
                self.config[mentat.const.CKEY_CORE_DATABASE][mentat.const.CKEY_CORE_DATABASE_EVENTSTORAGE]
            )
            cmd = "psql {} -c \"copy (select * from events where detecttime >= '{}'::timestamptz and detecttime <= '{}'::timestamptz limit 50) to stdout\" > {}".format(
                dbname,
                time_l.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                time_h.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                os.path.join(dir_tmp, "events.dat"),
            )
            result["dump_commands"].append(cmd)
            self.execute_command(cmd)
            result["dumped_databases"].append(dbname)
        except subprocess.CalledProcessError:
            self.logger.warning("Unable to backup database '%s'", dbname)

        self.logger.info("Packing the database backup into archive file '%s'", backup_file)
        cmd = rf"tar -czPf {backup_file} {dir_tmp}"
        result["dump_commands"].append(cmd)
        self.execute_command(cmd)

        self.logger.info(
            "Creating the symlink '%s' to latest backup archive file '%s'",
            backup_link,
            backup_file,
        )
        if os.path.islink(backup_link):
            os.unlink(backup_link)
        cmd = rf"ln -s {backup_file} {backup_link}"
        result["dump_commands"].append(cmd)
        self.execute_command(cmd)

        self.logger.info("Removing local backup directory '%s'", dir_tmp)
        cmd = rf"rm -rf {dir_tmp}"
        result["dump_commands"].append(cmd)
        self.execute_command(cmd)

        sti = os.stat(backup_file)
        result["backup_file"] = backup_file
        result["backup_size"] = sti.st_size

        self.logger.info(
            "Created backup file '{}' with size {:,.2f} KB".format(
                result["backup_file"], (result["backup_size"] / 1024)
            )
        )
        return result

    def _copy_to_remote(self, backup_file, mount_point, interval):
        """
        Copy given backup file to target directory on remote storage.
        """
        tgt_dir = os.path.join(mount_point, interval)

        if os.path.isdir(tgt_dir):
            self.logger.info(
                "Copying backup file '%s' to remote directory '%s'",
                backup_file,
                tgt_dir,
            )
            cmd = f"cp -f --no-preserve=mode {backup_file} {tgt_dir}"
            self.execute_command(cmd)
        else:
            self.logger.error("Target directory '%s' does not exist", tgt_dir)

    def _clean_local_backups(self, backup_mask, backup_file):
        """
        Clean backup files locally present on current host, keep only the most
        recent one.
        """
        backup_files = sorted(glob.glob(backup_mask), reverse=True)
        self.logger.debug(
            "Found following local backup files >>>\n%s",
            pprint.pformat(backup_files, indent=4),
        )
        for bfl in backup_files:
            if bfl == backup_file:
                self.logger.info("Keeping local copy of latest backup file '%s'", backup_file)
            else:
                self.logger.info("Removing local copy of older backup file '%s'", bfl)
                os.remove(bfl)

    def _analyze_remote(self, mount_point, mode):
        """
        Analyze the storage of remote backups.
        """
        result = {"backups": []}
        tgtdir = os.path.join(mount_point, mode)
        previous = {}
        if os.path.isdir(tgtdir):
            self.logger.info("Analyzing remote backup directory '%s':", tgtdir)
            backupfiles = os.listdir(tgtdir)
            ptrn = re.compile("mentatdb_" + mode + r"_(\d{12})\.tar\.gz")
            for bfl in sorted(backupfiles, reverse=True):
                bfp = os.path.join(tgtdir, bfl)
                if not os.path.isfile(bfp):
                    continue
                match = ptrn.match(bfl)
                if not match:
                    continue
                anl = {
                    "file": bfl,
                    "path": bfp,
                    "ts_raw": match.group(1),
                    "ts_str": time.strftime("%Y-%m-%d", time.strptime(match.group(1), "%Y%m%d%H%M")),
                    "ts": time.mktime(time.strptime(match.group(1), "%Y%m%d%H%M")),
                }
                sti = os.stat(bfp)
                anl["size"] = sti.st_size
                if not previous:
                    anl["step"] = 0
                    anl["value"] = 1
                else:
                    anl["step"] = int(previous["ts"] - anl["ts"])
                    anl["value"] = int(previous["value"] + (anl["step"] / 86400))

                previous = anl

                result["backups"].append(anl)
            self.logger.debug("Backup analysis: %s", pprint.pformat(result))
        else:
            self.logger.error("Remote backup directory '%s' does not exist", tgtdir)
        return result

    def _remote_mount(self, mount_point):
        """
        Mount remote storage locally via sshfs.
        """
        rem_host = self.c(self.CONFIG_REMOTE_HOST)
        rem_dir = self.c(self.CONFIG_REMOTE_DIR)

        if not os.path.ismount(mount_point):
            self.logger.info("Mounting remote storage to path '%s'", mount_point)
            cmd = f"/usr/bin/sshfs -o idmap=user {rem_host}:{rem_dir} {mount_point}"
            self.execute_command(cmd)
        else:
            self.logger.info("Remote storage already mounted to path '%s'", mount_point)

    def _remote_unmount(self, mount_point):
        """
        Unmount locally mounted remote storage.
        """
        if os.path.ismount(mount_point):
            self.logger.info("Unmounting remote storage from path '%s'", mount_point)
            cmd = f"fusermount -u {mount_point}"
            self.execute_command(cmd)
        else:
            self.logger.info("Remote storage already unmounted from path '%s'", mount_point)

    def _make_connection_string(self, parameters):
        """
        Create PostgreSQL connection string out of connection parameter dictionary.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(**parameters)
