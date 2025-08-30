# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3
from pathlib import Path

import geopandas as gpd
from aequilibrae.project import Project
from aequilibrae.transit.functions.get_srid import get_srid as get_aeq_srid

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.ie.gmns.importer.util_functions import add_required_fields
from polaris.network.utils.srid import get_srid
from polaris.prepare.supply_tables.network.network_coding import mode_correspondence, link_type_correspondence
from polaris.utils.database.db_utils import commit_and_close


def import_nodes(project: Project, network):
    """Imports nodes from an existing AequilibraE Project into a Polaris database.

    Args:
        aeq_path (Project): AequilibraE project to import from.
        network (Network): a Polaris Network to import into
        transformer (pyproj.Transformer): a transformer to translate between coordinate systems. Defaults to None
    """
    nodes = project.network.nodes.data
    nodes = nodes[nodes.is_centroid == 0]
    aeq_crs = get_aeq_srid()
    proj_crs = get_srid(database_path=network.path_to_file)
    nodes = gpd.GeoDataFrame(nodes, geometry=nodes["geometry"], crs=aeq_crs).to_crs(proj_crs)
    nodes = nodes.assign(geo=nodes.geometry.to_wkb())

    drop_columns(nodes, ["ogc_fid", "is_centroid", "modes", "link_types", "geometry"])

    with commit_and_close(network.path_to_file, spatial=True) as conn:
        add_required_fields(nodes, "node", conn)
        data_cols = [str(x) for x in list(nodes.columns)]
        data_cols.remove("geo")  # make sure that the geo column is the last one
        data_cols.append("geo")
        param_bindings = ",".join(["?"] * (len(data_cols) - 1)) + f",GeomFromWKB(?, {proj_crs})"
        sql = f"INSERT INTO node({','.join(data_cols)}) VALUES({param_bindings})"

        conn.executemany(sql, nodes[data_cols].to_records(index=False))
        conn.commit()


def import_links(project: Project, network):
    """Imports links from an existing AequilibraE Project into a Polaris database.

    Args:
        aeq_path (Path): path to an AequilibraE project to import from.
        network (Network): a Polaris Network to import into
    """
    links = project.network.links.data

    # Basic data editing and consistency
    links = links[~(links.link_type == "centroid_connector")]
    for col in ["lanes_ab", "lanes_ba"]:
        links.loc[(links[col] > 0) & (links[col] < 1), col] = 1.0
        links[col] = links[col].round(0)

    drop_cols = ["distance", "direction", "travel_time_ab", "travel_time_ba", "free_flow_time", "is_link", "from_biway"]
    drop_columns(links, drop_cols)
    new_col_names = {
        "speed_ab": "fspd_ab",
        "speed_ba": "fspd_ba",
        "capacity_ab": "cap_ab",
        "capacity_ba": "cap_ba",
        "link_type": "type",
    }
    links = links.rename(columns=new_col_names)

    aeq_crs = get_aeq_srid()
    proj_crs = get_srid(database_path=network.path_to_file)
    links = gpd.GeoDataFrame(links, geometry=links["geometry"], crs=aeq_crs).to_crs(proj_crs)
    links = links.assign(geo=links.geometry.to_wkb())

    drop_columns(links, ["link_id", "geometry"])
    links.loc[:, "use"] = "ANY"
    links.loc[:, "type"] = links["type"].str.upper()
    for k, v in link_type_correspondence.items():
        links.loc[:, "type"] = links["type"].replace(k, v)

    with commit_and_close(network.path_to_file, spatial=True) as conn:
        link_types_from_aeq(links, conn, network.path_to_file)
        # Drop more non-needed columns
        drop_columns(links, ["a_node", "b_node", "modes", "ogc_fid"])

        add_required_fields(links, "link", conn)
        data_cols = [str(x) for x in list(links.columns)]
        data_cols.remove("geo")  # make sure that the geo column is the last one
        data_cols.append("geo")
        param_bindings = f'{",".join(["?"] * (len(data_cols) - 1))}, GeomFromWKB(?,{proj_crs})'
        sql = f'INSERT INTO Link ({",".join(data_cols)}) VALUES({param_bindings})'

        conn.executemany(sql, links[data_cols].to_records(index=False))


def import_network_from_aequilibrae(aeq_project: Project, network):
    """Imports nodes and links from an existing AequilibraE Project into a Polaris database.

    Args:
        aeq_path (Path): path to an AequilibraE project to import from.
        zones (Network): a Polaris Network.
    """
    import_nodes(aeq_project, network)
    import_links(aeq_project, network)

    with commit_and_close(network.path_to_file, spatial=True) as conn:
        conn.execute("UPDATE Link set fspd_ab=0 where lanes_ab=0;")
        conn.execute("UPDATE Link set fspd_ba=0 where lanes_ba=0;")


def link_types_from_aeq(links: gpd.GeoDataFrame, conn: sqlite3.Connection, path_to_file: Path):
    # Thorough documentation of the assumptions used in this code is provided
    # with the package documentation
    clt = DataTableAccess(path_to_file).get("link_type", conn=conn)

    link_types = links["type"].unique()
    adds = [ltype for ltype in link_types if ltype not in clt.link_type.values]
    if not adds:
        return

    data = []
    for ltype in adds:
        link_modes = "".join(list(links[links["type"] == ltype].modes.unique()))
        modes = ["ANY", "NONE"]
        for m, v in mode_correspondence.items():
            if m in link_modes:
                modes.extend(v)

        data.append([ltype, 10, "|".join(modes), 50, 1, "Automated network builder"])

    sql = """INSERT INTO Link_Type(link_type, "rank", use_codes, turn_pocket_length, turn_pockets, notes)
                             VALUES(?, ?, ?, ?, ?, ?)"""
    conn.executemany(sql, data)
    conn.commit()


def drop_columns(df, cols):
    for col in cols:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
