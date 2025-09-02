#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Mentat system management and inspection library.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


from mentat.datatype.sqldb import (
    EventClassModel,
    EventClassState,
    FilterModel,
    GroupModel,
    NetworkModel,
    SettingsReportingModel,
    UserModel,
)


class MentatFixtures:
    """
    Class representing Mentat real-time module configuration for control utility.
    """

    def __init__(self, eventservice, sqlservice, logservice):
        self.eventservice = eventservice
        self.sqlservice = sqlservice
        self.logservice = logservice

    @staticmethod
    def get_example_event_classes():
        return [
            EventClassModel(
                name="anomaly-host-miner",
                source_based=True,
                label_en="Hosts recently active as Bitcoin seed nodes.",
                label_cz="Zařízení nedávno aktivní v těžbě Bitcoinů.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/anomaly-host-miner",
                displayed_main=[],
                displayed_source=[],
                displayed_target=[],
                rule="'Anomaly.Behaviour' in Category and 'Miner' in Source.Type??[]",
                severity="low",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-login-rdp",
                source_based=True,
                label_en="The machine attempted to login to Remote Desktop Protocol service.",
                label_cz="Stroj se pokoušel připojovat ke službě Remote Desktop Protocol.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-login-rdp",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=["Port"],
                rule="'Attempt.Login' in Category and (3389 in Target.Port??[] or ['ms-wbt-server', 'rdp'] in Target.Proto??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-login-telnet",
                source_based=True,
                label_en="The machine attempted to login to Telnet service.",
                label_cz="Stroj se pokoušel připojovat ke službě Telnet.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-login-telnet",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=["Port"],
                rule="'Attempt.Login' in Category and ('telnet' in Target.Proto??[] or 'telnet' in Source.Proto??[] or 23 in Target.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-login-ssh",
                source_based=True,
                label_en="The machine attempted to login to SSH service.",
                label_cz="Stroj se pokoušel připojovat ke službě SSH.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-login-ssh",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=["Port", "ips"],
                rule="['Attempt.Login', 'Intrusion.UserCompromise'] in Category and ('ssh' in Target.Proto??[] or 'ssh' in Source.Proto??[] or 22 in Target.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-login-sip",
                source_based=True,
                label_en="The machine attempted to login over SIP protocol.",
                label_cz="Stroj se pokoušel připojovat pomocí SIP protokolu.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-login-sip",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=["Port", "ips"],
                rule="'Attempt.Login' in Category and (['sip', 'sip-tls'] in Target.Proto??[] or ['sip', 'sip-tls'] in Source.Proto??[] or 5060 in Target.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-exploit-http",
                source_based=True,
                label_en="The machine attempted to exploit HTTP/S service.",
                label_cz="Stroj se pokusil zneužít službu na HTTP/S.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-exploit-http",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=["Hostname", "Port", "ips"],
                rule="'Attempt.Exploit' in Category and ([80, 443] in Target.Port??[] or ['http', 'https', 'http-alt'] in Source.Proto??[] or ['http', 'https', 'http-alt'] in Target.Proto??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="attempt-exploit",
                source_based=True,
                label_en="The machine attempted to exploit some well-known service.",
                label_cz="Stroj se pokoušel zneužít některou známou službu.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/attempt-exploit",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                    "Ref",
                ],
                displayed_source=[],
                displayed_target=["Port", "ips"],
                rule="'Attempt.Exploit' in Category",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="avail-ddos",
                source_based=True,
                label_en="Following hosts were sources of DDoS attacks.",
                label_cz="Následující stroje byly zdroje DDoS útoků.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/avail-ddos",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[
                    "Port",
                    "InFlowCount",
                    "InPacketCount",
                    "InByteCount",
                    "OutFlowCount",
                    "OutPacketCount",
                    "OutByteCount",
                ],
                displayed_target=[],
                rule="['Availability.DoS', 'Availability.DDoS'] in Category",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="abusive-spam-backscatter",
                source_based=True,
                label_en="The mail server is misconfigured and spreading backscatter (misdirected bounces).",
                label_cz="Poštovní server je špatně nakonfigurován a šíří backscatter (nevyžádaná návratová hlášení).",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/abusive-spam-backscatter",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=[],
                rule="'Abusive.Spam' in Category and 'Backscatter' in Source.Type??[]",
                severity="low",
                subclassing="",
                state=EventClassState.DISABLED,
            ),
            EventClassModel(
                name="abusive-spam-spammer",
                source_based=True,
                label_en="The mail server is spreading spam.",
                label_cz="Poštovní server šíří spam.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/abusive-spam-spammer",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "PacketCount",
                    "ByteCount",
                    "protocols",
                ],
                displayed_source=[],
                displayed_target=[],
                rule="'Abusive.Spam' in Category and 'Spam' in Source.Type??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-qotd",
                source_based=True,
                label_en="Open access to QoTD service.",
                label_cz="Stroj má otevřeně přístupnou službu QoTD.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-qotd",
                displayed_main=[],
                displayed_source=["Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('qotd' in Source.Proto??[] or 17 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-ssdp",
                source_based=True,
                label_en="Open access to SSDP service.",
                label_cz="Stroj má otevřeně přístupnou službu SSDP.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-ssdp",
                displayed_main=[],
                displayed_source=["Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('ssdp' in Source.Proto??[] or 1900 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-ntp",
                source_based=True,
                label_en="Open access to NTP service.",
                label_cz="Stroj má otevřeně přístupnou službu NTP.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-ntp",
                displayed_main=[],
                displayed_source=["Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('ntp' in Source.Proto??[] or 123 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-domain",
                source_based=True,
                label_en="Open access to recursive DNS server.",
                label_cz="Na stroji je otevřený rekurzivní DNS resolver.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-domain",
                displayed_main=[],
                displayed_source=["Port", "Proto"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('domain' in Source.Proto??[] or 53 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-netbios",
                source_based=True,
                label_en="Open access to NetBIOS-NS service.",
                label_cz="Stroj má otevřeně přístupnou službu NetBIOS-NS.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-netbios",
                displayed_main=[],
                displayed_source=["Port", "Proto"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and (['netbios-ns', 'netbios-dgm', 'netbios-ssn'] in Source.Proto??[] or [137, 138, 139] in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-ipmi",
                source_based=True,
                label_en="Open access to Intelligent Platform Management Interface service.",
                label_cz="Stroj má otevřeně přístupnou službu Intelligent Platform Management Interface.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-ipmi",
                displayed_main=[],
                displayed_source=["Port", "Proto"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and (['ipmi', 'asf-rmcp'] in Source.Proto??[] or 623 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-chargen",
                source_based=True,
                label_en="Open access to Character Generator service.",
                label_cz="Stroj má otevřeně přístupnou službu Character Generator.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-chargen",
                displayed_main=[],
                displayed_source=["Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('chargen' in Source.Proto??[] or 19 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-snmp",
                source_based=True,
                label_en='Open access to SNMP service with "public" community.',
                label_cz='Stroj má otevřeně přístupnou službu SNMP s komunitou "public".',
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-snmp",
                displayed_main=[],
                displayed_source=["Port", "Proto"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ('snmp' in Source.Proto??[] or 161 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-tls-old",
                source_based=True,
                label_en="Old SSL/TLS is being used.",
                label_cz="Používaní zastaralého SSL/TLS.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-tls-old",
                displayed_main=[],
                displayed_source=["Hostname", "Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ['ssl2','ssl3'] in Source.Proto??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-tls-deprecated",
                source_based=True,
                label_en="Deprecated TLS is being used.",
                label_cz="Používaní nedoporučované verze TLS.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-tls-old",
                displayed_main=[],
                displayed_source=["Hostname", "Proto", "Port"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and ['tls1','tls11'] in Source.Proto??[]",
                severity="info",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-ciphers-old",
                source_based=True,
                label_en="Insecure cipher(s) offered.",
                label_cz="Nabízeny nedostatečně bezpečné šifry.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-ciphers-old",
                displayed_main=["Ref"],
                displayed_source=["Hostname", "Proto", "Port", "Ciphers"],
                displayed_target=[],
                rule="'Vulnerable.Config' in Category and Source.Ciphers?? and 'tls' in Source.Proto??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.SHADOW,
            ),
            EventClassModel(
                name="vulnerable-config-time-not-synced",
                source_based=True,
                label_en="Server time is out of sync.",
                label_cz="Serverový čas není synchronizovaný.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-time-not-synced",
                displayed_main=[],
                displayed_source=["Hostname", "Proto", "Port", "ClockSkew"],
                displayed_target=[],
                rule="Source.ClockSkew?? and 'Vulnerable.Config' in Category",
                severity="low",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-config-certificate-expired",
                source_based=True,
                label_en="Certificate is expired.",
                label_cz="Vypršela platnost certifikátu.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-config-certificate-expired",
                displayed_main=[],
                displayed_source=["Hostname", "Proto", "Port", "X509ExpiredTime"],
                displayed_target=[],
                rule="Source.X509ExpiredTime?? and 'Vulnerable.Config' in Category",
                severity="info",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-open-socks",
                source_based=True,
                label_en="Open SOCKS proxy.",
                label_cz="Stroj funguje jako otevřená SOCKS proxy.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/vulnerable-open-socks",
                displayed_main=[],
                displayed_source=["Port", "Proto"],
                displayed_target=[],
                rule="['Vulnerable.Config', 'Vulnerable.Open'] in Category and ('socks' in Source.Proto??[] or 1080 in Source.Port??[])",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="vulnerable-implementation",
                source_based=True,
                label_en="Vulnerable version of software was found.",
                label_cz="Byla nalezena zranitelná verze softvéru.",
                reference="",
                displayed_main=["Ref"],
                displayed_source=["Ref", "Hostname", "Proto", "Port", "services"],
                displayed_target=[],
                rule="'Vulnerable.Open' in Category and Ref??[] contains 'cvr:'",
                severity="medium",
                subclassing="Ref",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="anomaly-traffic-url",
                source_based=True,
                label_en="Botnet communication was intercepted and it contained URL belonging to your network.",
                label_cz="Byla zachycena komunikace botnetů, která obsahovala URL z Vaší sítě.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/anomaly-traffic-url",
                displayed_main=[],
                displayed_source=[],
                displayed_target=[],
                rule="'Anomaly.Traffic' in Category and 'OriginSandbox' in Source.Type??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.DISABLED,
            ),
            EventClassModel(
                name="anomaly-traffic",
                source_based=True,
                label_en="Communication of following hosts is unusually big or suspicious.",
                label_cz="Komunikace těchto strojů je neobvykle vysoká či podezřelá.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/anomaly-traffic",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "FlowCountDropped",
                    "PacketCount",
                    "PacketCountDropped",
                    "ByteCount",
                    "ByteCountDropped",
                    "AvgPacketSize",
                    "protocols",
                    "Ref",
                ],
                displayed_source=[
                    "InFlowCount",
                    "OutFlowCount",
                    "InPacketCount",
                    "OutPacketCount",
                    "InByteCount",
                    "OutByteCount",
                    "Interface",
                    "BitMask",
                    "Router",
                    "Port",
                ],
                displayed_target=["ips", "Port", "Interface"],
                rule="'Anomaly.Traffic' in Category",
                severity="low",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="intrusion-botnet-bot",
                source_based=True,
                label_en="The machine is compromised and serve as bot drone.",
                label_cz="Stroj je zkompromitován a je součástí botnetu.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/intrusion-botnet-bot",
                displayed_main=[],
                displayed_source=["Proto", "Port"],
                displayed_target=[],
                rule="'Intrusion.Botnet' in Category and 'Botnet' in Source.Type??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="intrusion-botnet-cc",
                source_based=True,
                label_en="The machine is a command and control server of botnet.",
                label_cz="Stroj je řídící (command and control) server botnetu.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/intrusion-botnet-cc",
                displayed_main=[],
                displayed_source=[],
                displayed_target=[],
                rule="'Intrusion.Botnet' in Category and 'CC' in Source.Type??[]",
                severity="medium",
                subclassing="",
                state=EventClassState.DISABLED,
            ),
            EventClassModel(
                name="recon-scanning",
                source_based=True,
                label_en="The machine performed some type of active scanning.",
                label_cz="Stroj se pokoušel o nějakou formu aktivního skenování.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/recon-scanning",
                displayed_main=["ConnCount", "FlowCount", "protocols", "Ref"],
                displayed_source=[],
                displayed_target=["Port", "ips", "Hostname"],
                rule="'Recon.Scanning' in Category",
                severity="low",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
            EventClassModel(
                name="anomaly-traffic-target",
                source_based=False,
                label_en="You were a target of a network attack, which was mitigated by our automated systems.",
                label_cz="Byli jste cílem síťového útoku, který byl omezen našimi automatizovanými systémy.",
                reference="https://csirt.cesnet.cz/cs/services/eventclass/anomaly-traffic-target",
                displayed_main=[
                    "ConnCount",
                    "FlowCount",
                    "FlowCountDropped",
                    "PacketCount",
                    "PacketCountDropped",
                    "ByteCount",
                    "ByteCountDropped",
                    "AvgPacketSize",
                    "protocols",
                    "Ref",
                ],
                displayed_source=[
                    "InFlowCount",
                    "OutFlowCount",
                    "InPacketCount",
                    "OutPacketCount",
                    "InByteCount",
                    "OutByteCount",
                    "BitMask",
                    "Port",
                    "ips",
                ],
                displayed_target=["relevant_ips", "ip_count", "Port"],
                rule="'Anomaly.Traffic' in Category and ['cz.cesnet.ftas', 'cz.cesnet.gc15'] in Node.Name??[] and 'ActionRegulated' in Target.Type??[]",
                severity="low",
                subclassing="",
                state=EventClassState.ENABLED,
            ),
        ]

    def import_to_db(self):
        """
        Import data fixtures into database.
        """
        account_user = UserModel(
            login="user",
            fullname="Demo User",
            email="user@bogus-domain.org",
            organization="BOGUS DOMAIN, a.l.e.",
            roles=["user"],
            enabled=True,
        )
        account_developer = UserModel(
            login="developer",
            fullname="Demo Developer",
            email="developer@bogus-domain.org",
            organization="BOGUS DOMAIN, a.l.e.",
            roles=["user", "developer"],
            enabled=True,
        )
        account_maintainer = UserModel(
            login="maintainer",
            fullname="Demo Maintainer",
            email="maintainer@bogus-domain.org",
            organization="BOGUS DOMAIN, a.l.e.",
            roles=["user", "maintainer"],
            enabled=True,
        )
        account_admin = UserModel(
            login="admin",
            fullname="Demo Admin",
            email="admin@bogus-domain.org",
            organization="BOGUS DOMAIN, a.l.e.",
            roles=["user", "admin"],
            enabled=True,
        )
        group = GroupModel(
            name="DEMO_GROUP",
            source="manual",
            description="Demo Group",
            enabled=True,
        )
        group.members.append(account_user)
        group.members.append(account_developer)
        group.members.append(account_maintainer)
        group.members.append(account_admin)

        group.managers.append(account_maintainer)
        group.managers.append(account_admin)

        SettingsReportingModel(
            group=group,
            emails_info=["abuse@bogus-domain.org"],
            redirect=True,
        )

        NetworkModel(
            group=group,
            netname="NETNAME1",
            source="manual",
            network="192.168.0.0/24",
            description="First demonstration IPv4 network",
        )
        NetworkModel(
            group=group,
            netname="NETNAME2",
            source="manual",
            network="195.113.144.0/24",
            description="Second demonstration IPv4 network",
        )
        NetworkModel(
            group=group,
            netname="NETNAME3",
            source="manual",
            network="2001::/16",
            description="First demonstration IPv6 network",
        )

        FilterModel(
            group=group,
            name="Filter Queeg",
            type="advanced",
            source_based=True,
            filter='Node.Name == "cz.cesnet.queeg"',
            description="Filter out all messages originating from cz.cesnet.queeg detection node",
        )

        global_filter = FilterModel(
            group=None,
            name="Filter Global",
            type="advanced",
            source_based=True,
            filter='Node.Name == "cz.cesnet.kryten"',
            description="Globally filter out all messages originating from cz.cesnet.kryten detection node",
        )

        objects = [
            account_user,
            account_developer,
            account_maintainer,
            account_admin,
            group,
            global_filter,
        ]
        objects.extend(MentatFixtures.get_example_event_classes())
        for dbobject in objects:
            try:
                self.sqlservice.session.add(dbobject)
                self.sqlservice.session.commit()
                self.logservice.info("Added demo object to database: '%s'", str(dbobject))
            except Exception as exc:
                self.sqlservice.session.rollback()
                self.logservice.info(
                    "Unable to add demo object to database: '%s' (%s)",
                    str(dbobject),
                    str(exc),
                )

    def import_event_classes_to_db(self):
        """
        Import event classes into database.
        """
        for event_class in MentatFixtures.get_example_event_classes():
            try:
                self.sqlservice.session.add(event_class)
                self.sqlservice.session.commit()
                self.logservice.info("Added event class to database: '%s'", str(event_class))
            except Exception as exc:
                self.sqlservice.session.rollback()
                self.logservice.info(
                    "Unable to add event class to database: '%s' (%s)",
                    str(event_class),
                    str(exc),
                )

    def remove_from_db(self):
        """
        Remove data fixtures from database.
        """
        q_account_user = self.sqlservice.session.query(UserModel).filter(UserModel.login == "user")
        q_account_developer = self.sqlservice.session.query(UserModel).filter(UserModel.login == "developer")
        q_account_maintainer = self.sqlservice.session.query(UserModel).filter(UserModel.login == "maintainer")
        q_account_admin = self.sqlservice.session.query(UserModel).filter(UserModel.login == "admin")
        q_group = self.sqlservice.session.query(GroupModel).filter(GroupModel.name == "DEMO_GROUP")
        objects_to_delete = [
            q_account_user,
            q_account_developer,
            q_account_maintainer,
            q_account_admin,
            q_group,
        ]

        for event_class in MentatFixtures.get_example_event_classes():
            objects_to_delete.append(
                self.sqlservice.session.query(EventClassModel).filter(EventClassModel.name == event_class.name)
            )

        for q_dbobject in objects_to_delete:
            try:
                dbobject = q_dbobject.first()
                if dbobject:
                    self.sqlservice.session.delete(dbobject)
                    self.sqlservice.session.commit()
                    self.logservice.info("Deleted demo object from database: '%s'", str(dbobject))
            except Exception as exc:
                self.sqlservice.session.rollback()
                self.logservice.info("Unable to remove demo object from database: '%s'", str(exc))
