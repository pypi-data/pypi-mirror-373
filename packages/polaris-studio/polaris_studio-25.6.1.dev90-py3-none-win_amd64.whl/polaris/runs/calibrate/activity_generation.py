# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

import pandas as pd
from polaris.runs.calibrate.utils import calculate_normalized_rmse, log_data
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.scenario_file import load_json, write_json
from polaris.runs.wtf_runner import render_wtf_file, sql_dir
from polaris.utils.database.db_utils import commit_and_close, has_column, has_table, run_sql
from polaris.utils.logging_utils import function_logging
from polaris.runs.scenario_compression import maybe_extract


@function_logging("Calibrating activities...")
def calibrate(config: ConvergenceConfig, current_iteration: ConvergenceIteration, use_planned: bool):
    cconfig = config.calibration
    simulated = load_simulated(current_iteration.files.demand_db, use_planned)
    simulated = {k: rate for k, (rate, _) in simulated.items()}
    target = load_target(cconfig.target_csv_dir / "activity_generation_targets.csv")

    top_level_key = "Activity_Generation_Model"
    model_file = Path(load_json(current_iteration.scenario_file)["ABM Controls"]["activity_generation_model_file"])
    output_dict = load_json(current_iteration.output_dir / "model_files" / model_file.name)[top_level_key]

    skipped_keys, data = [], []
    for key in simulated:
        if key not in target:
            skipped_keys.append(key)
            continue

        person_type, act_type = key
        name = f"{person_type}_{act_type}_ACTIVITY_FREQ"
        old_v = target[key]
        new_v = output_dict[name] + target[key] - simulated[key]

        output_dict[name] = new_v if new_v > 0 else target[key]
        data.append((person_type, act_type, target[key], simulated[key], old_v, new_v))

    log_data(data, ["person_type", "act_type", "target", "modelled", "old_v", "new_v"])

    if skipped_keys:
        logging.warning("  Skipped the following person/activity pairs as no target exists:")
        for per, act in skipped_keys:
            logging.warning(f"  {str(per):>20} - {str(act):<20}")

    write_json(config.data_dir / model_file, {top_level_key: output_dict})
    return calculate_normalized_rmse(simulated, target)


def load_target(target_file):
    return pd.read_csv(target_file).set_index(["pertype", "acttype"])["target"].to_dict()


def load_simulated(demand_database, use_planned: bool):
    with commit_and_close(maybe_extract(demand_database)) as conn:

        def missing_col(col):
            return not has_column(conn, "activity_rate_distribution", col)

        if (
            not has_table(conn, "activity_rate_distribution")
            or missing_col("activity_stage")
            or missing_col("person_count")
        ):
            run_sql(render_wtf_file(sql_dir / "activity_distribution.template.sql", 1.0), conn)
            conn.commit()

        condition = f"activity_stage == '{'planned' if use_planned else 'executed'}'"
        sql = f'SELECT "pertype", "acttype", "rate", "person_count" from activity_rate_distribution WHERE {condition};'
        return {(p, a): (rate, per_count) for p, a, rate, per_count in conn.execute(sql).fetchall()}
