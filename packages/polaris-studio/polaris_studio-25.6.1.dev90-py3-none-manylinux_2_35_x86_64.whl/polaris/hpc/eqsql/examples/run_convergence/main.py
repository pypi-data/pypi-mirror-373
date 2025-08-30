# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import stat
import datetime
import json
import logging
from logging import FileHandler
import os
import sys
import traceback
from pathlib import Path
from shutil import rmtree
from socket import gethostname

from custom_callbacks import (
    iterations_fn,
    pre_loop_fn,
    start_of_loop_fn,
    get_scenario_json_fn,
    end_of_loop_fn,
    async_end_of_loop_fn,
    post_loop_fn,
    build_polaris_crash_handler,
)
from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.project.polaris import Polaris
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.copy_utils import magic_copy
from polaris.utils.env_utils import get_based_on_env, get_data_root, is_not_windows, where_am_i_running
from polaris.utils.logging_utils import function_logging


def example_json():
    return {
        "run-id": "jamie_test_run",
        "where-is-polaris-exe": f"/mnt/ci/polaris-linux/develop/latest/ubuntu-20.04/Integrated_Model",
        "where-is-base-model": "/mnt/ci/models/RUN/Grid",
        "put-logs-here": "~/logs",
    }


def main(payload):
    # We get a task container helper object to allow us to log messages back to the db
    task_container = TaskContainer.from_env(payload)

    run_id = "not-specified"
    try:
        run_id = payload.get("run-id")
        model = setup_run(task_container, run_id)
        model.run_config = configure_run(task_container, model.run_config)
        task_container.log(f"Upgrading model: {model.model_path}")
        model.upgrade(max_migration=payload.get("max_migration", None))
        task_container.log(f"Running model: {str(model.model_path)}")
        model.run(
            pre_loop_fn=pre_loop_fn,
            start_of_loop_fn=start_of_loop_fn,
            iterations_fn=iterations_fn,
            scenario_file_fn=get_scenario_json_fn,
            end_of_loop_fn=end_of_loop_fn,
            async_end_of_loop_fn=async_end_of_loop_fn,
            post_loop_fn=post_loop_fn,
            polaris_crash_handler=build_polaris_crash_handler(model.run_config),
        )

        task_container.log("Finished model run")
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)  # we both print and log the traceback
        logging.critical(tb)
        exit(1)


def setup_run(task_container, run_id):
    payload = task_container.payload
    run_dir = get_data_root() / "models"
    model_dir = run_dir / f"{run_id}"

    # Delete model if need to overwrite, do it before logging so the .log doesnt get deleted
    if payload.get("overwrite-model-files", True):
        rmtree(model_dir, ignore_errors=True)

    # Setup logging as early as possible
    if "put-logs-here" in payload:
        file_server_log_dir = Path(payload["put-logs-here"]) / f"{run_id}"
    else:
        file_server_log_dir = Path(payload["put-results-here"])
    payload["put-logs-here"] = setup_logging(file_server_log_dir, model_dir)

    logging.info(f"Local Run Dir: {model_dir}")
    logging.info(f"Machine:       {gethostname()}")

    models_src_dir = Path(os.path.expanduser(payload["where-is-base-model"])).resolve()

    # Copy data if we need to overwrite (guaranteed to be fresh copy after logging setup is done)
    if model_dir.exists() and payload.get("overwrite-model-files", False):
        rmtree(model_dir)
        magic_copy(models_src_dir, model_dir)
    elif not model_dir.exists():
        magic_copy(models_src_dir, model_dir)

    if "where-is-warm-skim" in payload and payload["where-is-warm-skim"]:
        skim_src_dir = Path(os.path.expanduser(payload["where-is-warm-skim"])).resolve()
        for f in skim_src_dir.glob("*.omx"):
            dest = model_dir / f.name
            logging.info(f"Copying warm skim file: {f} to {dest}")
            magic_copy(f, dest, recursive=False)

    # Create a Polaris model object for interacting with
    model = Polaris.from_dir(model_dir)

    # We store the payload on the config object to allow for later callbacks to use the information therein
    model.run_config.user_data = task_container.payload

    # We copy the binaries (and deps) locally so that we are insulated from changes on the server
    def copy_exe_locally(exe_type):
        exe = Path(get_based_on_env(payload[f"where-is-{exe_type}-exe"]))
        exe_dir = exe.parent
        if (model_dir / f"{exe_type}_exe").exists():
            rmtree(model_dir / f"{exe_type}_exe")
        logging.info(f"Copying {exe_type} executable from {exe_dir}")
        magic_copy(exe_dir, model_dir / f"{exe_type}_exe", recursive=True)
        if exe_type == "polaris":
            exe = model.run_config.polaris_exe = model_dir / f"{exe_type}_exe" / exe.name
        else:
            raise RuntimeError("Unsupported executable type")

        if is_not_windows():
            os.chmod(exe, os.stat(exe).st_mode | stat.S_IEXEC)

    copy_exe_locally("polaris")
    if "where-is-cristal-exe" in payload:
        task_container.log(
            "DEPRECATED: Freight runs no longer use separate exe, set iterations appropriately to use cristal"
        )
        raise RuntimeError("Use polaris_exe for all run types by setting 'where-is-polaris-exe' parameter only.")

    task_container.log("Finished copying files")

    return model


def setup_logging(remote_dir, local_dir):
    date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")

    handlers = []

    # if we are running on bebop, the /mnt/q drives won't be mounted, so don't try to stream output there
    if Path(remote_dir).parent.exists():
        mkdir_p(remote_dir)
        handlers.append(FileHandler(os.path.join(remote_dir, f"convergence_runner_{date_stamp}_{gethostname()}.log")))

    mkdir_p(local_dir)
    handlers.append(FileHandler(os.path.join(local_dir, f"convergence_runner_{date_stamp}_{gethostname()}.log")))
    handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        handlers=handlers,
        force=True,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    return str(remote_dir)


@function_logging("Configuring Run")
def configure_run(task_container: TaskContainer, config: ConvergenceConfig):
    if "run-config" not in task_container.payload:
        return config

    # Tell the config object to extract and apply any changes specified by the user
    config.set_from_dict(task_container.payload["run-config"])

    return config


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        payload = json.loads(f.read())
    main(payload)
