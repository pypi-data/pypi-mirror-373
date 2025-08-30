# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from polaris.utils.database.data_table_access import DataTableAccess


def aggregation_layer(supply_file: Path, aggregation: str):
    area_layer = DataTableAccess(supply_file).get("zone" if aggregation == "zone" else "Counties")
    area_layer.geometry = area_layer.geometry.centroid

    area_layer = area_layer[[aggregation, "geo"]].assign(x=area_layer.geometry.x, y=area_layer.geometry.y)
    area_layer.rename(columns={aggregation: "node_id"}, inplace=True)
    return area_layer
