# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike

from polaris.network.transit.transit_elements.route import Route
from polaris.utils.database.data_table_access import DataTableAccess


def read_routes(conn: sqlite3.Connection, path_to_file: PathLike):
    data = DataTableAccess(path_to_file).get("transit_routes", conn)

    data.drop(columns=["seated_capacity", "design_capacity", "total_capacity", "number_of_cars", "geo"], inplace=True)
    data.rename(
        columns={
            "description": "route_desc",
            "longname": "route_long_name",
            "shortname": "route_short_name",
            "type": "route_type",
        },
        inplace=True,
    )
    routes = []
    valid_fields = Route(-1).available_fields
    drop_fields = [col for col in data.columns if col not in valid_fields]
    if drop_fields:
        logging.warning(f"transit_routes table has unexpected fields: {drop_fields}. They will be ignored")
    data = data[[col for col in data.columns if col in valid_fields]]

    for _, dt in data.iterrows():
        rt = Route(-1).from_row(dt)
        routes.append(rt)

    return routes
