#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.event` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import os
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import MagicMock, Mock, call

from ransack import get_values

import mentat.const
import mentat.idea.internal
import mentat.reports.event
import mentat.reports.utils
import mentat.services.eventstorage
import mentat.services.sqlstorage
from mentat.const import EventSections
from mentat.datatype.sqldb import (
    DetectorModel,
    EventClassModel,
    EventClassState,
    EventReportModel,
    FilterModel,
    GroupModel,
    NetworkModel,
    SettingsReportingModel,
)
from mentat.reports.aggregations import EventAggregator
from mentat.reports.data import DetectorData, ReportingProperties
from mentat.reports.tests.fixtures import EVENTS_OBJ

# -------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
# -------------------------------------------------------------------------------

REPORTS_DIR = "/var/tmp"


class TestMentatReportsEvent(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.event` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    template_vars = {
        "report_access_url": "https://URL/view=",
        "contact_email": "EMAIL1",
        "admin_email": "EMAIL2",
    }

    def setUp(self):
        """
        Perform test case setup.
        """
        self.sqlstorage = mentat.services.sqlstorage.StorageService(
            url="postgresql://mentat:mentat@localhost/mentat_utest", echo=False
        )
        self.sqlstorage.database_drop()
        self.sqlstorage.database_create()

        self.eventstorage = mentat.services.eventstorage.EventStorageService(
            dbname="mentat_utest",
            user="mentat",
            password="mentat",
            host="localhost",
            port=5432,
        )
        self.eventstorage.database_drop()
        self.eventstorage.database_create()
        for event in EVENTS_OBJ:
            event["_Mentat"]["StorageTime"] = datetime.datetime.utcnow()
            self.eventstorage.insert_event(event)

        group = GroupModel(name="abuse@cesnet.cz", source="manual", description="CESNET, z.s.p.o.")
        groups_dict = {"abuse@cesnet.cz": group}

        FilterModel(
            group=group,
            name="FLT1",
            source_based=True,
            type="basic",
            filter='Node.Name contains "org.example.kippo_honey"',
            description="DESC1",
            enabled=True,
        )
        FilterModel(
            group=group,
            name="FLT2",
            source_based=True,
            type="basic",
            filter="Source.IP4 in [10.0.0.0/24]",
            description="DESC2",
            enabled=True,
        )
        FilterModel(
            group=group,
            name="FLT3",
            source_based=True,
            type="basic",
            filter="Source.IP4 IN [10.0.1.0/28]",
            description="DESC3",
            enabled=True,
        )
        NetworkModel(group=group, netname="UNET1", source="manual", network="10.0.0.0/8")
        SettingsReportingModel(group=group)

        det1 = DetectorModel(name="org.example.kippo_honey", source="manual", credibility=0.72, hits=12)
        det2 = DetectorModel(name="org.example.dionaea", source="manual", credibility=0.36, hits=121)

        ec1 = EventClassModel(
            name="recon-scanning",
            source_based=True,
            label_en="The machine performed some type of active scanning.",
            label_cz="Stroj se pokoušel o nějakou formu aktivního skenování.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning",
            displayed_main=["ConnCount", "FlowCount", "protocols", "Ref"],
            displayed_source=["Port"],
            displayed_target=["Port", "ips", "Hostname"],
            rule="Category in ['Recon.Scanning']",
            severity="low",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        # Test event class that should render everything.
        ec2 = EventClassModel(
            name="test-event-class",
            source_based=False,
            label_en="Test report.",
            label_cz="Testovací report.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/test-event-class",
            displayed_main=[field.name for field in (DetectorData.get_all_fields_for_view(EventSections.MAIN))],
            displayed_source=[field.name for field in (DetectorData.get_all_fields_for_view(EventSections.SOURCE))],
            displayed_target=[field.name for field in (DetectorData.get_all_fields_for_view(EventSections.TARGET))],
            rule="Node.Name == org.example.kippo_honey",
            severity="low",
            subclassing="",
            state=EventClassState.ENABLED,
        )
        ec3 = EventClassModel(
            name="recon-scanning-target",
            source_based=False,
            label_en="Your IP range was scanned.",
            label_cz="Váš IP rozsah byl skenován.",
            reference="https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning-target",
            displayed_main=["ConnCount", "FlowCount", "protocols", "Ref"],
            displayed_source=["ips", "Port"],
            displayed_target=["Port", "ips", "Hostname"],
            rule="Category in ['Recon.Scanning']",
            severity="low",
            subclassing="",
            state=EventClassState.ENABLED,
        )

        for obj in [group, det1, det2, ec1, ec2, ec3]:
            self.sqlstorage.session.add(obj)
        self.sqlstorage.session.commit()

        self.reporting_settings = mentat.reports.utils.ReportingSettings(group, self.sqlstorage)
        settings_dict = {"abuse@cesnet.cz": self.reporting_settings}

        def lookup_mock(src, getall=False):
            if str(src).startswith("10."):
                return [{"abuse_group": "abuse@cesnet.cz", "is_base": False}]
            return []

        whoismodule_mock = mentat.services.whois.WhoisModule()
        whoismodule_mock.lookup = MagicMock(side_effect=lookup_mock)

        self.reporter = mentat.reports.event.EventReporter(
            Mock(),
            REPORTS_DIR,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../conf/templates/reporter")),
            [],
            "en",
            "UTC",
            self.eventstorage,
            self.sqlstorage,
            mailer=None,
            groups_dict=groups_dict,
            settings_dict=settings_dict,
            whoismodule=whoismodule_mock,
        )

    def tearDown(self):
        self.sqlstorage.session.close()
        self.sqlstorage.database_drop()
        self.eventstorage.database_drop()

    def test_01_save_to_json_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_json_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = "utest-security-report.json"
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_json_files(  # pylint: disable=locally-disabled,protected-access
                EVENTS_OBJ, report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

        # Test saving file with timestamp information.
        report_file = "utest-security-report-M20180726SL-HT9TC.json"
        report_path = os.path.join(REPORTS_DIR, "20180726", report_file)

        self.assertEqual(
            self.reporter._save_to_json_files(  # pylint: disable=locally-disabled,protected-access
                EVENTS_OBJ, report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

    def test_02_save_to_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = "utest-security-report.txt"
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_files(  # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT", report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

        # Test saving file with timestamp information.
        report_file = "utest-security-report-M20180726SL-HT9TC.txt"
        report_path = os.path.join(REPORTS_DIR, "20180726", report_file)

        self.assertEqual(
            self.reporter._save_to_files(  # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT", report_file
            ),
            (report_path, f"{report_path}.zip"),
        )
        self.assertTrue(os.path.isfile(report_path))
        self.assertTrue(os.path.isfile(f"{report_path}.zip"))
        os.unlink(report_path)
        os.unlink(f"{report_path}.zip")

    def test_03_filter_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.filter_events` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.sqlstorage.session.commit()
        reporting_properties = ReportingProperties(
            abuse_group, "low", datetime.datetime.now(), datetime.datetime.now(), is_target=False
        )

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, EVENTS_OBJ)
        self.assertEqual(fltlog, {"FLT1": 1, "FLT2": 1, "FLT3": 1})
        self.assertEqual(flt_cnt, 1)
        for events in aggr.values():
            self.assertEqual(len(events), 1)
        self.reporter.logger.assert_has_calls(
            [
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT1",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg01"),
                call.debug("Event matched filtering rules, all sources filtered"),
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT2",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg02"),
                call.debug(
                    "Event matched filtering rule '%s' of group %s.",
                    "FLT3",
                    "abuse@cesnet.cz",
                ),
                call.debug("Discarding event with ID '%s' from reports.", "msg02"),
            ]
        )
        self.sqlstorage.session.commit()

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, EVENTS_OBJ)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == "FLT1").one()
        self.assertEqual(flt1.hits, 2)

        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, EVENTS_OBJ)
        events, aggr, fltlog, flt_cnt = self.reporter.filter_events(reporting_properties, EVENTS_OBJ)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == "FLT1").one()
        self.assertEqual(flt1.hits, 4)

        self.assertEqual(len(list(aggr.values())), 1)
        aggr_value = list(aggr.values())[0]
        aggr_result = EventAggregator.aggregate_source(aggr_value)
        self.assertEqual(sorted(aggr_result.keys()), ["recon-scanning"])
        self.assertEqual(list(aggr_result["recon-scanning"].keys()), ["10.0.2.1"])

    def test_04_fetch_severity_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.fetch_severity_events` function.
        """
        self.maxDiff = None

        group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        self.sqlstorage.session.commit()

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg01", "msg02"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "medium",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                is_target=False,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg02"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "medium",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], ["msg01"])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "high",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() + datetime.timedelta(seconds=7200),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

        events = self.reporter.fetch_severity_events(
            ReportingProperties(
                group,
                "low",
                datetime.datetime.utcnow() - datetime.timedelta(seconds=7200),
                datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                is_target=True,
            )
        )
        self.assertEqual([x["ID"] for x in events], [])

    def test_06_render_report_summary(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_summary` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()

        report = self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_SUMMARY)
        # Test if it can be added to the database without errors.
        self.sqlstorage.session.add(report)

        report_txt = self.reporter.render_report(
            report,
            self.reporting_settings,
            self.template_vars,
            ["file1.json"],
        )
        if self.verbose:
            print("\n---\nSUMMARY REPORT IN EN:\n---\n")
            print(report_txt)

        # Check the whole content of the rendered report. The expected file can
        # be found in the "tests" submodule.
        self.assertEqual(
            self._clean_trailing_whitespaces(report_txt),
            self._load_expected_report_text("expected_summary_report_en.txt", report),
        )

        # Check Czech translations.
        self.reporting_settings.locale = "cs"
        self.reporting_settings.timezone = "Europe/Prague"

        report_txt = self.reporter.render_report(
            report,
            self.reporting_settings,
            self.template_vars,
            ["file1.json"],
        )
        if self.verbose:
            print("\n---\nSUMMARY REPORT IN CS:\n---\n")
            print(report_txt)

        # Check the whole content of the rendered report. The expected file can
        # be found in the "tests" submodule.
        self.assertEqual(
            self._clean_trailing_whitespaces(report_txt),
            self._load_expected_report_text("expected_summary_report_cz.txt", report),
        )

    def test_07_render_report_extra(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_extra` function.
        """

        def render_extra_report(events, locale="en", timezone="UTC"):
            if locale:
                self.reporting_settings.locale = locale
            if timezone:
                self.reporting_settings.timezone = timezone

            mock_report = self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_EXTRA, events)
            self.sqlstorage.session.add(mock_report)
            report_txt = self.reporter.render_report(
                mock_report, self.reporting_settings, self.template_vars, "192.168.1.1"
            )
            if self.verbose:
                print(f"\n---\nEXTRA REPORT IN {locale or 'en'}:\n---\n")
                print(report_txt)
            return report_txt, mock_report

        self.maxDiff = None
        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()

        report_txt_testclass_en, report_testclass_en = render_extra_report(EVENTS_OBJ[0:1])
        report_txt_scanning_en, report_scanning_en = render_extra_report(EVENTS_OBJ[1:2])
        # Check the whole content of the rendered reports. The expected files can
        # be found in the "tests" submodule.
        self.assertEqual(
            self._clean_trailing_whitespaces(report_txt_testclass_en),
            self._load_expected_report_text("expected_extra_report_en_testclass.txt", report_testclass_en),
        )
        self.assertEqual(
            self._clean_trailing_whitespaces(report_txt_scanning_en),
            self._load_expected_report_text("expected_extra_report_en_scanning.txt", report_scanning_en),
        )

        # Check Czech translations.
        report_txt_scanning_cz, _report = render_extra_report(EVENTS_OBJ[1:2], "cs", "Europe/Prague")
        self.assertTrue(report_txt_scanning_cz)
        self.assertEqual(report_txt_scanning_cz.split("\n")[0], "Vážení kolegové,")
        self.assertIn(
            "[1] Stroj se pokoušel o nějakou formu aktivního skenování.",
            report_txt_scanning_cz,
        )
        self.assertIn("První událost:", report_txt_scanning_cz)
        self.assertIn("2018-01-01 13:00:00 Z", report_txt_scanning_cz)
        self.assertIn("Cílové IP adresy", report_txt_scanning_cz)
        self.assertIn("Detaily z detektoru org.example.dionaea:", report_txt_scanning_cz)
        self.assertIn("------------------------------------------------", report_txt_scanning_cz)

    def test_08_render_report_target(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_target` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()
        mock_report = self._generate_mock_report(
            abuse_group,
            "low",
            mentat.const.REPORT_TYPE_TARGET,
            EVENTS_OBJ[1:2],
            True,
        )
        # Test if it can be added to the database without errors.
        self.sqlstorage.session.add(mock_report)

        report_txt = self.reporter.render_report(
            mock_report, self.reporting_settings, self.template_vars, "192.168.1.1"
        )
        if self.verbose:
            print("\n---\nTARGET REPORT (en):\n---\n")
            print(report_txt)

        # Check the whole content of the rendered report. The expected file can
        # be found in the "tests" submodule.
        self.assertEqual(
            self._clean_trailing_whitespaces(report_txt),
            self._load_expected_report_text("expected_target_report_en.txt", mock_report),
        )

    def test_09_get_structured_data_as_dataclass(self):
        """
        Test :py:class:`mentat.datatype.sqldb.EventReportModel.get_structured_data_as_dataclass` function.
        """
        self.maxDiff = None
        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == "abuse@cesnet.cz").one()

        report = self._generate_mock_report(abuse_group, "low", mentat.const.REPORTING_MODE_SUMMARY)

        # Check if function get_structured_data_as_dataclass does not change anything.
        structured_data_obj = report.get_structured_data_as_dataclass()
        self.assertEqual(asdict(structured_data_obj), report.structured_data)

    def test_10_filter_events_by_credibility(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.filter_events_by_credibility` function.
        """
        self.maxDiff = None

        ev1 = Mock(mentat.idea.internal.Idea)
        ev1.get_detectors = Mock(return_value=["org.example.kippo_honey"])
        ev1.get_id = Mock(return_value="idea_event1")
        ev2 = Mock(mentat.idea.internal.Idea)
        ev2.get_detectors = Mock(return_value=["org.example.dionaea"])
        ev2.get_id = Mock(return_value="idea_event2")
        ev3 = Mock(mentat.idea.internal.Idea)
        ev3.get_detectors = Mock(return_value=["org.example.new_detector"])
        ev3.get_id = Mock(return_value="idea_event3")

        events = {"10.3.12.13": [ev1, ev2], "133.13.42.13": [ev2], "64.24.35.24": [ev3]}

        _events_aggr, blocked_cnt = self.reporter.filter_events_by_credibility(events)

        self.assertEqual(blocked_cnt, 1)
        self.assertEqual(_events_aggr, {"10.3.12.13": [ev1], "64.24.35.24": [ev3]})
        self.reporter.logger.assert_has_calls(
            [
                call.info("Discarding event with ID '%s'.", "idea_event2"),
                call.info(
                    "Event with ID '%s' contains unknown detector '%s'. Assuming full credibility.",
                    "idea_event3",
                    "org.example.new_detector",
                ),
            ]
        )

        _events_aggr, _ = self.reporter.filter_events_by_credibility({"133.13.42.13": [ev2]})
        self.assertFalse(_events_aggr)

        detectors = {det.name: det for det in self.sqlstorage.session.query(DetectorModel).all()}
        self.assertEqual(detectors["org.example.kippo_honey"].hits, 12)
        self.assertEqual(detectors["org.example.dionaea"].hits, 123)

    # ---------------------------------------------------------------------------

    def _generate_mock_report(self, abuse_group, severity, rtype, events=None, is_target=False):
        if not events:
            events = EVENTS_OBJ

        report = EventReportModel(
            groups=[abuse_group],
            severity=severity,
            type=rtype,
            dt_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
            dt_to=datetime.datetime.utcnow(),
            evcount_rep=len(events),
            evcount_all=len(events),
            evcount_flt=len(events),
            evcount_flt_blk=1,
            evcount_thr=len(events),
            evcount_thr_blk=0,
            evcount_rlp=0,
            filtering={"FLT01": 1},
        )
        report.generate_label()
        report.calculate_delta()

        if rtype == mentat.const.REPORTING_MODE_EXTRA:
            report.parent = EventReportModel(
                groups=[abuse_group],
                severity=severity,
                type=mentat.const.REPORTING_MODE_SUMMARY,
                dt_from=datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                dt_to=datetime.datetime.utcnow(),
                evcount_rep=len(events),
                evcount_all=len(events),
                evcount_flt=len(events),
                evcount_flt_blk=1,
                evcount_thr=len(events),
                evcount_thr_blk=0,
                evcount_rlp=0,
                filtering={"FLT01": 1},
            )
            report.parent.generate_label()
            report.parent.calculate_delta()

        report.statistics = mentat.stats.idea.truncate_evaluations(mentat.stats.idea.evaluate_events(events, is_target))

        events_aggr = {}
        for obj in events:
            for src in get_values(obj, "Source.IP4") + get_values(obj, "Source.IP6"):
                events_aggr[src] = [obj]
        report.structured_data = self.reporter.prepare_structured_data(
            events_aggr, events_aggr, self.reporting_settings.timezone, is_target
        )
        return report

    @staticmethod
    def _load_expected_report_text(name: str, report: EventReportModel) -> str:
        path = Path(__file__).parent / "tests" / name
        # Label changes per report, so the placeholder in the example report must be replaced.
        with open(path, "r", encoding="utf8") as f:
            return f.read().replace("REPORT_LABEL", report.label)

    @staticmethod
    def _clean_trailing_whitespaces(text: str) -> str:
        return "\n".join(line.rstrip() for line in text.split("\n"))


# -------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
