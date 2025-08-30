# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# +
# %load_ext autoreload
# %autoreload 2

import datetime
import json
import logging
import os
import pathlib
import sys
import traceback
from pathlib import Path
from shutil import copytree, rmtree

from polaris.runs.scenario_file import load_yaml

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent.parent.parent.parent))

from polaris.runs.run_utils import copy_replace_file
from polaris.utils.dir_utils import mkdir_p
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_runner import run_polaris_convergence


def standard_job_definition(run_id, city):
    return {
        "run-id": run_id,
        "city": city,
        "where-is-polaris-exe": "/mnt/ci/polaris-linux/gpra22_tracking/ubuntu-2004/Integrated_Model",
        # "where-is-polaris-exe": "/mnt/q/FY22/2208 - SMART2.0 - GPRA Study Y2/03 - setup/polaris-linux/develop/Integrated_Model.gcc",
        "where-are-models": "/mnt/q/FY22/2210 - Transit Optim/base_models",
        "where-is-config": f"/mnt/q/FY22/2210 - Transit Optim/Config/{city}_{run_id}.yaml",
        # "where-are-callbacks": "/home/polaris/polaris/bin/hpc/python/gpra22/gpra_callbacks.py",
        "put-logs-here": "/mnt/q/FY22/2210 - Transit Optim/Logs",
        "put-results-here": "/mnt/q/FY22/2210 - Transit Optim/Model Results",
        "where-are-local-results": "/home/polaris/transit_opt/run_models",
    }


def main(payload):
    run_id = "-1"
    try:
        # run_id = payload.get("run-id")
        # init()
        run_dir, model_dir, config = setup_run(payload)
        run_run(payload, run_dir, model_dir, config)
        # report_run() # send back runstats to eq/sql
        # update_job(run_id, "FINISHED", "Completed all required steps")
    except Exception:
        tb = traceback.format_exc()
        # update_job(run_id, "FAILED", tb)
        print(tb, flush=True)


def setup_run(payload):
    run_id = payload.get("run-id")

    run_dir = Path(os.path.expanduser("~/transit_opt")).resolve()
    city = payload.get("city")
    model_dir = run_dir / "run_models" / f"{run_id}_{city}"
    file_server_log_dir = Path(payload["put-logs-here"]) / f"{run_id}_{city}"

    print(f"Transit Optim Local Run Dir: {run_dir}")

    mkdir_p(run_dir / "models")
    # pol_linux_dir = Path(os.path.expanduser(payload["where-is-polaris-exe"])).resolve()
    models_src_dir = Path(os.path.expanduser(payload["where-are-models"])).resolve()

    # copy model
    src_dir = models_src_dir / f"{city}"
    if model_dir.exists() and payload.get("overwrite-model-files", True):
        rmtree(model_dir)
        copytree(src_dir, model_dir)
    elif not model_dir.exists():
        copytree(src_dir, model_dir)

    payload["put-logs-here"] = setup_logging(file_server_log_dir, model_dir)

    # copy convergence config
    mkdir_p(model_dir / "convergence")
    config_src = Path(payload["where-is-config"])
    copy_replace_file(config_src, model_dir / "convergence")
    config_file = model_dir / "convergence" / config_src.name
    config = ConvergenceConfig.from_file(config_file)

    config.polaris_exe = payload["where-is-polaris-exe"]

    # We store the payload on the config object to allow for later callbacks to use the information therein
    payload.update(load_yaml(config_file))
    config.user_data = payload

    return run_dir, model_dir, config


def setup_logging(remote_dir, local_dir):
    mkdir_p(remote_dir)
    mkdir_p(local_dir)
    date_stamp = datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S")
    handler_f1 = logging.FileHandler(os.path.join(local_dir, f"convergence_runner_{date_stamp}_{gethostname()}.log"))
    handler_f2 = logging.FileHandler(os.path.join(remote_dir, f"convergence_runner_{date_stamp}_{gethostname()}.log"))
    handler_std = logging.StreamHandler(sys.stdout)
    logging.basicConfig(
        handlers=[handler_std, handler_f1, handler_f2], force=True, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return str(remote_dir)


def run_run(payload, run_dir, model_dir, config):
    # sys.path.append(str(model_dir / "convergence"))
    from fy22_transit_opt.transit_callbacks import (
        iterations_fn,
        pre_loop_fn,
        start_of_loop_fn,
        get_scenario_json_fn,
        end_of_loop_fn,
        async_end_of_loop_fn,
        post_loop_fn,
        build_polaris_crash_handler,
    )

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
