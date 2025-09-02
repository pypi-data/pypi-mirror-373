#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
Benchmarking module for the :py:mod:`mentat.services.whois` module.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import random
import timeit

import mentat.datatype.sqldb
import mentat.services.whois

# -------------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------------


def random_network():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.0"


def random_ips(networks):
    ips = []
    for netw in networks:
        chunks = netw.split(".")
        chunks[-1:] = [str(random.randint(1, 255))]
        ips.append(".".join(chunks))
    return ips


def prepare_whois_data():
    mentat.services.sqlstorage.init(
        {
            "__core__database": {
                "sqlstorage": {
                    "url": "postgresql://mentat:mentat@localhost/mentat_bench",
                    "echo": False,
                }
            }
        }
    )
    mentat.services.sqlstorage.service().database_drop()
    mentat.services.sqlstorage.service().database_create()

    networks = {}
    group = mentat.datatype.sqldb.GroupModel(name="abuse@cesnet.cz", source="manual", description="abuse@cesnet.cz")
    for i in range(3000):
        netw = random_network()
        while netw in networks:
            netw = random_network()
        networks[netw] = netw
        obj = mentat.datatype.sqldb.NetworkModel()
        obj.source = "benchmark"
        obj.netname = f"NET-{i}"
        obj.network = netw
        group.networks.append(obj)
    mentat.services.sqlstorage.service().session.add(group)

    mentat.services.sqlstorage.service().session.commit()
    mentat.services.sqlstorage.service().session.flush()
    return networks


WHOIS = None
IPS = None

# -------------------------------------------------------------------------------
# BENCHMARK TESTS
# -------------------------------------------------------------------------------


def b001():
    global WHOIS  # pylint: disable=locally-disabled,global-statement
    WHOIS = mentat.services.whois.WhoisService([mentat.services.whois.SqldbWhoisModule().setup()])


def b002():
    WHOIS.lookup(random.choice(IPS))


# -------------------------------------------------------------------------------


#
# Performance benchmarking of :py:mod:`pynspect.jpath` module.
#
if __name__ == "__main__":
    nets = prepare_whois_data()
    IPS = random_ips(nets)

    print(f"\n BENCHMARKING MENTAT.WHOIS MODULE (v{mentat.__version__})")
    print(f" {datetime.datetime.now()!s}\n")

    print("=" * 84)
    print(" {:22s} | {:16s} | {:20s} | {:20s}".format("Name", "Iterations (#)", "Duration (s)", "Speed (#/s)"))
    print("=" * 84)
    FORMAT_PTRN = " {:22s} | {:16,d} | {:20.10f} | {:15,.3f}"

    # ---------------------------------------------------------------------------

    ITERATIONS = 30

    #
    # Parsing of single reasonably complex JPath without caching.
    #
    RESULT = timeit.timeit("b001()", number=ITERATIONS, setup="from __main__ import b001")
    SPEED = ITERATIONS / RESULT
    print(FORMAT_PTRN.format("whois setup", ITERATIONS, RESULT, SPEED))

    # ---------------------------------------------------------------------------

    ITERATIONS = 10000

    #
    # Parsing of random reasonably complex JPath without caching.
    #
    RESULT = timeit.timeit("b002()", number=ITERATIONS, setup="from __main__ import b002")
    SPEED = ITERATIONS / RESULT
    print(FORMAT_PTRN.format("whois lookup", ITERATIONS, RESULT, SPEED))

    # ---------------------------------------------------------------------------

    print("=" * 84)
