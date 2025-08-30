# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import random
import urllib.request
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pygris

from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import commit_and_close


def ev_chargers(
    model_area: gpd.GeoDataFrame, supply_path: Path, api_key: str, max_dist: float, clustering_attempts: int
):
    """Add EV Chargers to the model with up-to-date data from  https://afdc.energy.gov/fuels/electricity_locations.html
    through the NREL API https://developer.nrel.gov/docs/transportation/alt-fuel-stations-v1/

    Args:
        model_area (GeoDataFrame): GeoDataFrame containing polygons with the model area
        supply_path (Path): Path to the supply file
        api_key (str): API key for the NREL API. If not provided it will be read from the environment variable
                       EV_API_KEY (if available)
    """

    states_gdf = pygris.states(cb=True, resolution="20m", cache=True)
    model_area = model_area.to_crs(states_gdf.crs)
    union = model_area.union_all()
    states = ",".join(states_gdf[states_gdf.geometry.intersects(union)].STUSPS.tolist())

    url = f"https://developer.nrel.gov/api/alt-fuel-stations/v1.json?state={states}&fuel_type=ELEC&api_key={api_key}"

    answer = urllib.request.urlopen(url).read()

    columns = [
        "latitude",
        "longitude",
        "access_code",
        "station_name",
        "ev_dc_fast_num",
        "ev_level1_evse_num",
        "ev_level2_evse_num",
        "ev_pricing",
    ]

    df = pd.DataFrame(json.loads(answer.decode("utf8"))["fuel_stations"])[columns]
    df = (
        df.dropna(subset=["latitude", "longitude"])
        .assign(loc_id=np.arange(df.shape[0]), cluster=np.arange(df.shape[0]))
        .set_index("loc_id")
    )
    geos = gpd.points_from_xy(df.longitude, df.latitude, crs="EPSG:4326")
    df.drop(columns=["latitude", "longitude"], inplace=True)
    srid = get_srid(database_path=supply_path)
    complete_gdf = gpd.GeoDataFrame(df, geometry=geos).to_crs(srid).sjoin(model_area.to_crs(srid), how="left")
    complete_gdf = complete_gdf[~complete_gdf.zone.isna()]
    results = {}
    mode_cluster = 0
    random.seed(42)
    for val, mode_gdf in complete_gdf.groupby("access_code"):
        if clustering_attempts >= 1:
            buffers = mode_gdf.buffer(max_dist)

            clusters = {}
            for _ in range(clustering_attempts):
                mode_gdf.loc[:, "cluster"] = 0
                cluster_count = 1
                indices = np.array(mode_gdf.index.to_numpy(), copy=True)
                random.shuffle(list(indices))
                for idx in indices:
                    if mode_gdf.loc[idx, "cluster"] == 0:
                        geo = mode_gdf.loc[idx, "geometry"]
                        mask = buffers.geometry.intersects(geo)
                        mode_gdf.loc[mask, "cluster"] = cluster_count
                        cluster_count += 1
                clusters[cluster_count] = np.array(mode_gdf.cluster.to_numpy(), copy=True)
            mode_gdf.loc[:, "cluster"] = clusters[min(clusters.keys())] + mode_cluster
            mode_cluster = mode_gdf.cluster.max()
        results[val] = mode_gdf
    final_gdf = gpd.GeoDataFrame(pd.concat(results.values(), ignore_index=True), crs=complete_gdf.crs)

    # We start creating the outputs
    # The actual stations. We get the first record for each cluster of plugs
    ev_charging_stations = final_gdf.drop_duplicates(subset=["cluster"]).assign(station_type=1)
    ev_charging_stations = ev_charging_stations.assign(geo=ev_charging_stations.geometry.apply(lambda x: x.wkb))
    ev_charging_stations.loc[ev_charging_stations.access_code.str.lower() == "public", "station_type"] = 0
    evcs = ev_charging_stations[["cluster", "station_type", "geo"]].to_records(index=False)

    # number of charging bays of each type per cluster
    value_vars = ["ev_dc_fast_num", "ev_level1_evse_num", "ev_level2_evse_num"]
    ev_charging_station_plugs = (
        final_gdf.groupby(["cluster"])
        .sum(numeric_only=True)
        .reset_index()
        .melt(id_vars=["cluster"], value_vars=value_vars)
    )
    ev_charging_station_plugs = ev_charging_station_plugs[ev_charging_station_plugs.value > 0]
    ev_charging_station_plugs = ev_charging_station_plugs.merge(
        pd.DataFrame({"plug_type": [2, 3, 1], "variable": value_vars}), on="variable"
    ).drop(columns=["variable"])
    ev_charging_station_plugs = ev_charging_station_plugs.assign(
        plug_count=ev_charging_station_plugs["value"].astype(int)
    )
    cvcsp = ev_charging_station_plugs[["cluster", "plug_type", "plug_count"]].to_records(index=False)

    with commit_and_close(supply_path, spatial=True) as conn:
        srid = get_srid(conn=conn)
        # Before updating the database, we make sure that this database was created with the same plug times we were considering when writing this code
        types_on_db = pd.read_sql("SELECT * from EV_Charging_Station_Plug_Types", conn)
        assert int(types_on_db.loc[types_on_db["plug_type_id"] == 1].power_level.iloc[0]) == 1000
        assert int(types_on_db.loc[types_on_db["plug_type_id"] == 2].power_level.iloc[0]) == 7000
        assert int(types_on_db.loc[types_on_db["plug_type_id"] == 3].power_level.iloc[0]) == 50000

        conn.executemany(
            f"Insert into EV_Charging_Stations (ID, station_type, geo) values (?, ?, GeomFromWKB(?, {srid}))", evcs
        )

        conn.executemany(
            "Insert into EV_Charging_Station_Plugs (station_id, plug_type, plug_count) values (?, ?,?)", cvcsp
        )

        conn.execute("INSERT INTO EV_Charging_Station_Service_Bays SELECT ID, 1 FROM EV_Charging_Stations")
