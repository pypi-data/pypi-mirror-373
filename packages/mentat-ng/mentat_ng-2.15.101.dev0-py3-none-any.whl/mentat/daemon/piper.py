#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides base implementation of generic *pipe-like* message processing
daemon represented by the :py:class:`pyzenkit.zendaemon.ZenDaemon` class.
It builds on top of :py:mod:`pyzenkit.zendaemon` module and adds couple of other
usefull features:

* Automated inclusion and bootstrapping of :py:mod:`mentat.daemon.component.filer`
  daemon component.
* Additional configurations and command line arguments related to filer protocol.


Filer daemon component
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This module automatically takes care of inclusion and bootstrapping of
:py:mod:`mentat.daemon.component.filer` daemon component. This component implements
the filesystem message exchange queue, aka. **filer protocol**. This is a fairly
simple protocol inspired by *Postfix MTA* that uses ordinary filesystem directories
for exchanging messages between multiple modules/processess. Each process has a
directory asigned to him which represents his message queue. Passing a message for
processing means simply puting a file into this directory, or more specifically
into one of its subdirectories.

The designated filesystem message queue directory must contain and use following
subdirectories:

* ``incoming``: input queue containing only complete messages
* ``pending``: daemon working directory and pending queue
* ``tmp``: work directory for other processes
* ``errors``: messages causing problems during processing

Enqueue message
    Equeuing a new message can be done by anyone including the owner of the queue
    and it means creating a new file in ``incoming`` subdirectory.
    However it is required that all files in this directory are complete and final,
    so ussually it is necessary to create the temporary file in different location
    (ussually ``tmp``) and then move it to the ``incoming`` queue.

    Key requirement here is, that the *move* operation must be atomic, so that multiple
    instances of the same daemon may run on the same queue and thus enable cheap
    paralelization. The atomic move should be achived simply by keeping the whole
    queue directory structure on the same disk partition.

    Once message is in the ``incoming`` subdirectory, it must be considered a property
    of the queue owner and no other process (except other instances of the same
    daemon) must not modify it in any way.

Dequeue message
    Dequeueing a message is done only by the owner of the queue and it means atomically
    moving the related message file into ``pending`` subdirectory. In that instant
    process that moved the message owns it and may work with it. When the work is
    there are following options how to handle the message file:

    * Move the message file to ``errors`` subdirectory in case there was any error
      during processing.
    * Move the message to ``incoming`` subdirectory of another daemon to pass the
      message to next step in processing chain.
    * Delete the message permanently from filesystem in case it is not needed anymore.


Custom configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Custom command line options
````````````````````````````````````````````````````````````````````````````````

``--queue-in-dir``
    Name of the input queue directory.

    *Type:* ``string``

``--queue-out-dir``
    Name of the output queue directory.

    *Type:* ``string``, *default:* ``None``

``--queue-out-limit``
    Limit on the number of the files for the output queue directory.

    *Type:* ``integer``, *default:* ``10000``

``--queue-out-wait``
    Waiting time when the output queue limit is reached in seconds.

    *Type:* ``integer``, *default:* ``10``

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import os

import pyzenkit.baseapp
import pyzenkit.zendaemon

import mentat.const
import mentat.daemon.base
import mentat.daemon.component.filer
import mentat.dirq


class PiperDaemon(mentat.daemon.base.MentatBaseDaemon):
    """
    This module provides base implementation of generic *pipe-like* message processing
    daemon.
    """

    # List of core configuration keys.
    CORE_FILEQUEUE = "filequeue"

    # List of possible configuration keys.
    CONFIG_QUEUE_IN_DIR = "queue_in_dir"
    CONFIG_QUEUE_IN_PERMS = "queue_in_perms"
    CONFIG_QUEUE_IN_WAIT = "queue_in_wait"
    CONFIG_QUEUE_OUT_DIR = "queue_out_dir"
    CONFIG_QUEUE_OUT_LIMIT = "queue_out_limit"
    CONFIG_QUEUE_OUT_WAIT = "queue_out_wait"

    def __init__(self, **kwargs):
        #
        # Override default configurations.
        #
        kwargs.setdefault("default_queue_out_dir", None)

        super().__init__(**kwargs)

    def _init_argparser(self, **kwargs):
        """
        Initialize piper daemon command line argument parser. This method overrides the
        base implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon._init_argparser`
        and it must return valid :py:class:`argparse.ArgumentParser` object. It
        appends additional command line options custom for this daemon object.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param kwargs: Various additional parameters passed down from object constructor.
        :return: Valid argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for common daemon arguments.
        #
        arggroup_daemon = argparser.add_argument_group("common piper daemon arguments")

        arggroup_daemon.add_argument(
            "--queue-in-dir",
            type=str,
            default=None,
            help="name of the input queue directory",
        )
        arggroup_daemon.add_argument(
            "--queue-in-wait",
            type=int,
            default=None,
            help="waiting time when the input queue is empty in seconds",
        )
        arggroup_daemon.add_argument(
            "--queue-out-dir",
            type=str,
            default=None,
            help="name of the output queue directory",
        )
        arggroup_daemon.add_argument(
            "--queue-out-limit",
            type=int,
            default=None,
            help="limit on the number of the files for the output queue directory",
        )
        arggroup_daemon.add_argument(
            "--queue-out-wait",
            type=int,
            default=None,
            help="waiting time when the output queue limit is reached in seconds",
        )

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default piper daemon configurations. This method overrides the base
        implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_QUEUE_IN_DIR, self.name),
            (self.CONFIG_QUEUE_IN_PERMS, mentat.const.DFLT_QUEUE_IN_PERMS),
            (self.CONFIG_QUEUE_IN_WAIT, mentat.const.DFLT_QUEUE_IN_CHECK_INTERVAL),
            (self.CONFIG_QUEUE_OUT_DIR, None),
            (self.CONFIG_QUEUE_OUT_LIMIT, mentat.const.DFLT_QUEUE_SIZE_LIMIT),
            (self.CONFIG_QUEUE_OUT_WAIT, mentat.const.DFLT_QUEUE_OUT_CHECK_INTERVAL),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _init_components(self, **kwargs):
        """
        Initialize requested daemon components.

        This method is called from the main constructor in :py:func:`pyzenkit.zendaemon.ZenDaemon.__init__`
        as a part of the **__init__** stage of application`s life cycle.
        """
        # Prepend the FilerDaemonComponent to the beginning of the component list.
        components = kwargs.get(self.CONFIG_COMPONENTS, [])
        components.insert(0, mentat.daemon.component.filer.FilerDaemonComponent())
        kwargs[self.CONFIG_COMPONENTS] = components

        super()._init_components(**kwargs)

    def _configure_postprocess(self):
        """
        Perform postprocessing of configuration values and calculate *core* configurations.

        This method is called from the :py:func:`pyzenkit.baseapp.BaseApp._stage_setup_configuration`
        as a port of the **setup** stage of application`s life cycle.
        """
        super()._configure_postprocess()

        ccfg = {}
        ccfg[mentat.dirq.DirectoryQueue.CONFIG_DIR_QUEUE] = self._get_queue_dir_path(self.c(self.CONFIG_QUEUE_IN_DIR))
        ccfg[mentat.dirq.DirectoryQueue.CONFIG_DIR_NEXT_QUEUE] = self._get_queue_dir_path(
            self.c(self.CONFIG_QUEUE_OUT_DIR)
        )
        ccfg[mentat.dirq.DirectoryQueue.CONFIG_QUEUE_PERMS] = self.c(self.CONFIG_QUEUE_IN_PERMS)
        ccfg[mentat.daemon.component.filer.FilerDaemonComponent.CONFIG_QUEUE_OUT_LIMIT] = self.c(
            self.CONFIG_QUEUE_OUT_LIMIT
        )
        ccfg[mentat.daemon.component.filer.FilerDaemonComponent.CONFIG_QUEUE_OUT_WAIT] = self.c(
            self.CONFIG_QUEUE_OUT_WAIT
        )
        ccfg[self.CONFIG_USER] = self.c(self.CONFIG_USER)
        ccfg[self.CONFIG_GROUP] = self.c(self.CONFIG_GROUP)
        self.config[self.CORE][self.CORE_FILEQUEUE] = ccfg

    def _get_queue_dir_path(self, queue_dir):
        if not queue_dir:
            return queue_dir
        queue_dir = str(queue_dir)
        if not os.path.dirname(queue_dir):
            return os.path.join(self.paths[self.PATH_VAR], "spool", queue_dir)
        return queue_dir


class DemoPrintComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Demonstration implementation of a daemon component capable of printing the
    message being processed to log.
    """

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": "message_process",
                "callback": self.cbk_event_message_process,
                "prepend": False,
            }
        ]

    def cbk_event_message_process(self, daemon, args):
        """
        Print the message contents into the log.
        """
        daemon.logger.info("Processing message: '%s': '%s'", str(args["id"]), str(args["data"]).strip())
        daemon.queue.schedule("message_commit", args)
        self.inc_statistic("cnt_printed")
        return (daemon.FLAG_CONTINUE, None)


class DemoPiperDaemon(PiperDaemon):
    """
    Minimalistic class for demonstration purposes.
    """

    def __init__(self, name=None, description=None):
        """
        Initialize demonstration piper daemon. This method overrides the base
        implementation in :py:func:`mentat.daemon.piper.PiperDaemon.__init__` and
        t aims to even more simplify the script object creation.

        :param str name: Optional daemon name.
        :param str description: Optional daemon description.
        """
        if not name:
            name = "demo-piperdaemon.py"
        if not description:
            description = "DemoPiperDaemon - Demonstration of generic pipe-like message processing daemon"

        super().__init__(
            name=name,
            description=description,
            #
            # Configure required deamon paths.
            #
            path_bin="tmp",
            path_cfg="tmp",
            path_var="tmp",
            path_log="tmp",
            path_tmp="tmp",
            path_run="tmp",
            #
            # Override default configurations.
            #
            default_stats_interval=mentat.const.DFLT_INTERVAL_STATISTICS,
            default_runlog_interval=mentat.const.DFLT_INTERVAL_RUNLOG,
            #
            # Schedule initial events.
            #
            schedule=[
                ("message_enqueue", {"data": '{"testA1": 1, "testA2": 2}'}),
                ("message_enqueue", {"data": '{"testB1": 1, "testB2": 2}'}),
                ("message_enqueue", {"data": '{"testC1": 1, "testC2": 2}'}),
                ("message_enqueue", {"data": '{"testD1": 1, "testD2": 2}'}),
                ("message_enqueue", {"data": '{"testE1": 1, "testE2": 2}'}),
                ("message_enqueue", {"data": '{"testF1": 1, "testF2": 2}'}),
                (mentat.const.DFLT_EVENT_START,),
            ],
            schedule_after=[
                (
                    mentat.const.DFLT_INTERVAL_STATISTICS,
                    mentat.const.DFLT_EVENT_LOG_STATISTICS,
                ),
                (
                    mentat.const.DFLT_INTERVAL_RUNLOG,
                    mentat.const.DFLT_EVENT_SAVE_RUNLOG,
                ),
            ],
            #
            # Define required daemon components.
            #
            components=[DemoPrintComponent()],
        )


# -------------------------------------------------------------------------------


#
# Perform the demonstration.
#
if __name__ == "__main__":
    # Prepare demonstration environment.
    DMN_NAME = "demo-piperdaemon.py"
    pyzenkit.baseapp.BaseApp.json_save(
        f"/tmp/{DMN_NAME}.conf",
        {
            "test_a": 1,
            "queue_out_dir": "/tmp/demo-piperdaemon.py.queue.done",
            "queue_out_limit": 2,
            "queue_out_wait": 5,
        },
    )
    with contextlib.suppress(FileExistsError):
        os.mkdir(f"/tmp/{DMN_NAME}")
        os.mkdir(f"/tmp/{DMN_NAME}.queue")
        os.mkdir(f"/tmp/{DMN_NAME}.queue.done")

    # Perform demonstration run.
    DemoPiperDaemon().run()
