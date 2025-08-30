# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def export_locations_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    locs = DataTableAccess(path_to_file).get("Location", conn=conn).to_crs(target_crs)

    locs.loc[:, "x"] = np.round(locs.geometry.x, 6)
    locs.loc[:, "y"] = np.round(locs.geometry.y, 6)

    locs.rename(
        columns={
            "location": "loc_id",
            "x": "x_coord",
            "y": "y_coord",
            "link": "link_id",
            "offset": "lr",
            "land_use": "loc_type",
            "zone": "zone_id",
        },
        inplace=True,
    )

    links = pd.read_sql("Select link link_id, node_a ref_node_id from Link", conn)

    locs = locs.merge(links, on="link_id", how="left")

    cols = ["loc_id", "link_id", "ref_node_id", "lr", "x_coord", "y_coord", "loc_type", "zone_id"]

    locs.loc[:, "link_id"] = 2 * locs.link_id + locs["dir"]
    locs[cols].to_csv(join(gmns_folder, "location.csv"), index=False)
