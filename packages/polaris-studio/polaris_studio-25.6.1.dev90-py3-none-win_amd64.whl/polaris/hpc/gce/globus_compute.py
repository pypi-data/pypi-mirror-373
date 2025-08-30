# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
#!/usr/bin/env python3

from polaris.hpc.eqsql.task import Task
from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.runs.gap_reporting import first_and_only


def run_in_gce(task: Task, worker_id="gce-crossover-4"):
    tc = TaskContainer.from_task(task)
    tc.log("Task has been picked up and is being dispatched to GlobusCompute", worker_id=worker_id)

    from globus_compute_sdk import Client

    gcc = Client()

    # Find the appropriate endpoint and function UUIDs
    # TODO: currently endpoint is hardcoded, try to make this depend on the size of the task...
    endpoint_id = get_endpoint_uuid(gcc)  # , worker_id)
    func_uuid = gcc.register_function(run_task_on_xover, "run_task")

    # We use a batch (of size 1) to run the task without waiting for its output
    batch = gcc.create_batch()
    batch.add(function_id=func_uuid, args=(task,))
    result = gcc.batch_run(endpoint_id=endpoint_id, batch=batch)

    # Send some stats to the DB log
    tc.log(f"Task id: {result['tasks']}")
    tc.log(f"Task group id: {result['task_group_id']}")


def run_task_on_xover(task):
    """Self contained function that can be serialised out to a compute node to run a task."""
    from polaris.utils.db_config import DbConfig
    from polaris.hpc.eqsql.task_runner import try_run_task
    from polaris.hpc.eqsql.eq import update_worker, worker_id

    engine = DbConfig.eqsql_db().create_engine()

    # Create a worker id and mark it with this task
    with engine.connect() as conn:
        update_worker(conn, worker_id(), None, "starting", f"Starting up to run task: {task.task_id}")

    # Actually do the task
    try_run_task(engine, task)

    # Clear the worker status (as we are now killing the worker)
    with engine.connect() as conn:
        update_worker(conn, worker_id(), None, "dead", f"Finished task: {task.task_id}")


def get_endpoint_uuid(gcc, endpoint_name="crossover-polaris-4"):
    endpoint = first_and_only([e for e in gcc.get_endpoints() if e["name"] == endpoint_name])
    return endpoint["uuid"]
