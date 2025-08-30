# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import geopandas as gpd
import pandas as pd
from census import Census


def get_pop(zone_level: str, zone_candidates: gpd.GeoDataFrame, year, census_key):
    c = Census(census_key)
    all_pop_data = []
    data_fields = {
        "pop_persons": "B01001_001E",
        "white": "DP05_0077E",
        "black": "DP05_0078E",
        "pop_households": "B25011_001E",
        "pop_group_quarters": "B26001_001E",
    }
    if year == 2016:
        data_fields["white"] = "DP05_0077E"
        data_fields["black"] = "DP05_0078E"

    for _, state_fips, county_fips in zone_candidates[["STATEFP", "COUNTYFP"]].drop_duplicates().to_records():
        fields_ = [x for x in data_fields.values() if "DP" not in x]

        if zone_level == "tracts":
            data1 = c.acs5.state_county_tract(
                fields=("GEO_ID", *fields_),
                state_fips=state_fips,
                county_fips=county_fips,
                tract="*",
                year=year,
            )
            df1 = (
                pd.DataFrame(data1)
                .rename(columns={data_fields[x]: x for x in data_fields if data_fields[x] in fields_})
                .drop(columns=["state", "county", "tract"])
            )

            dp_fields = [x for x in data_fields.values() if "DP" in x]
            data2 = c.acs5dp.state_county_tract(
                fields=("GEO_ID", *dp_fields),
                state_fips=state_fips,
                county_fips=county_fips,
                tract="*",
                year=year,
            )
            df2 = pd.DataFrame(data2).rename(
                columns={data_fields[x]: x for x in data_fields if data_fields[x] in dp_fields}
            )

            pop_data = df1.merge(df2, on="GEO_ID")
            pop_data = pop_data.assign(
                percent_white=pop_data.white / pop_data.pop_persons, percent_black=pop_data.black / pop_data.pop_persons
            )
        else:
            data1 = c.acs5.state_county_blockgroup(
                fields=("GEO_ID", *fields_),
                state_fips=state_fips,
                county_fips=county_fips,
                blockgroup="*",
                year=year,
            )
            pop_data = (
                pd.DataFrame(data1)
                .rename(columns={data_fields[x]: x for x in data_fields if data_fields[x] in fields_})
                .drop(columns=["state", "county", "tract"])
            )

            pop_data = pop_data.assign(percent_white=0, percent_black=0)

        all_pop_data.append(pop_data.fillna(value=0))

    pop_data = pd.concat(all_pop_data)

    # We remove a useless prefix from the data
    geo_ids = pop_data["GEO_ID"].str.split("US", expand=True, n=1)
    pop_data["GEOID"] = geo_ids[geo_ids.columns[-1]].astype(str)

    return pop_data
