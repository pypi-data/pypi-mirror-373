#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing pre-caching functions and features. Use
case for this module is precaching distinct values of selected database table
column values. These can be then used for example for generating value selection
widgets for user interface.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.

It is further based on :py:mod:`mentat.script.fetcher` module, which provides
database fetching and message post-processing capabilities.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-precache.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-precache.py --debug

    # Run with increased logging level.
    mentat-precache.py --log-level debug


Available script commands
-------------------------

``precache`` (*default*)
    Perform pre-caching of selected database table column values. These values
    can be then used for various use cases like generating value selection widgets
    for user interface etc.

Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--allow-empty``
    Allow storing empty item sets as valid result (*flag*).

    *Type:* ``boolean``, *default:* ``False``

Custom config file options
^^^^^^^^^^^^^^^^^^^^^^^^^^

``itemsets``
    List of requested itemsets to be precached. It must be in a form of ``list``
    constaining ``list`` of two ``strings``, index 0 is a name of the itemset,
    index 1 is a name of event table column.

    Example configuration::

        "itemsets": [
            ["itemset-stat-categories",        "category"],
            ["itemset-stat-sourcetypes",       "source_type"],
            ["itemset-stat-targettypes",       "target_type"],
            ["itemset-stat-detectors",         "node_name"],
            ["itemset-stat-detectortypes",     "node_type"],
            ["itemset-stat-protocols",         "protocol"],
            ["itemset-stat-groups",            "resolvedabuses"],
            ["itemset-stat-target-groups",     "targetabuses"],
            ["itemset-stat-classes",           "eventclass"],
            ["itemset-stat-target-classes",    "targetclass"],
            ["itemset-stat-severities",        "eventseverity"],
            ["itemset-stat-target-severities", "targetseverity"],
            ["itemset-stat-inspectionerrors",  "inspectionerrors"],
            ["itemset-stat-tlps",              "tlp"]
        ],

    *Type:* ``list of list of strings``, *default:* ``[]``

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime

import mentat.const
import mentat.script.fetcher


class MentatPrecacheScript(mentat.script.fetcher.FetcherScript):
    """
    Implementation of Mentat module (script) providing pre-caching functions and
    features.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_ITEMSETS = "itemsets"
    CONFIG_ALLOW_EMPTY = "allow_empty"

    def __init__(self):
        """
        Initialize cleanup script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.eventservice = None
        self.sqlservice = None

        super().__init__(
            description="mentat-precache.py - Mentat database pre-caching script",
        )

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
            "--allow-empty",
            action="store_true",
            default=None,
            help="allow storing empty item sets as valid result (flag)",
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
            (self.CONFIG_ITEMSETS, None),
            (self.CONFIG_ALLOW_EMPTY, False),
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
        self.config[self.CONFIG_INTERVAL] = "10_minutes"

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "precache"

    def cbk_command_precache(self):
        """
        Implementation of the **precache** command (*default*).

        Perform pre-caching of selected database table column values. These values
        can be then used for various use cases like generating value selection
        widgets for user interface etc.
        """
        result = {"messages": {"info": [], "warning": []}, "itemsets": {}}

        for iset in self.c(self.CONFIG_ITEMSETS):
            self.logger.debug("Precaching itemset '%s': '%s'", iset[0], iset[1])

            # In order to have a better default than min(storagetime), use the time of the last run.
            PSTATE_KEY_LAST_RUN = f"ts_str_last_run_{iset[1]}"
            previous_run_ts = self.pstate.get(PSTATE_KEY_LAST_RUN, None)
            # Between the start and the end of a query, new events could be processed. In order to
            # not miss those new events, save the time now.
            last_run = datetime.datetime.now(datetime.UTC)

            try:
                items = self.eventservice.distinct_values(iset[1], previous_run_ts)
                self.pstate[PSTATE_KEY_LAST_RUN] = last_run

                if not items:
                    msg = f"Empty item set for '{iset[0]}' has been retrieved from database."
                    self.logger.warning(msg)
                    result["messages"]["warning"].append(msg)
                    if not self.config[self.CONFIG_ALLOW_EMPTY]:
                        continue

                result["messages"]["info"].append(f"Successfully updated item set '{iset[0]}'")
                result["itemsets"][iset[0]] = items

            except Exception as err:  # pylint: disable=locally-disabled,broad-except
                self.error(f"Unable to fetch item set '{iset[0]}' from database: {str(err).strip()}")

        return result
