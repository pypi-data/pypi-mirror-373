# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from os import PathLike
from os.path import join

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.ie.gmns.importer.add_link_types import add_link_types
from polaris.network.ie.gmns.importer.gmns_field_compatibility import link_field_translation
from polaris.network.ie.gmns.importer.util_functions import add_required_fields
from polaris.network.utils.srid import get_srid


def import_gmns_links(gmns_folder: str, source_crs, proj_crs, conn: sqlite3.Connection, path_to_file: PathLike):
    logging.info("Importing Links")
    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation
    links = pd.read_csv(join(gmns_folder, "link.csv"))

    # Drop unnecessary fields from OSM2GMNS
    if "osm_way_id" in links:
        links.drop(columns=["is_link", "from_biway", "link_type"], errors="ignore", inplace=True)

    # Replace geometries in case they have been provided in a different file (allowed by the standard)
    if "geometry_id" in links:
        if links.geometry_id.values[0] > 0:  # type: ignore
            links.drop(columns=["geometry"], errors="ignore")
            geo_file = join(gmns_folder, "geometry.csv")
            cols = list(links.columns) + ["geometry"]
            links = links.merge(pd.read_csv(geo_file), on="geometry_id")
            links = links[cols]
            links = links.drop(columns=["geometry_id"], errors="ignore")

    links.rename(columns=link_field_translation, inplace=True, errors="ignore")
    links.drop(columns=["link", "length"], inplace=True)

    # Direction in polaris is controlled by the existence of lanes in each direction, so we make sure that they exist
    if "lanes" not in links:
        links = links.assign(lanes=1)
    links.loc[links.lanes <= 0, "lanes"] = 1

    # We separate links in both directions
    ab_links = pd.DataFrame(links, copy=True)
    ba_links = pd.DataFrame(links, copy=True)
    ba_links.rename(columns={"node_a": "node_b", "node_b": "node_a"}, inplace=True)
    indices = ["node_a", "node_b", "osm_way_id"] if "osm_way_id" in links else ["node_a", "node_b"]
    ab_links.set_index(indices, inplace=True)
    ba_links.set_index(indices, inplace=True)
    ba_links = ba_links[ba_links.index.isin(ab_links.index)]

    # Now we remove from the AB links, those that are actually BA
    # To do that, we have two steps

    # 1st step is to separate records for links that only have one direction
    ba_links.reset_index(inplace=True)
    ba_links.rename(columns={"node_a": "node_b", "node_b": "node_a"}, inplace=True)
    ba_links.set_index(indices, inplace=True)
    ab_links_unique = ab_links[~ab_links.index.isin(ba_links.index)]

    # The 2nd step is to keep in the AB side, only one direction for the links, which we
    # assume is assume is the one where the a_node is smaller than the b_node
    # And we achieve that with some Pandas magic
    ba_links.reset_index(inplace=True)
    ba_links.rename(columns={"node_a": "node_b", "node_b": "node_a"}, inplace=True)
    ba_links.set_index(indices, inplace=True)
    ab_links_duplicate = ab_links[~ab_links.index.isin(ab_links_unique.index)]
    ab_links_duplicate.reset_index(inplace=True)
    ab_links_duplicate = ab_links_duplicate[ab_links_duplicate.node_a > ab_links_duplicate.node_b]
    ab_links_duplicate.set_index(indices, inplace=True)
    ab_links = pd.concat([ab_links_unique, ab_links_duplicate])

    # Now we can join and go forward with this
    links = ab_links.join(ba_links, how="left", lsuffix="_ab", rsuffix="_ba")
    links.drop(columns=["geo_ba"], inplace=True)
    links.rename(columns={"geo_ab": "geo"}, inplace=True)

    all_ab_cols = [x for x in links.columns if "_ab" in str(x)]

    # We check if any of the ab/ba is actually single-direction
    ideal_links_table = DataTableAccess(path_to_file).get("link", conn)
    for ab_col in [str(x) for x in all_ab_cols if x not in list(ideal_links_table.columns)]:
        if "_ab" not in ab_col:
            continue

        ba_col = ab_col.replace("_ab", "_ba")
        links.rename(columns={ab_col: ab_col.replace("_ab", "")}, inplace=True)
        links.drop(columns=[ba_col], inplace=True)
    # We add the link use codes
    links.loc[:, "use"] = links.use.str.upper()
    links.loc[:, "type"] = links["type"].str.upper()

    add_link_types(links, conn, path_to_file)

    geos = gpd.GeoSeries.from_wkt(links.geo).set_crs(source_crs).to_crs(proj_crs)
    links.geo = np.array([shapely.to_wkt(geo, rounding_precision=6) for geo in geos])

    add_required_fields(links, "link", conn)
    columns = [str(x) for x in list(links.columns)]

    columns.remove("geo")
    param_bindings = f'{",".join(["?"] * (len(columns)))}, GeomFromText(?,{get_srid(conn=conn)})'
    sql = f'INSERT INTO Link ({",".join(columns + ["geo"])}) VALUES({param_bindings})'

    conn.executemany(sql, links[columns + ["geo"]].to_records(index=False))
    conn.commit()
