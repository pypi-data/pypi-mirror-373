# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from math import log10, ceil
from os.path import join

import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def export_links_to_gmns(gmns_folder: str, target_crs, conn, path_to_file):
    links = DataTableAccess(path_to_file).get("Link", conn=conn).to_crs(target_crs)
    links.drop(columns=["setback_a", "setback_b"], inplace=True)
    links.drop(columns=["cap_ba", "cap_ab", "bearing_a", "bearing_b"], inplace=True)
    tolls = DataTableAccess(path_to_file).get("Toll_Pricing", conn=conn)
    tolls.drop(columns=["start_time", "end_time"], inplace=True)
    tolls.rename(columns={"link": "link_id", "price": "toll"}, inplace=True)

    # Treats geometries
    base_id = 10 ** ceil(log10(links.link.max()))
    links = links.assign(geometry_id=links.link + base_id)
    geo_array = links.geometry.to_wkt(rounding_precision=6)
    geo_df = pd.DataFrame({"geometry_id": links.geometry_id, "geometry": geo_array})
    geo_df.to_csv(join(gmns_folder, "geometry.csv"), index=False)
    links.drop(columns=["geo"], inplace=True)

    # Converts units to the GMNS standard
    links.loc[:, "length"] /= 1000
    links.loc[:, "fspd_ab"] *= 3.6
    links.loc[:, "fspd_ba"] *= 3.6

    links.rename(columns={"link": "link_id", "control_type": "ctrl_type", "type": "facility_type"}, inplace=True)
    links.rename(columns={"use": "allowed_uses"}, inplace=True)
    links = links.assign(dir_flag=1, directed=1)

    links.loc[:, "allowed_uses"] = links.allowed_uses.str.replace("|", ", ", regex=False)

    # Separate into AB and BA directions and treat them in separate
    ab_links = pd.DataFrame(links[links.lanes_ab > 0])
    ab_links.drop(columns=[x for x in ab_links.columns if "_ba" in str(x)], inplace=True)
    ab_links.rename(columns={"node_a": "from_node_id", "node_b": "to_node_id", "fspd_ab": "free_speed"}, inplace=True)
    ab_links.rename(columns={"lanes_ab": "lanes"}, inplace=True)
    ab_links = ab_links.merge(tolls[tolls.dir == 0], on="link_id", how="left")
    ab_links.loc[:, "link_id"] *= 2

    ba_links = pd.DataFrame(links[links.lanes_ba > 0])
    ba_links.drop(columns=[x for x in ba_links.columns if "_ab" in str(x)], inplace=True)
    ba_links.rename(columns={"node_b": "from_node_id", "node_a": "to_node_id", "fspd_ba": "free_speed"}, inplace=True)
    ba_links.rename(columns={"lanes_ba": "lanes"}, inplace=True)
    ba_links.loc[:, "dir_flag"] = -1
    ba_links = ba_links.merge(tolls[tolls.dir == 1], on="link_id", how="left")
    ba_links.loc[:, "link_id"] = 2 * ba_links.link_id + 1

    links = pd.concat([ab_links, ba_links])
    links.to_csv(join(gmns_folder, "link.csv"), index=False)
