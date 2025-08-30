# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import itertools
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import us
from census import Census

from polaris.prepare.popsyn.geo_crosswalk import get_tract_to_puma_crosswalk
from polaris.utils.list_utils import first_and_only
from polaris.utils.user_configs import UserConfig


def get_default_group_spec(year: int) -> List:
    """
    Default control total mapping. Links column names to a collection of contributing census data columns.
    Classification is tied to c++ definitions (see Activity_Simulator_Types.h for enums) and needs to
    be consistent with seed data.
    """
    base = {
        "name": "hh",
        "columns": [
            ("HOUSEHOLDS", ["B25011_001E", "B26001_001E"]),
        ],
        "check": ["B25011_001E", "B26001_001E"],
    }

    group_0 = {
        "name": "tenure-quarters",
        "columns": [
            ("HHT_OWN_MARRIED", ["B25011_004E"]),
            ("HHT_OWN_FAMILY_MALE", ["B25011_009E"]),
            ("HHT_OWN_FAMILY_FEMALE", ["B25011_013E"]),
            ("HHT_OWN_NONFAMILY_SINGLE", ["B25011_018E"]),
            ("HHT_OWN_NONFAMILY_NOTALONE", ["B25011_022E"]),
            ("HHT_RENT_MARRIED", ["B25011_028E"]),
            ("HHT_RENT_FAMILY_MALE", ["B25011_033E"]),
            ("HHT_RENT_FAMILY_FEMALE", ["B25011_037E"]),
            ("HHT_RENT_NONFAMILY_SINGLE", ["B25011_042E"]),
            ("HHT_RENT_NONFAMILY_NOTALONE", ["B25011_046E"]),
            ("HHT_GQ", ["B26001_001E"]),
        ],
        "check": ["B25011_001E", "B26001_001E"],
    }

    group_1 = {
        "name": "Income",
        "columns": [
            ("HHINC_LESS20K", ["B19001_002E", "B19001_003E", "B19001_004E", "B26001_001E"]),
            ("HHINC_20TO35K", ["B19001_005E", "B19001_006E", "B19001_007E"]),
            ("HHINC_35TO50K", ["B19001_008E", "B19001_009E", "B19001_010E"]),
            ("HHINC_50TO75k", ["B19001_011E", "B19001_012E"]),
            ("HHINC_75TO100K", ["B19001_013E"]),
            ("HHINC_100TO150K", ["B19001_014E", "B19001_015E"]),
            ("HHINC_OVER150K", ["B19001_016E", "B19001_017E"]),
        ],
        "check": ["B19001_001E", "B26001_001E"],
    }

    group_2 = {
        "name": "HU_Type",
        "columns": [
            ("HUTYPE_SF", ["B25032_003E", "B25032_004E", "B25032_014E", "B25032_015E"]),
            (
                "HUTYPE_2TO9UNITS",
                ["B25032_005E", "B25032_006E", "B25032_007E", "B25032_016E", "B25032_017E", "B25032_018E"],
            ),
            (
                "HUTYPE_10+UNITS",
                ["B25032_008E", "B25032_009E", "B25032_010E", "B25032_019E", "B25032_020E", "B25032_021E"],
            ),
            ("HUTYPE_OTHER", ["B25032_011E", "B25032_012E", "B25032_022E", "B25032_023E"]),
            ("HU_GROUP_QUARTERS", ["B26001_001E"]),
        ],
        "check": ["B25032_001E", "B26001_001E"],
    }

    group_3 = {
        "name": "vehicles",
        "columns": [
            ("NVEH_0", ["B08201_002E", "B26001_001E"]),
            ("NVEH_1", ["B08201_003E"]),
            ("NVEH_2", ["B08201_004E"]),
            ("NVEH_3+", ["B08201_005E", "B08201_006E"]),
        ],
        "check": ["B08201_001E", "B26001_001E"],
    }

    group_4 = {
        "name": "hhsize",
        "columns": [
            ("HHSIZE_1", ["B25009_003E", "B25009_011E", "B26001_001E"]),
            ("HHSIZE_2", ["B25009_004E", "B25009_012E"]),
            ("HHSIZE_3", ["B25009_005E", "B25009_013E"]),
            ("HHSIZE_4", ["B25009_006E", "B25009_014E"]),
            ("HHSIZE_5", ["B25009_007E", "B25009_015E"]),
            ("HHSIZE_6", ["B25009_008E", "B25009_016E"]),
            ("HHSIZE_7+", ["B25009_009E", "B25009_017E"]),
        ],
        "check": ["B25009_001E", "B26001_001E"],
    }

    group_5 = {
        "name": "number_people",
        "columns": [
            ("PERSONS", ["DP05_0001E"]),
        ],
        "check": ["DP05_0001E"],
    }

    group_6 = {
        "name": "gender",
        "columns": [
            ("SEX_MALE", ["DP05_0002E"]),
            ("SEX_FEMALE", ["DP05_0003E"]),
        ],
        "check": ["DP05_0001E"],
    }

    if year == 2016:
        group_7 = {
            "name": "age",
            "columns": [
                ("AGE_UNDER_15", ["DP05_0004E", "DP05_0005E", "DP05_0006E"]),
                ("AGE_15to24", ["DP05_0007E", "DP05_0008E"]),
                ("AGE_25to34", ["DP05_0009E"]),
                ("AGE_35to44", ["DP05_0010E"]),
                ("AGE_45to54", ["DP05_0011E"]),
                ("AGE_55to64", ["DP05_0012E", "DP05_0013E"]),
                ("AGE_65plus", ["DP05_0014E", "DP05_0015E", "DP05_0016E"]),
            ],
            "check": ["DP05_0001E"],
        }
    else:
        group_7 = {
            "name": "age",
            "columns": [
                ("AGE_UNDER_15", ["DP05_0005E", "DP05_0006E", "DP05_0007E"]),
                ("AGE_15to24", ["DP05_0008E", "DP05_0009E"]),
                ("AGE_25to34", ["DP05_0010E"]),
                ("AGE_35to44", ["DP05_0011E"]),
                ("AGE_45to54", ["DP05_0012E"]),
                ("AGE_55to64", ["DP05_0013E", "DP05_0014E"]),
                ("AGE_65plus", ["DP05_0015E", "DP05_0016E", "DP05_0017E"]),
            ],
            "check": ["DP05_0001E"],
        }

    # If we want to use RAC1P in PUMS use the following columns and change linker_file.txt accordingly
    # group_8 = {
    #     "name": "race",
    #     "columns": [
    #         ("RACE_WHITE", ["DP05_0037E"]),
    #         ("RACE_BLACK", ["DP05_0038E"]),
    #         ("RACE_INDIAN", ["DP05_0039E"]),
    #         ("RACE_ASIAN", ["DP05_0044E"]),
    #         ("RACE_OTHER", ["DP05_0052E", "DP05_0057E", "DP05_0035E"]),
    #     ],
    #     "check": ["DP05_0033E"],
    # }

    if year == 2016:
        group_8 = {
            "name": "race",
            "columns": [
                ("RACE_WHITE", ["DP05_0072E"]),
                ("RACE_BLACK", ["DP05_0073E"]),
                ("RACE_INDIAN", ["DP05_0074E", "DP05_0076E"]),
                ("RACE_ASIAN", ["DP05_0075E"]),
                ("RACE_OTHER", ["DP05_0077E", "DP05_0078E"]),
                ("RACE_HISPANIC", ["DP05_0066E"]),
            ],
            "check": ["DP05_0065E"],
        }

    else:
        group_8 = {
            "name": "race",
            "columns": [
                ("RACE_WHITE", ["DP05_0077E"]),
                ("RACE_BLACK", ["DP05_0078E"]),
                ("RACE_INDIAN", ["DP05_0079E", "DP05_0081E"]),
                ("RACE_ASIAN", ["DP05_0080E"]),
                ("RACE_OTHER", ["DP05_0082E", "DP05_0083E"]),
                ("HISPANIC", ["DP05_0071E"]),
            ],
            "check": ["DP05_0070E"],
        }

    if year == 2016:
        group_9 = {
            "name": "EDUCATION_EMPLOYMENT",
            "columns": [
                ("EDUC_LESSHS_EMPLOYED", ["B23006_004E", "B23006_006E"]),
                ("EDUC_LESSHS_UNEMPLOYED", ["B23006_007E"]),
                ("EDUC_LESSHS_NILF", ["B23006_008E"]),
                ("EDUC_HS_EMPLOYED", ["B23006_011E", "B23006_013E"]),
                ("EDUC_HS_UNEMPLOYED", ["B23006_014E"]),
                ("EDUC_HS_NILF", ["B23006_015E"]),
                ("EDUC_SOMECOLLEGE_EMPLOYED", ["B23006_018E", "B23006_020E"]),
                ("EDUC_SOMECOLLEGE_UNEMPLOYED", ["B23006_021E"]),
                ("EDUC_SOMECOLLEGE_NILF", ["B23006_022E"]),
                ("EDUC_COLLEGE_EMPLOYED", ["B23006_025E", "B23006_027E"]),
                ("EDUC_COLLEGE_UNEMPLOYED", ["B23006_028E"]),
                ("EDUC_COLLEGE_NILF", ["B23006_029E"]),
                ("EDUC_UNDER25", ["DP05_0004E", "DP05_0005E", "DP05_0006E", "DP05_0007E", "DP05_0008E"]),
                ("EDUC_65PLUS", ["DP05_0014E", "DP05_0015E", "DP05_0016E"]),
            ],
            "check": ["DP05_0001E"],
        }
    else:
        group_9 = {
            "name": "EDUCATION_EMPLOYMENT",
            "columns": [
                ("EDUC_LESSHS_EMPLOYED", ["B23006_004E", "B23006_006E"]),
                ("EDUC_LESSHS_UNEMPLOYED", ["B23006_007E"]),
                ("EDUC_LESSHS_NILF", ["B23006_008E"]),
                ("EDUC_HS_EMPLOYED", ["B23006_011E", "B23006_013E"]),
                ("EDUC_HS_UNEMPLOYED", ["B23006_014E"]),
                ("EDUC_HS_NILF", ["B23006_015E"]),
                ("EDUC_SOMECOLLEGE_EMPLOYED", ["B23006_018E", "B23006_020E"]),
                ("EDUC_SOMECOLLEGE_UNEMPLOYED", ["B23006_021E"]),
                ("EDUC_SOMECOLLEGE_NILF", ["B23006_022E"]),
                ("EDUC_COLLEGE_EMPLOYED", ["B23006_025E", "B23006_027E"]),
                ("EDUC_COLLEGE_UNEMPLOYED", ["B23006_028E"]),
                ("EDUC_COLLEGE_NILF", ["B23006_029E"]),
                ("EDUC_UNDER25", ["DP05_0005E", "DP05_0006E", "DP05_0007E", "DP05_0008E", "DP05_0009E"]),
                ("EDUC_65PLUS", ["DP05_0015E", "DP05_0016E", "DP05_0017E"]),
            ],
            "check": ["DP05_0001E"],
        }

    groups = [base, group_0, group_1, group_2, group_3, group_4, group_5, group_6, group_7, group_8, group_9]

    return groups


def maybe_sanitise_geo_id(control_totals: pd.DataFrame, geoid_column_name: str = "GEO_ID") -> pd.DataFrame:
    str_to_remove = "1400000US"
    control_totals[geoid_column_name] = control_totals[geoid_column_name].str.replace(str_to_remove, "")
    return control_totals


def download_control_totals(
    group_spec: List,
    state: us.states.State,
    data_year: int,
    county_fips: Optional[Union[str, np.ndarray, list]],
) -> pd.DataFrame:
    api_key = UserConfig().census_api
    if api_key is None:
        raise ValueError(
            "Empty Census API key, please create on at https://api.census.gov/data/key_signup.html then set it in your "
            "user configuration file."
        )

    # figure out columns to download
    acs_data_to_load = set(itertools.chain.from_iterable([x[1] for group in group_spec for x in group["columns"]]))
    # add control data sets
    acs_data_to_load = acs_data_to_load.union(set(itertools.chain.from_iterable([x["check"] for x in group_spec])))

    # split into B* and DP* - different calls
    dp_fields = list(filter(lambda x: x.startswith("DP"), acs_data_to_load))
    detailed_fields = list(filter(lambda x: not x.startswith("DP"), acs_data_to_load))

    # county_fips
    if (county_fips is None) or (len(county_fips) == 0):  # type: ignore
        county_fips = "*"
    elif isinstance(county_fips, list) or isinstance(county_fips, np.ndarray):
        county_fips = ",".join(county_fips)

    # download data
    census_api = Census(api_key)
    dp_data = pd.DataFrame(
        census_api.acs5dp.state_county_tract(
            fields=("GEO_ID", *dp_fields),
            state_fips=state.fips,
            county_fips=county_fips,
            tract="*",
            year=data_year,
        )
    )

    detailed_data = pd.DataFrame(
        census_api.acs5.state_county_tract(
            fields=("GEO_ID", *detailed_fields),
            state_fips=state.fips,
            county_fips=county_fips,
            tract="*",
            year=data_year,
        )
    )

    data = detailed_data.merge(dp_data, on="GEO_ID", how="outer", validate="1:1").set_index("GEO_ID")
    return data


def aggregate_raw_data(data: pd.DataFrame, group_spec: List) -> pd.DataFrame:
    control_totals = []
    for control_group in group_spec:
        all_columns_this_group = {}
        for control_column_name, raw_column_keys in control_group["columns"]:
            control_column_values = data[raw_column_keys].sum(axis=1)
            all_columns_this_group[control_column_name] = control_column_values
        all_columns_this_group_df = pd.DataFrame(all_columns_this_group)  # type: ignore
        if not np.allclose(
            all_columns_this_group_df.sum(axis=1), data[control_group["check"]].sum(axis=1)
        ):  # type: ignore
            logging.critical(f"Test totals not matching for group {control_group['name']}")
            raise ValueError(f"Test totals not matching for group {control_group['name']}")
        control_totals.append(all_columns_this_group_df)
    control_totals = pd.concat(control_totals, axis=1).reset_index()  # type: ignore
    return control_totals  # type: ignore


def attach_puma_ids(
    control_totals: pd.DataFrame,
    state: us.states.State,
    county_fips: Optional[Union[str, list, np.ndarray]],
) -> pd.DataFrame:
    # TODO [jzill 13Jun23]: make geo_id names consistent
    geo_cross_walk = get_tract_to_puma_crosswalk(state, county_fips)
    control_totals = control_totals.merge(
        geo_cross_walk,
        left_on="GEO_ID",
        right_on="GEOID",
        how="left",
        validate="1:1",
    )
    # note I found an instance in LA where a control total tract is not in the tract to puma crosswalk
    # (tract 06037137000) so let's better check and remove here because we need puma as upper geometry
    filter_ = control_totals.GEOID.isnull()
    if filter_.sum() > 0:
        logging.warning(
            f"Removing {filter_.sum()} out of {control_totals.shape[0]} tracts where we couldn't find a matching PUMA."
        )
        control_totals = control_totals.loc[~filter_]

    return control_totals


def create_control_totals(
    working_dir: Path,
    states_and_counties: List[Tuple[us.states.State, Optional[Union[str, list, np.ndarray]]]],
    data_year: int,
    use_cached_data: bool = False,
) -> pd.DataFrame:
    g = get_default_group_spec(data_year)

    controls = []
    for state, county_fips in states_and_counties:
        if use_cached_data:
            raw_data = pd.read_csv(working_dir / f"raw_acs5_{state.abbr}.csv", index_col="GEO_ID")
        else:
            raw_data = download_control_totals(g, state, data_year, county_fips)
            raw_data.to_csv(working_dir / f"raw_acs5_{state.abbr}.csv")

        control_totals = aggregate_raw_data(raw_data, g)
        control_totals = maybe_sanitise_geo_id(control_totals)
        control_totals = attach_puma_ids(control_totals, state, county_fips)

        filter_ = control_totals["HOUSEHOLDS"] == 0
        if filter_.sum() > 0:
            logging.info(f"Removing {filter_.sum()} out of {control_totals.shape[0]} tracts without population")
            control_totals = control_totals.loc[~filter_]

        controls.append(control_totals)

    return pd.concat(controls, ignore_index=True)


# Simple method of getting a population estimate from the 'zones' file.
def get_zones_total_pop(zone_file: Path) -> int:
    sep = "," if zone_file.suffix == ".csv" else "\t"
    df = pd.read_csv(zone_file, sep=sep)
    df.columns = df.columns.str.lower()
    person_col = first_and_only([col for col in df.columns if "person" in col or "pop" in col])
    return int(df[person_col].sum())
