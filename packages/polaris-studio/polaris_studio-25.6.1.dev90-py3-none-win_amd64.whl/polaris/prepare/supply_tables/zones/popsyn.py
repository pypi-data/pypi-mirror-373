# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

import geopandas as gpd

from polaris.network.utils.srid import get_srid
from polaris.prepare.supply_tables.utils.census_geographies import constrain_to_model_area, get_census_geography
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.pandas_utils import fuzzy_rename


def add_popsyn_regions(
    model_area: gpd.GeoDataFrame,
    counties: gpd.GeoDataFrame,
    census_geo: str,
    supply_path: Path,
    year: int,
    replace: bool,
):
    """Add population synthesis regions based on the requested census zoning system.

    Args:
        model_area (GeoDataFrame): GeoDataFrame containing polygons covering the model area
        census_geo (str): Census subdivision level to use -> Census tracts or block groups
        supply_path (Path): Path to the supply database we are building
        year (int): Release year for the geometries to be retrieved
    """

    zone_candidates = get_census_geography(counties, census_geo, year)
    zone_candidates = constrain_to_model_area(zone_candidates, model_area)
    fuzzy_rename(zone_candidates, "GEOID", "GEOID", inplace=True)
    zone_candidates = zone_candidates.assign(popsyn_region=zone_candidates.GEOID).drop_duplicates("popsyn_region")

    with commit_and_close(supply_path, spatial=True) as conn:
        srid = get_srid(conn=conn)
        zone_candidates = zone_candidates.to_crs(srid)
        zone_candidates = zone_candidates.assign(wkb_=zone_candidates.geometry.to_wkb())
        records = zone_candidates[["popsyn_region", "wkb_"]].to_records(index=False)
        if replace:
            conn.execute("DELETE from PopSyn_Region;")
        conn.executemany(
            f"INSERT INTO Popsyn_Region (popsyn_region, geo) VALUES (?, CastToMulti(GeomFromWKB(?, {srid})))", records
        )
