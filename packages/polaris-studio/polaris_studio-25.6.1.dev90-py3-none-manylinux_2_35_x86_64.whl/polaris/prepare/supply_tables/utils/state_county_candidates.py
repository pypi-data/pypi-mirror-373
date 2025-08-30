# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import geopandas as gpd
import pandas as pd
import pygris
import us


def get_state_counties(model_area: gpd.GeoDataFrame, year: int) -> gpd.GeoDataFrame:
    pol = model_area.union_all()
    area = gpd.GeoSeries([pol], crs=model_area.crs)

    return counties_for_area(area, year=year)


def counties_for_model(zones: gpd.GeoDataFrame, year) -> gpd.GeoDataFrame:
    tol = 1e-3
    model_area = zones.to_crs(4326).union_all().buffer(tol).buffer(-tol)
    area = gpd.GeoSeries([model_area], crs=4326)

    counties = counties_for_area(area, year=year)
    if counties is None:
        return None

    # Get only the counties for which each zone is primarily in
    # This avoids getting bordering counties that have just touch the modelling area
    counties.to_crs(zones.crs, inplace=True)
    ovrly = zones[["zone", "geo"]].overlay(counties)
    ovrly = ovrly.assign(overlap_area=ovrly.geometry.area)

    gdf_sorted = ovrly.sort_values(by="overlap_area", ascending=False)
    unique = gdf_sorted.drop_duplicates(subset="zone", keep="first")
    return counties[counties.GEOID.isin(unique.GEOID)]


def counties_for_area(area: gpd.GeoSeries, year) -> gpd.GeoDataFrame:
    """Get counties for the model area

    Args:
        area (gpd.GeoDataFrame): Model area

    Returns:
        gpd.GeoDataFrame: Counties for the model area
    """
    states = pygris.states(cache=True, year=year, cb=True)
    union = area.to_crs(states.crs).union_all()
    states_in_model_area = states[states.geometry.intersects(union)]

    data = []
    for _, rec in states_in_model_area.iterrows():
        state = rec.NAME
        counties = pygris.counties(state, cache=True, year=year)
        if "STATE" in rec:
            rec["STATEFP"] = rec["STATE"]
        if "STUSPS" not in rec:
            rec["STUSPS"] = us.states.lookup(rec["NAME"]).abbr
        counties = counties.assign(state_name=state, statefp=rec.STATEFP, state=rec.STUSPS)
        counties.rename(columns={"NAME": "name"}, inplace=True)
        data.append(counties[counties.intersects(union)])
    return pd.concat(data) if data else None
