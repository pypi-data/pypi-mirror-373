#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains data representation classes for reporting.
"""

__author__ = "Jakub Judiny <Jakub.Judiny@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

from dataclasses import Field, dataclass, field, fields
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, get_args, get_origin

from mentat.const import EventSections, tr_

if TYPE_CHECKING:
    from mentat.datatype.sqldb import GroupModel


@dataclass
class ReportingProperties:
    """
    Represents basic properties of the current reporting run.

    Attributes:
        group (GroupModel): Group for which the reports are generated.
        severity (str): Severity for which to perform reporting.
        lower_time_bound (datetime): Lower reporting time threshold.
        upper_time_bound (datetime): Upper reporting time threshold.
        template_vars (Optional[dict]): Dictionary containing additional template variables.
        has_test_data (bool): Switch to use test data for reporting.
        is_shadow (bool): If it is shadow reporting (True), or normal reporting (False).
        is_target (bool): If the reporting is target-based (True) or source-based (False).
    """

    group: "GroupModel"
    severity: str
    lower_time_bound: datetime
    upper_time_bound: datetime
    template_vars: Optional[dict] = None
    has_test_data: bool = False
    is_shadow: bool = False
    is_target: bool = False

    def get_current_section(self) -> str:
        section = "Shadow" if self.is_shadow else ""
        section += EventSections.TARGET if self.is_target else EventSections.SOURCE
        return section

    def _get_reporting_window_size(self) -> str:
        """
        Returns string of the difference between upper and lower time bound.
        """
        return str(self.upper_time_bound - self.lower_time_bound)

    def to_log_text(self) -> str:
        """
        Returns text representation of the most important properties of the reporting.
        This can be used e.g. for logging purposes.
        """
        severity_type = "target" if self.is_target else "source"
        reporting_type = "shadow" if self.is_shadow else "normal"
        return (
            f"{severity_type} severity '{self.severity}' and time interval "
            f"{self.lower_time_bound.isoformat()} -> {self.upper_time_bound.isoformat()} "
            f"({self._get_reporting_window_size()}). ({reporting_type} reporting)"
        )

    def get_event_search_parameters(self) -> dict[str, Any]:
        """
        Returns search parameters for event searching based on the
        reporting properties represented by this data class.
        """
        parameters: dict[str, Any] = {
            "st_from": self.lower_time_bound,
            "st_to": self.upper_time_bound,
        }

        # Shadow reports are also generated from Test data.
        if not self.has_test_data and not self.is_shadow:
            parameters.update(
                {
                    "categories": ["Test"],
                    "not_categories": True,
                }
            )

        if not self.is_target:
            parameters.update(
                {
                    "groups": [self.group.name],
                    "severities": [self.severity],
                    "shadow_reporting": self.is_shadow,
                }
            )
        else:
            parameters.update(
                {
                    "target_groups": [self.group.name],
                    "target_severities": [self.severity],
                    "shadow_reporting_target": self.is_shadow,
                }
            )

        return parameters


# ---------------------------------------------------------------------------
# Data classes related to event aggregation
# ---------------------------------------------------------------------------


@dataclass
class ViewField:
    """
    Fake field that can be used for return view "fields" and use them as normal
    dataclass fields when rendering reports. They do not hold any value.
    """

    name: str
    type_: type
    metadata: dict


@dataclass
class JsonSetFixMixin:
    """
    This class makes sure that dataclasses inheriting from it can be loaded
    from JSON dict that only have lists even if they have attributes with set
    type. This is needed because JSON cannot have sets or tuples, only list.
    """

    def __post_init__(self) -> None:
        for f in fields(self):
            val = getattr(self, f.name)
            if isinstance(val, list):
                expected_type = f.type
                origin = get_origin(expected_type)
                args = get_args(expected_type)

                if origin is set:
                    inner = args[0] if args else None
                    if get_origin(inner) is tuple:
                        setattr(self, f.name, {tuple(item) for item in val})
                    else:
                        setattr(self, f.name, set(val))


@dataclass
class ReportViewMixin:
    @staticmethod
    def get_section() -> EventSections:
        raise NotImplementedError()

    def get_display_name(self, field_to_display: Field | ViewField) -> Optional[str]:
        """
        Return the correct display name for the field, or None if the field should
        not be displayed (i.e. the display name is not set)
        """
        key = f"{self.get_section().lower()}_display_name"
        return field_to_display.metadata.get(key, None)

    @staticmethod
    def get_view_fields() -> list[ViewField]:
        return []

    @classmethod
    def get_all_fields_for_view(cls) -> list[Field | ViewField]:
        # Return only fields that have display name set for the current section,
        # otherwise they are there only for aggregation purposes.
        return (
            list(
                filter(
                    lambda x: x.metadata.get(f"{cls.get_section().lower()}_display_name") is not None,
                    fields(cls),
                )
            )
            + cls.get_view_fields()
        )


@dataclass
class SourceTargetNumericData(ReportViewMixin):
    ClockSkew: int = field(
        default=0,
        metadata={"source_display_name": tr_("Source clock skew"), "target_display_name": tr_("Target clock skew")},
    )
    InFlowCount: int = field(
        default=0,
        metadata={"source_display_name": tr_("Source InFlowCount"), "target_display_name": tr_("Target InFlowCount")},
    )
    OutFlowCount: int = field(
        default=0,
        metadata={"source_display_name": tr_("Source OutFlowCount"), "target_display_name": tr_("Target OutFlowCount")},
    )
    InPacketCount: int = field(
        default=0,
        metadata={
            "source_display_name": tr_("Source InPacketCount"),
            "target_display_name": tr_("Target InPacketCount"),
        },
    )
    OutPacketCount: int = field(
        default=0,
        metadata={
            "source_display_name": tr_("Source OutPacketCount"),
            "target_display_name": tr_("Target OutPacketCount"),
        },
    )
    InByteCount: int = field(
        default=0,
        metadata={"source_display_name": tr_("Source InByteCount"), "target_display_name": tr_("Target InByteCount")},
    )
    OutByteCount: int = field(
        default=0,
        metadata={"source_display_name": tr_("Source OutByteCount"), "target_display_name": tr_("Target OutByteCount")},
    )

    @staticmethod
    def get_view_fields() -> list[ViewField]:
        return [
            ViewField(
                "ip_count",
                list[str],
                {
                    "source_display_name": tr_("Total source IP count"),
                    "target_display_name": tr_("Total target IP count"),
                },
            ),
        ]


@dataclass
class SourceNumericData(SourceTargetNumericData):
    @staticmethod
    def get_section() -> EventSections:
        return EventSections.SOURCE


@dataclass
class TargetNumericData(SourceTargetNumericData):
    @staticmethod
    def get_section() -> EventSections:
        return EventSections.TARGET


@dataclass
class SourceTargetListData(JsonSetFixMixin, ReportViewMixin):
    Port: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source port"),
            "target_display_name": tr_("Target port"),
        },
    )
    Hostname: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source hostname"),
            "target_display_name": tr_("Target hostname"),
        },
    )
    MAC: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source MAC"),
            "target_display_name": tr_("Target MAC"),
        },
    )
    Proto: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source protocol"),
            "target_display_name": tr_("Target protocol"),
        },
    )
    URL: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source URL"),
            "target_display_name": tr_("Target URL"),
        },
    )
    Ref: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source reference"),
            "target_display_name": tr_("Target reference"),
        },
    )
    Email: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source e-mail"),
            "target_display_name": tr_("Target e-mail"),
        },
    )
    Router: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source router"),
            "target_display_name": tr_("Target router"),
        },
    )
    Netname: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source netname"),
            "target_display_name": tr_("Target netname"),
        },
    )
    Interface: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source interface"),
            "target_display_name": tr_("Target interface"),
        },
    )
    BitMask: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source bitmask"),
            "target_display_name": tr_("Target bitmask"),
        },
    )
    services: set[tuple[str, str]] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source service"),
            "target_display_name": tr_("Target service"),
        },
    )
    X509ExpiredTime: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source X509 expired at"),
            "target_display_name": tr_("Target X509 expired at"),
        },
    )
    ips: set[str] = field(
        default_factory=set,
        metadata={
            "source_display_name": tr_("Source IP addresses"),
            "target_display_name": tr_("Target IP addresses"),
        },
    )


@dataclass
class SourceListData(SourceTargetListData):
    @staticmethod
    def get_section() -> EventSections:
        return EventSections.SOURCE


@dataclass
class TargetListData(SourceTargetListData):
    # This attribute is only relevant for target-based reports!
    relevant_ips: set[str] = field(
        default_factory=set,
        metadata={"target_display_name": tr_("Your target IPs")},
    )

    @staticmethod
    def get_section() -> EventSections:
        return EventSections.TARGET


@dataclass
class MainNumericData(ReportViewMixin):
    ConnCount: int = field(
        default=0,
        metadata={"main_display_name": tr_("Connection count")},
    )
    FlowCount: int = field(
        default=0,
        metadata={"main_display_name": tr_("Flow count")},
    )
    PacketCount: int = field(
        default=0,
        metadata={"main_display_name": tr_("Packet count")},
    )
    ByteCount: int = field(
        default=0,
        metadata={"main_display_name": tr_("Byte count")},
    )
    AvgPacketSize: int = field(
        default=0,
        metadata={"main_display_name": tr_("Average packet size")},
    )
    FlowCountDropped: int = field(
        default=0,
        metadata={"main_display_name": tr_("Dropped flow count")},
    )
    PacketCountDropped: int = field(
        default=0,
        metadata={"main_display_name": tr_("Dropped packet count")},
    )
    ByteCountDropped: int = field(
        default=0,
        metadata={"main_display_name": tr_("Dropped byte count")},
    )
    ByteCountFromAvg: int = field(default=0)

    @staticmethod
    def get_section() -> EventSections:
        return EventSections.MAIN


@dataclass
class MainListData(JsonSetFixMixin, ReportViewMixin):
    Ref: set[str] = field(
        default_factory=set,
        metadata={"main_display_name": tr_("Reference")},
    )
    UsernameAndPassword: set[tuple[str, str]] = field(
        default_factory=set,
        metadata={"main_display_name": tr_("Username, password")},
    )

    @staticmethod
    def get_section() -> EventSections:
        return EventSections.MAIN

    @staticmethod
    def get_view_fields() -> list[ViewField]:
        return [
            ViewField("protocols", list[str], {"main_display_name": tr_("Protocols")}),
        ]


# -------------------------------


@dataclass
class DetectorData:
    main_numeric_data: MainNumericData = field(default_factory=MainNumericData)
    main_list_data: MainListData = field(default_factory=MainListData)
    source_numeric_data: SourceNumericData = field(default_factory=SourceNumericData)
    source_list_data: SourceListData = field(default_factory=SourceListData)
    target_numeric_data: TargetNumericData = field(default_factory=TargetNumericData)
    target_list_data: TargetListData = field(default_factory=TargetListData)

    @classmethod
    def from_dict(cls, data: dict) -> "DetectorData":
        def filter_fields(cls_: Any, d: dict) -> dict:
            """Extract only keys from dict `d` that match fields of the dataclass `cls_`."""
            return {f.name: d[f.name] for f in fields(cls_) if f.name in d}

        return cls(
            main_numeric_data=MainNumericData(**data.get("main_numeric_data", filter_fields(MainNumericData, data))),
            main_list_data=MainListData(**data.get("main_list_data", filter_fields(MainListData, data))),
            source_numeric_data=SourceNumericData(
                **data.get("source_numeric_data", filter_fields(SourceNumericData, data.get(EventSections.SOURCE, {}))),
            ),
            source_list_data=SourceListData(
                **data.get("source_list_data", filter_fields(SourceListData, data.get(EventSections.SOURCE, {})))
            ),
            target_numeric_data=TargetNumericData(
                **data.get("target_numeric_data", filter_fields(TargetNumericData, data.get(EventSections.TARGET, {}))),
            ),
            target_list_data=TargetListData(
                **data.get("target_list_data", filter_fields(TargetListData, data.get(EventSections.TARGET, {})))
            ),
        )

    @staticmethod
    def get_all_fields_for_view(section: EventSections) -> list[Field | ViewField]:
        if section == EventSections.MAIN:
            return MainListData.get_all_fields_for_view() + MainNumericData.get_all_fields_for_view()
        if section == EventSections.SOURCE:
            return SourceListData.get_all_fields_for_view() + SourceNumericData.get_all_fields_for_view()
        if section == EventSections.TARGET:
            return TargetListData.get_all_fields_for_view() + TargetNumericData.get_all_fields_for_view()
        raise TypeError("Wrong section")

    def get_protocols(self) -> set[str]:
        """
        Return protocols from both the source and target sections.
        """
        return self.source_list_data.Proto | self.target_list_data.Proto

    def get_ip_count(self, section: str) -> int:
        """
        Returns number of IPs in the section from args.
        """
        if section == EventSections.SOURCE:
            return len(self.source_list_data.ips)
        if section == EventSections.TARGET:
            return len(self.target_list_data.ips)
        raise TypeError("Wrong section")

    def finalize(self) -> None:
        """
        Makes final calculations after all events are processed.
        """
        main_numeric_data = self.main_numeric_data
        if main_numeric_data.ByteCountFromAvg:
            main_numeric_data.AvgPacketSize = round(main_numeric_data.ByteCountFromAvg / main_numeric_data.PacketCount)


@dataclass
class AggregatedData:
    first_time: datetime = datetime.max
    last_time: datetime = datetime.min
    event_count: int = 0
    # Reference to the initial report - used only in relapsed reports.
    reference: Optional[str] = None
    detector_data: dict[str, DetectorData] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AggregatedData":
        first_time = data.get("first_time", datetime.max)
        last_time = data.get("last_time", datetime.min)

        # Handle datetime string decoding
        if isinstance(first_time, str):
            first_time = datetime.fromisoformat(first_time)
        if isinstance(last_time, str):
            last_time = datetime.fromisoformat(last_time)

        return cls(
            first_time=first_time,
            last_time=last_time,
            event_count=data.get("event_count", 0) or data.get("count", 0),
            reference=data.get("reference"),
            detector_data={
                name: DetectorData.from_dict(det_data) for name, det_data in data.get("detector_data", {}).items()
            },
        )

    def get_detector_count(self) -> int:
        """
        Return the number of detectors in detector_data.
        """
        return len(self.detector_data)

    def initialize_detector(self, name: str) -> DetectorData:
        """
        Adds a detector to detector_data keys and initializes DetectorData for it.
        Returns the initialized DetectorData.
        """
        return self.detector_data.setdefault(name, DetectorData())

    def update(self, start_time: datetime, end_time: datetime) -> None:
        """
        Updates the data based on data from one event. Detector data are
        not updated by this method.
        """
        self.event_count += 1
        self.first_time = min(start_time, self.first_time)
        self.last_time = max(end_time, self.last_time)

    def finalize(self) -> None:
        """
        Makes final calculations after all events are processed.
        """
        for detector_value in self.detector_data.values():
            detector_value.finalize()


# -------------------------------


@dataclass
class TargetReportData:
    """
    Target results have this structure:
    {
        '*event_class*': {
            'first_time': ...,
            ...
            'detector_data': {
                '*detector*': {
                    ...
                }
            }
        }
    }

    This is because information in target reports are not divided into several
    ip address sections, but all information are displayed in one main section.
    """

    regular: dict[str, AggregatedData]
    relapsed: dict[str, AggregatedData]
    timezone: str

    @classmethod
    def from_dict(cls, data: dict) -> "TargetReportData":
        return cls(
            timezone=data["timezone"],
            regular={k: AggregatedData.from_dict(v) for k, v in data["regular"].items()},
            relapsed={k: AggregatedData.from_dict(v) for k, v in data["relapsed"].items()},
        )


@dataclass
class SourceReportData:
    """
    Source results have this structure:
    {
        '*event_class*': {
            '*ip*': {
                'first_time': ...,
                ...
                'detector_data': {
                    '*detector*': {
                        ...
                    }
                }
            }
        }
    }

    So compared to target reports, data for event classes are further
    divided based on ip addresses.
    """

    regular: dict[str, dict[str, AggregatedData]]
    relapsed: dict[str, dict[str, AggregatedData]]
    timezone: str

    @classmethod
    def from_dict(cls, data: dict) -> "SourceReportData":
        def build_nested_agg(d: dict[str, dict]) -> dict[str, dict[str, AggregatedData]]:
            return {
                event_class: {ip: AggregatedData.from_dict(agg_data) for ip, agg_data in ip_map.items()}
                for event_class, ip_map in d.items()
            }

        return cls(
            timezone=data["timezone"],
            regular=build_nested_agg(data["regular"]),
            relapsed=build_nested_agg(data["relapsed"]),
        )
