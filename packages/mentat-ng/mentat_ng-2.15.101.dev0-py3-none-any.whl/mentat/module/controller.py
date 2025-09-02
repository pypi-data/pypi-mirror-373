#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#

# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing Mentat system control functions and features.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

The Mentat system is a collection of many real-time processing and post-processing
modules. Launching and managing so many processes would be really tedious work. And
that is exactly the use-case for this module. Its purpose is to start/stop/restart
all preconfigured real-time message processing modules and enable/disable all
preconfigured message post-processing modules (cronjobs).


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-controller.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-controller.py --debug

    # Run with increased logging level.
    mentat-controller.py --log-level debug

    # Determine the current status of Mentat system and all of its modules.
    mentat-controller.py
    mentat-controller.py --command status

    # Same as above, only execute and produce output in Nagios plugin compatible
    # mode.
    mentat-controller.py --command status --nagios-plugin --log-level warning

    # Start/stop/restart all configured real-time message processing modules.
    mentat-controller.py --command start
    mentat-controller.py --command stop
    mentat-controller.py --command restart

    # Enable/Disable all configured message post-processing modules (cronjobs).
    mentat-controller.py --command enable
    mentat-controller.py --command disable

    # Send signal to all configured real-time message processing modules.
    mentat-controller.py --command signal-usr1

    # Work with particular modules.
    mentat-controller.py --command start --target mentat-storage.py
    mentat-controller.py --command stop --target mentat-enricher.py mentat-inspector.py
    mentat-controller.py --command signal-usr1 --target mentat-inspector.py


Available script commands
-------------------------

``status`` (*default*)
    Detect and display the status of configured modules. The ``--target``
    command line option (*repeatable*) or ``target`` configuration file
    directive enables user to choose which modules should be affected by
    the command. All modules will be affected by default.

``start``
    Start configured modules. The ``--target`` command line option (*repeatable*)
    or ``target`` configuration file directive enables user to choose which
    modules should be affected by the command. All modules will be affected by default.

``stop``
    Stop configured modules. The ``--target`` command line option (*repeatable*)
    or ``target`` configuration file directive enables user to choose which
    modules should be affected by the command. All modules will be affected by default.

``restart``
    Restart configured modules. The ``--target`` command line option (*repeatable*)
    or ``target`` configuration file directive enables user to choose which
    modules should be affected by the command. All modules will be affected by default.

``enable``
    Enable configured cron modules. The ``--target`` command line option (*repeatable*)
    or ``target`` configuration file directive enables user to choose which
    modules should be affected by the command. All cron modules will be affected by default.

``disable``
    Disable configured cron modules. The ``--target`` command line option (*repeatable*)
    or ``target`` configuration file directive enables user to choose which
    modules should be affected by the command. All cron modules will be affected by default.

``signal-hup``
    Send signal *HUP* to configured modules. The ``--target`` command line
    option (*repeatable*) or ``target`` configuration file directive enables
    user to choose which modules should be affected by the command. All
    modules will be affected by default.

``signal-kill``
    Send signal *KILL* to configured modules. The ``--target`` command line
    option (*repeatable*) or ``target`` configuration file directive enables
    user to choose which modules should be affected by the command. All
    modules will be affected by default.

``signal-usr1``
    Send signal *USR1* to configured modules. The ``--target`` command line
    option (*repeatable*) or ``target`` configuration file directive enables
    user to choose which modules should be affected by the command. All
    modules will be affected by default.

``signal-usr2``
    Send signal *USR2* to configured modules. The ``--target`` command line
    option (*repeatable*) or ``target`` configuration file directive enables
    user to choose which modules should be affected by the command. All
    modules will be affected by default.

``pidfiles-clean``
    Clean up dangling PID files (files without matching running process).


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--target module-id``
    Target module(s) for the current command (*repeatable*).

    *Type:* ``string``

``--nagios-plugin``
    Execute as Nagios plugin (flag).

    *Type:* ``bool``, *default:* ``False``


Custom configuration file options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``modules``
    List of real-time message processing modules that should be managed.

    *Type:* ``list of dicts``

``cronjobs``
    List of message post-processing modules that should be managed.

    *Type:* ``list of dicts``

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import pprint
import signal
import time

import mentat.const
import mentat.script.base
import mentat.system

# Translation table to translate signal numbers to their names.
SIGNALS_TO_NAMES_DICT = {getattr(signal, n): n for n in dir(signal) if n.startswith("SIG") and "_" not in n}

CRON_SCRIPT_DIR = "/etc/cron.d"


class MentatControllerScript(mentat.script.base.MentatBaseScript):
    """
    Implementation of Mentat module (script) providing Mentat system control
    functions and features.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_TARGET = "target"
    CONFIG_NAGIOS_PLUGIN = "nagios_plugin"
    CONFIG_MODULES = "modules"
    CONFIG_CRONJOBS = "cronjobs"

    def __init__(self):
        """
        Initialize controller script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.modules = None
        self.cronjobs = None

        super().__init__(description="mentat-controller.py - Mentat system control script")

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

        # Specify the target module(s) for the command
        arggroup_script.add_argument(
            "--target",
            help="target module(s) for the current command (*repeatable*)",
            action="append",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--nagios-plugin",
            help="execute in Nagios plugin compatible mode (flag)",
            action="store_true",
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

        cfgs = ((self.CONFIG_TARGET, None), (self.CONFIG_NAGIOS_PLUGIN, False)) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _sub_stage_setup(self):
        """
        **SUBCLASS HOOK**: Perform additional custom setup actions.

        This method is called from the main setup method :py:func:`pyzenkit.baseapp.BaseApp._stage_setup`
        as a part of the **setup** stage of application`s life cycle.
        """
        self.modules = mentat.system.make_module_list(self.c(self.CONFIG_MODULES))
        self.cronjobs = mentat.system.make_cronjob_list(self.c(self.CONFIG_CRONJOBS))

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "status"

    def get_system_status(self):
        """
        Convenience method for getting overall system status.

        :return: Structured dictionary with preprocessed information.
        :rtype: dict
        """
        return mentat.system.system_status(
            self.modules,
            self.cronjobs,
            self.paths.get(self.PATH_CFG),
            CRON_SCRIPT_DIR,
            self.paths.get(self.PATH_LOG),
            self.paths.get(self.PATH_RUN),
        )

    def cbk_command_status(self):
        """
        Implementation of the **status** command (*default*).

        Detect and display the status of configured modules. The ``--target``
        command line option (*repeatable*) or ``target`` configuration file
        directive enables user to choose which modules should be affected by
        the command. All modules will be affected by default.
        """
        status = self.get_system_status()

        self.logger.info("Status of configured Mentat real-time modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            self.logger.info("Real-time module '%s': '%s'", mname, stat[1])
        self.logger.info("Overall real-time module status: '%s'", status["resultm"][1])

        self.logger.info("Status of configured Mentat cronjob modules:")
        modulelist = self._get_target_c()
        for mname in modulelist:
            stat = status["cronjobs"].get(mname)
            if stat is None:
                self.logger.info("Cronjob module '%s': Module is not configured", mname)
                continue
            self.logger.info("Cronjob module '%s': '%s'", mname, stat[1])
        self.logger.info("Overall cronjob module status: '%s'", status["resultc"][1])

        for msgcat in ["info", "notice", "warning", "error"]:
            if status["messages"][msgcat]:
                for prob in status["messages"][msgcat]:
                    getattr(self.logger, msgcat)(prob[0])

        self.logger.info("Overall Mentat system status: '%s'", status["result"][1])

        if not self.c(self.CONFIG_NAGIOS_PLUGIN):
            self.retc = status["result"][0]  # pylint: disable=locally-disabled,attribute-defined-outside-init
        else:
            if status["result"][0] == mentat.system.STATUS_RT_RUNNING_OK:
                print("MENTATCTRL OK - All modules up and running;")
                self.retc = mentat.const.NAGIOS_PLUGIN_RC_OK
            else:
                print(
                    "MENTATCTRL CRITICAL - System is not in healthy state;|{};{};{}".format(
                        status["resultm"][1], status["resultc"][1], status["result"][1]
                    )
                )
                self.retc = mentat.const.NAGIOS_PLUGIN_RC_CRITICAL
        return self.RESULT_SUCCESS

    def cbk_command_start(self):
        """
        Implementation of the **start** command.

        Start configured modules. The ``--target`` command line option (*repeatable*)
        or ``target`` configuration file directive enables user to choose which
        modules should be affected by the command. All modules will be affected
        by default.
        """
        status = self.get_system_status()

        self.logger.info("Starting all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue

            proc = status["processes"].get(mname, None)

            if stat[0] == mentat.system.STATUS_RT_RUNNING_OK:
                self.logger.info(
                    "Module '%s': Module is already running properly, nothing to do",
                    mname,
                )
            elif stat[0] == mentat.system.STATUS_RT_NOT_RUNNING:
                self.logger.info("Module '%s': Launching module", mname)
                self._module_start(self.modules[mname], proc)
            elif stat[0] == mentat.system.STATUS_RT_RUNNING_FEWER:
                self.logger.info(
                    "Module '%s': Module is running in fewer than required instances",
                    mname,
                )
            elif stat[0] == mentat.system.STATUS_RT_RUNNING_MORE:
                self.logger.info(
                    "Module '%s': Module is running in more than required instances",
                    mname,
                )
            else:
                self.logger.error(
                    "Module '%s': Module is in weird state, unable to perform automatic startup",
                    mname,
                )

        self.logger.info("Waiting for modules to fully start up")
        time.sleep(1)
        status = self.get_system_status()
        self.retc = status["resultm"][0]  # pylint: disable=locally-disabled,attribute-defined-outside-init

        if self.retc == mentat.system.STATUS_RT_RUNNING_OK:
            self.logger.info("System startup seems successful")
            return self.RESULT_SUCCESS

        self.logger.error("System startup seems to have failed")
        return self.RESULT_FAILURE

    def cbk_command_enable(self):
        """
        Implementation of the **enable** command.

        Enable configured cron modules. The ``--target`` command line option (*repeatable*)
        or ``target`` configuration file directive enables user to choose which
        modules should be affected by the command. All modules will be affected
        by default.
        """
        status = self.get_system_status()

        self.logger.info("Enabling all configured Mentat cron modules:")
        modulelist = self._get_target_c()
        for mname in modulelist:
            stat = status["cronjobs"].get(mname)
            meta = status["cron_files"].get(mname)
            if stat is None or (stat[0] == mentat.system.STATUS_CJ_DISABLED and meta is None):
                self.logger.info("Cron module '%s': Module is not configured", mname)
                continue

            if stat[0] == mentat.system.STATUS_CJ_ENABLED:
                self.logger.info("Cron module '%s': Module is already enabled, nothing to do", mname)
            elif stat[0] == mentat.system.STATUS_CJ_DISABLED:
                self.logger.info("Cron module '%s': Enabling module", mname)
                self._module_enable(self.cronjobs[mname], meta)
            else:
                self.logger.error(
                    "Cron module '%s': Module is in weird state, unable to perform automatic startup",
                    mname,
                )

        status = self.get_system_status()
        self.retc = status["resultc"][0]  # pylint: disable=locally-disabled,attribute-defined-outside-init

        if self.retc == mentat.system.STATUS_CJ_ENABLED:
            self.logger.info("System startup seems successful")
            return self.RESULT_SUCCESS

        self.logger.error("System startup seems to have failed")
        return self.RESULT_FAILURE

    def cbk_command_stop(self):
        """
        Implementation of the **stop** command.

        Stop configured modules. The ``--target`` command line option (*repeatable*)
        or ``target`` configuration file directive enables user to choose which
        modules should be affected by the command. All modules will be affected
        by default.
        """
        self.logger.info("Stopping all configured Mentat modules:")
        modulelist = self._get_target()

        # We will try to make at most 20 attempts to stop all Mentat modules.
        for i in range(1, 20):
            status = self.get_system_status()

            nextmodulelist = []
            if not modulelist:
                break

            # Process all modules from the list.
            for mname in modulelist:
                stat = status["modules"].get(mname)
                if stat is None:
                    self.logger.info("Module '%s': Module is not configured", mname)
                    continue
                proc = status["processes"].get(mname, None)

                if stat[0] == mentat.system.STATUS_RT_NOT_RUNNING:
                    # In case this is a first attempt the module was already not running.
                    if i == 1:
                        self.logger.info(
                            "Module '%s': Module is already not running, nothing to do",
                            mname,
                        )
                    # Otherwise the stop was successful.
                    else:
                        self.logger.info("Module '%s': Module successfully stopped", mname)
                    continue

                if stat[0] in (
                    mentat.system.STATUS_RT_RUNNING_OK,
                    mentat.system.STATUS_RT_RUNNING_PF_MISSING,
                    mentat.system.STATUS_RT_RUNNING_PID_MISSMATCH,
                    mentat.system.STATUS_RT_RUNNING_INCONSISTENT,
                    mentat.system.STATUS_RT_RUNNING_FEWER,
                    mentat.system.STATUS_RT_RUNNING_MORE,
                ):
                    # Perform attemt to stop the module and mark it for another check in next iteration.
                    self.logger.info("Module '%s': Stopping module, attempt #%s", mname, i)
                    try:
                        self._module_signal(self.modules[mname], proc, signal.SIGINT)
                    except ProcessLookupError:
                        if i > 1:
                            self.logger.debug(
                                "Module '%s': probably already stopped on the previous attempt",
                                mname,
                            )
                        else:
                            raise
                    nextmodulelist.append(mname)
                    continue

                self.logger.error(
                    "Module '%s': Module is in weird state, unable to perform full automatic shutdown",
                    mname,
                )

            # In case there are any modules marked for check in next iteration, wait for them to shut down.
            if nextmodulelist:
                self.logger.info("Waiting for modules to fully shut down")
                time.sleep(1)

            # Prepare module list for another iteration.
            modulelist = nextmodulelist

        # Review the overall Mentat system status.
        status = self.get_system_status()
        self.retc = status["resultm"][0]  # pylint: disable=locally-disabled,attribute-defined-outside-init

        if self.retc == mentat.system.STATUS_RT_NOT_RUNNING:
            self.logger.info("System shutdown seems successful")
            # STATUS_RT_NOT_RUNNING has code 5. In case of stopping modules, this is a wanted state, so we
            # need to set successful return code.
            self.retc = 0
            return self.RESULT_SUCCESS

        self.logger.error("System shutdown seems to have failed")
        return self.RESULT_FAILURE

    def cbk_command_disable(self):
        """
        Implementation of the **disable** command.

        Disable configured cron modules. The ``--target`` command line option (*repeatable*)
        or ``target`` configuration file directive enables user to choose which
        modules should be affected by the command. All modules will be affected
        by default.
        """
        status = self.get_system_status()

        self.logger.info("Disabling all configured Mentat cron modules:")
        modulelist = self._get_target_c()
        for mname in modulelist:
            stat = status["cronjobs"].get(mname)
            meta = status["cron_files"].get(mname)
            if stat is None or (stat[0] == mentat.system.STATUS_CJ_DISABLED and meta is None):
                self.logger.info("Cron module '%s': Module is not configured", mname)
                continue

            if stat[0] == mentat.system.STATUS_CJ_ENABLED:
                self.logger.info("Cron module '%s': Disabling module", mname)
                self._module_disable(self.cronjobs[mname], meta)
            elif stat[0] == mentat.system.STATUS_CJ_DISABLED:
                self.logger.info("Cron module '%s': Module is already disabled, nothing to do", mname)
            else:
                self.logger.error(
                    "Cron module '%s': Module is in weird state, unable to perform automatic shutdown",
                    mname,
                )

        status = self.get_system_status()
        self.retc = status["result"][0]  # pylint: disable=locally-disabled,attribute-defined-outside-init

        if self.retc == mentat.system.STATUS_CJ_DISABLED:
            self.logger.info("System shutdown seems successful")
            # STATUS_CJ_DISABLED has code 5. In case of disabling cron modules, this is a wanted state, so we
            # need to set successful return code.
            self.retc = 0
            return self.RESULT_SUCCESS

        self.logger.error("System shutdown seems to have failed")
        return self.RESULT_FAILURE

    def cbk_command_restart(self):
        """
        Implementation of the **restart** command.

        Restart configured modules. The ``--target`` command line option (*repeatable*)
        or ``target`` configuration file directive enables user to choose which
        modules should be affected by the command. All modules will be affected
        by default.
        """
        result = self.cbk_command_stop()
        if result == self.RESULT_FAILURE:
            return self.RESULT_FAILURE
        return self.cbk_command_start()

    def cbk_command_signal_kill(self):
        """
        Implementation of the **signal-kill** command.

        Send signal *KILL* to configured modules. The ``--target`` command line
        option (*repeatable*) or ``target`` configuration file directive enables
        user to choose which modules should be affected by the command. All
        modules will be affected by default.
        """
        status = self.get_system_status()

        self.logger.info("Killing all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            proc = status["processes"].get(mname, None)

            if stat[0] == mentat.system.STATUS_RT_NOT_RUNNING:
                self.logger.info("Module '%s': Module is already not running, nothing to do", mname)
            elif stat[0] in (
                mentat.system.STATUS_RT_RUNNING_OK,
                mentat.system.STATUS_RT_RUNNING_PF_MISSING,
                mentat.system.STATUS_RT_RUNNING_PID_MISSMATCH,
                mentat.system.STATUS_RT_RUNNING_INCONSISTENT,
                mentat.system.STATUS_RT_RUNNING_FEWER,
                mentat.system.STATUS_RT_RUNNING_MORE,
            ):
                self.logger.info("Module '%s': Killing module", mname)
                self._module_signal(self.modules[mname], proc, signal.SIGKILL)
            else:
                self.logger.error("Module '%s': Module is in weird state, unable to kill it", mname)

        return self.RESULT_SUCCESS

    def cbk_command_signal_hup(self):
        """
        Implementation of the **signal-hup** command.

        Send signal *HUP* to configured modules. The ``--target`` command line
        option (*repeatable*) or ``target`` configuration file directive enables
        user to choose which modules should be affected by the command. All
        modules will be affected by default.
        """
        status = self.get_system_status()

        self.logger.info("Sending SIGHUP signal to all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            proc = status["processes"].get(mname, None)

            if stat[0] == mentat.system.STATUS_RT_RUNNING_OK:
                self._module_signal(self.modules[mname], proc, signal.SIGHUP)
            else:
                self.logger.error("Module '%s': Unable to send signal", mname)

        return self.RESULT_SUCCESS

    def cbk_command_signal_usr1(self):
        """
        Implementation of the **signal-usr1** command.

        Send signal *USR1* to configured modules. The ``--target`` command line
        option (*repeatable*) or ``target`` configuration file directive enables
        user to choose which modules should be affected by the command. All
        modules will be affected by default.
        """
        status = self.get_system_status()

        self.logger.info("Sending SIGUSR1 signal to all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            proc = status["processes"].get(mname, None)

            if stat[0] == mentat.system.STATUS_RT_RUNNING_OK:
                self._module_signal(self.modules[mname], proc, signal.SIGUSR1)
            else:
                self.logger.error("Module '%s': Unable to send SIGUSR1 signal", mname)

        return self.RESULT_SUCCESS

    def cbk_command_signal_usr2(self):
        """
        Implementation of the **signal-usr2** command.

        Send signal *USR2* to configured modules. The ``--target`` command line
        option (*repeatable*) or ``target`` configuration file directive enables
        user to choose which modules should be affected by the command. All
        modules will be affected by default.
        """
        status = self.get_system_status()

        self.logger.info("Sending SIGUSR2 signal to all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            proc = status["processes"].get(mname, None)

            if stat[0] == mentat.system.STATUS_RT_RUNNING_OK:
                self._module_signal(self.modules[mname], proc, signal.SIGUSR2)
            else:
                self.logger.error("Module '%s': Unable to send SIGUSR2 signal", mname)

        return self.RESULT_SUCCESS

    def cbk_command_pidfiles_clean(self):
        """
        Implementation of the **pidfiles-clean** command.

        Clean up dangling PID files (files without matching running process).
        """
        status = self.get_system_status()

        self.logger.info("Cleaning up dangling PID files of all configured Mentat modules:")
        modulelist = self._get_target()
        for mname in modulelist:
            stat = status["modules"].get(mname)
            if stat is None:
                self.logger.info("Module '%s': Module is not configured", mname)
                continue
            pidf = status["pid_files"].get(mname, None)
            if stat[0] == mentat.system.STATUS_RT_DEAD_PF_EXISTS:
                for pid in pidf:
                    self.logger.info(
                        "Module '%s': Removing dangling PID file '%s' of missing process '%d'",
                        mname,
                        pidf[pid]["path"],
                        pid,
                    )
                    os.unlink(pidf[pid]["path"])

    # ---------------------------------------------------------------------------

    def _get_target(self):
        """
        Get target module(s) of the command.

        By default targets are all modules from configuration file, this can however
        be overriden by giving command line optin '--target'.
        """
        target = self.c(self.CONFIG_TARGET)
        if target and isinstance(target, list):
            return target
        return self.modules.keys()

    def _get_target_c(self):
        """
        Get target cron module(s) of the command.

        By default targets are all modules from configuration file, this can however
        be overriden by giving command line optin '--target'.
        """
        target = self.c(self.CONFIG_TARGET)
        if target and isinstance(target, list):
            return target
        return self.cronjobs.keys()

    # ---------------------------------------------------------------------------

    @staticmethod
    def _prepare_command(mod_data):
        """
        Prepare system command for execution of given module.
        """
        path = mod_data.executable
        # From documentation https://docs.python.org/3/library/os.html#os.execv:
        # "...the arguments to the child process should start with the name of
        # the command being run, but this is not enforced..."
        args = [
            path,
        ]
        if mod_data.name != os.path.basename(mod_data.executable):
            args = args + ["--name", mod_data.name]
        if mod_data.paralel:
            args = args + [
                "--paralel",
            ]
        if mod_data.args:
            args = args + mod_data.args
        return (path, args)

    def _execute(self, mod_data):
        """
        Execute one instance of given module.
        """
        (executable, arguments) = self._prepare_command(mod_data)

        newpid = os.fork()
        if newpid == 0:
            self.logger.info(
                "Module '%s': Worker process '%d' ready, executing command '%s' with arguments '%s'",
                mod_data.name,
                os.getpid(),
                executable,
                pprint.pformat(arguments),
            )
            os.sync()
            os.execvp(executable, arguments)

            # In case the os.execv() call was successful we should never reach
            # this point in code. If we are here, there was a critical error.
            self.logger.critical(
                "Module '%s': Worker process '%d' was unable to execute module",
                mod_data.name,
                os.getpid(),
            )
            os._exit(1)  # pylint: disable=locally-disabled,protected-access
        else:
            self.logger.info("Module '%s': Waiting for worker process '%d'", mod_data.name, newpid)
            time.sleep(1)

    def _module_start(self, mod_data, processes):
        """
        Start required number of instances of given module.
        """
        instances = 1
        if mod_data.paralel:
            instances = mod_data.count
        if processes:
            instances = instances - len(processes.keys())

        for i in range(instances):
            self.logger.info("Module '%s': Launching instance '%d'", mod_data.name, i)
            self._execute(mod_data)

    def _module_enable(self, mod_data, meta):
        """
        Enable given cron module.
        """
        link_path = os.path.join(CRON_SCRIPT_DIR, meta["name"])
        self.logger.debug(
            "Module '%s': Creating symlink from '%s' to '%s'",
            mod_data.name,
            meta["path"],
            link_path,
        )
        os.symlink(meta["path"], link_path)

    def _module_disable(self, mod_data, meta):
        """
        Disable given cron module.
        """
        self.logger.debug(
            "Module '%s': Removing symlink '%s'",
            mod_data.name,
            meta["link"],
        )
        os.remove(meta["link"])

    # ---------------------------------------------------------------------------

    def _signal(self, mod_data, pid, sig):
        """
        Send given signal to given system process.
        """
        self.logger.info(
            "Module '%s': Sending signal '%s' to process '%d'",
            mod_data.name,
            SIGNALS_TO_NAMES_DICT.get(sig, sig),
            pid,
        )
        os.kill(pid, sig)

    def _module_signal(self, mod_data, processes, sig):
        """
        Send given signal to given module.
        """
        for pid in sorted(processes.keys()):
            self._signal(mod_data, pid, sig)
