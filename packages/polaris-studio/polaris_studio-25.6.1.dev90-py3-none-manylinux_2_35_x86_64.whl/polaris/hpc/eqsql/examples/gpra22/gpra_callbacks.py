# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import copy
import logging
import shutil
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from datetime import datetime
from glob import glob
from pathlib import Path
from socket import gethostname
from typing import List

subprocess.run(f"{sys.executable} -m pip install boto3 pyomo", shell=True, check=True)

from polaris.utils.copy_utils import magic_copy
from transit_optimization import run_transit_optimization, copy_transit_files
from pricingSetter import PricingSetter
from veh_tech import factor_up_ev_plugs

from polaris.utils.func_utils import can_fail
from polaris.utils.logging_utils import function_logging
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.convergence.scenario_mods import get_scenario_for_iteration
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig, ConvergenceIteration
from polaris.runs.scenario_file import apply_modification, find_recursively_dic_with_key, load_json
from polaris.runs.mep_processing import MEP_Processor
from polaris.utils.database.db_utils import read_sql, read_about_model_value, write_about_model_value
from polaris.utils.database.db_utils import commit_and_close
from gpra_config import GPRAConfig

from polaris.runs.convergence.convergence_callback_functions import (
    clean_db_for_dta,
    copy_log_to,
    default_async_fn,
    default_end_of_loop_fn,
)

fmlm_revenue_sql = """
    SELECT case when revenue is null then 0.0 else revenue end as revenue
    FROM (SELECT sum(fare) as revenue, count(*) as demand FROM TNC_Request
    WHERE assigned_vehicle is not null and service_mode == 15);
"""


def get_type_counts(filename):
    return read_sql("select type, count(*) as cnt from trip group by type;", filename)


def iterations_fn(config):
    if config.user_data.transit:
        return config.filter_based_on_start_iter(
            [
                ConvergenceIteration(is_skim=True, iteration_number=1),
                ConvergenceIteration(iteration_number=1),
                ConvergenceIteration(iteration_number=2),
                ConvergenceIteration(iteration_number=3),
                ConvergenceIteration(iteration_number=4),
                ConvergenceIteration(iteration_number=5),
                ConvergenceIteration(is_skim=True, iteration_number=2),
                ConvergenceIteration(iteration_number=6),
                ConvergenceIteration(iteration_number=7),
                ConvergenceIteration(iteration_number=8),
                ConvergenceIteration(iteration_number=9),
                ConvergenceIteration(iteration_number=10),
                ConvergenceIteration(is_skim=True, iteration_number=3),
                ConvergenceIteration(iteration_number=11),
                ConvergenceIteration(iteration_number=12),
                ConvergenceIteration(iteration_number=13),
                ConvergenceIteration(iteration_number=14),
                ConvergenceIteration(iteration_number=15, is_last=True),
            ]
        )
    elif config.user_data.fmlm:
        return config.filter_based_on_start_iter(
            [
                ConvergenceIteration(is_skim=True, iteration_number=1),
                ConvergenceIteration(iteration_number=1),
                ConvergenceIteration(iteration_number=2),
                ConvergenceIteration(iteration_number=3),
                ConvergenceIteration(iteration_number=4),
                ConvergenceIteration(iteration_number=5),
                ConvergenceIteration(is_skim=True, iteration_number=2),
                ConvergenceIteration(iteration_number=6),
                ConvergenceIteration(iteration_number=7),
                ConvergenceIteration(iteration_number=8),
                ConvergenceIteration(iteration_number=9),
                ConvergenceIteration(iteration_number=10),
                ConvergenceIteration(is_skim=True, iteration_number=3),
                ConvergenceIteration(iteration_number=11),
                ConvergenceIteration(iteration_number=12),
                ConvergenceIteration(iteration_number=13),
                ConvergenceIteration(iteration_number=14),
                ConvergenceIteration(iteration_number=15, is_last=True),
            ]
        )

    # Or just use the default
    return config.iterations()


@function_logging("Before iteration setup")
def pre_loop_fn(config, iterations, inputs: PolarisInputs):
    with commit_and_close((config.data_dir / f"{config.db_name}-Demand.sqlite")) as conn:
        conn.execute("UPDATE trip set type = 22 WHERE type <= 10;")
        conn.commit()

    with commit_and_close((config.data_dir / f"{config.db_name}-Supply.sqlite")) as conn:
        conn.execute("UPDATE link set fspd_ba = 20 where fspd_ba < 10 and lanes_ba > 0;")
        conn.execute("UPDATE link set fspd_ab = 20 where fspd_ab < 10 and lanes_ab > 0;")
        conn.commit()

    copy_warm_start_files(config)

    if config.user_data.pricing:
        input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)

        gpra_config = config.user_data
        pricing_mods = {
            # NOTE: the following params used to exist on the ConvergenceConfig object but need to be moved to the
            # GPRA Config object (not done as we aren't actually running GPRA22 anymore)
            # The transit opt has costs that are not dep on scale_factor so assumes that budget
            # is relative to a 100% sample.
            "cordon_charge_dollar_per_entry": gpra_config.cordon_charge,
        }
        apply_modification(
            config.data_dir / "pricing_settings.yaml",
            pricing_mods,
            config.data_dir / "pricing_settings.yaml",
        )
        ps = PricingSetter(config.data_dir / "pricing_settings.yaml", supply_db=input_files.supply_db)

        ps.set_cordon_links_in_supply()

    if config.user_data.veh_tech and not config.start_iteration_from:
        factor_up_ev_plugs(inputs.supply_db, 2.5)


def copy_warm_start_files(config):
    gpra_config = config.user_data
    if gpra_config.is_base():
        return  # nothing to do as this run is the #1 source of warm start files

    # don't warm start if this is a restarted run, otherwise we lose any info that has been updated to this point
    if config.start_iteration_from:
        logging.info("Skipping warm-start as we are restarting a crashed run")
        return

    files_to_copy = ["highway_skim_file.omx", "transit_skim_file.omx"]

    if gpra_config.transit:
        # Transit runs start from the converged outputs of their non-transit twin
        previous_config: GPRAConfig = copy.copy(gpra_config)
        previous_config.transit = False
        files_to_copy += [f"{config.db_name}-{x}.sqlite" for x in ["Demand", "Supply", "Result"]]
        files_to_copy += [f"{config.db_name}-Result.h5"]

    else:
        # all other scenarios do their own abm init start but still need skims from base
        previous_config = GPRAConfig(city=gpra_config.city)
    src_run_id = previous_config.to_run_id()

    results_dir = Path(gpra_config.payload["put-results-here"])
    src_dir = results_dir / f"{src_run_id}_{previous_config.city}"

    logging.info(f"Copying warm-start outputs from run {src_dir}")

    for f in files_to_copy:
        logging.info(f"  - {f}")
        target_file = config.data_dir / f
        if target_file.exists():
            target_file.unlink()
        magic_copy(src_dir / f, target_file, recursive=False)
    logging.info(f"Finished copying warm-start files")


@function_logging("Start of loop processing")
def start_of_loop_fn(config: ConvergenceConfig, current_iteration, mods, scenario_file):
    gpra_config = config.user_data

    additional_budget_transit, additional_budget_fmlm, additional_budget = 0.0, 0.0, 0.0

    input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)

    # clean_db_for_abm(input_files)
    if current_iteration.is_dta:
        clean_db_for_dta(PolarisInputs.from_dir(config.data_dir, config.db_name))

    # always turn time-dependent routing on if results db exists in run directory
    mods["time_dependent_routing"] = input_files.result_h5.exists()

    if gpra_config.pricing:
        ps = PricingSetter(
            config.data_dir / "pricing_settings.yaml",
            supply_db=input_files.supply_db,
            demand_db=input_files.demand_db,
            result_db=input_files.result_h5,
        )

        first_regular_iter = current_iteration.iteration_number == 1 and not current_iteration.is_skim

        # only transit warm starts from something other than base
        if gpra_config.transit or not first_regular_iter:
            # Prior demand where tolling was on (i.e. warm_started from pricing=true or iter > 1)
            additional_budget = ps.get_total_revenue()
        else:  # first regular iteration of non-transit requires an estimate of revenue
            additional_budget = ps.get_total_estimated_revenue()

    if gpra_config.fmlm and gpra_config.transit:
        additional_budget_transit = 0.5 * additional_budget
        additional_budget_fmlm = 0.5 * additional_budget
    elif gpra_config.fmlm:
        additional_budget_transit = 0.0
        additional_budget_fmlm = additional_budget
    elif gpra_config.transit:
        additional_budget_transit = additional_budget
        additional_budget_fmlm = 0.0
    # do more stuff to parcel out to various levels

    if gpra_config.fmlm:
        json_dict = load_json(scenario_file)
        per_mi = find_recursively_dic_with_key(json_dict, "tncandride_cost_per_mile")["tncandride_cost_per_mile"]
        per_min = find_recursively_dic_with_key(json_dict, "tncandride_cost_per_minute")["tncandride_cost_per_minute"]
        base = find_recursively_dic_with_key(json_dict, "tncandride_base_fare")["tncandride_base_fare"]

        input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)
        with closing(sqlite3.connect(input_files.supply_db)) as conn:
            discount_rate_prev = read_about_model_value(conn, "fmlm_discount_rate", cast=float, default=0.0)
            if current_iteration.is_skim:
                revenue = max(1.0, float(read_sql(fmlm_revenue_sql, input_files.demand_db).iloc[0, 0]))
                revenue /= 1 - discount_rate_prev

                additional_budget_fmlm = min(additional_budget_fmlm, 0.49 * revenue)
                discount_rate = 0.5 + min(max(0.0, (additional_budget_fmlm) / revenue), 0.49)

                if gpra_config.fmlm and gpra_config.transit:
                    additional_budget_transit = max(0.0, additional_budget - additional_budget_fmlm)

                write_about_model_value(conn, "fmlm_discount_rate", discount_rate)
                conn.commit()
            else:
                discount_rate = discount_rate_prev

        mods["tncandride_cost_per_mile"] = per_mi * (1.0 - discount_rate)
        mods["tncandride_cost_per_minute"] = per_min * (1.0 - discount_rate)
        mods["tncandride_base_fare"] = base * (1.0 - discount_rate)

    if gpra_config.transit and current_iteration.is_skim:
        first_opt_itr = current_iteration.iteration_number == 1
        input_files = PolarisInputs.from_dir(config.data_dir, config.db_name)
        transit_mods = {
            # The transit opt has costs that are not dep on scale_factor so assumes that budget
            # is relative to a 100% sample.
            "additional_budget": additional_budget_transit / config.population_scale_factor,
            "cost_adjustment_factor": 1.4,
            "traffic_scale_factor": config.population_scale_factor,
            "additional_budget_factor_for_freq": 0.0,
        }
        modified_optim_file = apply_modification(
            Path(__file__).parent / "transit_optimization_settings.yaml",
            transit_mods,
            config.data_dir / "transit_optimization_settings.yaml",
        )

        run_transit_optimization(modified_optim_file, input_files.supply_db, input_files.demand_db, first_opt_itr)

    config.user_data.task_container.log(f"Start of loop {current_iteration}")


def get_scenario_json_fn(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    # Get the default set of mods
    mods, f = get_scenario_for_iteration(config, current_iteration)

    json_content = load_json(f)

    def get_value(key):
        return find_recursively_dic_with_key(json_content, key)[key]

    # TODO: JAMIE - Setting telecommute to be always base, revert for real GPRA
    if config.user_data.tele_commute_and_ecomm:
        mods["flexible_work_percentage"]: 0.66
        tele_mods = {
            "Z_CONSTANT": 0.7,
            "Z_FLEX_WORK_INDICATOR": 1.89,
            "O_CONSTANT": -0.46,
        }
    else:
        mods["flexible_work_percentage"]: 0.42
        tele_mods = {
            "Z_CONSTANT": -1.7,
            "Z_FLEX_WORK_INDICATOR": 1.89,
            "O_CONSTANT": -0.65,
        }
    # mods["flexible_work_percentage"]: 0.42
    # tele_mods = {
    #     "Z_CONSTANT": -1.7,
    #     "Z_FLEX_WORK_INDICATOR": 1.89,
    #     "O_CONSTANT": -0.65,
    # }

    tele_key = "telecommute_choice_model_file"
    mods[tele_key] = str(apply_modification(get_value(tele_key), tele_mods))

    tnc_key = "tnc_fleet_model_file"
    mods[tnc_key] = str(apply_modification(get_value(tnc_key), {"Operator_1.Operator_1_use_fmlm": True}))

    if config.user_data.signal_coord:
        mods["use_traffic_api"] = True

    if config.user_data.veh_tech:
        mods["L3_automation_cost"] = 1
    else:
        mods["L3_automation_cost"] = 7000

    veh_tech = "high" if config.user_data.veh_tech else "low"
    mods["fleet_vehicle_distribution_file_name"] = f"vehicle_distribution_fleet_2035_{veh_tech}.txt"
    mods["vehicle_distribution_file_name"] = f"vehicle_distribution_{config.db_name.lower()}_2035_{veh_tech}.txt"

    # Make sure that decision makers have the opportunity to choose from  the veh tech options set above
    is_first_normal = current_iteration.is_standard and current_iteration.iteration_number == 1
    replan_vehicle_ownership = (is_first_normal or current_iteration.is_abm_init) and config.num_outer_loops <= 1
    mods["Population synthesizer controls.replan.vehicle_ownership"] = replan_vehicle_ownership

    ecomm = "64" if config.user_data.tele_commute_and_ecomm else "32"
    mods["ecommerce_choice_model_file"] = f"{config.db_name}EcommerceChoiceModel_0_{ecomm}DelRate.json"

    return mods, f


def end_of_loop_fn(config, current_iteration: ConvergenceIteration, output_dir, polaris_inputs):
    """Put your post run processing code here."""
    logging.info("  GPRA Specific END OF LOOP")
    city = config.user_data.city
    run_id = config.user_data.to_run_id()
    log_folder = config.user_data.payload["put-logs-here"]

    # User code  goes here
    config.user_data.task_container.log(f"Finished loop {current_iteration}")

    name = f"{run_id}-{city}-{current_iteration}-{gethostname()}-{datetime.now().strftime('%Y-%M-%d')}.txt"
    copy_log_to(output_dir, Path(log_folder), name=name)

    if current_iteration.is_skim and config.user_data.transit:
        copy_transit_files(config.data_dir, config.data_dir / f"{config.db_name}_{current_iteration}")

    # Call the default eol code (if you want to)
    default_end_of_loop_fn(config, current_iteration, output_dir, polaris_inputs)


def build_polaris_crash_handler(config):
    run_id = config.user_data.to_run_id()
    log_folder = config.user_data.payload["put-logs-here"]

    @can_fail
    def polaris_crash_handler(output_dir, stderr_buffer):
        with open(output_dir / "log" / "polaris_progress.log", "a") as log:
            log.write("\nPOLARIS crashed, stdout and stderr appended here (should contain stack trace):\n")
            for line in stderr_buffer:
                log.write(line + "\n")
        return copy_log_to(output_dir, Path(log_folder), name=f"{run_id}-{output_dir.name}-CRASH.txt")

    return polaris_crash_handler


def async_end_of_loop_fn(config: ConvergenceConfig, current_iteration: ConvergenceIteration, output_dir):
    default_async_fn(config, current_iteration, output_dir)

    # We need to run MEP on the last iteration BEFORE the data is deleted
    if current_iteration.is_last:
        mep = MEP_Processor()
        mep.create_mep_inputs(output_dir, PolarisInputs.from_dir(output_dir, config.db_name))

    # if not (current_iteration.is_last or current_iteration.next_iteration.is_last):
    #     delete_big_files(output_dir)

    # We copy back and delete iterations as we go
    city = config.user_data.city
    run_id = config.user_data.to_run_id()
    results_dir = Path(config.user_data.payload["put-results-here"])
    dest_iteration_dir = results_dir / f"{run_id}_{city}" / f"{city}_{current_iteration}"
    magic_copy(str(output_dir), str(dest_iteration_dir))
    shutil.rmtree(output_dir)


def post_loop_fn(config: ConvergenceConfig, iterations: List[ConvergenceIteration]):
    city = config.user_data.city

    results_dir = Path(config.user_data.payload["put-results-here"])
    output_folder = results_dir / f"{config.user_data.to_run_id()}_{city}"
    magic_copy(str(config.data_dir), str(output_folder))

    delete_all_files(config.data_dir)


@can_fail
@function_logging("Deleting big files in {output_dir}")
def delete_big_files(output_dir):
    def foo(pattern):
        return glob(str(output_dir / f"*{pattern}")) + glob(str(output_dir / f"*{pattern}.tar.gz"))

    files_to_delete = []  # foo("-Result.sqlite") + foo("highway_skim_file.bin") + foo("transit_skim_file.bin")
    for f in files_to_delete:
        logging.info(f"  - {f}")
        Path(f).unlink(missing_ok=True)


@can_fail
@function_logging("Deleting all files in {data_dir}")
def delete_all_files(data_dir):
    files = [e for ext in ["sqlite", "h5", "omx", "hdf5", "gz"] for e in Path(data_dir).rglob(f"*.{ext}")]
    logging.info(f"Starting with big files (sqlite, omx, h5, tar.gz)")
    for f in files:
        logging.info(f"  {f.name} - {f.stat().st_size}")
        f.unlink()
        time.sleep(1)  # put a 1 sec delay between each big file to prevent wsl delete bug
    remaining_size = sum(f.stat().st_size for f in Path(data_dir).glob("**/*") if f.is_file())
    logging.info(f"Now deleting whatever remains ({remaining_size} bytes)")
    shutil.rmtree(data_dir)
