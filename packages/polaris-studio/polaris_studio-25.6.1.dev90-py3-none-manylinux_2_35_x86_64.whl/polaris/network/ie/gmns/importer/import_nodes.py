# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os.path import join

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from polaris.network.ie.gmns.importer.gmns_field_compatibility import node_field_translation
from polaris.network.ie.gmns.importer.util_functions import add_required_fields


def import_gmns_nodes(gmns_folder: str, source_crs, proj_crs, conn):
    logging.info("Importing Nodes")
    node_file = join(gmns_folder, "node.csv")

    # We import nodes
    nodes = pd.read_csv(node_file)

    # Fields that are completely empty don't need to be imported
    nodes.dropna(how="all", axis=1, inplace=True)

    # We rename the fields to be compatible with Polaris
    nodes.rename(columns=node_field_translation, inplace=True, errors="ignore")

    geos = gpd.points_from_xy(nodes.x, nodes.y, crs=source_crs).to_crs(proj_crs)
    nodes = nodes.assign(geo=np.array([shapely.to_wkt(geo, rounding_precision=6) for geo in geos]))
    add_required_fields(nodes, "node", conn)

    data_cols = [str(x) for x in list(nodes.columns)]
    data_cols.remove("geo")
    param_bindings = ",".join(["?"] * len(data_cols)) + f",GeomFromText(?, {proj_crs})"
    data_cols.append("geo")
    sql = f"INSERT INTO node({','.join(data_cols)}) VALUES({param_bindings})"

    conn.executemany(sql, nodes[data_cols].to_records(index=False))
    conn.commit()
