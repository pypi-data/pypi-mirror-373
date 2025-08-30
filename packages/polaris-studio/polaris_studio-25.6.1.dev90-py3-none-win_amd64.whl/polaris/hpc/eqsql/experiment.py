# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import NamedTuple

import pandas as pd
from polaris.hpc.eqsql.task import Task
from sqlalchemy import text


class Experiment(NamedTuple):
    exp_id: str

    def tasks(self, engine):
        df = pd.DataFrame([(t.task_id, t.running_on, t.status, t.message) for t in self._get_all_tasks(engine)])
        df.columns = ["task_id", "running_on", "status", "message"]
        return df

    def get_logs(self, engine):
        with engine.connect() as conn:
            task_ids = [t.task_id for t in self._get_all_tasks(engine)]
            sql = text("SELECT * FROM task_log where task_id = ANY(:task_ids)")
            logs = pd.read_sql(sql, conn, params={"task_ids": task_ids})
            return logs.sort_values("created_at")

    def _get_all_tasks(self, engine):
        return Task.by_exp_id(engine, self.exp_id)
