# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# EQ-SQL eq.py
import datetime
import json
import logging
import os
import time
from socket import gethostname
from typing import Any, Dict, Optional

import pandas as pd
from polaris.hpc.eqsql.eq_db import DBResult, try_db
from polaris.hpc.eqsql.eq_db import RUNNING, QUEUED, FINISHED, FAILED, IDLE
from polaris.hpc.eqsql.eq_db import tasks_table, task_log_table, workers_table
from polaris.hpc.eqsql.task import Task
from polaris.hpc.eqsql.utils import from_cursor_result, from_row, clear_idle_pg_connection, check_worker_regex
from sqlalchemy import Connection, func, select, text
from sqlalchemy.dialects.postgresql import insert

EQ_ABORT = "EQ_ABORT"
EQ_TIMEOUT = "EQ_TIMEOUT"
EQ_STOP = "EQ_STOP"


@try_db()
@clear_idle_pg_connection()
def insert_task(
    conn: Connection,
    definition: str,
    input: str,
    exp_id: str,
    worker_id: Optional[str] = None,
    task_type: int = 1,
    priority: int = 1,
    status="queued",
) -> DBResult:
    """Inserts the specified task in to the database, creating
    a task entry for it, adding that task to the queue and returning the new task id

    Args:
        conn: the connection object to the database
        definition: the task definition
        input: input argments or data for the task
        worker_id: a string (which can contain wildcards %) to limit which workers can pick up this task
        task_type: the type of this task (1 - default, other values can be used to lock jobs to specific workers)
        priority: the priority of this task from (1 - low) to (9 - high)

    Returns:
        The newly created task id
    """

    # Make sure that these are strings for inserting.
    input = input if isinstance(input, str) else json.dumps(input)
    definition = definition if isinstance(definition, str) else json.dumps(definition)

    # check if worker_id regex is valid
    if worker_id is not None:
        check_worker_regex(worker_id)

    stmt = (
        tasks_table.insert()
        .values(
            input=input,
            definition=definition,
            worker_id=worker_id,
            task_type=task_type,
            priority=priority,
            exp_id=exp_id,
            status=status,
        )
        .returning(text("task_id"))
    )
    task_id = conn.execute(stmt).first()[0]  # type: ignore
    logging.info(f"Task created with id: {task_id}")
    cursor_result = conn.execute(tasks_table.select().filter(tasks_table.c.task_id == task_id))
    return from_cursor_result(Task, cursor_result)


@try_db()
@clear_idle_pg_connection()
def update_task(conn: Connection, task_id: int, status: str, definition: Optional[Dict], input: Optional[Any]):
    c = tasks_table.c
    update_dict = {"updated_at": "now()"}
    if status is not None:
        update_dict["status"] = status
    if input is not None:
        update_dict["input"] = input if isinstance(input, str) else json.dumps(input)
    if definition is not None:
        update_dict["definition"] = definition if isinstance(definition, str) else json.dumps(definition)
    sql = tasks_table.update().filter(c.task_id == task_id).values(**update_dict).returning(c)  # type: ignore
    result = conn.execute(sql)
    return from_cursor_result(Task, result)


def finish_task(conn: Connection, task_id: int, output: str, worker_id: str, start_time=None) -> DBResult:
    return complete_task(conn, task_id, output, worker_id, FINISHED, start_time)


def fail_task(conn: Connection, task_id: int, output: str, worker_id: str, start_time=None) -> DBResult:
    return complete_task(conn, task_id, output, worker_id, FAILED, start_time)


@try_db()
def complete_task(
    conn: Connection, task_id: int, output: str, worker_id: str, status: str, start_time=None
) -> DBResult:
    """Updates the specified task in the tasks table when the task is completed.
    Output from the task can be optionally stored in the "output" column.

    Args:
        conn: the connection object to the database
        task_id: the id of the task to update
        output: the output (data, log, results, etc) to store with the task
        worker_id: the id of the worker which is finalising this task
        status: the status the task completed with
        start_time: the original start time of the underlying task - used to create timing message
    Returns:
        DBResult with the updated task object (if successful)
    """

    message = f"Complete in {datetime.datetime.now() - start_time} seconds" if start_time is not None else "Complete"
    update_worker(conn, worker_id=worker_id, task_id=task_id, status=IDLE, message=f"Just finished with task {task_id}")
    tu = (
        tasks_table.update()
        .filter(tasks_table.c.task_id == task_id)
        .values(status=status, output=str(output), updated_at=func.now(), message=message)
    )
    sql = tu.returning(tasks_table.c)  # type: ignore

    rv = conn.execute(sql)

    if rv is not None:
        return from_cursor_result(Task, rv)
    return DBResult.failure("No such record")


@try_db()
def get_next_task(conn: Connection, eq_type: int, delay: float, timeout: float, worker_id: str) -> DBResult:
    """Pops the highest priority task of the specified work type off
    of the db out queue.

    This call repeatedly attempts (polls) the pop operation by executing sql until
    the operation completes or the timeout duration has passed. The interval between
    polls starts at the given delay and increases by 1/4 second after each attempt.

    Args:
        conn: the connection object to the database
        eq_type: the type of the work to pop from the queue
        delay: the initial polling delay value
        timeout: the duration after which this call will timeout and return
        worker_id: the identifier of the worker attempting to pop a task

    Returns:
        A `Task` object representing the next task to be processed (on success) or the reason
        that a task could not be popped (on failure).
    """

    tu = tasks_table.update().filter(tasks_table.c.task_id.in_(_get_next_task_id_sql(eq_type)))  # type: ignore
    sql = tu.values(status="running", running_on=worker_id).returning(tasks_table.c)  # type: ignore

    result = _queue_pop(conn, sql, delay, timeout, worker__id=worker_id)
    if result.succeeded:
        task = from_row(Task, result.value)
        result.value = task
        update_worker(conn, worker_id, task.task_id, "running", f"starting to run task {result.value.task_id}")
    conn.commit()
    return result


def _get_next_task_id_sql(eq_type):
    c = tasks_table.c
    return (
        select(c.task_id)
        .limit(1)
        .with_for_update(skip_locked=True)
        .filter(
            # Look for queued jobs of the correct type
            ((c.task_type == eq_type) | (c.task_type == 0))
            & (c.status == QUEUED)
            # Make sure the job didn't request a specific worker, or requested the current worker
            & ((c.worker_id == None) | text(":worker__id ~ worker_id"))  # noqa: E711
        )
        .order_by(
            c.task_type,  #  prefer tasks with type 0 (control-tasks) over all other types
            text("( :worker__id ~ worker_id ) ASC"),  # prefer tasks that are targetting this worker
            c.priority.desc(),
            c.updated_at,
        )
    )


@try_db()
def insert_task_log(conn: Connection, eq_task_id: int, message: str, worker_id: Optional[str] = None) -> DBResult:
    """Adds a new log message for the specified task.

    Args:
        conn: the connection object to the database
        eq_task_id: the id of the task to be updated
        message: the log message to append to the task log
        worker_id: optional worker_id of the worker inserting the log message
    Returns:
        None
    """
    c = tasks_table.c
    conn.execute(task_log_table.insert().values([eq_task_id, message, worker_id]))
    update_dict = {"message": message, "updated_at": func.now()}
    if worker_id is not None:
        update_dict["running_on"] = worker_id
    conn.execute(tasks_table.update().values(update_dict).filter(c.task_id == eq_task_id))

    # Also update the worker with the latest message
    update_worker(conn, worker_id=worker_id, task_id=eq_task_id, status=RUNNING, message=message)

    return DBResult.success(None)


@try_db()
def query_task_log(conn: Connection, eq_task_id: int) -> DBResult:
    """Queries for all log messages relating to the specified task.

    Args:
        conn: the connection object to the database
        eq_task_id: the id of the task to query

    Returns:
        A dataframe containing all log messages and their timestamps
    """
    sql = task_log_table.select().filter(task_log_table.c.task_id == eq_task_id)
    return DBResult.success(pd.read_sql(sql, conn))


@try_db()
def update_worker(conn: Connection, worker_id: str, task_id: int, status: str, message: str):
    stmt = insert(workers_table).values(
        worker_id=worker_id, task_id=task_id, status=status, message=message, updated_at=func.now()
    )
    stmt_ = stmt.on_conflict_do_update(index_elements=[workers_table.c.worker_id], set_=stmt.excluded)  # type: ignore
    conn.execute(stmt_)
    conn.commit()


@try_db()
def _queue_pop(conn: Connection, sql_pop: str, delay: float, timeout: float, **kwargs) -> DBResult:
    """Performs the actual queue pop as defined the sql string.

    This call repeatedly attempts (polls) the pop operation by executing sql until
    the operation completes or the timeout duration has passed. The interval between
    polls starts at the given delay and increases by 1/4 second after each attempt.

    Args:
        conn: the connection object to the database
        sql_pop: the sql query that defines the pop operation
        delay: the initial polling delay value
        timeout: the duration after which this call will timeout
            and return.

    Returns:
        The first row of the result of the given SQL (on success) or EQ_ABORT/EQ_TIMEOUT (on failure).
    """
    start = time.time()
    while True:
        rs = conn.execute(sql_pop, parameters=kwargs).first()  # type: ignore
        if rs is not None:
            conn.commit()
            return DBResult.success(rs)
        if time.time() - start > timeout:
            return DBResult.failure(EQ_TIMEOUT)
        time.sleep(delay)
        if delay < 30:
            delay += 0.25


def worker_id():
    if "WORKER_ID" not in os.environ:
        os.environ["WORKER_ID"] = gethostname()
    return os.environ["WORKER_ID"]
