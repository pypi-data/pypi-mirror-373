# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from aequilibrae.project.project import Project

from polaris.utils.database.db_utils import add_column_unless_exists


def impute_missing_attributes(aeq_project: Project, imputation_parameters: dict, path_to_file: Path) -> None:
    """Imputes missing attributes on a network based on attributes similarity and distance"""

    algo = imputation_parameters["algorithm"]
    vars_to_impute = list(imputation_parameters["fields_to_impute"])

    if algo not in ["knn", "iterative"]:
        raise ValueError('Invalid imputation algorithm. Algorithms available: "knn" and "iterative".')

    logging.info(f"Running data imputation using {algo} algorithm")

    dflnk = aeq_project.network.links.data
    list_fixed_speeds = dflnk[(~dflnk.speed_ab.apply(np.isreal)) | ~dflnk.speed_ba.apply(np.isreal)].link_id.values

    if len(list_fixed_speeds) > 0:
        make_speeds_numeric(aeq_project, list_fixed_speeds)
        dflnk = aeq_project.network.links.data

    gdf_links = gpd.GeoDataFrame(dflnk, geometry=dflnk.geometry)
    gdf_links["centroid"] = gdf_links.geometry.centroid
    gdf_links["centroid_x"] = gdf_links.centroid.x
    gdf_links["centroid_y"] = gdf_links.centroid.y

    modes_dummies = pd.get_dummies(gdf_links["modes"])
    df_to_impute = pd.concat([modes_dummies, gdf_links[["centroid_x", "centroid_y"] + vars_to_impute]], axis=1)
    df_to_impute = pd.concat([pd.get_dummies(gdf_links["link_type"]), df_to_impute], axis=1)

    list_imputed_cols = []
    for col in vars_to_impute:
        if df_to_impute[col].isnull().sum() > 0:
            list_imputed_cols.append(f"imp_{col}")

    if list_imputed_cols:
        imputed_df_cols = list(df_to_impute.columns) + list_imputed_cols

        if algo == "knn":
            from sklearn.impute import KNNImputer

            imputer = KNNImputer(n_neighbors=5, add_indicator=True)
        elif algo == "iterative":
            from sklearn.experimental import enable_iterative_imputer  # noqa: F401
            from sklearn.impute import IterativeImputer

            max_iter = imputation_parameters["max_iter"]
            imputer = IterativeImputer(random_state=1234, add_indicator=True, max_iter=max_iter)

        df_imputed = imputer.fit_transform(df_to_impute)
        df_imputed = pd.DataFrame(df_imputed, columns=imputed_df_cols)

        fldr = path_to_file / "supply" / "imputation"
        fldr.mkdir(exist_ok=True, parents=True)
        df_imputed.to_csv(fldr / "osm_data_imputation_results.csv")

        for var in vars_to_impute:
            dflnk[var] = df_imputed[var]

        for col in list_imputed_cols:
            dflnk[col] = df_imputed[col]

        dflnk["imputations"] = dflnk[list_imputed_cols].sum(axis=1)
        df_imputations = dflnk.query("imputations>0").copy()

        list_zip_arr = [df_imputations[var] for var in vars_to_impute]
        list_zip_arr.append(df_imputations["link_id"])
        attr_zip = list(zip(*list_zip_arr))

        qry = ", ".join([f"{var}=?" for var in vars_to_impute])
        with aeq_project.db_connection as conn:
            conn.executemany(f"UPDATE links SET {qry} WHERE link_id=?;", attr_zip)

    with aeq_project.db_connection as conn:
        add_column_unless_exists(conn, "links", "free_flow_time", "REAL")
        add_column_unless_exists(conn, "links", "capacity_ab", "REAL")
        add_column_unless_exists(conn, "links", "capacity_ba", "REAL")
        conn.commit()

        # Makes sure we have enough lanes in each valid direction
        conn.execute("UPDATE links SET lanes_ab = 1 WHERE lanes_ab < 1 and direction>=0")
        conn.execute("UPDATE links SET lanes_ba = 1 WHERE lanes_ba < 1 and direction<=0")
        conn.execute("UPDATE links SET lanes_ab = 0 WHERE direction<0")
        conn.execute("UPDATE links SET lanes_ba = 0 WHERE direction>0")

        # Makes speeds 5km/h minimum
        conn.execute("UPDATE links SET speed_ab = 5 WHERE speed_ab < 5")
        conn.execute("UPDATE links SET speed_ba = 5 WHERE speed_ba < 5")

        # Sets free-flow travel times
        conn.execute("UPDATE links SET free_flow_time = 60 * (distance/1000) / speed_ab;")
        conn.execute("UPDATE links SET free_flow_time = coalesce(free_flow_time, 60 * (distance/1000) / speed_ba);")
        # Computes capacities
        conn.execute("UPDATE links SET capacity_ab = lanes_ab * (1800+10*(speed_ab-50)) where lanes_ab>0;")
        conn.execute("UPDATE links SET capacity_ba = lanes_ba * (1800+10*(speed_ba-50)) where lanes_ba>0;")


def make_speeds_numeric(aeq_project, list_fixed_speeds):
    """Enforces numerical values on speed attributes.
    Args:
        aeq_project (Project): AequilibraE project
        list_fixed_speeds (list:`int`): a list of link ids with speeds to fix
    """
    columns_fixed = ["speed_ab", "speed_ba", "link_id"]
    df_links = aeq_project.network.links.data
    for var in ["speed_ab", "speed_ba"]:
        clean_field = df_links[var].astype(str).str.extract(r"([-+]?\d*\.?\d+)")  # noqa: W605
        df_links[var] = clean_field.astype(float, errors="ignore")
    df_fixed = df_links[df_links.link_id.isin(list_fixed_speeds)][columns_fixed]

    list_zip_arr = []
    for col in df_fixed.columns:
        list_zip_arr.append(df_fixed[col])

    attr_zip = list(zip(*list_zip_arr))
    with aeq_project.db_connection as conn:
        conn.executemany("UPDATE links SET speed_ab=?, speed_ba=? WHERE link_id=?;", attr_zip)
