# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import inspect
import logging
import traceback
from functools import wraps

from sqlalchemy import Engine, text
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, TIMESTAMP, func

# task statuses
QUEUED = "queued"
RUNNING = "running"
FINISHED = "finished"
FAILED = "failed"
CANCELLING = "cancelling"
CANCELLED = "cancelled"

# worker statuses
IDLE = "idle"
DEAD = "dead"


class DBResult:
    def __init__(self, succeeded, value, reason):
        self.succeeded = succeeded
        self.value = value
        self.reason = reason

    @classmethod
    def success(cls, value):
        return DBResult(True, value, None)

    @classmethod
    def failure(cls, reason):
        return DBResult(False, None, reason)


def try_db():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            fn_name = inspect.currentframe().f_code.co_name
            try:
                rv = function(*args, **kwargs)
                rv = rv if isinstance(rv, DBResult) else DBResult.success(rv)  # Wrap in a DBResult if not already
                return rv
            except Exception as e:
                logging.error(f"error while running: {function.__name__} from within {fn_name}")
                logging.error(f"error: {e}")
                logging.error(traceback.format_exc())
                return DBResult.failure(e)

        return wrapper

    return decorator


metadata_obj = MetaData()


tasks_table = Table(
    "tasks",
    metadata_obj,
    Column("task_id", Integer, primary_key=True, autoincrement=True),
    Column("task_type", Integer, nullable=False),
    Column("worker_id", Text),
    Column("exp_id", Text),
    Column("priority", Integer, nullable=False, default=1),
    Column("status", String(10), nullable=False, default=QUEUED),
    Column("definition", Text),
    Column("input", Text),
    Column("output", Text),
    Column("message", Text),
    Column("running_on", Text),
    Column("created_at", TIMESTAMP, nullable=False, default=func.now()),
    Column("updated_at", TIMESTAMP, nullable=False, default=func.now()),
)

task_log_table = Table(
    "task_log",
    metadata_obj,
    Column("task_id", Integer, nullable=False),
    Column("message", Text),
    Column("worker_id", Text),
    Column("created_at", TIMESTAMP, nullable=False, default=func.now()),
)

workers_table = Table(
    "workers",
    metadata_obj,
    Column("worker_id", Text, primary_key=True, nullable=False),
    Column("status", Text),
    Column("message", Text),
    Column("task_id", Integer, nullable=True),
    Column("updated_at", TIMESTAMP, nullable=False, default=func.now()),
)


def create_db(engine: Engine, delete_first=False):
    if delete_first:
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS tasks, task_log, workers;"))
    metadata_obj.create_all(engine)
