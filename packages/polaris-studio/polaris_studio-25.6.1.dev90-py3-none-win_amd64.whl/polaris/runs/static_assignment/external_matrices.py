# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path
from typing import List, Dict

from scipy.sparse._coo import coo_matrix as coo_type

from polaris.analyze.trip_metrics import TripMetrics


def build_external_trip_matrices(supply_path: Path, demand_path: Path, intervals: List[int]) -> Dict[int, coo_type]:
    trip_metr = TripMetrics(supply_path, demand_path)

    external_matrices = {}

    modes = ["SOV", "TAXI", "MD_TRUCK", "HD_TRUCK", "BPLATE", "LD_TRUCK"]
    for prev_interv, interv in zip([0] + intervals[:-1], intervals):
        matrix = trip_metr.trip_matrix(from_start_time=prev_interv * 60, to_start_time=interv * 60, modes=modes)
        external_matrices[interv] = matrix.to_aeq()
    return external_matrices
