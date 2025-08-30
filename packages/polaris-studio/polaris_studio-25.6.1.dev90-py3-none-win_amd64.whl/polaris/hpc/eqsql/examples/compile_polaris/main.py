#!/usr/bin/env python
# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import json
import logging
import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

from polaris.utils.env_utils import WhereAmI, where_am_i_running

try:
    from git import Repo
except:
    subprocess.run(f"{sys.executable} -m pip install --upgrade pip", shell=True, check=True)
    subprocess.run(f"{sys.executable} -m pip install GitPython", shell=True, check=True)
    from git import Repo


from polaris.hpc.eqsql.task_container import TaskContainer
from polaris.utils.dir_utils import with_dir


def main():
    # The first command line arg will be the json payload from the database
    if len(sys.argv) == 2:
        with open(sys.argv[1], "r") as f:
            payload_raw = f.read()
            payload = json.loads(payload_raw)
    else:
        payload_raw = "hello mum"
        payload = {
            "source_dir": "/home/james.cook/git/test/polaris-linux",
            "branch": "develop",
            "username": "gitlab",
            "password": os.environ["GITLAB_PASSWORD"],
            "modules": "gcc/10 hdf5/1.12 cmake/3.24 anaconda3",
        }

    # We get a task container helper object to allow us to log messages back to the db
    task_container = TaskContainer.from_env(None)

    # Log a message back to the db
    task_container.log(f"Got payload {payload}")

    # Make sure we have a git repo to work with
    source_dir = ensure_cloned(task_container, payload)

    # Update fields in the payload with sensible defaults
    payload = check_modules(payload)
    payload = set_install_dir(source_dir, payload)

    # Actually compile
    build_source(source_dir, task_container, payload)

    task_container.log(f"Binaries installed here: {payload['install_dir']}")
    task_container.log(f"Finished")


def ensure_cloned(task_container, payload):
    source_dir = Path(payload["source_dir"])
    if not source_dir.exists():
        task_container.log(f"Cloning repo to {source_dir}")

        source_dir.mkdir(parents=True, exist_ok=True)
        user = payload["username"]
        if "password" in payload:
            pwd = payload["password"]
        elif "password_file" in payload:
            with open(payload["password_file"]) as f:
                pwd = f.read().strip()
        else:
            raise RuntimeError("No gitlab password supplied")

        url = f"https://{user}:{pwd}@git-out.gss.anl.gov/polaris/code/polaris-linux.git"

        repo = Repo.clone_from(url, source_dir, branch=payload["branch"])
    else:
        task_container.log(f"Using existing repo at {source_dir}")
        repo = Repo(source_dir)
        if repo.is_dirty():
            raise RuntimeError("Can't compile from a dirty working dir")
        repo.git.checkout(payload["branch"])

    repo.git.pull()
    return source_dir


def build_source(source_dir, task_container, payload):
    with with_dir(source_dir):
        with open("tmp_build.sh", "w") as f:
            if "modules" in payload:
                f.write(f"module load {payload['modules']}\n")
            f.write(f"python build.py -cb > build.out 2>&1\n")

        with open("build-config.json", "w") as f:
            deps_dir = payload.get("deps_dir", "/lcrc/project/POLARIS/bebop/opt/polaris/deps")
            f.write(
                dedent(
                    f"""
                    {{
                        "linux": {{
                            "deps_dir": "{deps_dir}",
                            "compiler": "gcc",
                            "do_build": true,
                            "do_configure": true,
                            "do_test": false,
                            "build_type": "release",
                            "install_dir": {payload['install_dir']},
                            "verbose": false,
                            "enable_libs": [],
                            "separate_branch_builds": false,
                            "license": "FALSE",
                            "only_core": "FALSE",
                            "generator": "Unix Makefiles",
                            "cxx_compiler": "g++",
                            "working_dir": "{source_dir}"
                        }}
                    }}"""
                )
            )

        output = subprocess.check_output(f"/bin/bash tmp_build.sh", shell=True, cwd=source_dir, encoding="utf-8")
        task_container.log(output)


def check_modules(payload):
    if "modules" in payload:
        return payload
    where = where_am_i_running()
    if where == WhereAmI.BEBOP_CLUSTER:
        payload["modules"] = "binutils gcc/11.4 hdf5/1.14 anaconda3"
    elif where == WhereAmI.CROSSOVER_CLUSTER:
        payload["modules"] = "gcc/10 hdf5/1.12 cmake/3.24 anaconda3"
    elif where == WhereAmI.IMPROV_CLUSTER:
        payload["modules"] = "gcc/11.4 hdf5/1.14 anaconda3"
    else:
        logging.info("Don't know which modules to load ?!")
    return payload


def set_install_dir(source_dir, payload):
    if "install_dir" not in payload:
        payload["install_dir"] = "null"
    else:
        repo = Repo(source_dir)
        commit = repo.head.commit
        branch = payload["branch"]
        date = commit.committed_datetime.strftime("%Y%m%d")
        sha = commit.hexsha[0:8]
        install_dir = Path(payload["install_dir"]) / f"{branch}_{date}_{sha}"
        payload["install_dir"] = f'"{install_dir}"'
    return payload


if __name__ == "__main__":
    main()
