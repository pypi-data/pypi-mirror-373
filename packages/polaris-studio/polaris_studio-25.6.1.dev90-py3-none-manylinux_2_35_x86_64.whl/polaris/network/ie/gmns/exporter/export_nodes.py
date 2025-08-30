# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

import numpy as np

from polaris.utils.database.data_table_access import DataTableAccess


def export_nodes_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    nodes = DataTableAccess(path_to_file).get("Node", conn=conn).to_crs(target_crs)
    nodes.loc[:, "x"] = np.round(nodes.geometry.x, 6)
    nodes.loc[:, "y"] = np.round(nodes.geometry.y, 6)

    nodes.rename(columns={"node": "node_id", "x": "x_coord", "y": "y_coord", "zone": "zone_id"}, inplace=True)
    nodes.rename(columns={"control_type": "ctrl_type"}, inplace=True)
    nodes.loc[nodes.ctrl_type == "stop_sign", "ctrl_type"] = "stop"
    nodes.loc[nodes.ctrl_type == "all_stop", "ctrl_type"] = "4_stop"
    nodes.drop(columns=["geo"], inplace=True)
    nodes.to_csv(join(gmns_folder, "node.csv"), index=False)
