# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from datetime import datetime
import logging
from time import sleep
from typing import NamedTuple

from polaris.hpc.eq_utils import git_pull, query_workers, restart_worker, terminate_worker
from polaris.hpc.eqsql.eq import insert_task
from polaris.hpc.eqsql.eq_db import workers_table
from polaris.hpc.eqsql.utils import clear_idle_pg_connection, from_id, update_from_db, update_to_db
from polaris.utils.env_utils import WhereAmI, where_am_i_running


class Worker(NamedTuple):
    worker_id: str
    status: str
    message: str
    task_id: int
    updated_at: datetime

    @classmethod
    def from_id(cls, engine, worker_id):
        return from_id(cls, engine, worker_id)

    def mark_dead(self, engine, update_task=True):
        """Useful if a worker has gone offline without informing the database"""
        updated_message = f"DEAD: {self.message}" if not self.message.startswith("DEAD") else self.message
        update_to_db(self, engine, status="dead", message=updated_message)
        if self.task_id is not None and update_task:
            from polaris.hpc.eqsql.task import Task

            task = Task.from_id(engine, self.task_id)
            if task.running_on == self.worker_id:
                task.mark_failed(engine, False)

    def terminate(self, engine):
        """Tell the worker to shutdown and update the db appropriately"""
        return terminate_worker(engine, self.worker_id)

    abort = terminate  # type:ignore

    def restart(self, engine):
        """Tell the worker to restart and reload code"""
        return restart_worker(engine, self.worker_id)

    def git_pull(self, engine):
        return git_pull(engine, self.worker_id)

    @clear_idle_pg_connection()
    def clean_model_folder(self, engine):
        logging.warning(
            "This will clear the entire model folder, you have 15 seconds to make sure no other jobs are running on this worker."
        )
        sleep(15)

        env = where_am_i_running(self.worker_id)
        if env in (WhereAmI.CROSSOVER_CLUSTER, WhereAmI.BEBOP_CLUSTER, WhereAmI.IMPROV_CLUSTER):
            raise RuntimeError("Not going to delete the entire models folder on LCRC sorry - do it by hand.")

        with engine.connect() as conn:
            task = {"task-type": "control-task", "control-type": "EQ_CLEAN_FOLDER"}
            insert_task(
                conn=conn,
                task_type=0,
                exp_id=f"eq_clean_{self.worker_id}",
                worker_id=f"^{self.worker_id}$",
                definition=task,
                input={"folder": "~/models"},
            )

    @property
    def machine_id(self):
        return "-".join(self.worker_id.split("-")[0:-1])

    @property
    def primary_key(self):
        return self.worker_id

    def update_from_db(self, engine):
        return update_from_db(self, engine)

    def update_to_db(self, engine, **kwargs):
        return update_to_db(self, engine, **kwargs)

    @classmethod
    def table(cls):
        return workers_table

    @classmethod
    def key_col(cls):
        return workers_table.c.worker_id

    @classmethod
    def all(cls, engine, **kwargs):
        df = query_workers(engine, style_df=False, **kwargs)

        def from_row(row):
            return Worker(row.worker_id, row.status, row.message, row.task_id, row.updated_at)

        return [from_row(row) for i, row in df.iterrows()]
