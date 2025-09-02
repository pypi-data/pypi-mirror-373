#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains classes for aggregation of events for reporting.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from dataclasses import fields

import typedcols
from ransack import get_values

from mentat.const import EventSections
from mentat.idea.internal import Idea
from mentat.reports.data import AggregatedData, DetectorData


class EventAggregator:
    """
    Class used for aggregating IDEA events for reporting purposes.
    """

    @staticmethod
    def _aggregate_main_section(detector_result: DetectorData, event: Idea) -> None:
        """
        Aggregates the "main" section of the IDEA message.
        """
        main_numeric_data = detector_result.main_numeric_data
        for field in fields(main_numeric_data):
            if field.name == "AvgPacketSize":
                # Sums packet size of all packets. Average is counted only after all events are aggregated.
                if event.get("AvgPacketSize") and event.get("PacketCount"):
                    main_numeric_data.ByteCountFromAvg += event.get("AvgPacketSize") * event.get("PacketCount")
            else:
                setattr(
                    main_numeric_data,
                    field.name,
                    getattr(main_numeric_data, field.name) + event.get(field.name, 0),
                )

        # -------------------------------

        main_list_data = detector_result.main_list_data
        for field in fields(main_list_data):
            if field.name == "UsernameAndPassword":
                # Aggregated as a tuple (Username, Password)
                for cred in get_values(event, "Credentials"):
                    if cred.get("Username") or cred.get("Password"):
                        main_list_data.UsernameAndPassword.add((cred.get("Username", ""), cred.get("Password", "")))
            else:
                for value in get_values(event, field.name):
                    getattr(main_list_data, field.name).add(value)

    @staticmethod
    def _aggregate_source_and_target_sections(
        detector_result: DetectorData, source_sections: list[dict], target_sections: list[dict]
    ) -> None:
        """
        Aggregates the Source and Target sections of the IDEA message.
        """
        source_numeric_data = detector_result.source_numeric_data
        target_numeric_data = detector_result.target_numeric_data
        for section_type, data_fields in [
            (EventSections.SOURCE, source_numeric_data),
            (EventSections.TARGET, target_numeric_data),
        ]:
            for field in fields(data_fields):
                for section in target_sections if section_type == EventSections.TARGET else source_sections:
                    if field.name == "ClockSkew":
                        # Final result will contain a ClockSkew that has the largest absolute
                        # value (so the sign is ignored when making the comparison).
                        if abs(section.get(field.name, 0)) > abs(getattr(data_fields, field.name)):
                            setattr(data_fields, field.name, section.get(field.name, 0))
                    else:
                        setattr(
                            data_fields,
                            field.name,
                            getattr(data_fields, field.name) + section.get(field.name, 0),
                        )

        # -------------------------------

        source_list_data = detector_result.source_list_data
        target_list_data = detector_result.target_list_data
        for field_list, sections in [
            (source_list_data, source_sections),
            (target_list_data, target_sections),
        ]:
            for field in fields(field_list):
                field_values = getattr(field_list, field.name)
                for section in sections:
                    if field.name == "ips":
                        # Iterate through both IPv4 and IPv6 addresses and save them to "ips" field.
                        for value in list(section.get("IP4") or []) + list(section.get("IP6") or []):
                            field_values.add(str(value))
                    elif field.name == "services":
                        # Aggregated as a tuple (ServiceName, ServiceVersion)
                        if section.get("ServiceName"):
                            field_values.add((section.get("ServiceName"), section.get("ServiceVersion")))
                    else:
                        # If it is a list, iterate through all the values and save them.
                        if isinstance(section.get(field.name, []), (list, typedcols.TypedList)):
                            for value in section.get(field.name, []):
                                field_values.add(str(value))
                        # If it is a single value, simply save the one value.
                        elif section.get(field.name) is not None:
                            field_values.add(str(section.get(field.name)))

    @classmethod
    def _aggregate_data(cls, partial_result: AggregatedData, event: Idea, source_sections: list[dict]) -> None:
        """
        Aggregates all data from the given event.
        """
        detector_result = partial_result.initialize_detector(event.get_last_detector_name())

        partial_result.update(
            event.get("EventTime") or event["DetectTime"],
            event.get("CeaseTime") or event.get("EventTime") or event["DetectTime"],
        )
        cls._aggregate_main_section(detector_result, event)
        cls._aggregate_source_and_target_sections(detector_result, source_sections, event.get(EventSections.TARGET, []))

    @staticmethod
    def _get_relevant_source_sections(event: Idea, ip: str) -> list[dict]:
        """
        Returns all source sections of the event, where the ip from args is included.
        """
        sections = []
        for section in event.get(EventSections.SOURCE, []):
            if ip in list(map(str, section.get("IP4", []))) or ip in list(map(str, section.get("IP6", []))):
                sections.append(section)
        return sections

    @classmethod
    def aggregate_source(cls, events: dict[str, list[Idea]]) -> dict[str, dict[str, AggregatedData]]:
        """
        Aggregate given list of events to dictionary structure that can be used to generate report message.
        In "Source", only data from source sections that include the particular IP address are aggregated.
        """
        result: dict[str, dict[str, AggregatedData]] = {}
        for ip, ip_events in events.items():
            for event in ip_events:
                event_class = event.get_whole_class() or "None"
                source_sections = cls._get_relevant_source_sections(event, str(ip))
                partial_result = result.setdefault(event_class, {}).setdefault(str(ip), AggregatedData())
                cls._aggregate_data(partial_result, event, source_sections)

        for abuse_value in result.values():
            for aggregated_data in abuse_value.values():
                aggregated_data.finalize()
        return result

    @classmethod
    def aggregate_target(cls, events: dict[str, list[Idea]]) -> dict[str, AggregatedData]:
        """
        Aggregate given list of events to dictionary structure that can be used to generate report message.
        """
        result: dict[str, AggregatedData] = {}
        processed_events_IDs = set()
        for ip, ip_events in events.items():
            for event in ip_events:
                event_class = event.get_whole_target_class() or "None"
                source_sections = event.get(EventSections.SOURCE, [])
                partial_result = result.setdefault(event_class, AggregatedData())
                detector_result = partial_result.initialize_detector(event.get_last_detector_name())

                # For target-based reporting, the same event can be saved under
                # many IPs, so this is for event deduplication.
                # Without this, events could be processed more than once.
                detector_result.target_list_data.relevant_ips.add(str(ip))
                if event.get_id() in processed_events_IDs:
                    # Event was already processed, skip it.
                    continue
                processed_events_IDs.add(event.get_id())

                cls._aggregate_data(partial_result, event, source_sections)

        for aggregated_data in result.values():
            aggregated_data.finalize()
        return result
