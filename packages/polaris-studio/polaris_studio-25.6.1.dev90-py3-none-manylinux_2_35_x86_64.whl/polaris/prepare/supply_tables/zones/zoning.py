# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

import geopandas as gpd
import numpy as np

from polaris.network.utils.srid import get_srid
from polaris.prepare.supply_tables.utils.census_geographies import constrain_to_model_area, get_census_geography
from polaris.utils.database.db_utils import commit_and_close
from .population import get_pop


def add_zoning(
    model_area: gpd.GeoDataFrame, state_counties: gpd.GeoDataFrame, census_geo: str, supply_path: Path, year, api_key
):
    """Create zoning system based on census subdivisions

    Args:
        model_area (GeoDataFrame): GeoDataFrame containing polygons with the model area
        census_geo (str): Census subdivision level to use for zoning -> Census tracts or block groups
        supply_path (Path): Path to the supply database we are building
        year (int): Year for which the population should be retrieved for
        api_key (str): Census API key
    """

    zone_candidates = get_census_geography(state_counties, census_geo, year)

    cols = ["zone", "pop_households", "pop_persons", "pop_group_quarters", "percent_white", "percent_black", "wkb_"]
    pop_data = get_pop(census_geo, zone_candidates, year, api_key)

    crs = zone_candidates.crs.to_epsg()
    zone_candidates.GEOID = zone_candidates.GEOID.astype(str)
    zone_candidates = zone_candidates.merge(pop_data, on="GEOID")
    zone_candidates = gpd.GeoDataFrame(zone_candidates, crs=crs, geometry=zone_candidates.geometry)

    zone_candidates = constrain_to_model_area(zone_candidates, model_area)

    zone_candidates = zone_candidates.assign(zone=np.arange(zone_candidates.shape[0]) + 1)
    with commit_and_close(supply_path, spatial=True) as conn:
        srid = get_srid(conn=conn)
        zone_candidates = zone_candidates.to_crs(srid)

        zone_candidates = zone_candidates.assign(wkb_=zone_candidates.geometry.to_wkb())
        records = zone_candidates[cols].to_records(index=False)
        c = ",".join(cols[:-1])
        w = ",".join(["?"] * (len(cols) - 1))
        conn.executemany(f"INSERT INTO Zone ({c}, geo) VALUES ({w}, CastToMulti(GeomFromWKB(?, {srid})))", records)
