# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
from shutil import which
import subprocess
from typing import List
from pydantic import BaseModel

from polaris.utils.list_utils import first_and_only

numactl = which("numactl")


class NumaNodeHardware(BaseModel):
    node_id: int
    free: int
    total: int
    cpus: List[int]
    cpus_in_use: int = 0

    @property
    def num_cpus(self):
        return len(self.cpus)

    @property
    def num_free_cpus(self):
        return len(self.cpus) - self.cpus_in_use

    def __repr__(self):
        return f"[Node {self.node_id} free={self.num_free_cpus}]"


class NumaHardware(BaseModel):
    available: bool
    num_nodes: int
    nodes: List[NumaNodeHardware]

    @classmethod
    def not_available(cls):
        return cls(available=False, num_nodes=0, nodes=[])

    @classmethod
    def from_cli(cls):
        if numactl is None:
            return cls.not_available()
        return cls.from_str(subprocess.run(["numactl", "--hardware"], capture_output=True, text=True).stdout)

    @classmethod
    def from_str(cls, numactl_output):
        numactl_output = [e for e in numactl_output.split("\n") if e.strip() != ""]
        if len(numactl_output) == 1 or any("No NUMA available" in e for e in numactl_output):
            return cls.not_available()

        num_nodes = first_and_only(e for e in numactl_output if "available" in e)
        num_nodes = int(re.match("available: ([0-9]+) nodes", num_nodes)[1])

        def get_mb(line):
            return int(re.match(".*: ([0-9]+) MB", line)[1])

        def get_cpu(line):
            return [int(e) for e in line.split(":")[1].strip().split(" ")]

        totals = [get_mb(e) for e in numactl_output if re.match("node [0-9]+ size", e)]
        frees = [get_mb(e) for e in numactl_output if re.match("node [0-9]+ free", e)]
        cpus = [get_cpu(e) for e in numactl_output if re.match("node [0-9]+ cpus", e)]
        if len(totals) != len(frees) or len(totals) != num_nodes:
            raise RuntimeError("Couldn't parse numactl output - inconsistent number of nodes")

        nodes = [
            NumaNodeHardware(total=t, free=f, cpus=c, node_id=i)
            for t, f, c, i in zip(totals, frees, cpus, range(0, num_nodes))
        ]

        return cls(available=True, num_nodes=num_nodes, nodes=nodes)
