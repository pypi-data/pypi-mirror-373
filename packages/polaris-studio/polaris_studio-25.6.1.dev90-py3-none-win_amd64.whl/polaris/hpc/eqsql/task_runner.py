# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import datetime
import json
import logging
import os
import subprocess
import sys
import traceback
from multiprocessing import Process
from pathlib import Path
from shutil import which
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep

import psutil
from polaris.hpc.eqsql.task_container import TaskContainer
import sqlalchemy
from polaris.hpc.eqsql.eq import fail_task, finish_task, worker_id, update_worker
from polaris.hpc.eqsql.eq_db import CANCELLED, CANCELLING, DEAD, FINISHED, RUNNING
from polaris.hpc.eqsql.task import Task
from polaris.utils.cmd_runner import run_cmd
from polaris.utils.copy_utils import magic_copy
from polaris.utils.env_utils import WhereAmI, where_am_i_running
from polaris.utils.dir_utils import slow_rmtree, with_dir

POLARIS_DIR = Path(__file__).resolve().absolute().parent.parent.parent.parent


def try_run_task_in_bg(engine: sqlalchemy.Engine, task: Task):
    # If we have a control task - run that on the main thread
    task_type = task.definition["task-type"]
    if task_type in ["control-task"]:
        return run_control_task(engine, task)

    # Otherwise... Start a new process to run this task
    p = Process(target=try_run_task_conn_str, args=(engine.url, task))
    p.start()

    def kill_process():
        p_ = psutil.Process(p.pid)
        for child in p_.children(recursive=True):
            child.kill()
        p.kill()

    # while that process is running...
    while p.is_alive():
        # keep checking the db for cancel events
        task = task.update_from_db(engine)
        if task.status in [CANCELLING, CANCELLED]:
            logging.info("Terminating task (got signal from DB)")
            kill_process()
            sleep(2)
            if p.is_alive():
                sleep(5)
            if p.is_alive():
                logging.info("Terminating again! Why won't it die?")
                kill_process()
                sleep(30)
            if p.is_alive():
                raise RuntimeError(f"Couldn't terminate task {task.task_id}")
            return task.update_to_db(engine, status=CANCELLED, message="Cancelled while running")
        elif task.status == RUNNING:
            # logging.info("still running")
            pass
        elif task.status == FINISHED:
            # logging.info("task finished")
            pass
        else:
            logging.info(f"WTF: {task}")

        sleep(5)  # wait some period before checking the DB again

    p.join()


def add_globus_endpoints_from_task(task: Task):
    if "additional-endpoints" not in task.definition:
        logging.info("No globus dependencies to add")
        return

    from polaris.utils.copy_utils import GlobusLocation

    additional_endpoints = task.definition["additional-endpoints"]
    GlobusLocation.set_additional_endpoints(additional_endpoints)
    os.environ["GLOBUS_ADD_ENDPOINTS"] = json.dumps(additional_endpoints)


def try_run_task_conn_str(conn_string: str, task: Task):
    engine = sqlalchemy.create_engine(conn_string, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    return try_run_task(engine, task)


def try_run_task(engine: sqlalchemy.Engine, task: Task):
    try:
        start_time = datetime.datetime.now()
        run_task(engine, task)
    except Exception:
        with engine.connect() as conn:
            tb = traceback.format_exc()
            fail_task(conn, task.task_id, tb, worker_id=worker_id(), start_time=start_time)
            logging.warning(tb)


def run_task(engine, task):
    add_globus_endpoints_from_task(task)
    os.environ["EQSQL_TASK_ID"] = str(task.task_id)

    tc = TaskContainer(engine=engine, payload=None, task=task)
    tc.log(f"Starting run of {task.task_id} on {worker_id()}")

    task_type = task.definition["task-type"]
    logging.info(str(task))
    if task_type in ["control-task"]:
        run_control_task(engine, task)
    elif task_type in ["python-script"]:
        run_script_task(engine, task)
    elif task_type == "python-module":
        run_module_task(engine, task)
    elif task_type in ["bash-script"]:
        run_bash_task(engine, task)
    elif task_type in ["null", "pass"]:
        with engine.connect() as conn:
            finish_task(conn, task.task_id, None, worker_id())
    else:
        message = f"Don't know how to handle task type: '{task_type}'"
        logging.error(message)
        with engine.connect() as conn:
            fail_task(conn, task.task_id, message, worker_id())


git_dir = Path(__file__).resolve().parent.parent.parent.parent


def run_control_task(engine, task):
    task_type = task.definition["control-type"]
    if task_type == "EQ_ABORT":
        logging.info("Got EQ_ABORT - Stopping everything so that worker loop job can terminate")
        Path(os.environ["WORKER_LOOP_RUN_FILE"]).unlink()
        with engine.connect() as conn:
            finish_task(conn, task.task_id, "Aborted", worker_id())
            update_worker(conn, worker_id(), None, DEAD, "Shutdown by EQ_ABORT")
        exit(0)
    elif task_type == "EQ_RESTART":
        logging.info("Got EQ_RESTART - exiting to allow outer loop to restart the worker loop")
        with engine.connect() as conn:
            finish_task(conn, task.task_id, "Restarted", worker_id())
        exit(0)
    elif task_type == "EQ_GIT_PULL":
        logging.info("Got EQ_PULL - exiting to allow outer loop to restart the worker loop")
        output = subprocess.check_output(f"{which('git')} pull", shell=True, cwd=git_dir, encoding="utf-8")
        print(output)
        with engine.connect() as conn:
            if "Already up to date" in output:
                finish_task(conn, task.task_id, f"Git pull already up to date on {worker_id()}", worker_id())
            else:
                finish_task(conn, task.task_id, f"Git pull updated on {worker_id()}", worker_id())
                exit(0)
    elif task_type == "EQ_CLEAN_FOLDER":
        folder = Path(os.path.expanduser(task.input["folder"]))
        logging.info(f"Got EQ_CLEAN_FOLDER - attempting to clean folder: {folder}")
        for sub_dir in folder.glob("*"):
            logging.info(f"Deleting: {sub_dir}")
            slow_rmtree(sub_dir)
        with engine.connect() as conn:
            finish_task(conn, task.task_id, f"Cleaned folder {folder}", worker_id())
    else:
        logging.info(f"Got {task} - Don't know what to do, so I'm exiting to allow outer loop to restart me")
        exit(0)


def run_script_task(engine, task):
    py_file = Path(os.path.expanduser(task.definition["script"]))
    if not py_file.is_absolute():
        with with_dir(POLARIS_DIR):
            py_file = py_file.resolve()
    if not py_file.exists():
        logging.error(f"Script [{py_file}] could not be found")
        with engine.connect() as conn:
            finish_task(conn, task.task_id, f"Script [{py_file}] could not be found", worker_id())
        return None
    return run_python_script(engine, py_file, task)


def run_bash_task(engine, task):
    try:
        start_time = datetime.datetime.now()
        cmd = task.definition["command"]
        rv = subprocess.run(
            cmd, shell=True, cwd=POLARIS_DIR, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        logging.info(rv)
        logging.info(rv.stdout)
        with engine.connect() as conn:
            if rv.returncode == 0:
                finish_task(conn, task.task_id, rv.stdout.strip(), worker_id(), start_time)
            else:
                fail_task(conn, task.task_id, rv.stdout.strip(), worker_id(), start_time)
    except Exception as e:
        with engine.connect() as conn:
            fail_task(conn, task.task_id, str(e), worker_id(), start_time)


def run_module_task(engine, task):
    directory = Path(os.path.expanduser(task.definition["directory"]))
    entry_point = Path(os.path.expanduser(task.definition["entry-point"]))

    # See if we can copy the script from whereever it lives via globus
    where_am_i = where_am_i_running()
    if where_am_i in [WhereAmI.BEBOP_CLUSTER, WhereAmI.CROSSOVER_CLUSTER, WhereAmI.IMPROV_CLUSTER]:
        tmp_dir = "/lcrc/project/POLARIS/tmp"
    else:
        tmp_dir = None
    with TemporaryDirectory(dir=tmp_dir) as temp_dir:
        temp_dir = Path(temp_dir)
        logging.info(f"Created temporary directory: {temp_dir}")
        magic_copy(directory, temp_dir / "module")
        run_python_script(engine, temp_dir / "module" / entry_point, task)


def run_python_script(engine, py_file, task):
    # put payload into tmp.json
    payload_file = payload_to_json(task.input)

    # Run the given script with the tmp.json as the only arg, clean up tmp.json after cmd finishes
    cmd = [sys.executable, "-u", py_file, payload_file.name]
    working_dir = Path(payload_file.name).parent
    stdout = []
    start_time = datetime.datetime.now()
    rv = run_cmd(cmd, printer=print, ignore_errors=True, working_dir=working_dir, stderr_buf=stdout)
    os.unlink(payload_file.name)

    fn = finish_task if rv == 0 else fail_task
    with engine.connect() as conn:
        fn(conn, task.task_id, "\n".join(stdout[-10:]), worker_id(), start_time)


def payload_to_json(payload):
    f = NamedTemporaryFile(delete=False, mode="w")
    if isinstance(payload, str):
        f.write(payload)
    else:
        json.dump(payload, f)
    f.close()
    logging.info(f"Created file {f.name} with content {payload}")
    return f
