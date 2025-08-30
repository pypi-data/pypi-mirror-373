# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from typing import Any, NamedTuple

from polaris.hpc.eqsql.eq import insert_task_log, worker_id
from polaris.hpc.eqsql.task import Task
from polaris.utils.db_config import DbConfig
from sqlalchemy import Engine

WORKER_ID = worker_id()


class TaskContainer(NamedTuple):
    """
    This class exists to collect together the data for a task so that it can be passed around as part of the
    config.user_data field.
    """

    engine: Engine
    payload: Any
    task: Task

    @classmethod
    def from_env(cls, payload=None):
        if "EQSQL_TASK_ID" in os.environ:
            engine = DbConfig.eqsql_db().create_engine()
            task = Task.from_id(engine, int(os.environ["EQSQL_TASK_ID"]))
            return cls(engine=engine, payload=payload, task=task)
        return cls(engine=None, payload=payload, task=None)

    @classmethod
    def from_task(cls, task, payload=None):
        return cls(engine=DbConfig.eqsql_db().create_engine(), payload=payload, task=task)

    def log(self, message, worker_id=WORKER_ID):
        if self.engine is not None:
            self.log_to_engine(message, worker_id)
        logging.info(message)

    def log_to_engine(self, message, worker_id):
        try:
            with self.engine.connect() as conn:
                insert_task_log(conn, self.task.task_id, message, worker_id)
        except Exception:
            logging.error("Failed sending back log message to DB!!")
            logging.error(message)
