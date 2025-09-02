#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a real-time message processing daemon capable of sampling
`IDEA <https://idea.cesnet.cz/en/index>`__ messages according to various policies.

This daemon is implemented using the :py:mod:`pyzenkit.zendaemon` framework and
so it provides all of its core features. See the documentation for in-depth
details.

It is further based on :py:mod:`mentat.daemon.piper` module, which provides
*pipe-like* message processing features. See the documentation for in-depth
details.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-sampler.py --help

    # Run in debug mode and stay in foreground (enable output of debugging
    # information to terminal and do not daemonize).
    mentat-sampler.py --no-daemon --debug

    # Run with increased logging level.
    mentat-sampler.py --log-level debug
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import mentat.const
import mentat.daemon.component.commiter
import mentat.daemon.component.parser
import mentat.daemon.component.sampler
import mentat.daemon.piper


class MentatSamplerDaemon(mentat.daemon.piper.PiperDaemon):
    """
    Implementation of Mentat module (real-time daemon) capable of sampling
    `IDEA <https://idea.cesnet.cz/en/index>`__ messages according to various policies.
    """

    CONFIG_SAMPLING_KEYS = "sampling_keys"
    CONFIG_SAMPLING_LIMIT = "sampling_limit"
    CONFIG_SAMPLING_POLICY = "sampling_policy"

    def __init__(self):
        """
        Initialize sampler daemon object. This method overrides the base
        implementation in :py:func:`pyzenkit.zendaemon.ZenDaemon.__init__` and
        it aims to even more simplify the daemon object creation by providing
        configuration values for parent contructor.
        """
        super().__init__(
            description="mentat-sampler.py - IDEA message sampling daemon",
            #
            # Define required daemon components.
            #
            components=[
                mentat.daemon.component.parser.ParserDaemonComponent(),
                mentat.daemon.component.sampler.SamplerDaemonComponent(),
                mentat.daemon.component.commiter.CommiterDaemonComponent(),
            ],
        )

    def _init_argparser(self, **kwargs):
        """
        Initialize daemon command line argument parser. This method overrides the
        base implementation in :py:func:`mentat.daemon.piper.PiperDaemon._init_argparser`
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
        # Create and populate options group for common script arguments.
        #
        arggroup_daemon = argparser.add_argument_group("custom daemon arguments")

        arggroup_daemon.add_argument("--sampling-limit", type=int, default=None, help="sampling limit")
        arggroup_daemon.add_argument("--sampling-policy", type=str, default=None, help="sampling policy")

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default daemon configurations. This method overrides the base
        implementation in :py:func:`mentat.daemon.piper.PiperDaemon._init_config`
        and it appends additional configurations via ``cfgs`` parameter.

        This method is called from the main constructor in :py:func:`pyzenkit.baseapp.BaseApp.__init__`
        as a part of the **__init__** stage of application`s life cycle.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_SAMPLING_LIMIT, 10),
            (self.CONFIG_SAMPLING_POLICY, "simple"),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)
