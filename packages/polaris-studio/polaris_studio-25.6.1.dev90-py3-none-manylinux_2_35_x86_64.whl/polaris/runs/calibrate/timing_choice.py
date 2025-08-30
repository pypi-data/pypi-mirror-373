# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import csv
import math
from pathlib import Path

import pandas as pd
from polaris.runs.calibrate.utils import calculate_normalized_rmse, log_data
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.scenario_file import load_json, write_json
from polaris.runs.wtf_runner import render_wtf_file, sql_dir
from polaris.utils.database.db_utils import commit_and_close, has_table, run_sql
from polaris.utils.dict_utils import denest_dict
from polaris.utils.logging_utils import function_logging

periods = {
    "NIGHT": range(0, 6),
    "AMPEAK": range(6, 9),
    "AMOFFPEAK": range(9, 12),
    "PMOFFPEAK": range(12, 16),
    "PMPEAK": range(16, 19),
    "EVENING": range(19, 24),
}


def hour_to_period(h):
    for k, r in periods.items():
        if h in r:
            return k
    raise RuntimeError(f"Can't time period for {h}")


columns = [
    "EAT_OUT",
    "ERRANDS",
    "HEALTHCARE",
    "LEISURE",
    "PERSONAL",
    "RELIGIOUS",
    "SERVICE",
    "SHOP_MAJOR",
    "SHOP_OTHER",
    "SOCIAL",
    "WORK",
    "WORK_PART",
    "WORK_HOME",
    "SCHOOL",
    "PICKUP",
    "HOME",
    "TOTAL",
]

columns_calib = [
    "EAT_OUT",
    "ERRANDS",
    "HEALTHCARE",
    "LEISURE",
    "PERSONAL",
    "RELIGIOUS",
    "SERVICE",
    "SHOP_MAJOR",
    "SHOP_OTHER",
    "SOCIAL",
]


@function_logging(f"Calibrating timing choice model")
def calibrate(config: ConvergenceConfig, current_iteration: ConvergenceIteration, use_planned: bool):
    output_files = PolarisInputs.from_dir(current_iteration.output_dir)
    model_file = Path(load_json(current_iteration.scenario_file)["ABM Controls"]["timing_choice_model_file"])
    top_level_key = "Activity_Timing_Choice_Model"
    output_dict = load_json(current_iteration.output_dir / "model_files" / model_file.name)[top_level_key]

    target = load_target(config.calibration.target_csv_dir / "timing_choice_targets.csv")
    simulated = load_simulated(output_files, config.population_scale_factor, use_planned)

    data = []
    for act_type in columns_calib:
        for period in periods:
            target_, simulated_ = target[act_type][period], simulated[act_type][period]
            var_name = f"C_{period}_{act_type}"
            old_v = float(output_dict[var_name])

            if simulated_ and target_ > 0:
                new_v = old_v + config.calibration.step_size * math.log(target_ / simulated_)
            else:
                new_v = old_v

            output_dict[var_name] = new_v
            data.append((act_type, period, target_, simulated_, old_v, new_v))

    log_data(data, ["act_type", "period", "target", "simulated", "old_v", "new_v"])
    write_json(config.data_dir / model_file, {top_level_key: output_dict})

    return calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))


def load_simulated(output_files, population_sample_rate, warm_calibrate):
    sql = f"""
        SELECT start_time as hour, EAT_OUT, ERRANDS, HEALTHCARE, LEISURE, PERSONAL, RELIGIOUS, SERVICE, SHOP_MAJOR,
                SHOP_OTHER, SOCIAL, WORK, WORK_PART, WORK_HOME, SCHOOL, PICKUP, HOME, total
        FROM activity_Start_Distribution
        WHERE activity_stage == '{'planned' if warm_calibrate else 'executed'}'
        """

    with commit_and_close(output_files.demand_db) as conn:
        if not has_table(conn, "activity_start_distribution"):
            run_sql(render_wtf_file(sql_dir / "activity_start_distribution.template.sql", population_sample_rate), conn)
            conn.commit()
        rows = conn.execute(sql).fetchall()

    df = pd.DataFrame(data=rows, columns=["hour"] + columns).fillna(0.0)
    df = df.assign(period=df.hour.apply(hour_to_period))
    df = df.groupby("period").sum() / df[columns].sum()
    return df.fillna(0.0).to_dict()


def load_target(target_file):
    target = {}
    records = []
    with open(target_file, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            row["PERIOD"] = row["PERIOD"].upper()
            records.append(row)

    for act_type in columns:
        target[act_type] = {}
        for period in periods:
            for row in records:
                if row["PERIOD"] == period:
                    share = float(row[act_type])
                    target[act_type][period] = share
    return target
