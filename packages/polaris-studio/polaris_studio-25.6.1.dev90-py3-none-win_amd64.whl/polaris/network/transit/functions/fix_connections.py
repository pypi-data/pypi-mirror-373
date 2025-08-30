# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from math import log10, floor
from os import PathLike

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.starts_logging import logger
from polaris.network.traffic.intersec import Intersection


def fix_connections_table(
    conn_tbl: pd.DataFrame, map_matching: pd.DataFrame, conn: sqlite3.Connection, path_to_file: PathLike
):
    data_tables = DataTableAccess(path_to_file)
    max_link = conn.execute("select max(link) from link").fetchone()[0]
    links = data_tables.get("Link", conn)[["link", "node_a", "node_b"]]

    def build_key(df, max_link):
        multiplier = floor(log10(max_link)) + 3
        multiplier = pow(10, multiplier)
        key = df.link * multiplier + df.dir * (multiplier / 10) + df.to_link * 10 + df.to_dir
        return key

    conn_tbl = conn_tbl.assign(datakey=build_key(conn_tbl, max_link))

    map_matching.sort_values(by=["pattern_id", "index"], inplace=True)
    map_matching = map_matching.assign(
        to_link=map_matching.link.shift(-1),
        to_dir=map_matching.dir.shift(-1),
        to_pattern_id=map_matching.pattern_id.shift(-1),
    )
    map_matching = map_matching[map_matching.pattern_id == map_matching.to_pattern_id]
    map_matching.to_link = map_matching.to_link.astype(int)
    map_matching.to_dir = map_matching.to_dir.astype(int)
    map_matching = map_matching[(map_matching.link != map_matching.to_link) | (map_matching.dir != map_matching.to_dir)]
    map_matching = map_matching.assign(datakey=build_key(map_matching, max_link))

    missing_db = map_matching.loc[~map_matching.datakey.isin(conn_tbl.datakey)]
    if missing_db.empty:
        return
    logger.info(f"Adding {missing_db.shape[0]:,} new connections")

    # Let's add the node where the connection should be connected to
    miss_ab = missing_db.query("dir==0").merge(links[["link", "node_b"]].rename(columns={"node_b": "node"}), on="link")
    miss_ba = missing_db.query("dir==1").merge(links[["link", "node_a"]].rename(columns={"node_a": "node"}), on="link")
    missing_db = pd.concat([miss_ab, miss_ba], ignore_index=True)

    for node in missing_db.node.unique():  # type: int
        df = missing_db[missing_db.node == node]
        intersec = Intersection(data_tables, path_to_file)
        intersec.load(int(node), conn)
        for _, rec in df.iterrows():
            intersec.add_movement(rec.link, rec.to_link, note="required_by_pt_map_matching", conn=conn)
