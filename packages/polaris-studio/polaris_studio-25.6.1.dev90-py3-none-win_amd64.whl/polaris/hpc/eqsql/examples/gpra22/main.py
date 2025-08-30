# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import datetime
import json
import logging
import os
import sys
import traceback
from logging import FileHandler
from pathlib import Path
from shutil import rmtree
from socket import gethostname

from gpra_callbacks import (
    iterations_fn,
    pre_loop_fn,
    start_of_loop_fn,
    get_scenario_json_fn,
    end_of_loop_fn,
    async_end_of_loop_fn,
    post_loop_fn,
    build_polaris_crash_handler,
)

# from gpra_db import update_job, init
from gpra_config import GPRAConfig
from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.project.polaris import Polaris
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_runner import run_polaris_convergence
from polaris.runs.run_utils import copy_replace_file
from polaris.utils.copy_utils import magic_copy
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.env_utils import get_data_root, where_am_i_running
from polaris.utils.logging_utils import function_logging


def example_json():
    return {
        "run-id": "001",
        "city": "Grid",
        "where-is-polaris-exe": f"/mnt/ci/polaris-linux/develop/Integrated_Model.gcc",
        "where-are-models": "/mnt/ci/models",
        "where-is-config": "/mnt/q/FY22/2208 - SMART2.0 - GPRA Study Y2/01 - Scenario Definitions/convergence_configs/runs/001_Grid.yaml",
        "put-logs-here": "/mnt/q/FY22/2208 - SMART2.0 - GPRA Study Y2/01 - Scenario Definitions/logs",
        "where-are-callbacks": "/home/polaris/polaris/bin/hpc/python/gpra_callbacks.py",
        "project-dir": "~/gpra22",
    }


def main(payload):
    run_id = "-1"
    try:
        run_id = payload.get("run-id")
        task_container = TaskContainer.from_env(payload)
        task_container.log("Got Payload")

        run_dir, model_dir, config = setup_run(task_container)
        config = configure_run(task_container, config)
        run_run(payload, run_dir, model_dir, config)
        task_container.log("Completed all required steps")
    except Exception:
        tb = traceback.format_exc()
        print(tb, flush=True)
        logging.critical(tb)
        exit(1)


def setup_run(task_container):
    payload = task_container.payload

    run_id = payload.get("run-id")
    gpra_config = GPRAConfig.from_run_id(run_id)
    gpra_config.payload = payload
    gpra_config.task_container = task_container

    run_dir = get_data_root()
    city = payload.get("city")
    model_dir = run_dir / "models" / f"{run_id}_{city}"
    file_server_log_dir = Path(payload["put-logs-here"]) / f"{run_id}_{city}"

    print(f"GPRA Local Run Dir: {run_dir}")

    mkdir_p(run_dir / "models")
    models_src_dir = Path(os.path.expanduser(payload["where-are-models"])).resolve()

    # copy model
    low_or_high_ecomm = "high" if gpra_config.tele_commute_and_ecomm else "low"
    src_dir = models_src_dir / f"{city}-{low_or_high_ecomm}"
    if model_dir.exists() and payload.get("overwrite-model-files", True):
        rmtree(model_dir)
        magic_copy(src_dir, model_dir)
    elif not model_dir.exists():
        magic_copy(src_dir, model_dir)

    gpra_config.payload["put-logs-here"] = setup_logging(file_server_log_dir, model_dir)

    # copy convergence config
    mkdir_p(model_dir / "convergence")
    config_src = Path(payload["where-is-config"])
    copy_replace_file(config_src, model_dir / "convergence")
    config_file = model_dir / "convergence" / config_src.name
    config = ConvergenceConfig.from_file(config_file)

    # Upgrade the model
    Polaris(model_dir, config_file).upgrade()

    # We store the payload on the config object to allow for later callbacks to use the information therein
    config.user_data = gpra_config

    if "where-is-polaris-exe" in payload:
        exe = task_container.payload["where-is-polaris-exe"]

        # Allow for different exe on different systems - convert the keys into WhereAmI enums for lookup
        if isinstance(exe, dict):
            lu = {where_am_i_running(k): v for k, v in exe.items()}
            exe = lu[where_am_i_running()]
        config.polaris_exe = exe
    else:
        raise "no exe defined"

    task_container.log("Finished copying files")

    return run_dir, model_dir, config


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

    logging.basicConfig(handlers=handlers, force=True, format="%(asctime)s - %(levelname)s - %(message)s")
    return str(remote_dir)


@function_logging("Configuring Run")
def configure_run(task_container, config: ConvergenceConfig):
    if "run-config" not in task_container.payload:
        return config

    run_config = task_container.payload["run-config"]
    for k, v in run_config.items():
        setattr(config, k, v)

    task_container.log("Finished configuring")

    return config


def run_run(payload, run_dir, model_dir, config):
    logging.info(f"Running Polaris Convergence {run_dir} on {gethostname()}")
    run_polaris_convergence(
        config,
        pre_loop_fn=pre_loop_fn,
        start_of_loop_fn=start_of_loop_fn,
        iterations_fn=iterations_fn,
        scenario_file_fn=get_scenario_json_fn,
        end_of_loop_fn=end_of_loop_fn,
        async_end_of_loop_fn=async_end_of_loop_fn,
        post_loop_fn=post_loop_fn,
        polaris_crash_handler=build_polaris_crash_handler(config),
    )


# -

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        payload = json.loads(f.read())
    main(payload)
