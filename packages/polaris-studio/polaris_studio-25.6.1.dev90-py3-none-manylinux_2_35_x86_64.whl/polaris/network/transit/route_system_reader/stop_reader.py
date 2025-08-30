# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike
from typing import List

import numpy as np

from polaris.network.constants import WALK_AGENCY_ID
from polaris.network.transit.transit_elements.stop import Stop
from polaris.utils.database.data_table_access import DataTableAccess


def read_stops(conn: sqlite3.Connection, target_crs, path_to_file: PathLike) -> List[Stop]:
    data = DataTableAccess(path_to_file).get("transit_stops", conn).to_crs(target_crs)
    data = data[data.agency_id != WALK_AGENCY_ID]
    data = data[data.agency_id > 1]
    data.loc[:, "X"] = np.round(data.geometry.x, 6)
    data.loc[:, "Y"] = np.round(data.geometry.y, 6)

    data.drop(columns=["moved_by_matching", "Z"], inplace=True)
    data.rename(
        columns={
            "description": "stop_desc",
            "name": "stop_name",
            "street": "stop_street",
            "transit_zone_id": "zone_id",
            "Y": "stop_lat",
            "X": "stop_lon",
        },
        inplace=True,
    )

    valid_fields = Stop(-1).available_fields
    drop_fields = [col for col in data.columns if col not in valid_fields]
    if drop_fields:
        logging.warning(f"transit_stops table has unexpected fields: {drop_fields}. They will be ignored")
    data = data[[col for col in data.columns if col in valid_fields]]
    return [Stop(-1).from_row(dt) for _, dt in data.iterrows()]
