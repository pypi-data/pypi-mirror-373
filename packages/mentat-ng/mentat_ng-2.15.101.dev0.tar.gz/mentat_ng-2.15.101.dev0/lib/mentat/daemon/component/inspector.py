#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Daemon component providing simple yet powerfull message processing tools
based on performing conditional actions according to list of filtering
rules.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.

.. _subsubsection-configuration:

Setup configuration
^^^^^^^^^^^^^^^^^^^


This daemon component requires that following configurations are provided by
external daemon:

inspection_rules
    List of inspection rules. See section :ref:`subsubsection-inspection-rules`
    below for more information about available actions.

fallback_actions
    List of fallback actions. See section :ref:`subsubsection-inspection-actions`
    below for more information about available actions.


.. _subsubsection-inspection-rules:

Inspection rules
^^^^^^^^^^^^^^^^

Inspection rules define what actions should be performed with what messages.
Every inspection rule may have following attributes:

rule
    Filtering rule compatible with ransack library. All
    messages will be compared to this rule and actions will be performed with those
    that match.

    (``string``, **mandatory**)

name
    Optional name for the rule to be used in logs and other user output. This should
    be something brief and meaningfull to uniquelly identify the rule. When not set
    this defaults to **rule** attribute.

    (``string``, *optional*)

description
    Optional user description of the meaning of the rule. When not set defaults to ``???``.

    (``string``, *optional*)

final
    Boolean flag indicating the rule is final and all subsequent rules should not be
    considered. When not set defaults to ``False``.

    (``boolean``, *optional*)


enabled
    Boolean flag indicating the rule is enabled or disabled. When not set defaults
    to ``True``.

    (``boolean``, *optional*)

actions
    List of inspection action to be performed upon filter match. See section
    :ref:`subsubsection-inspection-actions` for more details.


.. _subsubsection-inspection-actions:

Inspection actions
^^^^^^^^^^^^^^^^^^

Every action has following common attributes:

action
    Type of the action. See below for list of all currently available actions.

    (``string``, **mandatory**)

name
    Optional name for the action to be used in logs and other user output. This should
    be something brief and meaningfull to uniquelly identify the action. When not set
    this defaults to **action** attribute.

    (``string``, *optional*)

description
    Optional user description of the meaning of the action. When not set defaults to ``???``.

    (``string``, *optional*)

enabled
    Boolean flag indicating the action is enabled or disabled. When not set defaults
    to ``True``.

    (``boolean``, *optional*)

args
    Dictionary of additional arguments for the action. The appropriate arguments
    are specific for particular action. See below for more information for each
    action.

    (``dict``, *optional*)

There are following inspection actions, that can be performed with matching messages
or as fallback action:

tag
    Tag the corresponding message at given JPath with given value. The tag value
    may be only constant value.

    *Arguments:*

    * **path** - JPath to be set (``string``, **mandatory**)
    * **value** - value to be set (``any``, **mandatory**)
    * **overwrite** - flag indicating whether existing value should be overwritten, or not, defaults to ``True`` (``boolean``, *optional*)
    * **unique** - flag indicating whether value should be unique, or not, defaults to ``False`` (``boolean``, *optional*)

set
    Set the corresponding message at given JPath with result of given expression.
    The expression must be compatible with ransack language.

    *Arguments:*

    * **path** - JPath to be set (``string``, **mandatory**)
    * **expression** - ransack compatible expression to be set (``string``, **mandatory**)
    * **overwrite** - flag indicating whether existing value should be overwritten, or not, defaults to ``True`` (``boolean``, *optional*)
    * **unique** - flag indicating whether value should be unique, or not, defaults to ``False`` (``boolean``, *optional*)

report
    Report the corresponding message via email.

    *Arguments:*

    * **to** - recipient email address (``string``, **mandatory**)
    * **from** - sender email address (``string``, **mandatory**)
    * **subject** - email report subject (``string``, **mandatory**)
    * **report_type** - email report type, will be inserted into ``X-Cesnet-Report-Type`` email header (``string``, **mandatory**)

    .. todo::
        Finish usage of default arguments and then update this documentation. Currently every argument is mandatory, which makes users repeat themselves.

drop
    Drop the corresponding message from processing (filter out).

    *This action currently does not have any arguments.*

dispatch
    Dispatch (move) the corresponding message into another queue directory.

    *Arguments:*

    * **queue_tgt** - path to target queue (``string``, **mandatory**)

duplicate
    Duplicate (copy) the corresponding message into another queue directory.

    *Arguments:*

    * **queue_tgt** - path to target queue (``string``, **mandatory**)

log
    Log the corresponding message into daemon module log.

    *Arguments:*

    * **label** - log message label, defaults to ``Inspection rule matched`` (``string``, **optional**)

"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime
import pprint
import traceback

from sqlalchemy import select
from sqlalchemy.sql import func

import pyzenkit.baseapp
import pyzenkit.zendaemon
from ransack import Filter, Parser

import mentat.const
import mentat.services.sqlstorage
from mentat.datatype.sqldb import EventClassModel, EventClassState
from mentat.idea.internal import (
    JPATH_RC_VALUE_DUPLICATE,
    JPATH_RC_VALUE_EXISTS,
    JPATH_RC_VALUE_SET,
    jpath_set,
)


class InspectorDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    ZenDaemonComponent encapsulating ransack library.
    """

    EVENT_MSG_PROCESS = "message_process"
    EVENT_LOG_STATISTICS = "log_statistics"

    STATS_CNT_TAGGED = "cnt_tagged"
    STATS_CNT_SET = "cnt_set"
    STATS_CNT_REPORTED = "cnt_reported"
    STATS_CNT_DROPPED = "cnt_dropped"
    STATS_CNT_DISPATCHED = "cnt_dispatched"
    STATS_CNT_DUPLICATED = "cnt_duplicated"
    STATS_CNT_LOGGED = "cnt_logged"
    STATS_CNT_FALLBACKS = "cnt_fallbacks"
    STATS_CNT_ERRORS = "cnt_errors"
    STATS_COUNTERS = "counters"

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get("cid", "inspector")

        self.default_action_args = {
            "tag": {"overwrite": True, "unique": False},
            "set": {"overwrite": True, "unique": False},
        }

        self.inspection_rules_key = kwargs.get("inspection_rules_key", "inspection_rules")
        self.fallback_actions_key = kwargs.get("fallback_actions_key", "fallback_actions")
        self.add_event_class_rules_key = kwargs.get("add_event_class_rules_key", "add_event_class_rules")

        self.inspection_rules = None
        self.fallback_actions = None
        self.inspection_rules_cfg = None
        self.fallback_actions_cfg = None

        self.parser = Parser()
        self.filter = Filter()

        # Permit changing of default event mapping
        self.event_map = kwargs.get(
            "event_map",
            {
                self.EVENT_MSG_PROCESS: self.EVENT_MSG_PROCESS,
                self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS,
            },
        )

        self.statistics_cur[self.STATS_COUNTERS] = {}

        self.sqlstorage_manager = None

        self.should_do_db_checks = False
        self.last_db_check = None
        self.last_db_update_and_count = None

    def get_event_classes(self):
        """
        Returns a list of all enabled event classes.
        """
        return (
            self.sqlstorage_manager.service()
            .session.query(EventClassModel)
            .filter(EventClassModel.state != EventClassState.DISABLED)
            .all()
        )

    def get_last_event_class_update_and_count(self):
        """
        Returns tuple including date of the last event class
        table update, and count of all tables.
        Count of all tables must be considered in case one of the
        event classes is removed, which would not be mirrored
        in the last update date.
        """
        select_max_update = select(func.max(EventClassModel.last_update))  # pylint: disable=locally-disabled,not-callable
        max_update = self.sqlstorage_manager.service().session.scalars(select_max_update).first()
        select_count = select(func.count(EventClassModel.id))  # pylint: disable=locally-disabled,not-callable
        count = self.sqlstorage_manager.service().session.scalars(select_count).first()
        return (max_update, count)

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                "event": self.event_map[self.EVENT_MSG_PROCESS],
                "callback": self.cbk_event_message_process,
                "prepend": False,
            },
            {
                "event": self.event_map[self.EVENT_LOG_STATISTICS],
                "callback": self.cbk_event_log_statistics,
                "prepend": False,
            },
        ]

    def _setup_action_args(self, action, args):
        """
        Setup default action arguments.
        """
        if action in self.default_action_args:
            for arg_name, arg_val in self.default_action_args[action].items():
                if arg_name not in args:
                    args[arg_name] = arg_val

        if action == "set":
            args["expressionc"] = self.parser.parse(args["expression"])

        return args

    def _setup_action(self, daemon, action, rule=None):
        """
        Setup configuration structure for single action.
        """
        acth = "rule_action_{}".format(action["action"])
        if not hasattr(self, acth) or not callable(getattr(self, acth)):
            if rule:
                raise pyzenkit.zendaemon.ZenDaemonComponentException(
                    "Unknown inspection rule action '{}':'{}'".format(rule, action["action"])
                )

            raise pyzenkit.zendaemon.ZenDaemonComponentException(
                "Unknown fallback action '{}'".format(action["action"])
            )

        act = {}
        act["action"] = action.get("action")
        act["name"] = action.get("name", action["action"])
        act["description"] = action.get("description", "???")
        act["actionh"] = acth
        act["enabled"] = action.get("enabled", True)
        act["args"] = action.get("args", {})

        if not act["enabled"]:
            if rule:
                daemon.logger.info(
                    "[STATUS] Component '{}': Inspection rule action '{}':'{}' is disabled in the configuration and will be skipped".format(
                        self.cid, rule, act["name"]
                    )
                )
            else:
                daemon.logger.info(
                    "[STATUS] Component '{}': Fallback action '{}' is disabled in the configuration and will be skipped".format(
                        self.cid, act["name"]
                    )
                )
            return None

        act["args"] = self._setup_action_args(act["action"], act["args"])

        if rule:
            daemon.logger.info(
                "[STATUS] Component '{}': Inspection rule action '{}':'{}' successfully loaded".format(
                    self.cid, rule, act["name"]
                )
            )
        else:
            daemon.logger.info(
                "[STATUS] Component '{}': Fallback action '{}' successfully loaded".format(self.cid, act["name"])
            )
        return act

    def _setup_rule(self, daemon, rule):
        """
        Setup configuration structure for single rule.
        """
        newr = {}
        newr["rule"] = rule.get("rule")
        newr["name"] = rule.get("name", rule["rule"])
        newr["description"] = rule.get("description", "???")
        newr["final"] = rule.get("final", False)
        newr["enabled"] = rule.get("enabled", True)

        if not newr["enabled"]:
            daemon.logger.info(
                "[STATUS] Component '{}': Inspection rule '{}' is disabled in the configuration and will be skipped".format(
                    self.cid, newr["name"]
                )
            )
            return None

        tree = self.parser.parse(rule["rule"])
        newr["ransack_rule"] = tree

        newr["actions"] = []
        for action in rule["actions"]:
            # Action may be disabled by configuration option 'enabled'.
            # In that case _setup_action() returns none.
            act = self._setup_action(daemon, action, newr["name"])
            if act:
                newr["actions"].append(act)

        daemon.logger.info(
            "[STATUS] Component '{}': Inspection rule '{}' successfully loaded".format(self.cid, newr["name"])
        )
        return newr

    def setup_inspection_rules(self, daemon):
        """
        Performs inspection rules setup.
        This method can also be called later in case the inspection
        rules need to be reloaded.
        """
        self.inspection_rules = []
        self.inspection_rules_cfg = daemon.c(self.inspection_rules_key)

        if self.inspection_rules_cfg:
            daemon.dbgout(
                f"[STATUS] Component '{self.cid}': Loading inspection rules {pprint.pformat(self.inspection_rules_cfg)}"
            )

        # Add rules for event class assignment, if it is enabled.
        event_class_rules = []
        if daemon.c(self.add_event_class_rules_key):
            self.should_do_db_checks = True
            self.last_db_check = datetime.datetime.now()
            if self.last_db_update_and_count is None:
                self.last_db_update_and_count = self.get_last_event_class_update_and_count()
            for event_class in self.get_event_classes():
                event_class_rules.extend(event_class.get_inspection_rules())

        for rule in self.inspection_rules_cfg + event_class_rules:
            try:
                # Rule may be disabled by configuration option 'enabled'.
                # In that case _setup_rule() returns none.
                res = self._setup_rule(daemon, rule)
                if res:
                    self.inspection_rules.append(res)
            except:  # pylint: disable=locally-disabled,bare-except
                daemon.logger.warning(
                    "[STATUS] Component '{}': Unable to load inspection rule '{}': '{}'".format(
                        self.cid,
                        rule.get("name", rule.get("rule", "__NORULE__")),
                        traceback.format_exc(),
                    )
                )

    def setup(self, daemon):
        """
        Perform component setup.
        """
        #
        # Setup inspection rules
        #
        self.sqlstorage_manager = mentat.services.sqlstorage.StorageServiceManager(daemon.config)
        self.setup_inspection_rules(daemon)

        #
        # Setup fallback actions
        #
        self.fallback_actions = []
        self.fallback_actions_cfg = daemon.c(self.fallback_actions_key)
        if self.fallback_actions_cfg:
            daemon.dbgout(
                f"[STATUS] Component '{self.cid}': Loading fallback actions {pprint.pformat(self.fallback_actions_cfg)}"
            )
            for action in self.fallback_actions_cfg:
                try:
                    act = self._setup_action(daemon, action)
                    if act:
                        self.fallback_actions.append(act)
                except:  # pylint: disable=locally-disabled,bare-except
                    daemon.logger.warning(
                        "[STATUS] Component '{}': Unable to load fallback action '{}': '{}'".format(
                            self.cid,
                            action.get("action", "__NOACTION__"),
                            traceback.format_exc(),
                        )
                    )

        if not self.inspection_rules:
            raise pyzenkit.zendaemon.ZenDaemonComponentException(
                "Empty inspection rule list, perhaps you do not need inspection daemon after all"
            )

    # ---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Perform inspection of given message.
        """
        # Reload event classes when DB table was updated.
        if self.should_do_db_checks:
            # Check database changes only every X seconds (based on constant INSPECTOR_DB_CHECK_INTERVAL in mentat.const).
            if (
                self.last_db_check + datetime.timedelta(seconds=mentat.const.INSPECTOR_DB_CHECK_INTERVAL)
                < datetime.datetime.now()
            ):
                self.last_db_check = datetime.datetime.now()
                last_update_and_count = self.get_last_event_class_update_and_count()
                if last_update_and_count != self.last_db_update_and_count:
                    self.setup_inspection_rules(daemon)
                    daemon.logger.debug("Successfully updated rules because the event class table was updated.")

        daemon.logger.debug(
            "Component '{}': Inspecting message '{}':'{}'".format(self.cid, args["id"], args["idea_id"])
        )
        try:
            matches = 0
            result_flag = daemon.FLAG_CONTINUE
            for rule in self.inspection_rules:
                if self.filter.eval(rule["ransack_rule"], args["idea"]) is True:
                    daemon.logger.info(
                        "Component '{}': Message '{}':'{}' matched inspection rule '{}'".format(
                            self.cid, args["id"], args["idea_id"], rule["name"]
                        )
                    )
                    self.statistics_cur[self.STATS_COUNTERS][rule["name"]] = (
                        self.statistics_cur[self.STATS_COUNTERS].get(rule["name"], 0) + 1
                    )
                    matches = matches + 1
                    for action in rule["actions"]:
                        actioncbk = getattr(self, action["actionh"])
                        action_result = actioncbk(
                            daemon,
                            args["id"],
                            args["idea_id"],
                            args["idea"],
                            action,
                            rule,
                        )
                        if action_result == daemon.FLAG_STOP:
                            result_flag = daemon.FLAG_STOP
                    if rule.get("final"):
                        break
                else:
                    daemon.logger.debug(
                        "Component '{}': Message '{}':'{}' missed inspection rule '{}'".format(
                            self.cid, args["id"], args["idea_id"], rule["name"]
                        )
                    )

            if not matches:
                self.inc_statistic(self.STATS_CNT_FALLBACKS)
                if self.fallback_actions:
                    daemon.logger.debug(
                        "Component '{}': Message '{}':'{}' missed all inspection rules, performing fallback actions".format(
                            self.cid, args["id"], args["idea_id"]
                        )
                    )
                    for action in self.fallback_actions:
                        actioncbk = getattr(self, action["actionh"])
                        action_result = actioncbk(daemon, args["id"], args["idea_id"], args["idea"], action)
                        if action_result == daemon.FLAG_STOP:
                            result_flag = daemon.FLAG_STOP
                else:
                    daemon.logger.debug(
                        "Component '{}': Message '{}':'{}' missed all inspection rules, no fallback actions to perform".format(
                            self.cid, args["id"], args["idea_id"]
                        )
                    )

            return (result_flag, args)
        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Message '{}':'{}' caused some trouble during processing: '{}'".format(
                    self.cid, args["id"], args["idea_id"], traceback.format_exc()
                )
            )
            daemon.queue.schedule("message_banish", args)
            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ""

        for k in [
            self.STATS_CNT_TAGGED,
            self.STATS_CNT_SET,
            self.STATS_CNT_REPORTED,
            self.STATS_CNT_DROPPED,
            self.STATS_CNT_DISPATCHED,
            self.STATS_CNT_DUPLICATED,
            self.STATS_CNT_LOGGED,
            self.STATS_CNT_FALLBACKS,
            self.STATS_CNT_ERRORS,
        ]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]["cnt"], stats[k]["inc"], stats[k]["spd"])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        stats_str = f"{stats_str}\n\t--- Filter stats ---"
        for k in stats[self.STATS_COUNTERS]:
            stats_str = "{}\n\t{:40s}  {:>12,d} ({:>+10,d}, {:>8,.2f} #/s)".format(
                stats_str,
                k,
                stats[self.STATS_COUNTERS][k]["cnt"],
                stats[self.STATS_COUNTERS][k]["inc"],
                stats[self.STATS_COUNTERS][k]["spd"],
            )

        daemon.logger.info(f"Component '{self.cid}': *** Processing statistics ***{stats_str}")
        return (daemon.FLAG_CONTINUE, args)

    # ---------------------------------------------------------------------------

    def rule_action_tag(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Tag given message according given arguments.
        """
        args = action["args"]
        res = jpath_set(
            message,
            args["path"],
            args["value"],
            overwrite=args["overwrite"],
            unique=args["unique"],
        )

        logargs = [
            self.cid,
            mid,
            args["path"],
            args["value"],
            args["overwrite"],
            args["unique"],
        ]

        if res == JPATH_RC_VALUE_SET:
            daemon.logger.debug(
                "Component '{}': Tag - Message '{}' path '{}':'{}' key successfully set (O:{} U:{})".format(*logargs)
            )
            daemon.queue.schedule("message_update", {"id": mid, "idea_id": iid, "idea": message})
        elif res == JPATH_RC_VALUE_EXISTS:
            daemon.logger.debug(
                "Component '{}': Tag - Message '{}' path '{}':'{}' key already exists, not overwriting (O:{} U:{})".format(
                    *logargs
                )
            )
        elif res == JPATH_RC_VALUE_DUPLICATE:
            daemon.logger.debug(
                "Component '{}': Tag - Message '{}' path '{}':'{}' value already exists, not inserting (O:{} U:{})".format(
                    *logargs
                )
            )

        self.inc_statistic(self.STATS_CNT_TAGGED)
        return daemon.FLAG_CONTINUE

    def rule_action_set(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Set given message key according given arguments.
        """
        args = action["args"]
        value = self.filter.eval(args["expressionc"], message)
        res = jpath_set(
            message,
            args["path"],
            value,
            overwrite=args["overwrite"],
            unique=args["unique"],
        )

        logargs = [
            self.cid,
            mid,
            args["path"],
            args["expression"],
            pprint.pformat(value),
            args["overwrite"],
            args["unique"],
        ]

        if res == JPATH_RC_VALUE_SET:
            daemon.logger.debug(
                "Component '{}': Set - Message '{}' path '{}':'{}'=>{} key successfully set (O:{} U:{})".format(
                    *logargs
                )
            )
            daemon.queue.schedule("message_update", {"id": mid, "idea_id": iid, "idea": message})
        elif res == JPATH_RC_VALUE_EXISTS:
            daemon.logger.debug(
                "Component '{}': Set - Message '{}' path '{}':'{}'=>{} key already exists, not overwriting (O:{} U:{})".format(
                    *logargs
                )
            )
        elif res == JPATH_RC_VALUE_DUPLICATE:
            daemon.logger.debug(
                "Component '{}': Set - Message '{}' path '{}':'{}'=>{} value already exists, not inserting (O:{} U:{})".format(
                    *logargs
                )
            )

        self.inc_statistic(self.STATS_CNT_SET)
        return daemon.FLAG_CONTINUE

    def rule_action_report(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Report given message according given arguments.
        """
        args = action["args"]

        daemon.logger.debug(
            "Component '{}': Report - Message '{}' to '{}' with subject '{}'".format(
                self.cid, mid, args["to"], args["subject"]
            )
        )
        daemon.queue.schedule(
            "email_send_idea",
            {
                "id": mid,
                "idea_id": iid,
                "idea": message,
                "rule": rule,
                "to": args["to"],
                "from": args["from"],
                "subject": args["subject"],
                "report_type": args["report_type"],
            },
        )

        self.inc_statistic(self.STATS_CNT_REPORTED)
        return daemon.FLAG_CONTINUE

    def rule_action_drop(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Drop given messsage from processing.
        """
        args = action["args"]

        label = args.get("label", "Inspection rule matched")
        daemon.logger.debug(f"Component '{self.cid}': Drop - Message '{mid}':'{iid}': '{label}'")
        daemon.queue.schedule("message_cancel", {"id": mid, "idea_id": iid})

        self.inc_statistic(self.STATS_CNT_DROPPED)
        return daemon.FLAG_STOP

    def rule_action_dispatch(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Dispatch given message into given target queue.
        """
        args = action["args"]

        daemon.logger.debug(
            "Component '{}': Dispatch - Message '{}' to target queue '{}'".format(self.cid, mid, args["queue_tgt"])
        )
        daemon.queue.schedule(
            "message_dispatch",
            {"id": mid, "idea_id": iid, "queue_tgt": args["queue_tgt"]},
        )

        self.inc_statistic(self.STATS_CNT_DISPATCHED)
        return daemon.FLAG_STOP

    def rule_action_duplicate(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Duplicate given message into given target queue.
        """
        args = action["args"]

        daemon.logger.debug(
            "Component '{}': Duplicate - Message '{}' to target queue '{}'".format(self.cid, mid, args["queue_tgt"])
        )
        daemon.queue.schedule(
            "message_duplicate",
            {"id": mid, "idea_id": iid, "queue_tgt": args["queue_tgt"]},
        )

        self.inc_statistic(self.STATS_CNT_DUPLICATED)
        return daemon.FLAG_CONTINUE

    def rule_action_log(self, daemon, mid, iid, message, action, rule=None):  # pylint: disable=locally-disabled,too-many-arguments,unused-argument
        """
        Log matching message with warning severity.
        """
        args = action["args"]
        label = args.get("label", "Inspection rule matched")

        daemon.logger.warning(f"Component '{self.cid}': Log - Message '{mid}':'{iid}': '{label}'")

        self.inc_statistic(self.STATS_CNT_LOGGED)
        return daemon.FLAG_CONTINUE
