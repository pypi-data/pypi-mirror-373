"""
This file contains definitions of common chart sections.
"""

from flask_babel import lazy_gettext

from .const import DataComplexity
from .model import ChartSection
from mentat.stats import idea

COMMON_CHART_SECTIONS = [
    ChartSection.new_common(
        idea.ST_SKEY_ABUSES,
        lazy_gettext("abuses"),
        lazy_gettext("Number of events per abuse"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a source "
            "<em>abuse group</em>. The source <em>abuse group</em> is assigned according to all "
            "source addresses contained in the event, multiple source <em>abuse groups</em> can "
            "therefore be assigned to the event and the total numbers in these charts may differ "
            "from the total number of events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Abuse group"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TGTABUSES,
        lazy_gettext("target abuses"),
        lazy_gettext("Number of events per target abuse"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a target "
            "<em>abuse group</em>. The target <em>abuse group</em> is assigned according to all "
            "target addresses contained in the event, multiple target <em>abuse groups</em> can "
            "therefore be assigned to the event and the total numbers in these charts may differ "
            "from the total number of events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Target abuse group"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_ANALYZERS,
        lazy_gettext("analyzers"),
        lazy_gettext("Number of events per analyzer"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an "
            "<em>analyzer</em>. In the context of Mentat system and IDEA events the "
            "<em>analyzer</em> is a name of a software that detected or emitted the IDEA event. "
            "Multiple <em>analyzers</em> can be assigned to the event and therefore the total "
            "numbers in these charts may differ from the total number of events displayed in the "
            "table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Analyzer"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_ASNS,
        lazy_gettext("ASNs"),
        lazy_gettext("Number of events per ASN"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a source "
            "<em>autonomous system number</em> (<abbr>ASN</abbr>). The source <em>ASN</em> is "
            "assigned according to all source addresses contained in the event, multiple source "
            "<em>ASNs</em> can therefore be assigned to the event and the total numbers in these "
            "charts may differ from the total number of events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("ASN"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_CATEGORIES,
        lazy_gettext("categories"),
        lazy_gettext("Number of events per category"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a "
            "<em>category</em>. Multiple <em>categories</em> can be assigned to the event and "
            "therefore the total numbers in these charts may differ from the total number of "
            "events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Category"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_CATEGSETS,
        lazy_gettext("category sets"),
        lazy_gettext("Number of events per category set"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>category "
            "set</em>. The <em>category set</em> is a string concatenation of alphabetically "
            "ordered unique set of all event categories and so it provides different grouped view "
            "of the event category statistics."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("Category set"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_COUNTRIES,
        lazy_gettext("countries"),
        lazy_gettext("Number of events per country"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a source "
            "<em>country</em>. The source <em>country</em> is assigned according to all source "
            "addresses contained in the event, multiple source <em>countries</em> can therefore "
            "be assigned to the event and the total numbers in these charts may differ from the "
            "total number of events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Country"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_DETECTORS,
        lazy_gettext("detectors"),
        lazy_gettext("Number of events per detector"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a "
            "<em>detector</em>. In the context of Mentat system and IDEA events the "
            "<em>detector</em> is an unique name of the node on which the IDEA event was detected "
            "or emited."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Detector"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_DETECTORSWS,
        lazy_gettext("detector software"),
        lazy_gettext("Number of events per detector software"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>detector "
            "software</em>. The <em>detector software</em> is a string concatenation of detector "
            "and analyzer names. Because an event may contain multiple analyzer names, multiple "
            "<em>detector software</em> strings can be produced for each event and the total "
            "numbers in these charts may differ from the total number of events displayed in the "
            "table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Detector software"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_DETECTORTPS,
        lazy_gettext("detector tags"),
        lazy_gettext("Number of events per detector type"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>detector "
            "type</em>. In the context of Mentat system and IDEA events each <em>detector</em> is "
            "an unique name of the node on which the IDEA event was detected or emitted and each "
            "may be assigned one or more tags to describe its type. Because an event may contain "
            "multiple <em>detector type tags</em>, the total numbers in these charts may differ "
            "from the total number of events displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Detector type"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_SOURCES,
        lazy_gettext("sources"),
        lazy_gettext("Number of events per source IP"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>source IP "
            "address</em>. Because an event may contain multiple <em>source IP addresses</em>, "
            "the total numbers in these charts may differ from the total number of events "
            "displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Source IP"),
        csag_group="ips",
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TARGETS,
        lazy_gettext("targets"),
        lazy_gettext("Number of events per target IP"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>target IP "
            "address</em>. Because an event may contain multiple <em>target IP addresses</em>, "
            "the total numbers in these charts may differ from the total number of events "
            "displayed in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Target IP"),
        csag_group="ips",
    ),
    ChartSection.new_common(
        idea.ST_SKEY_SRCPORTS,
        lazy_gettext("source ports"),
        lazy_gettext("Number of events per source port"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>source "
            "port</em>. Because an event may contain multiple <em>source ports</em>, the total "
            "numbers in these charts may differ from the total number of events displayed in the "
            "table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Source port"),
        csag_group="ports",
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TGTPORTS,
        lazy_gettext("target ports"),
        lazy_gettext("Number of events per target port"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>target "
            "port</em>. Because an event may contain multiple <em>target ports</em>, the total "
            "numbers in these charts may differ from the total number of events displayed in the "
            "table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Target port"),
        csag_group="ports",
    ),
    ChartSection.new_common(
        idea.ST_SKEY_PROTOCOLS,
        lazy_gettext("protocols"),
        lazy_gettext("Number of events per protocol/service"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>protocol "
            "or service</em>. Because an event may contain multiple <em>protocols</em>, the total "
            "numbers in these charts may differ from the total number of events displayed in the "
            "table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Protocol"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_SRCTYPES,
        lazy_gettext("source types"),
        lazy_gettext("Number of events per source type"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>source "
            "type</em>. Because an event may contain multiple <em>source type tags</em>, the "
            "total numbers in these charts may differ from the total number of events displayed "
            "in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Source type"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TGTTYPES,
        lazy_gettext("target types"),
        lazy_gettext("Number of events per target type"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to a <em>target "
            "type</em>. Because an event may contain multiple <em>target type tags</em>, the "
            "total numbers in these charts may differ from the total number of events displayed "
            "in the table above."
        ),
        DataComplexity.MULTI,
        lazy_gettext("Target type"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_CLASSES,
        lazy_gettext("classes"),
        lazy_gettext("Number of events per class"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an event "
            "<em>classification</em>. The event <em>class</em> is a cataloging mechanism "
            "similar to the categories. It is however internal only to Mentat system and attempts "
            "to group different events describing the same type of incidents."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("Event class"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TGTCLASSES,
        lazy_gettext("target classes"),
        lazy_gettext("Number of events per target class"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an event "
            "<em>target classification</em>. The event <em>target class</em> is a cataloging mechanism "
            "similar to the categories. It is however internal only to Mentat system and attempts "
            "to group different events describing the same type of incidents."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("Target class"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_SEVERITIES,
        lazy_gettext("severities"),
        lazy_gettext("Number of events per severity"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an event "
            "<em>severity</em>. The event <em>severity</em> is internal only to Mentat system and "
            "is assigned by predefined set of rules based on the event classification."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("Severity"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TGTSEVERITIES,
        lazy_gettext("target severities"),
        lazy_gettext("Number of events per target severity"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an event "
            "<em>target severity</em>. The event <em>target severity</em> is internal only to Mentat system and "
            "is assigned by predefined set of rules based on the event classification."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("Target severity"),
    ),
    ChartSection.new_common(
        idea.ST_SKEY_TLPS,
        lazy_gettext("tlps"),
        lazy_gettext("Number of events per TLP"),
        lazy_gettext(
            "This view shows total numbers of IDEA events aggregated according to an event "
            "<em>TLP (Traffic Light Protocol)</em> value, which is used to decide who can "
            "see the event."
        ),
        DataComplexity.SINGLE,
        lazy_gettext("TLP"),
    ),
]

COMMON_CHART_SECTIONS_MAP = {chs.key: chs for chs in COMMON_CHART_SECTIONS}
