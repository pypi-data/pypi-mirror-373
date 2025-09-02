#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This Mentat module is a script providing functions for generating `IDEA <https://idea.cesnet.cz/en/index>`__
messages, mainly for testing or development purposes.

The messsages are generated using prepared templates filled with randomized values
of certain keys.

Currently this script is work in progress and many features are hardcoded, like
the lists of values for message randomization process.

This script is implemented using the :py:mod:`pyzenkit.zenscript` framework and
so it provides all of its core features. See the documentation for more in-depth
details.


Message templates
-----------------

Message templates are based on :py:mod:`jinja2` templates. The location of template
directory can be adjusted with command line option ``--template-dir`` or configuration
file directive ``template_dir`` and by default is set to ``/etc/mentat/templates/idea``.


Usage examples
--------------

.. code-block:: shell

    # Display help message and exit.
    mentat-ideagen.py --help

    # Run in debug mode (enable output of debugging information to terminal).
    mentat-ideagen.py --debug

    # Run with increased logging level.
    mentat-ideagen.py --log-level debug

    # Generate given number of messages.
    mentat-ideagen.py --count 10

    # Generate random number of messages up to given max count.
    mentat-ideagen.py --random-count 10

    # Generate messages into given queue directory.
    mentat-ideagen.py --queue-dir /var/mentat/spool/mentat-inspector.py/incoming


Available script commands
-------------------------

``generate-random`` (*default*)
    Generate configured number of random test messages into target queue directory.


Custom configuration
--------------------

Custom command line options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``--count``
    Number of messages to be generated in one batch. This option is mutually
    exclusive with ``random-count`` and always comes as a second.

    *Type:* ``integer``, *default:* ``1``

``--random-count``
    Number of messages to be generated in one batch. This option is mutually
    exclusive with ``count`` and always takes precedence.

    *Type:* ``integer``, *default:* ``None``

``--steady``
    Generate messages continuously with given time backoff (*flag*).

    *Type:* ``boolean``, *default:* ``False``

``--back-off``
    Back-off time between message batches in seconds, used when ``steady`` is ``True``.

    *Type:* ``integer``, *default:* ``60``

``--queue-dir``
    Name of the target queue directory.

    *Type:* ``string``, *default:* ``/var/tmp``

``--temp-dir``
    Name of the temporary file directory.

    *Type:* ``string``, *default:* ``/var/tmp``

``--template``
    Name of template file for generating messages.

    *Type:* ``string``, *default:* ``msg.01.idea.j2``

``--template-dir``
    Name of the directory containing message templates.

    *Type:* ``string``, *default:* ``/etc/mentat/templates/idea``


"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import random
import string
import time

from jinja2 import Environment, FileSystemLoader

import mentat.const
import mentat.script.base

# -------------------------------------------------------------------------------


class MentatIdeagenScript(mentat.script.base.MentatBaseScript):
    """
    Implementation of Mentat module (script) providing functions for generating
    `IDEA <https://idea.cesnet.cz/en/index>`__ messages, mainly for testing or
    development purposes.
    """

    #
    # Class constants.
    #

    # List of configuration keys.
    CONFIG_COUNT = "count"
    CONFIG_RANDOM_COUNT = "random_count"
    CONFIG_BACK_OFF = "back_off"
    CONFIG_STEADY = "steady"
    CONFIG_QUEUE_DIR = "queue_dir"
    CONFIG_TEMP_DIR = "temp_dir"
    CONFIG_TEMPLATE = "template"
    CONFIG_TEMPLATE_DIR = "template_dir"

    CONFIG_LIST_SOURCE_IP4S = "list_source_ip4s"
    CONFIG_LIST_TARGET_IP4S = "list_target_ip4s"
    CONFIG_LIST_SOURCE_IP6S = "list_source_ip6s"
    CONFIG_LIST_TARGET_IP6S = "list_target_ip6s"

    CONFIG_LIST_SOURCE_MACS = "list_source_macs"
    CONFIG_LIST_TARGET_MACS = "list_target_macs"
    CONFIG_LIST_SOURCE_HOSTNAMES = "list_source_hostnames"
    CONFIG_LIST_TARGET_HOSTNAMES = "list_target_hostnames"
    CONFIG_LIST_SOURCE_URLS = "list_source_urls"
    CONFIG_LIST_TARGET_URLS = "list_target_urls"
    CONFIG_LIST_SOURCE_EMAILS = "list_source_emails"
    CONFIG_LIST_TARGET_EMAILS = "list_target_emails"

    CONFIG_LIST_SRCTGT_TAGS = "list_srctgt_tags"
    CONFIG_LIST_PROTOCOLS = "list_protocols"
    CONFIG_LIST_CATEGORIES = "list_categories"
    CONFIG_LIST_SEVERITIES = "list_severities"
    CONFIG_LIST_CLASSES = "list_classes"
    CONFIG_LIST_TARGET_CLASSES = "list_target_classes"
    CONFIG_LIST_NODE_NAMES = "list_node_names"
    CONFIG_LIST_NODE_SWS = "list_node_sws"
    CONFIG_LIST_NODE_TAGS = "list_node_tags"
    CONFIG_LIST_TLPS = "list_tlps"

    def __init__(self):
        """
        Initialize ideagen script object. This method overrides the base
        implementation in :py:func:`pyzenkit.zenscript.ZenScript.__init__` and
        it aims to even more simplify the script object creation by providing
        configuration values for parent contructor.
        """
        self.templ_env = None

        super().__init__(
            description="mentat-ideagen.py - IDEA message generation script for Mentat system",
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

        # Setup mutually exclusive group for regular counter vs. random counter.
        group_a = arggroup_script.add_mutually_exclusive_group()
        group_a.add_argument(
            "--count",
            help="number of messages to be generated in one batch",
            type=int,
            default=None,
        )
        group_a.add_argument(
            "--random-count",
            help="generate random number of messages",
            type=int,
            default=None,
        )

        arggroup_script.add_argument(
            "--steady",
            help="generate messages continuously with given time backoff (flag)",
            action="store_true",
            default=None,
        )
        arggroup_script.add_argument(
            "--back-off",
            help="back-off time between message batches in seconds",
            type=int,
            default=None,
        )
        arggroup_script.add_argument(
            "--queue-dir",
            help="name of the target queue directory",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--temp-dir",
            help="name of the temporary file directory",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--template",
            help="name of template file for generating messages",
            type=str,
            default=None,
        )
        arggroup_script.add_argument(
            "--template-dir",
            help="name of the directory containing message templates",
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
            (self.CONFIG_COUNT, 1),
            (self.CONFIG_RANDOM_COUNT, None),
            (self.CONFIG_STEADY, False),
            (self.CONFIG_BACK_OFF, 60),
            (
                self.CONFIG_QUEUE_DIR,
                os.path.join(
                    self.paths[self.PATH_VAR],
                    "spool",
                    "mentat-inspector.py",
                    "incoming",
                ),
            ),
            (
                self.CONFIG_TEMP_DIR,
                os.path.join(self.paths[self.PATH_VAR], "spool", "mentat-inspector.py", "tmp"),
            ),
            (self.CONFIG_TEMPLATE, "msg.01.idea.j2"),
            (
                self.CONFIG_TEMPLATE_DIR,
                os.path.join(self.paths[self.PATH_CFG], "templates", "idea"),
            ),
            (self.CONFIG_LIST_SOURCE_IP4S, []),
            (self.CONFIG_LIST_TARGET_IP4S, []),
            (self.CONFIG_LIST_SOURCE_IP6S, []),
            (self.CONFIG_LIST_TARGET_IP6S, []),
            (self.CONFIG_LIST_SOURCE_MACS, []),
            (self.CONFIG_LIST_TARGET_MACS, []),
            (self.CONFIG_LIST_SOURCE_HOSTNAMES, []),
            (self.CONFIG_LIST_TARGET_HOSTNAMES, []),
            (self.CONFIG_LIST_SOURCE_URLS, []),
            (self.CONFIG_LIST_TARGET_URLS, []),
            (self.CONFIG_LIST_SOURCE_EMAILS, []),
            (self.CONFIG_LIST_TARGET_EMAILS, []),
            (self.CONFIG_LIST_SRCTGT_TAGS, []),
            (self.CONFIG_LIST_PROTOCOLS, []),
            (self.CONFIG_LIST_CATEGORIES, []),
            (self.CONFIG_LIST_SEVERITIES, []),
            (self.CONFIG_LIST_CLASSES, []),
            (self.CONFIG_LIST_TARGET_CLASSES, []),
            (self.CONFIG_LIST_NODE_NAMES, []),
            (self.CONFIG_LIST_NODE_SWS, []),
            (self.CONFIG_LIST_NODE_TAGS, []),
            (self.CONFIG_LIST_TLPS, []),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _sub_stage_setup(self):
        """
        **SUBCLASS HOOK**: Perform additional custom setup actions.

        This method is called from the main setup method :py:func:`pyzenkit.baseapp.BaseApp._stage_setup`
        as a part of the **setup** stage of application`s life cycle.
        """
        self.templ_env = Environment(loader=FileSystemLoader(self.c(self.CONFIG_TEMPLATE_DIR)))

    # ---------------------------------------------------------------------------

    def get_default_command(self):
        """
        Return the name of the default script command. This command will be executed
        in case it is not explicitly selected either by command line option, or
        by configuration file directive.

        :return: Name of the default command.
        :rtype: str
        """
        return "generate_random"

    def cbk_command_generate_random(self):
        """
        Implementation of **generate-random** command (*default*).

        Generate configured number of random test messages into target queue
        directory.
        """
        result = {"cnt_messages": 0, "cnt_batches": 0}

        template = self.templ_env.get_template(self.c(self.CONFIG_TEMPLATE))
        counter = self.c(self.CONFIG_RANDOM_COUNT)
        if counter:
            counter = random.randint(1, counter)
        else:
            counter = self.c(self.CONFIG_COUNT)
        self.dbgout(f"Using template '{self.c(self.CONFIG_TEMPLATE)}' to generate {counter:d} message(s)")

        try:
            while True:
                result["cnt_batches"] += 1

                for idx in range(1, counter + 1):
                    variables = self._generate_variables()
                    idea_message = template.render(**variables)

                    ifn = self._save_message(variables["message_id"], idea_message)
                    self.logger.info(
                        "[%s] Message was generated and stored to file '%s'",
                        f"{idx:,d}",
                        ifn,
                    )
                    result["cnt_messages"] += 1

                if not self.c(self.CONFIG_STEADY):
                    break

                backoff = self.c(self.CONFIG_BACK_OFF)
                if backoff:
                    self.logger.info("Waiting for '%d' second(s) before next message batch", backoff)
                    time.sleep(backoff)

        except FileNotFoundError as err:
            self.logger.critical("%s", str(err))

        except PermissionError as err:
            self.logger.critical("%s", str(err))

        except KeyboardInterrupt:
            pass

        return result

    # ---------------------------------------------------------------------------

    @staticmethod
    def _generate_id(size=6, chars=string.ascii_lowercase + string.digits):
        """
        Generate random unique identifier of given length and using given set of
        characters.

        :param int size: Size of the identifier.
        :param list chars: List of the possible characters.
        :return: Unique identifier.
        :rtype: str
        """
        return "{}{}".format("testmsg-", "".join(random.choice(chars) for _ in range(size)))

    @staticmethod
    def _random_set(populace, mincnt=0, maxcnt=1):
        """
        Generate randomly sized list within given boundaries containing random
        set from given values.

        :param populace: Populace of items from which to choose (list or lambda).
        :param int mincnt: Minimal number of items in result.
        :param int maxcnt: Maximal number of items in result.
        :rtype: list
        """
        if not populace:
            return []

        result = []
        size = random.randint(mincnt, maxcnt)
        for _ in range(size):
            counter = 100
            while counter > 0:
                if isinstance(populace, list):
                    item = random.choice(populace)
                else:
                    item = populace()
                if item not in result:
                    result.append(item)
                    break
                counter = counter - 1
        return sorted(result)

    @staticmethod
    def _safe_choice(generation_list):
        """
        Returns result of random.choice(), but only if the input list
        is not empty, otherwise it returns None.
        """
        if generation_list:
            return random.choice(generation_list)
        return None

    def _generate_variables(self):
        """
        Generate random set of message variables. The :py:func:`random.choice`
        function is used for the randomization process.

        :return: Set of randomized variables to be used for filling-in the IDEA
                 message template.
        :rtype: dict
        """
        return {
            "message_id": self._generate_id(20),
            "tlp": self._safe_choice(self.c(self.CONFIG_LIST_TLPS)),
            "detect_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "source_ip4": self._random_set(self.c(self.CONFIG_LIST_SOURCE_IP4S), 1, 3),
            "target_ip4": self._random_set(self.c(self.CONFIG_LIST_TARGET_IP4S), 0, 2),
            "source_ip6": self._random_set(self.c(self.CONFIG_LIST_SOURCE_IP6S), 1, 3),
            "target_ip6": self._random_set(self.c(self.CONFIG_LIST_TARGET_IP6S), 0, 2),
            "source_mac": self._random_set(self.c(self.CONFIG_LIST_SOURCE_MACS), 1, 3),
            "target_mac": self._random_set(self.c(self.CONFIG_LIST_TARGET_MACS), 0, 2),
            "source_hostname": self._random_set(self.c(self.CONFIG_LIST_SOURCE_HOSTNAMES), 1, 3),
            "target_hostname": self._random_set(self.c(self.CONFIG_LIST_TARGET_HOSTNAMES), 0, 2),
            "source_url": self._random_set(self.c(self.CONFIG_LIST_SOURCE_URLS), 1, 3),
            "target_url": self._random_set(self.c(self.CONFIG_LIST_TARGET_URLS), 0, 2),
            "source_email": self._random_set(self.c(self.CONFIG_LIST_SOURCE_EMAILS), 1, 3),
            "target_email": self._random_set(self.c(self.CONFIG_LIST_TARGET_EMAILS), 0, 2),
            "source_port": self._random_set(lambda: random.randint(0, 65535), 0, 5),
            "target_port": self._random_set(lambda: random.randint(0, 65535), 0, 5),
            "source_proto": self._random_set(self.c(self.CONFIG_LIST_PROTOCOLS), 0, 3),
            "target_proto": self._random_set(self.c(self.CONFIG_LIST_PROTOCOLS), 0, 3),
            "source_type": self._random_set(self.c(self.CONFIG_LIST_SRCTGT_TAGS), 0, 2),
            "target_type": self._random_set(self.c(self.CONFIG_LIST_SRCTGT_TAGS), 0, 2),
            "category": self._random_set(self.c(self.CONFIG_LIST_CATEGORIES), 1, 3),
            "severity": self._safe_choice(self.c(self.CONFIG_LIST_SEVERITIES)),
            "target_severity": self._safe_choice(self.c(self.CONFIG_LIST_SEVERITIES)),
            "class": self._safe_choice(self.c(self.CONFIG_LIST_CLASSES)),
            "target_class": self._safe_choice(self.c(self.CONFIG_LIST_TARGET_CLASSES)),
            "node_sw": self._safe_choice(self.c(self.CONFIG_LIST_NODE_SWS)),
            "node_name": self._safe_choice(self.c(self.CONFIG_LIST_NODE_NAMES)),
            "node_type": self._random_set(self.c(self.CONFIG_LIST_NODE_TAGS), 0, 2),
        }

    def _save_message(self, msg_id, msg):
        """
        Save the given message into file. The message is first saved into temporary
        directory and then moved to target queue directory to make the messsage
        appear int target directory atomically.

        :param str msg_id: Message ID, will be used to generate the file name.
        :param msg: Message as JSON string.
        :return: Name of the file written.
        :rtype: str
        """
        tfn = os.path.join(self.c(self.CONFIG_TEMP_DIR), f"{msg_id}.idea")
        ifn = os.path.join(self.c(self.CONFIG_QUEUE_DIR), f"{msg_id}.idea")

        with open(tfn, "w", encoding="utf8") as imf:
            imf.write(msg)

        if tfn != ifn:
            os.rename(tfn, ifn)
        return ifn
