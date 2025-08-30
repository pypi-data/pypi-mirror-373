# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from polaris.utils.database.db_utils import read_and_close


def connectivity_auto(supply_db):
    """Checks auto network connectivity

    It computes paths between nodes in the network or between every single link/direction combination
    in the network
    """

    get_qry = "SELECT link flink, dir fdir, to_link tlink, to_dir tdir, 1.0 distance from Connection"

    with read_and_close(supply_db) as conn:
        records = pd.read_sql(get_qry, conn)
        loc_links = pd.read_sql("Select location, link from Location_Links", conn)
        locations = pd.read_sql("Select location from Location", conn)
        links = pd.read_sql("Select link, lanes_ab, lanes_ba from Link", conn)

    auto_net = records.assign(fnode=records.flink * 2 + records.fdir, tnode=records.tlink * 2 + records.tdir)
    if auto_net.empty:
        if not locations.empty:
            return {"connectivity auto": {"locations not connected": locations.location.to_list()}}

    # The graph is composed by connections, which behave as the edges, and link/directions, which represent
    # the vertices in the connected component analysis
    fnodes = auto_net.fnode.astype(np.int64).to_numpy()
    tnodes = auto_net.tnode.astype(np.int64).to_numpy()
    n = max(fnodes.max() + 1, tnodes.max() + 1)
    csr = coo_matrix((auto_net.distance.to_numpy(), (fnodes, tnodes)), shape=(n, n)).tocsr()

    n_components, labels = connected_components(csgraph=csr, directed=True, return_labels=True, connection="strong")

    # We then identify all the link/directions that have the highest connectivity degree (i.e. the biggest island)
    bc = np.bincount(labels)
    max_label = np.where(bc == bc.max())[0][0]
    isconn = np.where(labels == max_label)[0]

    # And compare them to the contents of the location_links table
    # Locations that don't have at least one associated link in the biggest island
    # are considered disconnected
    start_point = np.floor(isconn / 2).astype(np.int64)
    end_point = np.ceil(isconn / 2).astype(np.int64)

    start_point = np.unique(np.hstack((start_point, links.query("lanes_ba == 0").link.to_numpy())))
    end_point = np.unique(np.hstack((end_point, links.query("lanes_ab == 0").link.to_numpy())))

    connected = np.intersect1d(start_point, end_point)
    loc_links = loc_links[loc_links.link.isin(connected)]
    connected_locations = loc_links.location.unique()
    disconnected_locations = locations[~locations.location.isin(connected_locations)].location.to_list()

    return {"locations not connected": disconnected_locations} if disconnected_locations else []
