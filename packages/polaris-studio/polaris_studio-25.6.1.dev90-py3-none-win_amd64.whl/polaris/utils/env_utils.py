# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import importlib.util as iutil
import os
import re
import sys
from enum import IntEnum
from pathlib import Path
from socket import gethostname


def is_windows() -> bool:
    return os.name == "nt"


def is_not_windows() -> bool:
    return os.name != "nt"


def is_on_ci() -> bool:
    # CI_COMMIT_REF_NAME is defined for all GitLab runner environments, CI for GitHub Actions environments
    return env_var_defined("CI_COMMIT_REF_NAME") or env_var_defined("CI")


inside_qgis = iutil.find_spec("qgis") is not None


def env_var_defined(x) -> bool:
    return os.environ.get(x) is not None


def should_run_integration_tests() -> bool:
    if not is_on_ci():
        return True  # always allow tests to run locally

    # Otherwise, only run on named testing branch which are executed from linux
    integration_branches = ["fds/integration_test"]
    return is_not_windows() and any(branch == os.environ["CI_COMMIT_REF_NAME"] for branch in integration_branches)


class WhereAmI(IntEnum):
    DESKTOP = 0, "desktop"
    WSL_CLUSTER = 1, "wsl"
    CROSSOVER_CLUSTER = 2, "crossover"
    BEBOP_CLUSTER = 3, "bebop"
    IMPROV_CLUSTER = 4, "improv"
    HPC_CLUSTER = 5, "hpc"

    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    def __str__(self):
        return self.label


def where_am_i_running(clue=None) -> WhereAmI:
    clue = clue or gethostname()
    if "crossover" in clue or "xover" in clue:
        return WhereAmI.CROSSOVER_CLUSTER
    if "bebop" in clue or "bdw" in clue:
        return WhereAmI.BEBOP_CLUSTER
    if "ilogin" in clue or "improv" in clue or re.match("i[0-9].*", clue) is not None:
        return WhereAmI.IMPROV_CLUSTER
    if "VMS-C" in clue:
        return WhereAmI.WSL_CLUSTER
    if "VMS-HPC" in clue:
        return WhereAmI.HPC_CLUSTER
    return WhereAmI.DESKTOP


def get_based_on_env(lu: dict):
    # Allow for different values on different systems - convert the keys into WhereAmI enums for lookup
    if not isinstance(lu, dict):
        return lu

    def keyify(k):
        return k if isinstance(k, WhereAmI) else where_am_i_running(k)

    lu = {keyify(k): v for k, v in lu.items()}
    return lu[where_am_i_running()]


def get_data_root():
    if where_am_i_running() in (WhereAmI.CROSSOVER_CLUSTER, WhereAmI.BEBOP_CLUSTER, WhereAmI.IMPROV_CLUSTER):
        return Path("/lcrc/project/POLARIS/")
    return Path(os.path.expanduser("~/"))


def setup_path():
    polaris_dir = Path(__file__).resolve().absolute().parent.parent.parent
    if str(polaris_dir) not in sys.path:
        sys.path.append(str(polaris_dir))

    # also set the path via env variable for any child processes we kick off
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"] + ":" + str(polaris_dir)
    else:
        os.environ["PYTHONPATH"] = str(polaris_dir)
