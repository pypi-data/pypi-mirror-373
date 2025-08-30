# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shutil
import sqlite3
from contextlib import closing
from distutils.dir_util import copy_tree
from glob import glob
from pathlib import Path
from socket import gethostname

from bin.hpc.python.gpra22.transit_optimization import run_transit_optimization, copy_transit_files
from gpra22.gpra_db import update_job

import pandas as pd
from polaris.runs.convergence.convergence_callback_functions import (
    copy_log_to,
    default_async_fn,
    default_end_of_loop_fn,
)
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.convergence.scenario_mods import get_scenario_for_iteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.scenario_file import apply_modification, find_recursively_dic_with_key, load_json
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.func_utils import can_fail
from polaris.utils.logging_utils import function_logging

fmlm_revenue_sql = """
    SELECT case when revenue is null then 0.0 else revenue end as revenue
    FROM (SELECT sum(fare) as revenue, count(*) as demand FROM TNC_Request
    WHERE assigned_vehicle is not null and service_mode == 15);
"""


def load_sql(filename, sql):
    with closing(sqlite3.connect(filename)) as conn:
        return pd.read_sql(sql, conn)


def get_type_counts(filename):
    return load_sql(filename, "select type, count(*) as cnt from trip group by type;")


def iterations_fn(config):
    # This can be useful for debugging
    # return [
    #     ConvergenceIteration(is_skim=True),
    #     ConvergenceIteration(is_abm_init=True),
    #     ConvergenceIteration(iteration_number=1),
    #     ConvergenceIteration(iteration_number=2),
    #     ConvergenceIteration(iteration_number=3),
    #     ConvergenceIteration(iteration_number=4, is_last=True),
    # ]

    if config.user_data["transit"] or config.user_data["fmlm"]:
        return [
            ConvergenceIteration(is_skim=True, iteration_number=1),
            ConvergenceIteration(iteration_number=1),
            ConvergenceIteration(iteration_number=2),
            ConvergenceIteration(iteration_number=3),
            ConvergenceIteration(is_skim=True, iteration_number=2),
            ConvergenceIteration(iteration_number=4),
            ConvergenceIteration(iteration_number=5),
            ConvergenceIteration(iteration_number=6),
            ConvergenceIteration(is_skim=True, iteration_number=3),
            ConvergenceIteration(iteration_number=7),
            ConvergenceIteration(iteration_number=8),
            ConvergenceIteration(iteration_number=9, is_last=True),
        ]

    else:
        return [
            # ConvergenceIteration(is_skim=True),
            ConvergenceIteration(is_abm_init=True, iteration_number=1),
            ConvergenceIteration(iteration_number=2),
            ConvergenceIteration(iteration_number=3),
            ConvergenceIteration(iteration_number=4),
            ConvergenceIteration(iteration_number=5, is_last=True),
        ]

    # Or just use the default
    return config.iterations()


def pre_loop_fn(config, iterations, inputs):
    with closing(sqlite3.connect(config.data_dir / f"{config.db_name}-Demand.sqlite")) as conn:
        conn.execute("UPDATE trip set type = 22 WHERE type <= 10;")
        conn.commit()

    with closing(sqlite3.connect(config.data_dir / f"{config.db_name}-Supply.sqlite")) as conn:
        conn.execute("UPDATE link set fspd_ba = 20 where fspd_ba < 10 and lanes_ba > 0;")
        conn.execute("UPDATE link set fspd_ab = 20 where fspd_ab < 10 and lanes_ab > 0;")
        conn.commit()

    copy_warm_start_files(config)

    # if config.user_data['omers-key']:
    #     input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)
    #     ps = PricingSetter(config.data_dir / "pricing_settings.yaml", supply_db=input_files.supply_db)
    #     ps.set_cordon_links_in_supply()


def copy_warm_start_files(config):
    transit_config = config.user_data

    run_id = transit_config.get("run-id")
    base_city = transit_config.get("city")

    if run_id == "transit_000":
        return  # nothing to do as this run is the #1 source of warm start files

    files_to_copy = ["highway_skim_file.omx"]
    files_to_copy += [f"{config.db_name}-{x}.sqlite" for x in ["Demand", "Result"]]

    twin_id = "transit_000"

    # results_dir = Path(config.user_data["where-are-local-results"])
    results_dir = Path(config.user_data["put-results-here"])

    src_dir = results_dir / f"{twin_id}_{base_city}"

    logging.info(f"Copying warm-start outputs from run {src_dir}")

    for f in files_to_copy:
        logging.info(f"  - {f}")
        shutil.copyfile(src_dir / f, config.data_dir / f)


@function_logging("Start of loop processing")
def start_of_loop_fn(config: ConvergenceConfig, current_iteration, mods, scenario_file):
    gpra_config = config.user_data

    additional_budget_transit, additional_budget_fmlm, additional_budget = 0.0, 0.0, 0.0

    # always turn time-dependent routing on if results db exists in run directory
    input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)
    if (input_files.result_db).exists():
        mods["time_dependent_routing"] = True
        mods["time_dependent_routing_weight_factor"] = 1.0 / float(current_iteration.iteration_number)

    # if gpra_config.pricing:
    #     input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)
    #     ps = PricingSetter(
    #         config.data_dir / "pricing_settings.yaml",
    #         supply_db=input_files.supply_db,
    #         demand_db=input_files.demand_db,
    #         result_db=input_files.result_db,
    #     )
    #     first_regular_iter = current_iteration.iteration_number == 1 and not current_iteration.is_skim

    #     # only transit warm starts from something other than base
    #     if gpra_config.transit or not first_regular_iter:
    #         # Prior demand where tolling was on (i.e. warm_started from pricing=true or iter > 1)
    #         additional_budget = ps.get_total_revenue()
    #     else:  # first regular iteration of non-transit requires an estimate of revenue
    #         additional_budget = ps.get_total_estimated_revenue()

    # if gpra_config['fmlm'] and gpra_config['transit']:
    #     additional_budget_transit = 0.5 * additional_budget
    #     additional_budget_fmlm = 0.5 * additional_budget
    # elif gpra_config.fmlm:
    #     additional_budget_transit = 0.0
    #     additional_budget_fmlm = additional_budget
    # elif gpra_config.transit:
    #     additional_budget_transit = additional_budget
    #     additional_budget_fmlm = 0.0
    # do more stuff to parcel out to various levels

    fmlm_revenue = 0.0
    discount_rate = 0.5
    if gpra_config["fmlm"]:
        json_dict = load_json(scenario_file)
        per_mi = find_recursively_dic_with_key(json_dict, "tncandride_cost_per_mile")["tncandride_cost_per_mile"]
        per_min = find_recursively_dic_with_key(json_dict, "tncandride_cost_per_minute")["tncandride_cost_per_minute"]
        base = find_recursively_dic_with_key(json_dict, "tncandride_base_fare")["tncandride_base_fare"]

        mods["tncandride_cost_per_mile"] = per_mi * (1.0 - discount_rate)
        mods["tncandride_cost_per_minute"] = per_min * (1.0 - discount_rate)
        mods["tncandride_base_fare"] = base * (1.0 - discount_rate)

        first_opt_itr = current_iteration.iteration_number == 1
        fmlm_revenue = max(1.0, load_sql(input_files.demand_db, fmlm_revenue_sql).iloc[0, 0])
        if not first_opt_itr:
            fmlm_revenue /= 1 - discount_rate

    if gpra_config["transit"] and current_iteration.is_skim:
        first_opt_itr = current_iteration.iteration_number == 1
        input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)

        fmlm_subsidy_takeaway = fmlm_revenue * discount_rate
        fmlm_subsidy_takeaway = 0.0

        transit_mods = {
            # The transit opt has costs that are not dep on scale_factor so assumes that budget
            # is relative to a 100% sample.
            "fmlm_subsidy_takeaway": fmlm_subsidy_takeaway / config.population_scale_factor,
            "additional_budget": additional_budget_transit / config.population_scale_factor,
            "traffic_scale_factor": config.population_scale_factor,
            # NOTE: the following params used to exist on the ConvergenceConfig object but need to be moved to the
            # GPRA Config object (not done as we aren't actually running GPRA22 anymore)
            "cost_adjustment_factor": gpra_config.cost_adjustment_factor,
            "budget_lb_agency_type": gpra_config.budget_lb_agency_type,
            "cost_reduction_target": gpra_config.cost_reduction_target if first_opt_itr else 0.0,
        }
        modified_optim_file = apply_modification(
            Path(__file__).parent / "transit_optimization_settings.yaml",
            transit_mods,
            config.data_dir / "transit_optimization_settings.yaml",
        )

        run_transit_optimization(modified_optim_file, input_files.supply_db, input_files.demand_db, first_opt_itr)

    update_job(config.user_data["run-id"], "RUNNING", f"Start of loop {current_iteration}")


def get_scenario_json_fn(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    # Get the default set of mods
    mods, f = get_scenario_for_iteration(config, current_iteration)

    json_content = load_json(f)

    def get_value(key):
        return find_recursively_dic_with_key(json_content, key)[key]

    tnc_key = "tnc_fleet_model_file"
    mods[tnc_key] = str(apply_modification(get_value(tnc_key), {"Operator_1.Operator_1_use_fmlm": True}))

    return mods, f


def end_of_loop_fn(config, current_iteration: ConvergenceIteration, output_dir, polaris_inputs):
    """Put your post run processing code here."""
    logging.info("  GPRA Specific END OF LOOP")
    city = config.user_data["city"]
    run_id = config.user_data["run-id"]
    log_folder = config.user_data["put-logs-here"]

    copy_log_to(output_dir, Path(log_folder), name=f"{run_id}-{city}-{current_iteration}-{gethostname()}.txt")

    if current_iteration.is_skim and config.user_data["transit"]:
        copy_transit_files(config.data_dir, config.data_dir / f"{config.db_name}_{current_iteration}")

    # Call the default eol code (if you want to)
    default_end_of_loop_fn(config, current_iteration, output_dir, polaris_inputs)

    update_job(config.user_data["run-id"], "RUNNING", f"End of loop {current_iteration}")


def build_polaris_crash_handler(config):
    run_id = config.user_data["run-id"]
    log_folder = config.user_data["put-logs-here"]

    @can_fail
    def polaris_crash_handler(output_dir, stderr_buffer):
        with open(output_dir / "log" / "polaris_progress.log", "a") as log:
            log.write("\nPOLARIS crashed, stdout and stderr appended here (should contain stack trace):\n")
            for line in stderr_buffer:
                log.write(line + "\n")
        return copy_log_to(output_dir, Path(log_folder), name=f"{run_id}-{output_dir.name}-CRASH.txt")

    return polaris_crash_handler


async_end_of_loop_fn = default_async_fn


def post_loop_fn(config, iterations):
    early_iterations, final_iter = iterations[:-2], iterations[-1]
    city = config.user_data["city"]
    for iter in early_iterations:
        delete_big_files(config.data_dir / f"{city}_{iter}")

    results_dir = Path(config.user_data["put-results-here"])
    output_folder = results_dir / f"{config.user_data['run-id']}_{city}"
    mkdir_p(output_folder)
    copy_tree(str(config.data_dir), str(output_folder), preserve_mode=False, preserve_times=False)


@can_fail
def delete_big_files(output_dir):
    def f(pattern):
        return glob(str(output_dir / f"*{pattern}")) + glob(str(output_dir / f"*{pattern}.tar.gz"))

    files_to_delete = f("-Result.sqlite") + f("highway_skim_file.omx") + f("transit_skim_file.omx")
    logging.info("Deleting big files:")
    for f in files_to_delete:
        logging.info(f"  - {f}")
        Path(f).unlink(missing_ok=True)
