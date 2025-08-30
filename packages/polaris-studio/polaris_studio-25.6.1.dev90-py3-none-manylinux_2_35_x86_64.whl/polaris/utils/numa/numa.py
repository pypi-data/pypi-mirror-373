# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import psutil
import logging
import os
from pathlib import Path
import socket
from tempfile import gettempdir
from typing import List

from polaris.utils.file_utils import readlines
from polaris.utils.numa.numa_hardware_report import NumaHardware, NumaNodeHardware, numactl


def numa_available():
    if numactl is None:
        return False
    return NumaHardware.from_cli().available


def parse_numa_usage_file(f):
    num_threads = 1
    nodes_in_use = set()
    for line in (line for line in readlines(f) if ":" in line):
        key, val = line.strip().split(":")
        if key == "num threads":
            num_threads = int(val)
        if key == "numa nodes":
            nodes_in_use = [int(e) for e in val.strip().split(" ")]

    return {n: float(num_threads) / float(len(nodes_in_use)) for n in nodes_in_use}


def read_nodes_in_use():
    node_usage = {}
    logging.info(f"   Looking for numa files in {gettempdir()}")
    for f in Path(str(gettempdir())).glob(f"pstudio_proc_{socket.gethostname()}_*"):
        pid = int(f.name.split("_")[-1])
        if psutil.pid_exists(pid):
            logging.info(f"    => Found {f} which has a running pid")
            for n, t in parse_numa_usage_file(f).items():
                node_usage[n] = node_usage.get(n, 0) + t
        else:
            logging.info(f"    => Deleting numa node allocation file {f} as pid no longer exists")
            f.unlink()

    return node_usage


def write_nodes_in_use(nodes_to_use: List[NumaNodeHardware], num_threads: int):
    numa_options_file = Path(gettempdir()) / f"pstudio_proc_{socket.gethostname()}_{os.getpid()}"
    nodes = " ".join(str(e.node_id) for e in nodes_to_use)
    with open(numa_options_file, "w") as fp:
        fp.write(f"numa nodes: {nodes}\n")
        fp.write(f"num threads: {num_threads}\n")
        logging.debug(f"    Numa node file: {numa_options_file} - {nodes}")
    os.chmod(numa_options_file, 0o666)

    return numa_options_file


def get_numa_nodes_to_use(num_threads, numa_report=None, nodes_in_use=None):
    logging.info("    Getting numa nodes to use")
    numa_report = numa_report or NumaHardware.from_cli()

    # Figure out what nodes aren't in use
    node_usage = nodes_in_use if nodes_in_use is not None else read_nodes_in_use()
    for node_id, threads in node_usage.items():
        numa_report.nodes[node_id].cpus_in_use = threads

    # Best case scenario - we have a free node that is big enough
    n = [n for n in numa_report.nodes if n.cpus_in_use == 0 and n.num_cpus > num_threads]
    if n:
        logging.info("   => Picked single unused node")
        return n[:1]

    # next best scenario - we have a node that is big enough (pick the most free first)
    nodes = sorted(numa_report.nodes, key=lambda n: (-n.num_free_cpus, n.node_id))
    n = [n for n in nodes if n.num_free_cpus > num_threads]
    if n:
        logging.info("    => Picked single partially used node")
        return n[:1]

    # Fall back plan, just spread over all the remaining nodes
    num_satisfied, i = 0, 0
    n = []
    while num_satisfied < num_threads and i < len(nodes):
        num_satisfied += nodes[i].num_free_cpus
        n.append(nodes[i])
        i += 1
    logging.info(f"    => Spreading across nodes {n}")
    return n


def get_numactl_opts(nodes_to_use: List[NumaNodeHardware]):
    cpu_bind = f"--cpunodebind={','.join(str(e.node_id) for e in nodes_to_use)}"

    # mem_bind = f"--membind={','.join(str(e.node_id) for e in nodes_to_use)}"
    # We have removed the membind option as it was being too restrictive when calculated from the
    # core requirement - i.e. 2 nodes might be enough CPU but won't provide enough memory for the
    # model. This could be better handled by estimating (or user providing) the memory requirements
    # and then reserving nodes sufficient for the larger of the two (cpu reqs or mem requirements)
    # return ["numactl", cpu_bind, mem_bind]
    return ["numactl", cpu_bind]
