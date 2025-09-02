#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


import difflib
import json
import unittest
from pprint import pprint
from unittest.mock import Mock, call

import mentat.services.eventstorage
from mentat.daemon.component.storage import StorageDaemonComponent

mentat.services.eventstorage.init(
    {
        "__core__database": {
            "eventstorage": {
                "dbname": "mentat_utest",
                "user": "mentat",
                "password": "mentat",
                "host": "localhost",
                "port": 5432,
            }
        }
    }
)


class TestMentatDaemonStorage(unittest.TestCase):
    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    #
    # Test IDEA message in raw form.
    #
    idea_raw = {
        "Category": ["Attempt.Login"],
        "Target": [
            {
                "Proto": ["tcp", "ssh"],
                "IP4": ["195.113.165.128/25"],
                "Port": ["22"],
                "Anonymised": True,
            }
        ],
        "ID": "4dd7cf5e-4a95-49f6-8f04-947de998012c",
        "WinStartTime": "2016-06-21 11:55:02Z",
        "ConnCount": 2,
        "Source": [{"IP4": ["188.14.166.39"]}],
        "Note": "SSH login attempt",
        "Node": [
            {"Type": ["Relay"], "Name": "cz.cesnet.mentat.warden_filer"},
            {
                "SW": ["Kippo"],
                "AggrWin": "00:05:00",
                "Name": "cz.uhk.apate.cowrie",
                "Type": ["Connection", "Honeypot", "Recon"],
            },
        ],
        "_Mentat": {"StorageTime": "2016-06-21T14:00:07Z"},
        "WinEndTime": "2016-06-21 12:00:02Z",
        "Format": "IDEA0",
        "DetectTime": "2016-06-21 13:08:27Z",
    }

    def _clear_database(self):
        """
        Helper method, clear all contents of test event table.
        """
        storage = mentat.services.eventstorage.service()
        storage.database_drop()
        storage.database_create()

    def _build_daemon_mock(self):
        """
        Helper method, build and return daemon mock object.
        """
        daemon = Mock(
            config={
                "__core__database": {
                    "eventstorage": {
                        "dbname": "mentat_utest",
                        "user": "mentat",
                        "password": "mentat",
                        "host": "localhost",
                        "port": 5432,
                    }
                }
            }
        )
        daemon.attach_mock(
            Mock(
                # Define required configuration values in order they are required
                # from daemon instance (ussually in setup() method).
                side_effect=[
                    True,
                    5,
                    1,
                ]
            ),
            "c",
        )
        return daemon

    # ---------------------------------------------------------------------------

    def setUp(self):
        self._clear_database()

        self.obj = StorageDaemonComponent()

    def test_01_setup(self):
        """
        Perform the component setup tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock()

        # Setup daemon component.
        self.obj.setup(daemon)
        if self.verbose:
            pprint(daemon.mock_calls)

        daemon.logger.assert_has_calls(
            [
                call.debug("[STATUS] Component 'storage': Set up event storage service."),
                call.info("[STATUS] Component 'storage': Using bulk commits with '5' as enforced commit interval"),
                call.info("[STATUS] Component 'storage': Using bulk commits with '1' as bulk commit threshold"),
            ]
        )

    def test_02_process_internal(self):
        """
        Perform the mentat.idea.internal.Idea message processing tests.
        """
        self.maxDiff = None

        # Prepare mock object representing external daemon object.
        daemon = self._build_daemon_mock()

        # Setup daemon component.
        self.obj.setup(daemon)
        if self.verbose:
            pprint(daemon.mock_calls)

        # Setup was already tested, so reset the mock for less clutter.
        daemon.reset_mock()

        # This daemon component is expected to work with messages of either
        # mentat.idea.internal.Idea, or idea.lite.Idea class.
        idea_msg = mentat.idea.internal.Idea(self.idea_raw)
        idea_id = idea_msg["ID"]

        # Perform the actual processing.
        result = self.obj.cbk_event_message_process(
            daemon,
            {
                "id": f"{idea_id}.idea",
                "idea_id": idea_id,
                "data": json.dumps(self.idea_raw, sort_keys=True),
                "idea": idea_msg,
            },
        )
        if self.verbose:
            pprint(result)
            pprint(daemon.mock_calls)
        daemon.logger.assert_has_calls(
            [
                call.debug(
                    "Component 'storage': Storing message '4dd7cf5e-4a95-49f6-8f04-947de998012c.idea':'4dd7cf5e-4a95-49f6-8f04-947de998012c'."
                ),
                call.info(
                    "Component 'storage': Stored message '4dd7cf5e-4a95-49f6-8f04-947de998012c.idea':'4dd7cf5e-4a95-49f6-8f04-947de998012c' into database (bulk mode)."
                ),
            ]
        )

        #
        # Attempt to retrieve the message back from database, convert and compare.
        #
        storage = mentat.services.eventstorage.service()
        idea_out = storage.fetch_event(idea_id)
        if self.verbose:
            print("'mentat.idea.internal.Idea' out of PostgreSQL record based on 'mentat.idea.internal.Idea':")
            print(json.dumps(idea_out, indent=4, sort_keys=True, default=idea_out.json_default))
        orig = json.dumps(idea_msg, indent=4, sort_keys=True, default=idea_msg.json_default)
        new = json.dumps(idea_out, indent=4, sort_keys=True, default=idea_out.json_default)
        self.assertEqual(orig, new, list(difflib.context_diff(orig.split("\n"), new.split("\n"))))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
