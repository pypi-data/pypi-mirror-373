# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.transit.transit_elements.trip import Trip


def read_trips(conn: sqlite3.Connection, path_to_file: PathLike):
    data = DataTableAccess(path_to_file).get("transit_trips", conn)
    data.drop(columns=["seated_capacity", "design_capacity", "total_capacity", "is_artic"], inplace=True)
    data.drop(columns=["number_of_cars"], inplace=True)

    pats = pd.read_sql("Select pattern_id, route_id from Transit_Patterns", conn)
    data = data.merge(pats, on="pattern_id")
    data.trip = data.trip.astype(str)
    data.rename(
        columns={
            "trip": "trip_headsign",
            "dir": "direction_id",
            "pattern_id": "shape_id",
        },
        inplace=True,
    )

    valid_fields = Trip().available_fields
    drop_fields = [col for col in data.columns if col not in valid_fields]
    if drop_fields:
        logging.warning(f"transit_trips table has unexpected fields: {drop_fields}. They will be ignored")
    data = data[[col for col in data.columns if col in valid_fields]]
    data = data.assign(service_id=data.shape_id)
    return [Trip().from_row(dt) for _, dt in data.iterrows()]
