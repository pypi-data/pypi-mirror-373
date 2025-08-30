# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shutil
from pathlib import Path

import pandas as pd

from polaris.scenario_management.list_scenario_files import list_scenario_files, list_supply
from polaris.utils.testing.repository_structure import check_supply_sources, check_file_places


def assemble_scenario_files(git_dir: Path, scenario_name: str, full_warnings=False):
    logging.warning(f"Building scenario files for {scenario_name} in {git_dir}")
    logging.warning("Files may be overwritten. BE CAREFUL WHEN COMMITING IT BACK TO THE REPOSITORY!")
    base_dir = Path(git_dir)
    file_sources = list_scenario_files(base_dir, scenario_name)

    logging.info(f"Building {scenario_name}")
    supply_sources = list_supply(file_sources)
    check_supply_sources(base_dir, supply_sources)
    check_file_places(base_dir, file_sources, scenario_name, full_warnings)

    for source, _, target in file_sources:

        # Merge the SRID tables and overrides if they exist
        if "srids.csv" in source.parts:
            if target.exists():
                df = exclusive_records(pd.read_csv(source / "srids.csv"), pd.read_csv(target), "table_name")
                df.to_csv(target, index=False)
                continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, target)
        logging.info(f"Copied {source} to {target}")


def exclusive_records(additional_df, base_df, key):
    # Merge EVERYTHING from the main_df and complement with the stuff from the base_df
    df1 = base_df[~base_df[key].isin(additional_df[key])]
    return pd.concat([additional_df, df1], ignore_index=True)
