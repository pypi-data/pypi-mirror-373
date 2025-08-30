# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import multiprocessing
import shutil
import subprocess
import sys, os, traceback
from time import sleep
from tempfile import TemporaryDirectory
import datetime
import json
import logging

from socket import gethostname
from pathlib import Path

import pandas as pd
import numpy as np

from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.runs.scenario_utils import extract_iteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.env_utils import WhereAmI, get_data_root, where_am_i_running
from polaris.utils.logging_utils import function_logging
from polaris.utils.copy_utils import magic_copy


def main(payload):
    task_container = TaskContainer.from_env(payload)
    task_container.log("Got Payload")
    try:
        do_the_run(task_container)
    except Exception:
        tb = traceback.format_exc()
        task_container.log(tb)
        print(tb, flush=True)
        exit(1)


def do_the_run(task_container):

    if "run-id" not in task_container.payload:
        raise LookupError("Provide unique run-id. Use 'run-id'")
    if "get-results-from-here" not in task_container.payload:
        raise LookupError("Base directory for where results are. Use 'get-results-from-here'")
    if "polaris-output-dir" not in task_container.payload:
        raise LookupError("No model directory listed to run svtrip against. Use 'polaris-output-dir'")
    if "which-city-are-you-running" not in task_container.payload:
        raise LookupError("City db name not provided. Use 'which-city-are-you-running'")
    if "put-svtrip-results-here" not in task_container.payload:
        raise LookupError("Where should the results be written? Use 'put-svtrip-results-here'")
    if "iteration-choice-type" not in task_container.payload:
        raise LookupError("Should we choose best-iteration or last-iteration? Use 'iteration-choice-type'")

    local_dir_name = task_container.payload["run-id"]
    run_dir_path = Path(task_container.payload["get-results-from-here"])
    db_name = task_container.payload["which-city-are-you-running"]
    model_dir_name = task_container.payload["polaris-output-dir"]
    iteration_choice_type = task_container.payload["iteration-choice-type"]
    num_threads = task_container.payload.get("num-threads", None) or multiprocessing.cpu_count()

    local_dir = Path(get_data_root()) / "sv_trip" / local_dir_name
    local_dir.mkdir(parents=True, exist_ok=True)

    def get_iteration_num(output_dir):
        """Attempt to get an absolute iteration number from a string"""
        try:
            if "cristal" in output_dir:
                return -1
            if "abm_init" in output_dir:
                return -1
            return int(output_dir.split("_")[-1])
        except Exception:
            return -2

    def remote_get_best_iteration(run_dir):
        gap_file = run_dir / "gap_calculations.csv"
        magic_copy(gap_file, local_dir / gap_file.name, recursive=False)
        gaps = pd.read_csv(local_dir / gap_file.name)
        if gaps.shape[0] < 4:  # or gaps[gaps.directory.str.contains("iteration_16")].shape[0] == 0:
            raise RuntimeError(f"Not enough records ({gaps.shape[0]}) in gap_calculations_.csv (or missing it16)")

        gaps = gaps[gaps.directory.str.contains("iteration")]
        gaps["iteration"] = gaps.directory.apply(get_iteration_num)
        gaps = gaps.sort_values("iteration").tail(4).set_index("directory")
        iter_name = gaps.tail(4)["relative_gap_min0"].idxmin()
        return run_dir / iter_name

    def remote_get_last_iteration(run_dir):
        gap_file = run_dir / "gap_calculations.csv"
        with TemporaryDirectory(dir=str(local_dir)) as t:
            magic_copy(gap_file, Path(t) / gap_file.name, recursive=False)
            gaps = pd.read_csv(Path(t) / gap_file.name)
            gaps["iteration"] = gaps.directory.apply(get_iteration_num)

        logging.info(f"All iterations: {gaps.iteration}")
        gaps = gaps.sort_values(by=["iteration"])
        logging.info(f"Chosen iteration: {gaps.iteration.iloc[-1]}")
        iter_name = gaps.directory.iloc[-1]
        logging.info(f"Confirming chosen directory: {iter_name}")
        return run_dir / iter_name

    # find the results on the file server and determine the best iteration

    if iteration_choice_type == "best-iteration":
        model_src_dir = remote_get_best_iteration(run_dir_path / model_dir_name)
    elif iteration_choice_type == "last-iteration":
        model_src_dir = remote_get_last_iteration(run_dir_path / model_dir_name)
    else:
        raise RuntimeError(f"Unsupported iteration choice type: {iteration_choice_type}")

    # setup logging
    model_dir = local_dir / model_src_dir.stem
    needs_copying = not model_dir.exists()
    setup_logging(model_dir)

    # copy best iteration to local
    if needs_copying:
        logging.info(f"Copying {model_src_dir} -> {model_dir}")
        magic_copy(model_src_dir, model_dir)
        task_container.log("SVTrip - Finished copying down files")
    else:
        pass

    extract_iteration(model_dir, db_name=db_name)

    export_sv_trip(PolarisInputs.from_dir(model_dir, db_name), num_threads)
    task_container.log("SVTrip - Finished exporting files")
    copy_sv_trip_files(task_container, model_dir_name, db_name, model_dir)
    task_container.log("SVTrip - Finished copying up files")
    slow_rmtree_svtrip(model_dir)
    task_container.log("SVTrip - Finished deleting local files")


def setup_logging(local_dir):
    mkdir_p(local_dir)
    date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    handler_f1 = logging.FileHandler(os.path.join(local_dir, f"sv_trip_runner_{date_stamp}_{gethostname()}.log"))
    handler_std = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        handlers=[handler_std, handler_f1], force=True, format="%(asctime)s - %(levelname)s - %(message)s"
    )


@function_logging("    Exporting SV Trips (threads = {num_threads})")
def export_sv_trip(inputs: PolarisInputs, num_threads: int, subset_id=None, trip_ids_to_run=None):
    from SVTrip.svtrip import SVTrip

    svtrip = SVTrip()

    # svtrip.parameters.execution.run_parallel = False
    svtrip.parameters.execution.n_workers = num_threads
    svtrip.parameters.execution.jobs_per_thread = 15
    # svtrip.log_increment = 0.05
    if subset_id is not None:
        subset_id, num_subsets = subset_id
    else:
        subset_id, num_subsets = (1, 1)

    iteration_dir = inputs.demand_db.parent
    output_dir = iteration_dir / f"sv_trip_outputs_{subset_id}_of_{num_subsets}"
    output_dir.mkdir()
    (output_dir / f"based_on_{iteration_dir.name}").touch()
    svtrip.parameters.output.export_folder = output_dir

    svtrip.load_trips_from_polaris(inputs.demand_db, inputs.supply_db)
    if num_subsets > 1:
        trip_ids_to_run = [i for i in svtrip.list_trip_ids() if (i % num_subsets) == (subset_id - 1)]
    if trip_ids_to_run is not None:
        svtrip.isolate_trips(trip_ids_to_run)

    np.random.seed(123)
    # svtrip.set_logging_level(60)  # turn off any logging - it's WAY too verbose
    svtrip.run()
    svtrip.logger.critical("FINISHED")


@function_logging("  Copying SVTrip files to the Cluster file share")
def copy_sv_trip_files(task_container, model_dir_name, db_name, output_dir, subset_id=None):
    target_folders = task_container.payload["put-svtrip-results-here"]
    if isinstance(target_folders, str):
        target_folders = [target_folders]

    if subset_id is not None:
        subset_id, num_subsets = subset_id
    else:
        subset_id, num_subsets = (1, 1)

    sv_trip_dir = output_dir / f"sv_trip_outputs_{subset_id}_of_{num_subsets}"
    flag_file = sv_trip_dir / "copy_finished.txt"
    flag_file.unlink(missing_ok=True)

    for folder in target_folders:
        folder = Path(folder) / model_dir_name

        # Copy over the svtrip outputs
        dest_dir = folder / f"sv_trip_outputs_{subset_id}_of_{num_subsets}"
        magic_copy(str(sv_trip_dir), str(dest_dir))

        # Copy over the demand db used in svtrip
        if subset_id == 1:
            demand_db = f"{db_name}-Demand.sqlite"
            magic_copy(str(output_dir / demand_db), str(folder / demand_db), recursive=False)

        # Touch a flag file so that automated autonomie processing can be triggered
        flag_file.touch()
        magic_copy(str(flag_file), str(dest_dir / "copy_finished.txt"), recursive=False)
        flag_file.unlink()


def slow_rmtree_svtrip(dir: Path):
    """Work around the WSL bug that causes system failure when deleting too much
    data at once.
    """
    if where_am_i_running() != WhereAmI.WSL_CLUSTER:
        shutil.rmtree(dir)

    for x in dir.glob("*"):
        if x.is_dir():
            slow_rmtree_svtrip(x)
        else:
            is_big = x.stat().st_size > 10000000
            x.unlink()
            if is_big:
                sleep(1)  # put in a small pause after big files
    shutil.rmtree(dir)


if __name__ == "__main__":
    with open(sys.argv[1], "r") as f:
        main(json.loads(f.read()))
