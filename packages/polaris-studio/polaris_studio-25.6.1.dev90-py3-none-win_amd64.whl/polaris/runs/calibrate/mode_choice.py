# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import math
from pathlib import Path

import pandas as pd
from polaris.runs.calibrate.utils import calculate_normalized_rmse, log_data
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.runs.scenario_file import load_json, write_json
from polaris.runs.wtf_runner import render_sql, render_wtf_file, sql_dir
from polaris.utils.database.db_utils import commit_and_close, has_table, read_and_close, run_sql
from polaris.utils.dict_utils import denest_dict
from polaris.utils.logging_utils import function_logging
from polaris.utils.math_utils import clamp


@function_logging(f"Calibrating mode choices")
def calibrate(config: ConvergenceConfig, current_iteration: ConvergenceIteration, use_planned: bool):
    mode_choice_model_file = Path(load_json(current_iteration.scenario_file)["ABM Controls"]["mode_choice_model_file"])
    top_level_key = "ADAPTS_Mode_Choice_Model"
    output_dict = load_json(current_iteration.output_dir / "model_files" / mode_choice_model_file.name)[top_level_key]

    rmse_non_transit = calibrate_non_transit_modes(config, current_iteration.files, output_dict, use_planned)
    rmse_transit = calibrate_boardings(config, current_iteration.files, output_dict, use_planned)
    write_json(config.data_dir / mode_choice_model_file, {top_level_key: output_dict})

    return rmse_non_transit, rmse_transit


def calibrate_non_transit_modes(
    config: ConvergenceConfig, output_files: PolarisInputs, output_dict: dict, use_planned: bool
):
    simulated = load_simulated(output_files, config.population_scale_factor, use_planned)
    target = load_targets(config.calibration.target_csv_dir / "mode_choice_targets.csv", remove_transit=True)

    data = []
    for trip_type in ["HBW", "HBO", "NHB"]:
        t = target[trip_type]
        s = simulated[trip_type]
        for var_name, mode in var_name_map.items():
            if var_name in boarding_based_modes:
                continue

            var_name = f"{trip_type}_ASC_{var_name}"
            new_v = old_v = float(output_dict[var_name])

            if s[mode] > 0 and t[mode] > 0:
                new_v = old_v + config.calibration.step_size * math.log(t[mode] / s[mode])

            output_dict[var_name] = new_v = clamp(new_v, -10, 10)

            data.append((trip_type, mode, var_name, t[mode], s[mode], old_v, new_v))
    log_data(data, ["trip_type", "mode", "var_name", "target", "simulated", "old_v", "new_v"])

    return calculate_normalized_rmse(denest_dict(simulated), denest_dict(target))


def calibrate_boardings(config: ConvergenceConfig, output_files: PolarisInputs, output_dict: dict, use_planned: bool):
    targets_file = config.calibration.target_csv_dir / "mode_choice_boarding_targets.csv"
    if not targets_file.exists() or use_planned:
        return -1

    target_boardings = load_target_boardings(targets_file)
    simulated_boardings = load_simulated_boardings(output_files, config.population_scale_factor)

    boarding_step_size = min(4.0, 10 * config.calibration.step_size)
    mode_map_for_calibration = {
        "TRAM": "METRO",
        "METRO": "METRO",
        "COMM": "COMM",
        "BUS": "BUS",
        "FERRY": None,
        "CABLE": "METRO",
        "LIFT": None,
        "FUNICULAR": None,
        "TROLLEY": "METRO",
        "MONO": "METRO",
    }

    simul = {"BUS": 0, "COMM": 0, "METRO": 0}
    target = {"BUS": 0, "COMM": 0, "METRO": 0}

    simulated_PACE = 0
    target_PACE = 0

    for (agency, transit_type), value in simulated_boardings.items():
        if mode_map_for_calibration.get(transit_type) is None:
            continue
        if agency != "PACE":
            simul[mode_map_for_calibration.get(transit_type)] += value
        else:
            simulated_PACE = value

    for (agency, transit_type), value in target_boardings.items():
        if mode_map_for_calibration.get(transit_type) is None:
            continue
        if agency != "PACE":
            target[mode_map_for_calibration.get(transit_type)] += value
        else:
            target_PACE = value

    boarding_based_map = {"XitWlk": "BUS", "XitDrv": "COMM", "RailWlk": "METRO", "RailDrv": "COMM"}
    data, sample_size, total_error_sq = [], 0, 0.0
    for var_name, transit_type in boarding_based_map.items():
        updated_transit_type = mode_map_for_calibration.get(transit_type)
        for trip_type in ["HBW", "HBO", "NHB"]:
            final_name = f"{trip_type}_ASC_{var_name}"
            new_v = old_v = float(output_dict[final_name])

            if simul[updated_transit_type] > 0 and target[updated_transit_type] > 0:
                new_v = old_v + boarding_step_size * math.log(
                    target[updated_transit_type] / simul[updated_transit_type]
                )

            new_v = clamp(new_v, -10, 10)
            if trip_type == "NHB" and updated_transit_type == "COMM":
                new_v = -999.0

            output_dict[final_name] = new_v
            data.append((trip_type, var_name, target[updated_transit_type], simul[updated_transit_type], old_v, new_v))

    ## PACE exception start!
    final_name = "bTT_multiplier_suburb"
    if final_name in output_dict:
        new_v = old_v = float(output_dict[final_name])

        if simulated_PACE > 0 and target_PACE > 0:
            new_v = old_v + boarding_step_size * math.log(simulated_PACE / target_PACE)

        output_dict[final_name] = new_v = clamp(new_v, -10, 10)
        data.append(("PACE", final_name, target_PACE, simulated_PACE, old_v, new_v))

    log_data(data, columns=["trip_type", "var_name", "target", "simulated", "old_v", "new_v"])

    return calculate_normalized_rmse(simul, target)


def add_home_based(df):
    def set_home_based(group):
        # first is always home based, subseuqent activities depend on the type of the prev activity
        return group.assign(home_based=[True, *list(group["type"][0:-1] == "HOME")])

    return df.groupby("person").apply(set_home_based).reset_index(drop=True)


def add_purpose_cols(df, factor):
    def f(group):
        return pd.Series(
            {
                # "HBW": factor * sum(group["home_based"] & (group["type"] == "WORK")),
                "HBW": factor * sum(group["type"] == "WORK"),
                "HBO": factor * sum(group["home_based"] & (group["type"] != "WORK")),
                "NHB": factor * sum(~group["home_based"] & (group["type"] != "HOME")),
                "TOTAL": factor * group.shape[0],
            }
        )

    return df.groupby("mode").apply(f).reset_index()


def load_simulated(output_files, population_sample_rate, use_planned):
    if use_planned:
        sql = """SELECT m.mode_id as mode, a.person, a.type 
                 FROM Activity a 
                 JOIN mode m ON a.mode = m.mode_description 
                 JOIN person p ON a.person = p.person
                 WHERE type <> 'NO_MOVE'
                 AND trip == 0
                 AND p.age > 16
                 ORDER BY a.person, a.start_time;
              """
        with read_and_close(output_files.demand_db) as conn:
            activities = add_home_based(pd.read_sql(sql, conn))
            purpose_counts = add_purpose_cols(activities, 1.0 / population_sample_rate)
    else:
        with commit_and_close(output_files.demand_db) as conn:
            if not has_table(conn, "Mode_Distribution_Adult"):
                run_sql(render_wtf_file(sql_dir / "mode_share.template.sql", population_sample_rate), conn)
                conn.commit()

            sql = "SELECT MODE, HBW, HBO, NHB, total as TOTAL from Mode_Distribution_Adult;"
            purpose_counts = pd.read_sql(sql, conn)

    counts = {"HBO": {}, "HBW": {}, "NHB": {}, "TOTAL": {}}
    mode_to_code = {"AUTO": 0, "AUTO-PASS": 2, "WALK": 8, "BIKE": 7, "TAXI": 9}
    code_to_mode = {v: k for k, v in mode_to_code.items()}

    for _, row in purpose_counts.iterrows():
        if row["mode"] not in code_to_mode:
            continue

        mode = code_to_mode[row["mode"]]
        counts["HBW"][mode] = row["HBW"]
        counts["HBO"][mode] = row["HBO"]
        counts["NHB"][mode] = row["NHB"]
        counts["TOTAL"][mode] = row["TOTAL"]

    for mode in mode_to_code:
        for type in ["HBW", "HBO", "NHB", "TOTAL"]:
            if mode not in counts[type]:
                counts[type][mode] = 0

    totals = {k: sum(inner.values()) for k, inner in counts.items()}

    return {
        key: {mode: counts[key][mode] / totals[key] if totals[key] > 0 else 0.0 for mode in mode_to_code}
        for key in counts
    }


def load_simulated_boardings(output_files, population_sample_rate):
    query_load = "SELECT agency, mode, boardings from boardings_by_agency_mode"

    with commit_and_close(ScenarioCompression.maybe_extract(output_files.demand_db)) as conn:
        if not has_table(conn, "boardings_by_agency_mode"):
            attach = {"a": str(ScenarioCompression.maybe_extract(output_files.supply_db))}
            run_sql(render_wtf_file(sql_dir / "transit.template.sql", population_sample_rate), conn, attach=attach)
            conn.commit()
        rows = conn.execute(query_load).fetchall()
        return {(agency, mode): boardings for agency, mode, boardings in rows}


def load_targets(file, remove_transit=True):
    rv = pd.read_csv(file).set_index("TYPE").to_dict(orient="index")
    rv = {k.upper(): v for k, v in rv.items()}
    if not remove_transit:
        return rv

    modes_to_zero = ("TRANSIT", "RAIL", "PNR", "PNRAIL")
    for trip_type in ["HBW", "HBO", "NHB", "TOTAL"]:
        transit_share = sum(v for mode, v in rv[trip_type].items() if mode in modes_to_zero)
        rv[trip_type] = {
            mode: v / (1 - transit_share) if mode not in modes_to_zero else 0.0 for mode, v in rv[trip_type].items()
        }
    return rv


def load_target_boardings(fname):
    return pd.read_csv(fname).set_index(["agency", "type"])["boardings"].to_dict()


var_name_map = {
    "Auto": "AUTO",
    "Getride": "AUTO-PASS",
    "XitWlk": "TRANSIT",
    "XitDrv": "PNR",
    "RailWlk": "RAIL",
    "RailDrv": "PNRAIL",
    "Walk": "WALK",
    "Bike": "BIKE",
    "Taxi": "TAXI",
}

boarding_based_map = {}
boarding_based_modes = ["XitWlk", "XitDrv", "RailWlk", "RailDrv"]

target_modes = {
    "AUTO": 0,
    "AUTO-PASS": 2,
    "TRANSIT": 4,
    "RAIL": 5,
    "WALK": 8,
    "BIKE": 7,
    "TAXI": 9,
    "PNR": 11,
    "PNRAIL": 13,
}
