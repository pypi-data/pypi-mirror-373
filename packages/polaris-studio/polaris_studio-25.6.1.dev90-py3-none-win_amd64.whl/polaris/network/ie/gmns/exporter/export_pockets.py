# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def export_pockets_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    links = DataTableAccess(path_to_file).get("Link", conn=conn)
    links_ba = links.assign(dir=1)
    b = np.array(links_ba.node_b.values)
    links_ba.loc[:, "node_b"] = links_ba.node_a[:]
    links_ba.loc[:, "node_a"] = b[:]
    links_ab = links.assign(dir=0)

    links = pd.concat([links_ab, links_ba])[["link", "dir", "node_a", "length"]].rename(
        columns={"length": "link_length", "node_a": "ref_node_id"}
    )

    pockets = DataTableAccess(path_to_file).get("Pocket", conn=conn)
    pockets = pockets.assign(l_lanes_added=0, r_lanes_added=0)
    pockets.rename(columns={"length": "distance", "type": "pocket_type"}, inplace=True)
    pockets.distance = pockets.distance.astype(int)

    pockets.loc[pockets.pocket_type.str.contains("RIGHT"), "r_lanes_added"] = pockets.lanes
    pockets.loc[pockets.pocket_type.str.contains("LEFT"), "l_lanes_added"] = pockets.lanes

    pockets = pockets.merge(links, on=["link", "dir"], how="left")
    pockets.ref_node_id = pockets.ref_node_id.astype(int)
    pockets.link_length = pockets.link_length.astype(int)

    mpockets = pockets[pockets.pocket_type.str.contains("MERGE")]
    filter_flds = ["link", "dir", "distance", "ref_node_id"]
    mpockets = mpockets.groupby(filter_flds).sum()[["r_lanes_added", "l_lanes_added"]].reset_index()
    mpockets = mpockets.assign(start_lr=0, end_lr=mpockets.distance)

    tpockets = pockets[pockets.pocket_type.str.contains("TURN")]
    filter_flds = ["link", "dir", "distance", "link_length", "ref_node_id"]
    tpockets = tpockets.groupby(filter_flds).sum()[["r_lanes_added", "l_lanes_added"]].reset_index()
    tpockets = tpockets.assign(start_lr=tpockets.link_length - tpockets.distance, end_lr=tpockets.link_length)
    pockets = pd.concat([mpockets, tpockets])
    pockets.link = 2 * pockets.link + pockets["dir"]
    pockets.end_lr /= 1000
    pockets.start_lr /= 1000
    pockets.rename(columns={"link": "link_id"}, inplace=True)
    pockets.drop(columns=["link_length", "distance", "dir"], inplace=True)
    pockets = pockets.assign(segment_id=np.arange(pockets.shape[0]) + 1)

    pockets.to_csv(join(gmns_folder, "segment.csv"), index=False)
