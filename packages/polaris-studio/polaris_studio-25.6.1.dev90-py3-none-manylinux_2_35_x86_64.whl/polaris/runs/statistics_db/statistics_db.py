# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import socket

import sqlalchemy.engine
from sqlalchemy import TIMESTAMP, Column, Float, Integer, MetaData, Table, Text, func

from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_version import PolarisVersion
from polaris.utils.func_utils import can_fail

metadata_obj = MetaData()

iterations_table = Table(
    "iterations",
    metadata_obj,
    Column("iteration_uuid", Text, primary_key=True),
    Column("convergence_uuid", Text),
    Column("model_name", Text),
    Column("abm_config", Text),
    Column("iteration_type", Text),
    Column("iteration_number", Integer),
    Column("machine", Text),
    Column("exe_name", Text),
    Column("exe_sha", Text),
    Column("num_threads", Integer),
    Column("run_time", Float),  # runtime of the iteration in seconds
    Column("created_at", TIMESTAMP, default=func.now()),
)


def ensure_table_exists(engine: sqlalchemy.Engine):
    metadata_obj.create_all(engine)


@can_fail
def record_statistics(
    config: ConvergenceConfig,
    iteration: ConvergenceIteration,
    engine: sqlalchemy.Engine,
):
    ensure_table_exists(engine)
    with open(iteration.scenario_file, "r") as fl:
        specs = str(json.load(fl))

    # TODO: Handle key collisions on the primary ID
    version = PolarisVersion.from_exe(config.polaris_exe)
    stmt = iterations_table.insert().values(
        iteration_uuid=iteration.uuid,
        convergence_uuid=config.uuid,
        model_name=config.db_name,
        abm_config=specs,
        iteration_type=iteration.type(),
        iteration_number=iteration.iteration_number,
        machine=socket.gethostname(),
        exe_name=str(config.polaris_exe),
        exe_sha=version.git_sha,
        num_threads=config.num_threads,
        run_time=iteration.runtime,
    )

    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
