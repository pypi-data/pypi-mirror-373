# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
import sys
from os.path import join
from pathlib import Path

import pandas as pd
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.run_utils import get_output_dirs, get_output_dir_index, merge_csvs
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.db_utils import has_table, table_to_csv, run_sql_file, commit_and_close
from polaris.utils.func_utils import can_fail
from polaris.utils.list_utils import first_and_only
from polaris.utils.logging_utils import function_logging


def load_gaps(gap_path, run_id: str = None):
    try:
        df = pd.read_csv(gap_path, index_col=False)
        if run_id is not None:
            df = df.assign(run_id=run_id)
        return df
    except:
        logging.error(f"Gap path {gap_path} not found.")
        return None


@can_fail
@function_logging("        ~   Generating Gap Reports")
def generate_gap_report(config: ConvergenceConfig, output_dir):
    generate_gap_report_for_dir(output_dir)
    generate_summary_gap_report(config)


@function_logging("Generating Gap Reports")
def generate_all_gap_reports(config: ConvergenceConfig):
    folder_list = sorted(get_output_dirs(config), key=get_output_dir_index)
    [generate_gap_report_for_dir(folder) for folder in folder_list]
    generate_summary_gap_report(config)


def generate_summary_gap_report(config):
    merge_csvs(config, "gap_calculations.csv")
    merge_csvs(config, "gap_breakdown.csv")


def generate_gap_report_for_dir(dir_path):
    """creates the csvs if they are not existent. Untar file if needed and run the query"""

    logging.info(f"            - {dir_path}")
    files_in_directory = os.listdir(dir_path)
    if "gap_calculations.csv" in files_in_directory and "gap_breakdown.csv" in files_in_directory:
        return

    try:
        demand_file = first_and_only(Path(dir_path).glob("*-Demand.sqlite"))
        sql_dir = Path(__file__).parent / "sql"
        with commit_and_close(ScenarioCompression.maybe_extract(demand_file)) as conn:
            if has_table(conn, "gap_calculations"):
                conn.execute("drop table if exists gap_calculations")
            if has_table(conn, "gap_breakdown"):
                conn.execute("drop table if exists gap_breakdown")
            run_sql_file(sql_dir / "gap_calculations.sql", conn)
            run_sql_file(sql_dir / "gap_breakdown.sql", conn)

            table_to_csv(conn, "gap_calculations", join(dir_path, "gap_calculations.csv"))
            table_to_csv(conn, "gap_calculations_binned", join(dir_path, "gap_calculations_binned.csv"))
            table_to_csv(conn, "gap_breakdown", join(dir_path, "gap_breakdown.csv"))
            table_to_csv(conn, "gap_breakdown_binned", join(dir_path, "gap_breakdown_binned.csv"))

    except Exception as e:
        print("error on directory", dir_path)
        print(sys.exc_info())
        raise e
