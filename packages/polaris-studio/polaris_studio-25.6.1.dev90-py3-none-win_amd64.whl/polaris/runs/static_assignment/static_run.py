# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

from polaris.runs.calibrate.calibration import end_of_loop_fn_for_calibration
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_callback_functions import (
    copy_back_files,
    copy_tables_to_stats_db,
    run_wtf_analysis,
)
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.convergence.convergence_runner import run_polaris_convergence
from polaris.runs.convergence.scenario_mods import base_scenario_mods
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.run_utils import copy_replace_file
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.runs.static_assignment.assign_skim import assignment_skimming
from polaris.runs.static_assignment.external_matrices import build_external_trip_matrices
from polaris.runs.static_assignment.free_flow_skimmer import free_flow_skimming
from polaris.runs.static_assignment.static_assignment_inputs import STAInputs
from polaris.utils.cmd_runner import run_cmd
from polaris.utils.logging_utils import function_logging
from polaris.analyze.kpi_utils import planning_kpis


@function_logging("  Polaris run with Static Traffic Assignment")
def static_run(
    model_path: Path,
    sta_param=None,
    save_assignment_results=True,
    pces={"SOV": 1.0, "TAXI": 1.0, "MD_TRUCK": 2.5, "HD_TRUCK": 4.0, "BPLATE": 2.0, "LD_TRUCK": 1.8},
):
    from polaris import Polaris

    assig_pars = sta_param or STAInputs()
    mod_pth = Path(model_path)
    pol = Polaris.from_dir(mod_pth)
    config = pol.run_config
    config.do_abm_init = config.do_abm_init or pol.result_file.exists()
    inputs = PolarisInputs.from_dir(mod_pth)

    if not inputs.transit_skim.exists():
        raise FileNotFoundError("Transit skim file not found. File is a strict requirement for this procedure")

    external_trips = build_external_trip_matrices(inputs.supply_db, inputs.demand_db, config.skim_interval_endpoints)

    if config.do_skim:
        if inputs.highway_skim.exists():
            logging.warning("Run settings indicate skimming, but highway skims were found. Skimming will be skipped.")
        else:
            free_flow_skimming(config, inputs)
    config.do_skim = False

    def end_of_loop_fn(
        config: ConvergenceConfig,
        current_iteration: ConvergenceIteration,
        output_dir: Path,
        polaris_inputs: PolarisInputs,
    ):  # pragma : no cover

        assignment_skimming(
            external_trips,
            assig_pars,
            config,
            current_iteration,
            output_dir,
            polaris_inputs,
            save_assignment_results,
            pces=pces,
        )

        logging.info("  Finished run")

        copy_back_files(config, current_iteration)
        logging.info("    finished copying back files")

        copy_replace_file(polaris_inputs.supply_db, output_dir)

        end_of_loop_fn_for_calibration(config, current_iteration, output_dir)

    run_polaris_convergence(
        config,
        scenario_file_fn=scenario_mods_for_skimming,
        end_of_loop_fn=end_of_loop_fn,
        async_end_of_loop_fn=static_async_fn,
        cmd_runner=run_cmd_ignore_errors,
    )


def run_cmd_ignore_errors(cmd, working_dir, printer=print, ignore_errors=False, stderr_buf=None, **kwargs):
    run_cmd(cmd, working_dir, printer, ignore_errors=True, stderr_buf=stderr_buf)


def scenario_mods_for_skimming(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    mods, scenario_file = base_scenario_mods(config, current_iteration)
    mods["General simulation controls.early_exit"] = "after_activity_gen"
    mods["ABM Controls.tnc_feedback"] = False
    mods["Routing and skimming controls.time_dependent_routing"] = True
    return mods, scenario_file


@function_logging("        ~ RUNNING in background thread for iteration {current_iteration}")
def static_async_fn(config: ConvergenceConfig, curr_iter: ConvergenceIteration, output_dir):  # pragma : no cover
    run_wtf_analysis(config, curr_iter)

    # Use the above data to store fast (to read) kpis
    if not curr_iter.is_skim:
        from polaris.analyze.result_kpis import ResultKPIs

        kpi = ResultKPIs.from_iteration(curr_iter, include_kpis=planning_kpis)
        kpi.cache_all_available_metrics()

    copy_tables_to_stats_db(config, curr_iter)
    if not curr_iter.is_last:
        ScenarioCompression(output_dir).compress()
