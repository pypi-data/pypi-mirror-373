# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import math
from pathlib import Path

import pandas as pd
from polaris.runs.calibrate.utils import calculate_normalized_rmse, log_data
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.scenario_file import load_json, write_json
from polaris.runs.wtf_runner import render_wtf_file, sql_dir
from polaris.utils.database.db_utils import commit_and_close, has_table, run_sql
from polaris.utils.logging_utils import function_logging
from polaris.utils.math_utils import clamp


@function_logging("Calibrating destinations")
def calibrate(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    cconfig = config.calibration

    target = load_target(cconfig.target_csv_dir / "destination_choice_targets.csv")
    simulated = load_simulated(current_iteration.files.demand_db, current_iteration.files.supply_db)

    top_level_key = "ADAPTS_Destination_Choice_Model"
    model_file = Path(load_json(current_iteration.scenario_file)["ABM Controls"]["destination_choice_model_file"])
    output_dict = load_json(current_iteration.output_dir / "model_files" / model_file.name)[top_level_key]

    # We don't want to update the WORK asc unless there was ability for workplaces to change during the current iter
    is_workplace_changing = (
        config.workplace_stabilization.enabled
        and config.workplace_stabilization.should_choose_workplaces(current_iteration)
    )

    data, not_found_vars = [], []
    for var in map_vars:
        var_name = f"C_DISTANCE_{map_vars[var]}"
        if var_name not in output_dict:
            not_found_vars.append(var_name)

        # Get the current value - if it doesn't exist we will create it and give it a starting value of 1.0
        v = float(output_dict.get(var_name, 1.0))

        target_, simulated_ = target.get(var, 0), simulated.get(var, 0)
        if target_ <= 0 or simulated_ <= 0 or (var == "WORK" and not is_workplace_changing):
            new_v = v
        else:
            # Calculating delta - the value by which v will be changed
            delta = cconfig.step_size * math.log(simulated_ / target_)
            # When simulated > target, log(simulated/target) > 0, delta > 0
            # When simulated < target, log(simulated/target) < 0, delta < 0

            # Bounding new_v between (0.5v, 2v)
            lower_bound = max(0, (1 - cconfig.destination_vot_max_adj) * v)
            upper_bound = (1.0 + cconfig.destination_vot_max_adj) * v
            new_v = clamp(v + delta, lower_bound, upper_bound)

        data.append([var, map_vars[var], target_, simulated_, v, new_v])
        output_dict[var_name] = new_v

    if not_found_vars:
        logging.warning(f"Variables not found in the original Destination Choice File: {not_found_vars}")

    log_data(data, ["variable", "asc", "target", "modelled", "old_v", "new_v"])

    write_json(config.data_dir / model_file, {top_level_key: output_dict})
    return calculate_normalized_rmse(simulated, target)


def load_target(target_file, data_type="distance"):
    if data_type != "distance":
        return pd.read_csv(target_file).set_index("ACTIVITY_TYPE")["travel_time"].to_dict()
    return pd.read_csv(target_file).set_index("ACTIVITY_TYPE")["distance"].to_dict()


def load_simulated(demand_database, supply_database, data_type="distance"):
    with commit_and_close(demand_database) as conn:
        if (not has_table(conn, "ttime_By_ACT_Average")) or (not has_table(conn, "work_straight_line_dist_Average")):
            run_sql(render_wtf_file(sql_dir / "travel_time.template.sql", 1.0), conn, attach={"a": supply_database})
            conn.commit()

        sql = "SELECT acttype, ttime_avg, dist_avg from TTIME_by_ACT_Average"
        ttime_dist_data = conn.execute(sql).fetchall()
        if data_type == "distance":
            simulated = {act: avg_dist for act, tt, avg_dist in ttime_dist_data}
            # We replace work location trip distances with straight line distances from home to work to make
            # calibration more consistent with how POLARIS simulates work location choices, which is independent
            # of any stops on the way to work.
            sql = "SELECT dist_avg from work_straight_line_dist_Average"
            work_dist_dat = conn.execute(sql).fetchall()
            # assert len(work_dist_dat) == 1, "More than one average work-distance result"
            simulated["WORK"] = work_dist_dat[0][0]
        else:
            simulated = {act: tt for act, tt, avg_dist in ttime_dist_data}

        # TODO: document why are we doing this?
        simulated["OTHER"] = simulated.get("PERSONAL", 0)

        return simulated


map_vars = {
    "EAT OUT": "EAT_OUT",
    "OTHER": "OTHER",
    "PICKUP-DROPOFF": "PICK",
    "RELIGIOUS-CIVIC": "CIVIC",
    "SERVICE": "SERVICE",
    "SHOP-MAJOR": "MAJ_SHOP",
    "SHOP-OTHER": "MIN_SHOP",
    "SOCIAL": "SOCIAL",
    "WORK": "WORK",
    "LEISURE": "LEISURE",
    "ERRANDS": "ERRANDS",
    "HEALTHCARE": "HEALTHCARE",
}
