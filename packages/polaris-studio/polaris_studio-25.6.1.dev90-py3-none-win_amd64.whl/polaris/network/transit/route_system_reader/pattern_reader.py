# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike

from polaris.network.transit.transit_elements.pattern import Pattern
from polaris.utils.database.data_table_access import DataTableAccess


def read_patterns(conn: sqlite3.Connection, target_crs, path_to_file: PathLike):
    patterns = []
    data = DataTableAccess(path_to_file).get("transit_patterns", conn).to_crs(target_crs)
    if data.empty:
        return

    data.drop(columns=["matching_quality"], inplace=True)
    data.rename(columns={"pattern": "pattern_hash", "geo": "shape"}, inplace=True)

    valid_fields = Pattern(None, -1, None).available_fields
    drop_fields = [col for col in data.columns if col not in valid_fields]
    if drop_fields:
        logging.warning(f"transit_patterns table has unexpected fields: {drop_fields}. They will be ignored")
    data = data[[col for col in data.columns if col in valid_fields]]

    for _, dt in data.iterrows():
        pat = Pattern(None, dt.route_id, None).from_row(dt)
        pat.shape_length = pat.best_shape().length
        patterns.append(pat)
    return patterns
