# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import logging
import os
import sys
import traceback
from pathlib import Path
from shutil import rmtree

from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.project.polaris import Polaris
from polaris.runs.convergence.convergence_callback_functions import precache_kpis
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.utils.copy_utils import magic_copy
from polaris.utils.env_utils import get_data_root


def example_json():
    return {
        "where-is-base-model": "/mnt/ci/models/RUN",
        "city": "Grid",
        "run-id": "grid-kpi",
    }


def main(payload):
    # We get a task container helper object to allow us to log messages back to the db
    task_container = TaskContainer.from_env(payload)

    run_id = "not-specified"
    try:
        run_id = payload.get("run-id")
        city = payload.get("city")
        model = setup_run(task_container, run_id, city)
        for iter_dir in model.model_path.glob("*_iteration_*"):
            print(iter_dir)
            iter = ConvergenceIteration.from_dir(iter_dir)
            precache_kpis(iter, skip_cache=True)

    except Exception:
        tb = traceback.format_exc()
        # update_job(run_id, "FAILED", tb)
        print(tb, flush=True)
        logging.critical(tb)
        exit(1)


def setup_run(task_container, run_id, city):
    payload = task_container.payload
    run_dir = get_data_root() / "models"
    model_dir = run_dir / city

    print(f"Local Run Dir: {model_dir}")

    models_src_dir = Path(os.path.expanduser(payload["where-is-base-model"])).resolve()

    # copy model
    if model_dir.exists() and payload.get("overwrite-model-files", False):
        rmtree(model_dir)
        magic_copy(models_src_dir, model_dir)
    elif not model_dir.exists():
        magic_copy(models_src_dir, model_dir)

    model = Polaris.from_dir(model_dir)

    # We store the payload on the config object to allow for later callbacks to use the information therein
    model.run_config.user_data = task_container.payload

    task_container.log("Finished copying files")

    return model


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        payload = json.loads(f.read())
    main(payload)
