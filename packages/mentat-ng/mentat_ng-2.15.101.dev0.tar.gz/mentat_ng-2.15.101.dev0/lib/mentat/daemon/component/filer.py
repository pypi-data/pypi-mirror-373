#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Daemon component responsible for management of incoming and outgoing message queues.
Is is implemented as an encapsulation of :py:class:`mentat.dirq.DirectoryQueue`.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import shutil
import traceback

import pyzenkit.zendaemon

import mentat.dirq


class FilerDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    Implementation of ZenDaemonComponent encapsulating  mentat.dirq.DirectoryQueue.
    """

    EVENT_START = "start"
    EVENT_QUEUE_CHECK = "queue_check"
    EVENT_MSG_ENQUEUE = "message_enqueue"
    EVENT_MSG_NEXT = "message_next"
    EVENT_MSG_UPDATE = "message_update"
    EVENT_MSG_COMMIT = "message_commit"
    EVENT_MSG_BANISH = "message_banish"
    EVENT_MSG_CANCEL = "message_cancel"
    EVENT_MSG_DISPATCH = "message_dispatch"
    EVENT_MSG_DUPLICATE = "message_duplicate"
    EVENT_MSG_PROCESS = "message_process"
    EVENT_LOG_STATISTICS = "log_statistics"

    STATUS_RUNNING = "status_running"
    STATUS_PAUSED = "status_paused"

    CONFIG_QUEUE_IN_WAIT = "queue_in_wait"
    CONFIG_QUEUE_OUT_LIMIT = "queue_out_limit"
    CONFIG_QUEUE_OUT_WAIT = "queue_out_wait"

    STATS_CNT_ENQUEUED = "cnt_enqueued"
    STATS_CNT_FETCHED = "cnt_fetched"
    STATS_CNT_UPDATED = "cnt_updated"
    STATS_CNT_BANISHED = "cnt_banished"
    STATS_CNT_CANCELED = "cnt_canceled"
    STATS_CNT_COMMITTED = "cnt_committed"
    STATS_CNT_DISPATCHED = "cnt_dispatched"
    STATS_CNT_DUPLICATED = "cnt_duplicated"
    STATS_CNT_ERRORS = "cnt_errors"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "filer")

        # Initialize internal variables
        self.queue_in_dir = None
        self.queue_in_perms = None
        self.queue_out_dir = None
        self.queue_out_limit = None
        self.queue_out_wait = None
        self.dirq = None
        self.status = None
        self.wait_interval = None

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_START: self.EVENT_START,
                self.EVENT_QUEUE_CHECK: self.EVENT_QUEUE_CHECK,
                self.EVENT_MSG_ENQUEUE: self.EVENT_MSG_ENQUEUE,
                self.EVENT_MSG_NEXT: self.EVENT_MSG_NEXT,
                self.EVENT_MSG_UPDATE: self.EVENT_MSG_UPDATE,
                self.EVENT_MSG_COMMIT: self.EVENT_MSG_COMMIT,
                self.EVENT_MSG_BANISH: self.EVENT_MSG_BANISH,
                self.EVENT_MSG_CANCEL: self.EVENT_MSG_CANCEL,
                self.EVENT_MSG_DISPATCH: self.EVENT_MSG_DISPATCH,
                self.EVENT_MSG_DUPLICATE: self.EVENT_MSG_DUPLICATE,
                self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS,
            },
        )

    def get_events(self):
        """
        Get the mapping of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_START],
                "callback": self.cbk_event_start,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_QUEUE_CHECK],
                "callback": self.cbk_event_queue_check,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_ENQUEUE],
                "callback": self.cbk_event_message_enqueue,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_NEXT],
                "callback": self.cbk_event_message_next,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_UPDATE],
                "callback": self.cbk_event_message_update,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_COMMIT],
                "callback": self.cbk_event_message_commit,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_BANISH],
                "callback": self.cbk_event_message_banish,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_CANCEL],
                "callback": self.cbk_event_message_cancel,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_DISPATCH],
                "callback": self.cbk_event_message_dispatch,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_MSG_DUPLICATE],
                "callback": self.cbk_event_message_duplicate,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_LOG_STATISTICS],
                "callback": self.cbk_event_log_statistics,
                "prepend": False,
            },
        ]

    def setup(self, daemon):
        """
        Perform component setup.
        """
        self.queue_in_dir = daemon.cc(daemon.CORE_FILEQUEUE).get(mentat.dirq.DirectoryQueue.CONFIG_DIR_QUEUE)
        self.queue_in_perms = daemon.cc(daemon.CORE_FILEQUEUE).get(mentat.dirq.DirectoryQueue.CONFIG_QUEUE_PERMS)
        self.queue_out_dir = daemon.cc(daemon.CORE_FILEQUEUE).get(mentat.dirq.DirectoryQueue.CONFIG_DIR_NEXT_QUEUE)
        self.queue_out_limit = daemon.cc(daemon.CORE_FILEQUEUE).get(self.CONFIG_QUEUE_OUT_LIMIT)
        self.queue_out_wait = daemon.cc(daemon.CORE_FILEQUEUE).get(self.CONFIG_QUEUE_OUT_WAIT)

        # Make sure input queue directory exists
        self._prepare_workdir(
            daemon,
            self.queue_in_dir,
            daemon.c(daemon.CONFIG_USER),
            daemon.c(daemon.CONFIG_GROUP),
            self.queue_in_perms,
        )
        self._check_workdir_writability(daemon, self.queue_in_dir)

        # Make sure output queue directory is accessible and writeble
        if self.queue_out_dir:
            self._check_workdir_writability(daemon, self.queue_out_dir)

        self.dirq = mentat.dirq.DirectoryQueue(**daemon.cc(daemon.CORE_FILEQUEUE))
        self.status = self.STATUS_RUNNING
        self.wait_interval = daemon.c(self.CONFIG_QUEUE_IN_WAIT)

        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_QUEUE_CHECK}' mapped to '{self.event_map[self.EVENT_QUEUE_CHECK]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_ENQUEUE}' mapped to '{self.event_map[self.EVENT_MSG_ENQUEUE]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_NEXT}' mapped to '{self.event_map[self.EVENT_MSG_NEXT]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_UPDATE}' mapped to '{self.event_map[self.EVENT_MSG_UPDATE]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_COMMIT}' mapped to '{self.event_map[self.EVENT_MSG_COMMIT]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_BANISH}' mapped to '{self.event_map[self.EVENT_MSG_BANISH]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_CANCEL}' mapped to '{self.event_map[self.EVENT_MSG_CANCEL]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_DISPATCH}' mapped to '{self.event_map[self.EVENT_MSG_DISPATCH]}'"
        )
        daemon.dbgout(
            f"[STATUS] Component '{self.cid}': Event '{self.EVENT_MSG_DUPLICATE}' mapped to '{self.event_map[self.EVENT_MSG_DUPLICATE]}'"
        )

        daemon.logger.info(
            f"[STATUS] Component '{self.cid}': Using directory '{self.queue_in_dir}' as input message queue"
        )
        daemon.logger.info(
            f"[STATUS] Component '{self.cid}': Using '{self.wait_interval}' as wait time for empty input message queue"
        )
        if self.queue_out_dir:
            daemon.logger.info(
                f"[STATUS] Component '{self.cid}': Using directory '{self.queue_out_dir}' as output message queue"
            )
            daemon.logger.info(
                f"[STATUS] Component '{self.cid}': Using '{self.queue_out_limit}' as output message queue limit"
            )
            daemon.logger.info(
                f"[STATUS] Component '{self.cid}': Using '{self.queue_out_wait}' as wait time for full output message queue"
            )

    def _prepare_workdir(self, daemon, dir_name, user=None, group=None, perms=None):
        if not os.path.isdir(dir_name):
            daemon.logger.info(
                f"[STATUS] Component '{self.cid}': Preparing work directory '{dir_name}' ({user!s}:{group!s},{oct(perms)!s})"
            )
            try:
                os.makedirs(dir_name)
                if perms:
                    os.chmod(dir_name, perms)
                if user or group:
                    shutil.chown(dir_name, user=user[0], group=group[0])
            except Exception as exc:
                msg = f"Unable to create work directory '{dir_name}' with 'UID:{user!s},GID:{group!s},PERMS:{oct(perms)!s}' as current effective user 'EUID:{os.geteuid()},EGID:{os.getegid()}': '{traceback.format_exc()}'"
                daemon.logger.error(f"[STATUS] Component '{self.cid}': {msg}")
                raise pyzenkit.zendaemon.ZenDaemonComponentException(msg) from exc

    def _check_workdir_writability(self, daemon, dir_name):
        if not os.path.isdir(dir_name):
            msg = f"Work directory '{dir_name}' does not exist"
            daemon.logger.error(f"[STATUS] Component '{self.cid}': {msg}")
            raise pyzenkit.zendaemon.ZenDaemonComponentException(msg)
        if not os.access(dir_name, os.W_OK):
            msg = f"Work directory '{dir_name}' is not writable for current effective user 'EUID:{os.geteuid()},EGID:{os.getegid()}'"
            daemon.logger.error(f"[STATUS] Component '{self.cid}': {msg}")
            raise pyzenkit.zendaemon.ZenDaemonComponentException(msg)

    # ---------------------------------------------------------------------------

    def cbk_event_start(self, daemon, args):
        """
        Start the component.
        """
        daemon.logger.debug(f"Component '{self.cid}': Starting the filer component")
        daemon.queue.schedule(self.EVENT_QUEUE_CHECK)
        daemon.queue.schedule(self.EVENT_MSG_NEXT)
        return (daemon.FLAG_CONTINUE, args)

    def cbk_event_queue_check(self, daemon, args):
        """
        Check the size of output message queue and pause processing, when necessary.
        """
        daemon.logger.debug(f"Component '{self.cid}': Checking output queue size")

        wait_interval = self.wait_interval
        if self.queue_out_dir and self.queue_out_limit:
            if self.dirq.count_done() > self.queue_out_limit:
                wait_interval = self.queue_out_wait
                if self.status == self.STATUS_RUNNING:
                    daemon.logger.info(
                        f"Component '{self.cid}': Output queue limit '{self.queue_out_limit}' reached, pausing the processing for '{self.queue_out_wait}' second(s)"
                    )
                    self.status = self.STATUS_PAUSED
            else:
                if self.status == self.STATUS_PAUSED:
                    daemon.logger.info(f"Component '{self.cid}': Output queue free, resuming the processing")
                    self.status = self.STATUS_RUNNING
                    daemon.queue.schedule(self.EVENT_MSG_NEXT)

        daemon.queue.schedule_after(wait_interval, self.EVENT_QUEUE_CHECK)
        return (daemon.FLAG_CONTINUE, args)

    def cbk_event_message_enqueue(self, daemon, args):
        """
        Enqueue given message to the queue and schedule the processing event.
        """
        daemon.logger.debug(f"Component '{self.cid}': Adding new message into the queue")
        mid = self.dirq.enqueue(args["data"])
        if mid:
            daemon.logger.info(f"Component '{self.cid}': Added new message into the queue as '{mid}'")
            args["id"] = mid
            self.inc_statistic(self.STATS_CNT_ENQUEUED)
            return (daemon.FLAG_CONTINUE, args)

        daemon.logger.error(f"Component '{self.cid}': Unable to add new message into the queue")
        self.inc_statistic(self.STATS_CNT_ERRORS)
        return (daemon.FLAG_STOP, None)

    def cbk_event_message_next(self, daemon, args=None):
        """
        Fetch next message from the queue and schedule the processing event.
        """
        if self.status == self.STATUS_PAUSED:
            return (daemon.FLAG_STOP, args)

        daemon.logger.debug(f"Component '{self.cid}': Fetching a next message from queue")
        (mid, mdata) = self.dirq.next()
        if mid:
            self.inc_statistic(self.STATS_CNT_FETCHED)
            if not mdata or mdata.isspace():
                daemon.logger.error(f"Component '{self.cid}': Fetched empty message '{mid}'")
                daemon.queue.schedule(self.EVENT_MSG_BANISH, {"id": mid})
            else:
                daemon.logger.debug(f"Component '{self.cid}': Fetched message '{mid}'")
                daemon.queue.schedule(self.EVENT_MSG_PROCESS, {"id": mid, "data": mdata})

            if not daemon.is_done():
                daemon.queue.schedule(self.EVENT_MSG_NEXT)
            else:
                daemon.logger.info(
                    f"Component '{self.cid}': Daemon is in shutdown process, will not fetch any new messages"
                )
        else:
            if not daemon.is_done():
                daemon.logger.info(
                    f"Component '{self.cid}': Scheduling next queue check after '{self.wait_interval}' seconds"
                )
                daemon.queue.schedule_after(self.wait_interval, self.EVENT_MSG_NEXT)
            else:
                daemon.logger.info(
                    f"Component '{self.cid}': Daemon is in shutdown process, will not fetch any new messages"
                )

        return (daemon.FLAG_CONTINUE, None)

    def cbk_event_message_update(self, daemon, args):
        """
        Update the message within pending queue.
        """
        daemon.logger.debug("Component '{}': Updating message '{}'".format(self.cid, args["id"]))
        try:
            self.dirq.update(args["id"], args["data"])
            self.inc_statistic(self.STATS_CNT_UPDATED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to update message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to update message '{}': {}".format(self.cid, args["id"], traceback.format_exc())
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_message_commit(self, daemon, args):
        """
        Commit message from queue.
        """
        daemon.logger.debug("Component '{}': Committing message '{}'".format(self.cid, args["id"]))
        try:
            self.dirq.commit(args["id"])
            self.inc_statistic(self.STATS_CNT_COMMITTED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to commit message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to commit message '{}': {}".format(self.cid, args["id"], traceback.format_exc())
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_message_banish(self, daemon, args):
        """
        Banish message from queue.
        """
        daemon.logger.debug("Component '{}': Banishing message '{}'".format(self.cid, args["id"]))
        try:
            self.dirq.banish(args["id"])
            self.inc_statistic(self.STATS_CNT_BANISHED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to banish message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to banish message '{}': {}".format(self.cid, args["id"], traceback.format_exc())
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_message_cancel(self, daemon, args):
        """
        Cancel message from queue.
        """
        daemon.logger.debug("Component '{}': Cancelling message '{}'".format(self.cid, args["id"]))
        try:
            self.dirq.cancel(args["id"])
            self.inc_statistic(self.STATS_CNT_CANCELED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to cancel message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to cancel message '{}': {}".format(self.cid, args["id"], traceback.format_exc())
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_message_dispatch(self, daemon, args):
        """
        Dispatch message from queue to another queue.
        """
        daemon.logger.debug(
            "Component '{}': Dispatching message '{}' to target queue '{}'".format(
                self.cid, args["id"], args["queue_tgt"]
            )
        )
        try:
            self.dirq.dispatch(args["id"], args["queue_tgt"])
            self.inc_statistic(self.STATS_CNT_DISPATCHED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to dispatch message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to dispatch message '{}': {}".format(
                    self.cid, args["id"], traceback.format_exc()
                )
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_message_duplicate(self, daemon, args):
        """
        Duplicate message from queue to another queue.
        """
        daemon.logger.debug(
            "Component '{}': Duplicating message '{}' to target queue '{}'".format(
                self.cid, args["id"], args["queue_tgt"]
            )
        )
        try:
            self.dirq.duplicate(args["id"], args["queue_tgt"])
            self.inc_statistic(self.STATS_CNT_DUPLICATED)
            return (daemon.FLAG_CONTINUE, args)
        except (FileNotFoundError, PermissionError) as exc:
            daemon.logger.error(
                "Component '{}': Unable to duplicate message '{}': {}".format(self.cid, args["id"], str(exc))
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to duplicate message '{}': {}".format(
                    self.cid, args["id"], traceback.format_exc()
                )
            )
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, None)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [
            self.STATS_CNT_ENQUEUED,
            self.STATS_CNT_FETCHED,
            self.STATS_CNT_UPDATED,
            self.STATS_CNT_COMMITTED,
            self.STATS_CNT_BANISHED,
            self.STATS_CNT_CANCELED,
            self.STATS_CNT_DISPATCHED,
            self.STATS_CNT_DUPLICATED,
            self.STATS_CNT_ERRORS,
        ]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (daemon.FLAG_CONTINUE, args)
