# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def export_connection_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    connec = DataTableAccess(path_to_file).get("Connection", conn=conn).to_crs(target_crs)
    signal_nodes = pd.read_sql("select nodes from signal", conn).nodes
    signs = pd.read_sql("select link, dir, sign from sign", conn)

    # Manipulates link data (for number of lanes)
    link_sql = """select link, 0 dir, lanes_ab lanes from link where lanes_ab>0
                  UNION ALL
                  select link, 1 dir, lanes_ba lanes from link where lanes_ba>0"""
    links = pd.read_sql(link_sql, conn)
    connec = connec.merge(links.rename(columns={"lanes": "in_lanes"}), on=["link", "dir"], how="left")
    links.rename(columns={"link": "to_link", "dir": "to_dir", "lanes": "out_lanes"}, inplace=True)
    connec = connec.merge(links, on=["to_link", "to_dir"], how="left")

    # Manipulates pocket data
    pocket = DataTableAccess(path_to_file).get("Pocket", conn=conn)
    pocket = pocket.pivot(values="lanes", index=["link", "dir"], columns="type").fillna(0).reset_index()
    for col in ["LEFT_TURN", "RIGHT_TURN", "LEFT_MERGE", "RIGHT_MERGE"]:
        if col not in pocket.columns:
            pocket[col] = 0
    in_pkt = pocket[["link", "dir", "LEFT_TURN", "RIGHT_TURN"]]
    out_pkt = pocket[["link", "dir", "LEFT_MERGE", "RIGHT_MERGE"]].rename(columns={"link": "to_link", "dir": "to_dir"})
    connec = connec.merge(in_pkt, on=["link", "dir"], how="left").merge(out_pkt, on=["to_link", "to_dir"], how="left")
    connec.fillna(0, inplace=True)

    # Compute geometries for connections
    connec["geo"] = connec.geometry.to_wkt(rounding_precision=6)

    # Assigns intersection control type
    connec = connec.assign(ctrl_type="no_control")
    connec.loc[connec.node.isin(signal_nodes), "ctrl_type"] = "signal"

    connec = connec.merge(signs, on=["link", "dir"], how="left")
    connec.loc[connec.sign == "STOP", "ctrl_type"] = "stop_2_way"
    connec.loc[connec.sign == "ALL_STOP", "ctrl_type"] = "stop_4_way"

    col_renames = {
        "conn": "mvmt_id",
        "node": "node_id",
        "geo": "geometry",
        "link": "ib_link_id",
        "to_link": "ob_link_id",
    }
    connec.rename(columns=col_renames, inplace=True)
    connec = connec.assign(start_ib_lane=None, end_ib_lane=None, start_ob_lane=None, end_ob_lane=None)
    connec.lanes = connec.lanes.astype(str)
    connec.to_lanes = connec.to_lanes.astype(str)

    for idx, record in connec.iterrows():
        # Get the number of lanes in the link
        inlanes = record.lanes.split(",")

        def in_lane_for_value(value, record):
            if "L" in value:
                return -record.LEFT_TURN
            if "R" in value:
                return record.in_lanes + record.RIGHT_TURN
            return record.in_lanes - int(value) + 1

        connec.loc[[idx], "start_ib_lane"] = in_lane_for_value(inlanes[-1], record)
        if len(inlanes) > 1:
            connec.loc[[idx], "end_ib_lane"] = in_lane_for_value(inlanes[0], record)

        def out_lane_for_value(value, record):
            if "L" in value:
                return -record.LEFT_MERGE
            if "R" in value:
                return record.out_lanes + record.RIGHT_MERGE
            return record.out_lanes - int(value) + 1

        outlanes = record.to_lanes.split(",")
        connec.loc[[idx], "start_ob_lane"] = out_lane_for_value(outlanes[-1], record)
        if len(outlanes) > 1:
            connec.loc[[idx], "end_ob_lane"] = out_lane_for_value(outlanes[0], record)

    connec.ib_link_id = 2 * connec.ib_link_id + connec["dir"]
    connec.ob_link_id = 2 * connec.ob_link_id + connec["to_dir"]

    cols = [
        "mvmt_id",
        "node_id",
        "ib_link_id",
        "start_ib_lane",
        "end_ib_lane",
        "ob_link_id",
        "start_ob_lane",
        "end_ob_lane",
        "type",
        "ctrl_type",
        "geometry",
    ]

    connec["type"] = connec["type"].str.lower()
    connec[cols].to_csv(join(gmns_folder, "movement.csv"), index=False)
