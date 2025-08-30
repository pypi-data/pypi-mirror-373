# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.run_utils import merge_csvs
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.logging_utils import function_logging


@function_logging("Getting best iteration from {config.data_dir}")
def get_best_iteration(config: ConvergenceConfig, num_iters_to_use: int = 10):
    """Determine the best iteration for a convergence run based on the minimum relative gap.

    Args:
        *config* (:obj:`ConvergenceConfig`): Config object defining the convergence run

    Returns:
        *(Path)*: the full path to the sub-directory corresponding to the best iteration
    """

    # select lowest gap iteration
    gaps = merge_csvs(config, "gap_calculations.csv", save_merged=False)
    iter_name = gaps.tail(num_iters_to_use)["relative_gap_min0"].idxmin()

    logging.info(f"best iteration = {config.data_dir / iter_name}")
    return config.data_dir / iter_name


def get_last_iteration(model_dir: Path) -> Path:
    """Determine the last iteration run in a given model.

    Args:
        *model_dir* (:obj:`Path`): Path to the base model directory

    Returns:
        *(Path)*: the full path to the sub-directory corresponding to the last iteration
    """

    # Get the iterations which are normal iterations and which are finished
    finished_iterations = model_dir.glob("*_iteration_*/finished")
    finished_iterations = {int(e.parent.name.split("_iteration_")[1]): e for e in finished_iterations}
    if len(finished_iterations) == 0:
        return None

    last_iteration = sorted(finished_iterations.keys())[-1]
    last_iteration = finished_iterations[last_iteration].parent
    return last_iteration


def extract_iteration(sub_dir: Path, db_name: str, needed_files=["supply_db", "demand_db", "freight_db", "summary"]):
    """Ensures that a iteration directory contains the necessary files, extracting them from .tar.gz if needed.

    Throws an error if the needed files can't be found.
    """

    # check file existence and untar as needed
    files = PolarisInputs.from_dir(sub_dir, db_name)

    if "supply_db" in needed_files:
        ScenarioCompression.maybe_extract(files.supply_db)
    if "demand_db" in needed_files:
        ScenarioCompression.maybe_extract(files.demand_db)
    if "freight_db" in needed_files:
        ScenarioCompression.maybe_extract(files.freight_db)
    if all([getattr(files, f).exists() for f in needed_files]):
        return

    def pp(file):
        logging.error(f"      {file}: {'âœ”' if file.exists() else 'âœ˜'}")

    logging.error(f"{sub_dir} is missing needed files: ")
    [pp(getattr(files, f)) for f in needed_files]

    raise RuntimeError(f"{sub_dir} is missing needed files: ")
