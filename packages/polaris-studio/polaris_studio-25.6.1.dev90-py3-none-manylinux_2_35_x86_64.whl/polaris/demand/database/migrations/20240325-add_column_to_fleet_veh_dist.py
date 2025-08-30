# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shutil
import pandas as pd

from polaris.runs.scenario_file import get_scenario_value
from polaris.utils.database.db_utils import filename_from_conn


def migrate(conn):
    data_dir = filename_from_conn(conn).parent
    sc_file = data_dir / "scenario_abm.json"

    if not sc_file.exists():
        logging.warning(f"Not doing anything for migration 20240325 - can't find scenario file: {sc_file}")
        return

    logging.info(f"Getting files to operate on from {sc_file}")
    tnc_file = data_dir / get_scenario_value(sc_file, "tnc_fleet_model_file")

    logging.debug(f"Getting number of TNC operators from {tnc_file}")
    num_tnc_operators = get_scenario_value(tnc_file, "NO_OF_OPERATORS") if tnc_file.exists() else 1

    op_1_name = get_scenario_value(tnc_file, "OP_1") if tnc_file.exists() else "Operator1"
    fleet_veh_dist_file = data_dir / get_scenario_value(sc_file, "fleet_vehicle_distribution_file_name")

    df = pd.read_csv(fleet_veh_dist_file, sep=",|\t", engine="python")

    logging.error(f"Current file: {fleet_veh_dist_file}")
    logging.error(f"Current columns in veh distribution file: {df.columns.names}")

    if "fleet_type" not in df.columns:
        logging.error("File column names are outdated!! Use standard column names.")
        raise Exception

    if "fleet_id" not in df.columns:
        logging.warning(f"Fleet_id column missing from {fleet_veh_dist_file}, adding default value for one operator")
        if num_tnc_operators > 1:
            logging.warning("Migration assumes one operator")
            logging.warning("Manually add rows for your remaining TNC operators")

        df["fleet_id"] = ""  # assign a new col with default data
        df.loc[df["fleet_type"] == "TNC", "fleet_id"] = op_1_name
        shutil.move(fleet_veh_dist_file, fleet_veh_dist_file.with_suffix(fleet_veh_dist_file.suffix + ".backup"))
        sep = "," if fleet_veh_dist_file.name.endswith("csv") else "\t"
        df.to_csv(fleet_veh_dist_file, sep=sep, index=False)
