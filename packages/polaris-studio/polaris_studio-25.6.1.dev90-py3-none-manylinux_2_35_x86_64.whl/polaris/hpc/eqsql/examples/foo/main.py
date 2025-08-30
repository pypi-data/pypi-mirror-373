# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# This is an example script that can be run on the eqsql workers

import json
import sys
from pathlib import Path

from polaris.hpc.eqsql.task_container import TaskContainer

# We setup our python path to include the directory we are in
# This allows us to import other modules from this directory directly
my_dir = str(Path(__file__).parent)
if my_dir not in sys.path:
    sys.path.append(my_dir)


def main():
    # The first command line arg will be the json payload from the database
    with open(sys.argv[1], "r") as f:
        payload_raw = f.read()
        payload_json = json.loads(payload_raw)

    # We get a task container helper object to allow us to log messages back to the db
    task_container = TaskContainer.from_env(None)

    # Log a message back to the db
    task_container.log(f"Got payload with length {len(payload_raw)} which JSON evaluates to a {type(payload_json)}")

    # Import a function (bar) from another module (utils) in the current directory
    from utils import bar

    bar(open_time=payload_json.get("open-time", 10))

    task_container.log(f"Finished")


if __name__ == "__main__":
    main()
