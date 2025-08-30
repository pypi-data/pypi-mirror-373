# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sys
from pathlib import Path


def find_dir_containing(file):
    root_dir = os.path.abspath(".").split(os.path.sep)[0] + os.path.sep
    project_root = Path(os.getcwd())
    while not (project_root / file).exists() and project_root != root_dir:
        project_root = project_root.parent
    if project_root == root_dir:
        raise "can't find project root"
    return project_root


def add_path(p):
    p = str(Path(p).resolve())
    print(f"p={p}")
    if p not in sys.path:
        print(f"adding {p} to path")
        sys.path.append(p)


add_path(find_dir_containing("pyproject.toml"))

import os

# from bin.hpc.python.gpra22.gpra_db import (
#     init,
#     gpra_conn,
#     query_job,
#     add_job,
#     schedule_job,
#     clear_job_status,
#     query_machines,
#     all_nodes,
#     signal_nodes,
# )
# import bin.hpc.eqsql.eq


logging.basicConfig(
    stream=sys.stdout, format="%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z", level=logging.INFO
)
