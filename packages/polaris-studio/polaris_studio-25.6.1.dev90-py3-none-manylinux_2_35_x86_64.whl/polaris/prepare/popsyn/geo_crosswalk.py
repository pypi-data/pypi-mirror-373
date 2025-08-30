# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from typing import Optional, Union

import geopandas as gpd  # type: ignore
import numpy as np
import pandas as pd
import pygris
import us


def get_tract_to_puma_crosswalk(
    state: us.states.State,
    county_fips: Optional[Union[str, list, np.ndarray]],
    url: str = "https://www2.census.gov/geo/docs/maps-data/data/rel/2010_Census_Tract_to_2010_PUMA.txt",
    include_stateid_in_pumaid: bool = True,
):
    """ " Read puma to tract from census website"""
    # Now attach pumas based on tract ids. Important to specify dtype as string, they are zero-padded
    puma_to_tract = pd.read_csv(url, dtype=str)

    if county_fips is not None:
        if isinstance(county_fips, str):
            county_fips = county_fips.split(",")
        puma_to_tract = puma_to_tract.loc[puma_to_tract["COUNTYFP"].isin(county_fips)]

    puma_to_tract = puma_to_tract.loc[puma_to_tract["STATEFP"] == state.fips]

    # for crossborder models, we need to prepend stateid to pumaid
    if include_stateid_in_pumaid:
        puma_to_tract["STPUMA"] = puma_to_tract["STATEFP"] + puma_to_tract["PUMA5CE"]
    else:
        puma_to_tract["STPUMA"] = puma_to_tract["PUMA5CE"]

    puma_to_tract["STPUMA"] = puma_to_tract["STPUMA"].astype(int)

    puma_to_tract["GEOID"] = puma_to_tract["STATEFP"] + puma_to_tract["COUNTYFP"] + puma_to_tract["TRACTCE"]

    # some data checks - PUMA ids should be 5 digits, GEOIDs 11 digits
    if not (puma_to_tract["GEOID"].apply(lambda x: len(x)) == 11).all():
        raise ValueError("Tract ids are not 11 digits long - please double-check.")
    if not (puma_to_tract["PUMA5CE"].apply(lambda x: len(x)) == 5).all():
        raise ValueError("PUMA ids are not 5 digits long - please double-check.")

    return puma_to_tract


def find_counties_with_model_area_overlap(
    zones: gpd.GeoDataFrame,
    state: us.states,
    year: int,
    area_removal_threshold: float = 0.01,
    area_preserving_crs: str = "EPSG:5070",
):
    """Note: remove externals from zones"""
    tracts = pygris.tracts(state=state.fips, year=year, cache=True)
    zones["zone_area"] = zones.to_crs(area_preserving_crs).area

    tract_zones_overlay = gpd.overlay(tracts.to_crs(zones.crs), zones, how="intersection", keep_geom_type=False).to_crs(
        area_preserving_crs
    )  # to equal area crs for area calculations

    tract_zones_overlay["area"] = tract_zones_overlay.area
    tract_zones_overlay = tract_zones_overlay.loc[tract_zones_overlay["area"] > 0]
    tract_zones_overlay["zone_overlap"] = tract_zones_overlay["area"] / tract_zones_overlay["zone_area"]

    logging.debug(f"counties before removing small zone slivers: {tract_zones_overlay.COUNTYFP.unique()}")
    zone_filter = tract_zones_overlay.zone_overlap < area_removal_threshold
    if zone_filter.sum() > 0:
        logging.info(f"Removing small fragments that represent less than {area_removal_threshold:.0%} of each zone.")
        tract_zones_overlay = tract_zones_overlay.loc[~zone_filter]
    logging.debug(f"counties after removing small zone slivers: {tract_zones_overlay.COUNTYFP.unique()}")

    return tract_zones_overlay[["GEOID", "COUNTYFP"]]
