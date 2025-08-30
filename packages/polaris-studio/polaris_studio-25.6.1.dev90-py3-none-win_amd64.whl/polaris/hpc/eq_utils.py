# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import datetime
import logging
import time

import numpy as np
import pandas as pd
from polaris.hpc.eqsql.eq import insert_task
from polaris.hpc.eqsql.eq_db import CANCELLED, CANCELLING, FAILED, FINISHED, QUEUED, RUNNING, tasks_table
from polaris.hpc.eqsql.utils import clear_idle_pg_connection
from sqlalchemy import and_, or_, text

alpha = "66"
light_red, light_yellow = f"#fcc0c7{alpha}", f"#f7ed8d{alpha}"
light_blue, light_purple = f"#c8c8fa{alpha}", f"#c99df5{alpha}"
light_green, light_grey = f"#c4ffcf{alpha}", "#ffffff33"


@clear_idle_pg_connection()
def git_pull(engine, target):
    git_update_task = {"task-type": "control-task", "control-type": "EQ_GIT_PULL"}
    with engine.connect() as conn:
        insert_task(
            conn=conn, task_type=0, exp_id="git-pull", worker_id=f"^{target}$", definition=git_update_task, input={}
        )


@clear_idle_pg_connection()
def restart_worker(engine, target):
    task = {"task-type": "control-task", "control-type": "EQ_RESTART"}

    with engine.connect() as conn:
        insert_task(conn=conn, task_type=0, exp_id="eq-restart", worker_id=f"^{target}$", definition=task, input={})


@clear_idle_pg_connection()
def terminate_worker(engine, target):
    eq_abort_task = {"task-type": "control-task", "control-type": "EQ_ABORT"}
    with engine.connect() as conn:
        insert_task(
            conn=conn,
            task_type=0,
            exp_id="terminate-worker",
            worker_id=f"^{target}$",
            definition=eq_abort_task,
            input={},
        )


@clear_idle_pg_connection()
def pull_and_restart_all(engine, worker_id_startswith=None, sleep_time=20):
    # Get a list of active workers (that matches the given starting pattern)
    df = query_workers(engine, style_df=False)
    if worker_id_startswith is not None:
        df = df[df.worker_id.str.startswith(worker_id_startswith)]

    # Get the list of unique machines that these are running on
    df["machine"] = df.worker_id.str.split("-").str[0:2].str.join("-")
    machines = df.groupby("machine").count().index

    # git pull those machines
    for m in machines:
        logging.info(f"Git pull on machine: {m}")
        git_pull(engine, f"{m}.*")

    # Wait 20 seconds and then restart each worker to get it to see the updated code
    time.sleep(sleep_time)
    for w in df.worker_id:
        logging.info(f"Restart on worker: {m}")
        restart_worker(engine, w)


@clear_idle_pg_connection()
def task_queue(
    engine,
    clear_dead_threshold="7 days",
    recent_fail_threshold="10 hours",
    recent_finish_threshold="10 hours",
    sort_on="exp_id",
    cols=None,
    style_df=True,
):
    with engine.connect() as conn:
        running_or_waiting = tasks_table.c.status.in_([QUEUED, RUNNING])

        th_fail = datetime.datetime.now(datetime.timezone.utc) - pd.to_timedelta(recent_fail_threshold)
        th_fin = datetime.datetime.now(datetime.timezone.utc) - pd.to_timedelta(recent_finish_threshold)
        recently_failed = and_(
            tasks_table.c.status.in_([FAILED, CANCELLING, CANCELLED]), tasks_table.c.updated_at > th_fail
        )
        recently_finished = and_(tasks_table.c.status.in_([FINISHED]), tasks_table.c.updated_at > th_fin)
        stmt = tasks_table.select().filter(or_(running_or_waiting, recently_failed, recently_finished))
        df = add_time_since_update(pd.read_sql(stmt, conn))

    if df.empty:
        return df

    idx = (df.status == RUNNING) & (df.time_since_update > clear_dead_threshold)
    deads = df[idx].task_id.to_list()
    if len(deads) > 0:
        logging.info(f"The following tasks have been running for more than {clear_dead_threshold}.")
        logging.info("Marking them as failed: ")
        logging.info(str(deads))
        stmt = (
            tasks_table.update().filter(tasks_table.c.task_id.in_(deads)).values(status=FAILED).returning(tasks_table.c)
        )
        with engine.connect() as conn:
            conn.execute(stmt)
        df = df[~idx]

    cols = cols or ["task_id", "worker_id", "exp_id", "status", "message", "running_on", "time_since_update"]
    df = df.sort_values(sort_on)[cols]

    return df.style.apply(style_tasks_df, axis=1) if style_df else df


def style_tasks_df(s):
    highlight = ""
    if s.loc["status"] == "running":
        if s.time_since_update > datetime.timedelta(hours=3):
            highlight = f"background-color: {light_yellow}; color: #000;"
        else:
            highlight = f"background-color: {light_green}; color: #000;"
    elif s.loc["status"] == "failed":
        highlight = f"background-color: {light_red}; color: #000;"
    elif s.loc["status"] == "finished":
        highlight = f"background-color: {light_blue}; color: #000;"
    else:
        highlight = f"background-color: {light_grey}; color: #000;"
    # if s.loc["time_since_update"] >= running_crit_thresh:
    #     highlight = f"background-color: {light_red}; color: #000;"
    return [highlight for _ in s.index]


@clear_idle_pg_connection()
def recent_failed_tasks(engine, recent_threshold="7 days", sort_on="exp_id", cols=None):
    with engine.connect() as conn:
        stmt = tasks_table.select().filter(tasks_table.c.status.in_([FAILED]))
        df = add_time_since_update(pd.read_sql(stmt, conn))

    if df.empty:
        return df

    idx = df.time_since_update < recent_threshold
    cols = cols or ["task_id", "worker_id", "exp_id", "status", "message", "running_on", "time_since_update"]
    df = df[idx].sort_values(sort_on)[cols]

    return df


worker_sql = """
  SELECT w.*, t.exp_id
  FROM workers w
  LEFT join tasks t ON w.task_id = t.task_id
  WHERE w.status <> 'dead'
  order by worker_id;
"""


@clear_idle_pg_connection()
def query_workers(engine, clear_dead_threshold="3 days", clear_idle_threshold="10 minutes", style_df=True):
    with engine.connect() as conn:
        df = pd.read_sql(text(worker_sql), con=conn)
        df = add_time_since_update(df)
        df["task_id"] = df.task_id.apply(lambda x: "" if x is None or np.isnan(x) else str(int(x)))
        df["exp_id"] = df.exp_id.apply(lambda x: "" if x is None else str(x))
        if df.empty:
            return df

        if clear_dead_threshold is not None:
            idx1 = df.time_since_update > clear_dead_threshold
            idx2 = (df.status == "idle") & (df.time_since_update > clear_idle_threshold)
            deads = df[idx1 | idx2].worker_id.to_list()
            conn.execute(
                text("DELETE from workers where worker_id = ANY(:worker_ids);"), parameters={"worker_ids": deads}
            )
            df = df[~(idx1 | idx2)]

    return df.style.apply(style_worker_df, axis=1) if style_df else df


def style_worker_df(s):
    waiting_thresh = datetime.timedelta(minutes=3)
    running_warn_thresh = datetime.timedelta(hours=3)
    running_crit_thresh = datetime.timedelta(hours=5)
    highlight = ""
    if s.loc["status"] == "idle":
        if s.loc["time_since_update"] >= waiting_thresh:
            highlight = f"background-color: {light_yellow}; color: #000;"
    else:
        if s.loc["time_since_update"] >= running_crit_thresh:
            highlight = f"background-color: {light_red}; color: #000;"
        elif s.loc["time_since_update"] >= running_warn_thresh:
            highlight = f"background-color: {light_yellow}; color: #000;"
        else:
            highlight = f"background-color: {light_green}; color: #000;"
    return [highlight for _ in s.index]


@clear_idle_pg_connection()
def query_experiments(engine, experiment_ids, cols=None, style_df=True, cross_validate_to_workers=True):
    with engine.connect() as conn:
        stmt = tasks_table.select().filter(tasks_table.c.exp_id.in_(experiment_ids))
        df = add_time_since_update(pd.read_sql(stmt, conn))
        df = df.sort_values("task_id", ascending=False).drop_duplicates(["exp_id"])
    cols = cols or ["task_id", "worker_id", "exp_id", "status", "message", "running_on", "time_since_update"]
    missing_exp_id = set(experiment_ids) - set(df.exp_id)
    df = pd.concat([df, pd.DataFrame({"exp_id": list(missing_exp_id), "status": "no_record", "running_on": None})])
    df = df.sort_values("exp_id")[cols]
    df = df.reset_index(drop=True)
    df["machine_id"] = df.running_on.str.split("-").str[0:-1].apply(lambda x: None if x is None else "-".join(list(x)))
    df["task_id"] = df.task_id.fillna(-1).astype(int)

    def f(m):
        try:
            return int(m.split("_")[-1]) if m is not None and "iteration_" in m else 0
        except Exception:
            return 0

    df["iteration"] = df.message.apply(f)

    if cross_validate_to_workers:
        df_w = query_workers(engine, style_df=False)
        df_w = df_w[df_w.status == "running"]
        # display(df_w)
        exp_by_worker = df_w[["worker_id", "exp_id"]].set_index("worker_id").to_dict()["exp_id"]
        df["worker_thinks"] = df.running_on.apply(lambda w: exp_by_worker.get(w, "nothing"))
    return df.style.apply(style_experiment_df, axis=1) if style_df else df


def style_experiment_df(s):
    highlight = ""
    if s.loc["status"] == "running":
        if "worker_thinks" in s and s.worker_thinks != s.exp_id:
            highlight = f"background-color: {light_red}; color: #000;"
        elif s.time_since_update > datetime.timedelta(hours=5):
            highlight = f"background-color: {light_yellow}; color: #000;"
        else:
            highlight = f"background-color: {light_green}; color: #000;"

    elif s.loc["status"] == "queued":
        highlight = f"background-color: {light_grey}; color: #000;"
    elif s.loc["status"] == "no_record":
        highlight = f"background-color: {light_purple}; color: #000;"
    elif s.loc["status"] == "failed":
        highlight = f"background-color: {light_red}; color: #000;"
    elif s.loc["status"] == "finished":
        highlight = f"background-color: {light_blue}; color: #000;"
    return [highlight for _ in s.index]


def add_time_since_update(df):
    if df.empty:
        return df
    df["updated_at"] = df.updated_at.dt.floor("s")
    df["updated_at"] = df.updated_at.dt.tz_localize(datetime.timezone.utc)
    df["time_since_update"] = datetime.datetime.now(datetime.timezone.utc) - df["updated_at"]
    df["time_since_update"] = df.time_since_update.dt.floor("s")
    return df
