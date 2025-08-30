# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from pathlib import Path
from threading import Thread
from time import perf_counter
from typing import Union

from polaris.network.checker.supply_checker import SupplyChecker
from polaris.runs import polaris_runner
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_callback_functions import (
    default_end_of_loop_fn,
    default_start_of_loop_fn,
    do_nothing,
    default_async_fn,
    default_pre_loop_fn,
    default_iterations_fn,
)
from polaris.runs.convergence.scenario_mods import get_scenario_for_iteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.utils.checker_utils import check_critical
from polaris.utils.cmd_runner import run_cmd, no_printer
from polaris.utils.numa.numa import numa_available
from polaris.version import git_sha


def setup_from_backup(config: ConvergenceConfig):
    if config.backup_dir is None:
        return

    files = PolarisInputs.from_dir(config.data_dir, config.db_name)
    if not config.backup_dir.exists():
        logging.info("Creating a backup dir with files from root")
        # store the original inputs if no backup exists
        config.backup_dir.mkdir(parents=True)
        files.copy_to_dir(config.backup_dir, copy_skims=True)
    elif config.start_iteration_from is None:
        logging.info("Copying files from backup dir to root")
        files.restore_from_dir(config.backup_dir, restore_skims=True)
    else:
        logging.info("Skipping use of backup folder as we are restarting a failed run")


def run_polaris_convergence(
    config: Union[str, ConvergenceConfig],
    iterations_fn=default_iterations_fn,
    pre_loop_fn=default_pre_loop_fn,
    start_of_loop_fn=default_start_of_loop_fn,
    scenario_file_fn=get_scenario_for_iteration,
    end_of_loop_fn=default_end_of_loop_fn,
    post_loop_fn=do_nothing,
    async_end_of_loop_fn=default_async_fn,
    polaris_crash_handler=do_nothing,
    printer=no_printer,
    cmd_runner=run_cmd,
    result_evaluator=do_nothing,
):
    if isinstance(config, str) or isinstance(config, os.PathLike):
        config = ConvergenceConfig.from_file(Path(config))

    logging.info(f"Using Polaris-Studio git sha: {git_sha}")
    logging.info("Running Convergence Loop using the following config")
    [logging.info(x) for x in config.pretty_print("  ")]
    config.check_exe()

    # Figure out what iterations are being run
    iterations = link_iterations(iterations_fn(config))
    logging.info("Running the following iterations: ")
    logging.info(f"   {[str(e) for e in iterations]}")

    has_freight = any(config.freight.should_do_anything(e) for e in iterations)
    check_model_pre_run(config, has_freight)

    polaris_inputs = PolarisInputs.from_dir(config.data_dir, config.db_name)

    os.chdir(config.data_dir)

    logging.info("Setting backups...")
    setup_from_backup(config)

    threads = []

    # Callback: Setup that needs to be done before we start iterating
    pre_loop_fn(config, iterations, polaris_inputs)

    for current_iteration in iterations:
        logging.info("")
        logging.info(f"Starting iteration: {current_iteration}")

        # Callback: the user defined config function to get the scenario_file
        mods, scenario_file = scenario_file_fn(config, current_iteration)

        # Callback: the start of loop setup
        start_of_loop_fn(config, current_iteration, mods, scenario_file)

        current_iteration.runtime = -perf_counter()
        # run executable
        output_dir, scenario_file_ = polaris_runner.run(
            config.data_dir,
            config.polaris_exe,
            str(scenario_file),
            mods,
            config.num_threads,
            printer=printer,
            crash_handler=polaris_crash_handler,
            num_retries=config.num_retries,
            result_evaluator=result_evaluator,
            run_command=cmd_runner,
            numa_threads=config.num_threads if config.use_numa and numa_available() else None,
        )

        # handy if wanting to test something in the post-iteration phase - comment out above line, uncomment these two
        # scenario_file_ = apply_modification(scenario_file, mods)
        # output_dir = get_desired_output_dir(scenario_file_, config.data_dir)

        logging.info(f"Model run results are in dir: {output_dir}")
        current_iteration.runtime += perf_counter()
        current_iteration.set_output_dir(output_dir, scenario_file_, config.db_name)

        # Callback: end of loop processing which needs to be done before the next iteration
        end_of_loop_fn(config, current_iteration, output_dir, polaris_inputs)

        # Callback: the end of loop processing which can be run in a background thread
        t = run_async(async_end_of_loop_fn, config, current_iteration, output_dir)
        if t is not None:
            threads.append(t)

    logging.info("Waiting for async threads to complete")
    for t in threads:
        t.join()

    logging.info("FINISHED MAIN LOOP")
    post_loop_fn(config, iterations)


def check_model_pre_run(config: ConvergenceConfig, check_freight_db: bool):
    from polaris.project.polaris import Polaris

    model = Polaris.from_dir(config.data_dir)
    check_critical(model)

    # Logs consistency check errors
    checker = SupplyChecker(model.supply_file)
    checker.consistency_tests()
    if not len(checker.errors):
        logging.info(f"The Supply file has no additional consistency issues")
    else:
        logging.warning(f"The Supply file has {len(checker.errors)} consistency issues")
        for error in checker.errors:
            logging.error(error)


def run_async(async_end_of_loop_fn, config, current_iteration, output_dir):
    t = Thread(target=async_end_of_loop_fn, args=(config, current_iteration, output_dir))
    t.start()
    if config.async_inline:
        t.join()
        return None
    else:
        return t


def link_iterations(iterations):
    for curr, prev in zip(iterations[1:], iterations[:-1]):
        curr.previous_iteration = prev
        prev.next_iteration = curr
    return iterations
