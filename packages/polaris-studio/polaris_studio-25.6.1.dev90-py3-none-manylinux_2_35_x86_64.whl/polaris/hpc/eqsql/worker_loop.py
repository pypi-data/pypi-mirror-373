# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
#!/usr/bin/env python3
from datetime import datetime
import logging
import os
import signal
import sys
import traceback
import argparse
from pathlib import Path

from polaris.hpc.eqsql.eq import EQ_TIMEOUT, get_next_task, update_worker, worker_id
from polaris.hpc.eqsql.eq_db import DEAD, IDLE
from polaris.hpc.gce.globus_compute import run_in_gce
from polaris.hpc.eqsql.task_runner import try_run_task, try_run_task_in_bg
from polaris.utils.db_config import DbConfig
from polaris.utils.env_utils import setup_path


known_runners = ["fg", "bg", "gce"]


def main():
    args = parse_args()
    setup_path()
    loop(worker_id(), "bg", args)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-type", type=int, default=1)
    return parser.parse_args()


def main_gce():
    setup_path()
    loop("gce-crossover-4", "gce")


def loop(worker_id, runner, args):
    heartbeat_interval = 120.0
    if runner not in known_runners:
        raise RuntimeError(f"Unknown runner given: {runner}, expected one of {known_runners}")
    os.environ["WORKER_ID"] = worker_id
    idle_shutdown = int(os.environ.get("EQSQL_idle_shutdown", 0))
    idle_tracking_dir = Path(os.environ.get("EQSQL_idle_tracking_dir")) if idle_shutdown > 0 else None
    idle_tracking_file = idle_tracking_dir / worker_id if idle_shutdown > 0 else None
    write_idle(idle_tracking_file)

    engine = DbConfig.eqsql_db().create_engine()

    logging.info(f"{heartbeat_interval=}")
    logging.info(f"{idle_shutdown=}")
    logging.info(f"{runner=}")
    logging.info(f"{worker_id=}")
    logging.info(f"task_type={args.task_type}")

    while True:
        try:
            logging.info(f"trying to get task with type = {args.task_type}...")

            with engine.connect() as conn:
                # send heartbeat
                update_worker(conn, worker_id, None, IDLE, "Waiting for work")

                # try to get a task
                result = get_next_task(
                    conn, eq_type=args.task_type, delay=0.25, timeout=heartbeat_interval, worker_id=worker_id
                )

            if result.succeeded:
                task = result.value
                logging.info(f"Got a task {task.task_id}, running with {runner}")
                write_not_idle(idle_tracking_file)
                if runner == "bg":
                    try_run_task_in_bg(engine, task)
                elif runner == "fg":
                    try_run_task(engine, task)
                elif runner == "gce":
                    run_in_gce(task)
                write_idle(idle_tracking_file)

            elif result.reason != EQ_TIMEOUT:
                logging.error("Something went wrong, restarting!")
                logging.error(result.reason)
                exit(1)
            elif idle_tracking_dir is not None:
                idle_timer = min([read_idle(f) for f in idle_tracking_dir.glob("*")])
                if idle_timer >= idle_shutdown:
                    logging.info(f"Node idle time ({idle_timer}) exceeded idle_shutdown threshold ({idle_shutdown})")
                    Path(os.environ["WORKER_LOOP_RUN_FILE"]).unlink()
                    with engine.connect() as conn:
                        update_worker(conn, worker_id, None, DEAD, "Shutdown by idle_shutdown")
                    exit(0)

        except Exception:
            logging.info("An error occurred while handling a task.")
            logging.info(traceback.format_exc())
            logging.info("Exiting so that outer-loop can restart me")
            exit(1)


def read_idle(f):
    """returns how long the process corresponding to file "f" has been idle for."""
    with open(f) as f_:
        content = f_.read()

    if "RUNNING" in content:
        return 0

    idle_timer = datetime.now() - datetime.fromisoformat(content)
    return idle_timer.total_seconds()


def write_idle(f):
    if f is None:
        return
    with open(f, "w") as f_:
        f_.write(datetime.now().isoformat())


def write_not_idle(f):
    if f is None:
        return
    with open(f, "w") as f_:
        f_.write("RUNNING")


def signal_handler(signum, frame):
    logging.info("Gracefully exiting loop")
    logging.info(frame)
    exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if "--gce" in sys.argv:
        main_gce()
    else:
        main()
