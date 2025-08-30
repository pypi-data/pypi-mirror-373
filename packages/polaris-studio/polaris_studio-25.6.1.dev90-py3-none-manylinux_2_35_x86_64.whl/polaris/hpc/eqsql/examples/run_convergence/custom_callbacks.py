# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shutil
import time
from pathlib import Path
from typing import List

from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.runs.convergence.convergence_callback_functions import (
    copy_log_to,
    default_async_fn,
    default_end_of_loop_fn,
    default_pre_loop_fn,
    default_start_of_loop_fn,
)
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.convergence.scenario_mods import get_scenario_for_iteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.utils.copy_utils import magic_copy
from polaris.utils.func_utils import can_fail
from polaris.utils.logging_utils import function_logging


def iterations_fn(config: ConvergenceConfig):
    return config.iterations()


def get_scenario_json_fn(config: ConvergenceConfig, current_iteration: ConvergenceIteration):
    mods, file = get_scenario_for_iteration(config, current_iteration)
    # if "skim_graph" in str(config.data_dir) or "skim_clean" in str(config.data_dir):
    #     mods["generate_transit_skims"] = True

    return mods, file


def pre_loop_fn(config: ConvergenceConfig, iterations, polaris_inputs: PolarisInputs):
    return default_pre_loop_fn(config, iterations, polaris_inputs)


def start_of_loop_fn(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration, mods: dict, scenario_file: Path
):
    task_container = TaskContainer.from_env(None)
    task_container.log(f"Starting {current_iteration}")
    return default_start_of_loop_fn(config, current_iteration, mods, scenario_file)


def end_of_loop_fn(
    config: ConvergenceConfig, current_iteration: ConvergenceIteration, output_dir: Path, polaris_inputs: PolarisInputs
):
    return default_end_of_loop_fn(config, current_iteration, output_dir, polaris_inputs)


def async_end_of_loop_fn(config: ConvergenceConfig, current_iteration: ConvergenceIteration, output_dir):
    default_async_fn(config, current_iteration, output_dir)
    task_container = TaskContainer.from_env(None)
    if "put-results-here" in config.user_data:
        results_dir = Path(config.user_data["put-results-here"])
        dest_iteration_dir = results_dir / f"{config.db_name}_{current_iteration}"
        task_container.log(
            f"        ~ Copying back to {dest_iteration_dir} (exists={dest_iteration_dir.parent.exists()})"
        )
        magic_copy(str(output_dir), str(dest_iteration_dir))
        Path(output_dir / "copy-finished").touch()
        magic_copy(str(output_dir / "copy-finished"), str(dest_iteration_dir / "copy-finished"), recursive=False)
        task_container.log(f"        ~ Deleting {output_dir}")
        shutil.rmtree(output_dir)


def build_polaris_crash_handler(config: ConvergenceConfig):
    # TODO: Clean up use of user-data
    run_id = config.user_data.get("run-id")
    log_folder = config.user_data.get("put-logs-here", config.data_dir)

    @can_fail
    def polaris_crash_handler(output_dir, stderr_buffer):
        with open(output_dir / "log" / "polaris_progress.log", "a") as log:
            log.write("\nPOLARIS crashed, stdout and stderr appended here (should contain stack trace):\n")
            for line in stderr_buffer:
                log.write(line + "\n")
        return copy_log_to(output_dir, Path(log_folder), name=f"{run_id}-{output_dir.name}-CRASH.txt")

    return polaris_crash_handler


def post_loop_fn(config: ConvergenceConfig, iterations: List[ConvergenceIteration]):
    TaskContainer.from_env(None).log("Post processing after iteration")

    # Copy back everything that wasn't copied back during the model run
    output_folder = Path(config.user_data["put-results-here"])
    magic_copy(str(config.data_dir), str(output_folder))

    # Be a good house-guest and clean up after ourselves
    delete_all_files(config.data_dir)


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
