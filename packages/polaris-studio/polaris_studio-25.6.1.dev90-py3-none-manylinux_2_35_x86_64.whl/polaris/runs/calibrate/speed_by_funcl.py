# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import math
from pathlib import Path

import pandas as pd
from polaris.runs.calibrate.utils import calculate_normalized_rmse
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import load_link_types
from polaris.utils.logging_utils import function_logging
from polaris.runs.results.h5_results import H5_Results
import numpy as np


@function_logging("Calibrating speeds")
def calibrate(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    cconfig = config.calibration

    target = load_target(cconfig.target_csv_dir / "speed_by_funcl_targets.csv")
    simulated = load_simulated(current_iteration.files, config.population_scale_factor)

    # Update fspd_ab, fspd_ba based on 3am speeds in data?
    # Update capacity_expressway, capacity_arterial, etc. based on diff between targets in peak periods

    return calculate_normalized_rmse(simulated, target)


def load_target(target_file):
    if not target_file.exists():
        return None
    return pd.read_csv(target_file).set_index(["link_type", "time_period"])["speed"].to_dict()


def load_simulated(input_files: PolarisInputs, population_scale_factor):
    h5_results = H5_Results(ScenarioCompression.maybe_extract(input_files.result_h5))
    vmt_vht = h5_results.get_vmt_vht(population_scale_factor)

    vmt_vht_link = pd.concat([load_link_types(input_files.supply_db), vmt_vht], axis=1)
    vmt_vht_link_type = vmt_vht_link.groupby("type").sum().reset_index()

    def add_speed(label, hours):
        vmt = vmt_vht_link_type[[f"vmt_{i}" for i in hours]]
        vht = vmt_vht_link_type[[f"vht_{i}" for i in hours]]
        vmt_vht_link_type[f"vmt_{label}"] = vmt.sum(axis=1)
        vmt_vht_link_type[f"vht_{label}"] = vht.sum(axis=1)
        vmt_vht_link_type[f"speed_{label}"] = vmt_vht_link_type[f"vmt_{label}"] / vmt_vht_link_type[f"vht_{label}"]

    add_speed("AM", time_period_vars["AM"])
    add_speed("PM", time_period_vars["PM"])
    add_speed("OP", set(range(0, 24)) - time_period_vars["AM"] - time_period_vars["PM"])

    df = pd.melt(vmt_vht_link_type, id_vars=["type"], var_name="time_period", value_name="speed")
    df = df[df.time_period.str.contains("speed_")]
    df["time_period"] = df.time_period.str.replace("speed_", "")

    return df.set_index(["type", "time_period"]).speed.to_dict()


time_period_vars = {"AM": {6, 7, 8}, "PM": {15, 16, 17}}
