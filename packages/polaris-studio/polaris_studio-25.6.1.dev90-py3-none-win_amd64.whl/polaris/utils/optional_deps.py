# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from importlib import util as iutil

dep_list = {
    "aequilibrae": "builder",
    "pyproj": "builder",
    "requests": "builder",
    "geopandas": "builder",
}


def check_dependency(dep: str, raise_error=True):
    if iutil.find_spec(dep) is None:
        txt = " Please install it directly"
        txt += f" or try 'pip install polaris[{dep_list[dep]}]'" if dep in dep_list else "."
        if raise_error:
            raise ImportError(f"Dependency {dep} is not installed.{txt}")
        else:
            logging.warning(f"Dependency {dep} is not installed.{txt}")
