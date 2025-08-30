# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import zipfile
from os import PathLike
from os.path import join, dirname, realpath

from polaris.network.starts_logging import logger


def jumpstart_spatialite(network_file: PathLike):
    logger.info(f"Creating file at {network_file}")
    pth = join(dirname(dirname(realpath(__file__))), "data")
    base_name = "empty_spatialite"
    source_filename = join(pth, f"{base_name}.zip")

    with zipfile.ZipFile(source_filename, "r") as zf:
        data = zf.read(f"{base_name}.sqlite")
        with open(network_file, "wb") as output:
            output.write(data)
