# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np
import geopandas as gpd
import pandas as pd
import warnings
import pygris
from polaris.utils.pandas_utils import fuzzy_rename

warnings.filterwarnings("ignore", category=DeprecationWarning, module="pygris.internal_data")


def get_census_geography(counties, census_geo, year):
    kwargs = {"year": year, "cache": True}
    fn = pygris.tracts if census_geo == "tracts" else pygris.block_groups
    fuzzy_rename(counties, "COUNTYFP", "COUNTYFP", inplace=True)
    data = [fn(state=rec["state_name"], county=rec["COUNTYFP"], **kwargs) for _, rec in counties.iterrows()]

    if len(data) == 0:
        raise ValueError("Could not find any US State/county that overlaps the desired modeling area")

    # this is returning None in some case.
    # See: https://pyproj4.github.io/pyproj/stable/gotchas.html#why-does-the-epsg-code-return-when-using-epsg-xxxx-and-not-with-init-epsg-xxxx
    return gpd.GeoDataFrame(pd.concat(data), geometry=data[0]._geometry_column_name, crs=data[0].crs.to_epsg())


def constrain_to_model_area(gdf, model_area):
    model_area = gpd.GeoDataFrame(
        {"__not_keeping_col": np.arange(model_area.shape[0])}, geometry=model_area.geometry.to_crs(gdf.crs)
    )
    gdf_cols = gdf.columns.tolist()
    a = gdf.sjoin(model_area, how="inner", predicate="intersects")

    return a.loc[a.index.drop_duplicates(keep="first"), :][gdf_cols]
