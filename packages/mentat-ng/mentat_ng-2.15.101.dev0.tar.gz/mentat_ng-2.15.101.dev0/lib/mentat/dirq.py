#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Implementation of filesystem directory based queue for universal messages.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import errno
import json
import os
import shutil
import socket
import time
import traceback


class DirectoryQueueException(Exception):
    """
    This class represents all custom exceptions related to DirectoryQueue.
    """

    def __init__(self, description):
        self._description = description

    def __str__(self):
        return repr(self._description)


class DirectoryQueue:
    """
    Implementation of filesystem directory based queue for universal messages.
    """

    # Keys into internal statistics dictionary.
    STAT_CNT_QUEUED = "cnt_queued"
    STAT_CNT_DEQUEUED = "cnt_dequeued"
    STAT_CNT_COMMITS = "cnt_commits"
    STAT_CNT_ERRORS = "cnt_errors"
    STAT_CNT_UPDATES = "cnt_updates"
    STAT_CNT_CANCELS = "cnt_cancels"
    STAT_CNT_SKIPS = "cnt_skips"
    STAT_CNT_DISPATCHED = "cnt_dispatched"
    STAT_CNT_DUPLICATED = "cnt_duplicated"

    # Names of the internal queue work subdirectories.
    SUBDIR_INCOMING = "incoming"
    SUBDIR_PENDING = "pending"
    SUBDIR_ERRORS = "errors"
    SUBDIR_TMP = "tmp"

    CONFIG_DIR_QUEUE = "dir_queue"
    CONFIG_DIR_NEXT_QUEUE = "dir_next_queue"
    CONFIG_USER = "user"
    CONFIG_GROUP = "group"
    CONFIG_QUEUE_PERMS = "queue_perms"

    def __init__(self, dir_queue, **kwargs):
        """
        Initialize directory queue manager.

        The only mandatory argument to this constructor is the name of queue
        directory. In case they do not exist, all necessary working subdirectories
        will be created automatically during object instantination.
        """
        self.hostname = socket.gethostname()
        self.pid = os.getpid()
        self.dir_queue = dir_queue
        self.queue = []
        self.stats = {
            self.STAT_CNT_QUEUED: 0,
            self.STAT_CNT_DEQUEUED: 0,
            self.STAT_CNT_COMMITS: 0,
            self.STAT_CNT_ERRORS: 0,
            self.STAT_CNT_UPDATES: 0,
            self.STAT_CNT_CANCELS: 0,
            self.STAT_CNT_SKIPS: 0,
            self.STAT_CNT_DISPATCHED: 0,
            self.STAT_CNT_DUPLICATED: 0,
        }
        self.user = kwargs.get(self.CONFIG_USER, None)
        self.group = kwargs.get(self.CONFIG_GROUP, None)
        self.perms = kwargs.get(self.CONFIG_QUEUE_PERMS, None)

        self._prepare_queue_dir(self.dir_queue)

        self.dir_incoming = os.path.join(self.dir_queue, self.SUBDIR_INCOMING)
        self.dir_pending = os.path.join(self.dir_queue, self.SUBDIR_PENDING)
        self.dir_errors = os.path.join(self.dir_queue, self.SUBDIR_ERRORS)
        self.dir_tmp = os.path.join(self.dir_queue, self.SUBDIR_TMP)

        self.dir_next_queue = kwargs.get(self.CONFIG_DIR_NEXT_QUEUE, False)

        if self.dir_next_queue:
            # Possibly forbid moving between different partitions
            # if os.stat(self.dir_queue).st_dev != os.stat(self.dir_next_queue).st_dev:
            #    raise DirectoryQueueException("Desired queue_next directory '{}' is on different partition than queue directory '{}'".format(self.dir_next_queue, self.dir_queue))

            self._prepare_queue_dir(self.dir_next_queue)

            self.dir_next_incoming = os.path.join(self.dir_next_queue, self.SUBDIR_INCOMING)
            self.dir_next_tmp = os.path.join(self.dir_next_queue, self.SUBDIR_TMP)

            self.commit = self._commit_move
        else:
            self.commit = self._commit_remove

    def __str__(self):
        """
        Simple string serialization for development purposes.
        """
        return f"{type(self).__name__:s}({self.dir_queue:s})"

    def _prepare_queue_dir(self, dir_queue):
        """
        Prepare given queue directory.
        """
        if not os.path.isdir(dir_queue):
            self._prepare_queue_workdir(dir_queue, self.user, self.group, self.perms)
        self._check_writability(dir_queue)

        for subd in (
            os.path.join(dir_queue, self.SUBDIR_INCOMING),
            os.path.join(dir_queue, self.SUBDIR_PENDING),
            os.path.join(dir_queue, self.SUBDIR_ERRORS),
            os.path.join(dir_queue, self.SUBDIR_TMP),
        ):
            if not subd:
                continue
            if not os.path.isdir(subd):
                self._prepare_queue_workdir(subd, self.user, self.group, self.perms)
            self._check_writability(subd)

    def _prepare_queue_workdir(self, dir_name, user=None, group=None, perms=None):
        try:
            os.makedirs(dir_name)
            if perms:
                os.chmod(dir_name, perms)
            if user or group:
                shutil.chown(dir_name, user=user[0], group=group[0])
        except Exception as exc:
            raise DirectoryQueueException(
                f"Unable to create queue directory '{dir_name}' with 'UID:{user!s},GID:{group!s},PERMS:{oct(perms)!s}' as current effective user 'EUID:{os.geteuid()},EGID:{os.getegid()}': '{traceback.format_exc()}'"
            ) from exc

    def _check_writability(self, dir_name):
        if not os.access(dir_name, os.W_OK):
            raise DirectoryQueueException(
                f"Queue directory '{dir_name}' is not writable for current effective user 'EUID:{os.geteuid()},EGID:{os.getegid()}'"
            )

    def _generate_id(self, device=0, inode=0, suffix="msg"):
        """
        Generate unique ID for new messsage within queue.
        """
        return f"{self.hostname:s}.{self.pid:d}.{time.time():f}.{device:d}.{inode:d}.{suffix:s}"

    def _rescan_queue(self):
        """
        Rescan incoming queue subdirectory.
        """
        self.queue = os.listdir(self.dir_incoming)
        # return len(self.queue)

    def _load_file(self, filename):
        """
        Load and return contents of given file (helper method for testing).
        """
        with open(filename, "r", encoding="utf8") as tmpf:
            return tmpf.read()

    def _append_metadata(self, file_tgt, metadata):
        """
        Append given metadata to given file.
        """
        try:
            with open(f"{file_tgt}.meta", "w", encoding="utf8") as mf:
                json.dump(metadata, mf, sort_keys=True, indent=4)
        except OSError:
            pass

    # ---------------------------------------------------------------------------

    def enqueue(self, item):
        """
        Enqueue given item into the incoming queue subdirectory.
        """
        # First find a name unique within tmp directory
        tmpid = None
        tmpfn = None
        tmpfd = None
        while not tmpid:
            tmpid = self._generate_id()
            tmpfn = os.path.join(self.dir_tmp, tmpid)
            try:
                tmpfd = os.open(tmpfn, os.O_CREAT | os.O_RDWR | os.O_EXCL)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise  # other errors than duplicates should get noticed
                tmpid = None
        # Write data to file
        os.write(tmpfd, bytes(str(item), "UTF-8"))
        os.close(tmpfd)
        # Now generate a name unique within the whole filesystem
        stat = os.stat(tmpfn)
        newid = self._generate_id(stat.st_dev, stat.st_ino)
        os.rename(tmpfn, os.path.join(self.dir_incoming, newid))
        self.stats[self.STAT_CNT_QUEUED] += 1
        return newid

    def enqueue_file(self, item):
        """
        Enqueue given file directly into the incoming queue subdirectory.
        """
        itemid = os.path.basename(item)
        os.rename(item, os.path.join(self.dir_incoming, itemid))
        self.stats[self.STAT_CNT_QUEUED] += 1
        return itemid

    def next(self):
        """
        Fetch next item from incoming queue.
        """
        (next_id, next_file) = self.next_file()
        if next_file:
            data = None
            with open(next_file, encoding="utf8") as nf:
                data = "".join(nf.readlines())
            return (next_id, data)
        return (None, None)

    def next_file(self):
        """
        Fetch next file from incoming queue.
        """
        while True:
            if not self.queue:
                self._rescan_queue()
            try:
                itemid = self.queue.pop()
                file_name = os.path.join(self.dir_pending, itemid)
                os.rename(os.path.join(self.dir_incoming, itemid), file_name)
                self.stats[self.STAT_CNT_DEQUEUED] += 1
                return (itemid, file_name)
            # Pop from empty list => queue is empty
            except IndexError:
                return (None, None)
            except FileNotFoundError:
                self.stats[self.STAT_CNT_SKIPS] += 1
        return (None, None)

    def _commit_move(self, itemid):
        """
        Commit given message by moving related file into next queue directory.
        """
        shutil.move(
            os.path.join(self.dir_pending, itemid),
            os.path.join(self.dir_next_tmp, itemid),
        )
        os.rename(
            os.path.join(self.dir_next_tmp, itemid),
            os.path.join(self.dir_next_incoming, itemid),
        )
        self.stats[self.STAT_CNT_COMMITS] += 1

    def _commit_remove(self, itemid):
        """
        Commit given message by removing related file.
        """
        os.unlink(os.path.join(self.dir_pending, itemid))
        self.stats[self.STAT_CNT_COMMITS] += 1

    def update(self, itemid, item):
        """
        Update given message within pending queue.
        """
        itemfd = os.open(os.path.join(self.dir_pending, itemid), os.O_TRUNC | os.O_WRONLY)
        os.write(itemfd, bytes(str(item), "UTF-8"))
        os.close(itemfd)
        self.stats[self.STAT_CNT_UPDATES] += 1

    def reload(self, itemid):
        """
        Reload given message from within pending queue.
        """
        with open(os.path.join(self.dir_pending, itemid), encoding="utf8") as mf:
            return "".join(mf.readlines())
        return None

    def banish(self, itemid, metadata=None):
        """
        Banish given message into error folder.
        """
        file_src = os.path.join(self.dir_pending, itemid)
        file_tgt = os.path.join(self.dir_errors, itemid)
        os.rename(file_src, file_tgt)
        if metadata:
            self._append_metadata(file_tgt, metadata)
        self.stats[self.STAT_CNT_ERRORS] += 1

    def cancel(self, itemid):
        """
        Cancel given message (remove it from processing without moving to error folder).
        """
        os.unlink(os.path.join(self.dir_pending, itemid))
        self.stats[self.STAT_CNT_CANCELS] += 1

    def dispatch(self, itemid, target_folder, metadata=None):
        """
        Dispatch given message into designated target folder.
        """
        file_src = os.path.join(self.dir_pending, itemid)
        file_tgt = os.path.join(target_folder, itemid)
        shutil.move(file_src, file_tgt)
        if metadata:
            self._append_metadata(file_tgt, metadata)
        self.stats[self.STAT_CNT_DISPATCHED] += 1

    def duplicate(self, itemid, target_folder, metadata=None):
        """
        Duplicate given message into designated target folder.
        """
        file_org = os.path.join(self.dir_pending, itemid)
        file_src = os.path.join(self.dir_tmp, itemid)
        file_tgt = os.path.join(target_folder, itemid)
        shutil.copyfile(file_org, file_src)
        os.rename(file_src, file_tgt)
        if metadata:
            self._append_metadata(file_tgt, metadata)
        self.stats[self.STAT_CNT_DUPLICATED] += 1

    # ---------------------------------------------------------------------------

    def count_incoming(self):
        """
        Count number of messages in incoming queue subdirectory.
        """
        return len(os.listdir(self.dir_incoming))

    def count_pending(self):
        """
        Count number of messages in pending queue subdirectory.
        """
        return len(os.listdir(self.dir_pending))

    def count_errors(self):
        """
        Count number of messages in errors queue subdirectory.
        """
        return len(os.listdir(self.dir_errors))

    def count_done(self):
        """
        Count number of messages in done queue subdirectory.
        """
        if not self.dir_next_queue:
            return 0
        return len(os.listdir(self.dir_next_incoming))

    # ---------------------------------------------------------------------------

    def is_incoming(self, itemid):
        """
        Check if the given message is located in incoming queue subdirectory.
        """
        return os.path.isfile(os.path.join(self.dir_incoming, itemid))

    def is_pending(self, itemid):
        """
        Check if the given message is located in pending queue subdirectory.
        """
        return os.path.isfile(os.path.join(self.dir_pending, itemid))

    def is_error(self, itemid):
        """
        Check if the given message is located in errors queue subdirectory.
        """
        return os.path.isfile(os.path.join(self.dir_errors, itemid))

    # ---------------------------------------------------------------------------

    def statistics(self):
        """
        Get the internal statistics.
        """
        return self.stats


#
# Perform the demonstration.
#
if __name__ == "__main__":
    try:
        qdir_name = "/tmp/dirq.tmpd"
        os.mkdir(qdir_name)
    except FileExistsError:
        pass
    dq = DirectoryQueue(qdir_name)
    os.rmdir(qdir_name)
