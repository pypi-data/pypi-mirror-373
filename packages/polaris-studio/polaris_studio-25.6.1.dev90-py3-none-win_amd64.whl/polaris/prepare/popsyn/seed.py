# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import urllib.request as request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import us

from polaris.prepare.popsyn.geo_crosswalk import get_tract_to_puma_crosswalk


def get_pums_data(survey_year: int, state: us.states.State, file_type: str, working_dir: Path) -> pd.DataFrame:
    if file_type == "household":
        file_name_letter = "h"
    elif (file_type == "person") or (file_type == "people"):
        file_name_letter = "p"
    else:
        logging.critical(f"Can only download person or household file from PUMS, not {file_type}")
        raise ValueError(f"Can only download person or household file from PUMS, not {file_type}")

    pums_file = f"csv_{file_name_letter}{state.abbr.lower()}.zip"

    maybe_download_pums_archive(survey_year, pums_file, working_dir)

    zf = zipfile.ZipFile(working_dir / pums_file)
    possible_data_files = list(filter(lambda x: ".csv" in x, zf.namelist()))
    if not len(possible_data_files) == 1:
        logging.warning("Found more than one csv file in PUMS zip archive, reading only first one - double-check this")
    data = pd.read_csv(zf.open(possible_data_files[0]), dtype={"SERIALNO": str})
    if data.empty:
        logging.warning("Empty PUMS data")
    return data


def maybe_download_pums_archive(survey_year: int, pums_file: str, working_dir: Path) -> bool:
    url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{survey_year}/5-Year/{pums_file}"
    if (working_dir / pums_file).is_file():
        logging.info(f"File {pums_file} in directory {working_dir} already exists - skipping download")
        return False
    working_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Downloading PUMS file from {url}")
    request.urlretrieve(url, filename=(working_dir / pums_file))
    return True


def create_derived_hh_fields(hh: pd.DataFrame) -> pd.DataFrame:
    # There's a small fraction of households that doesn't fit this HHTENURE scheme- these all have TEN=4 so
    #  Occupied without payment of rent, but are all non-GQ hosueholds. Currently we remove these.
    #  Would it be better to put put these in rent or own?
    hh_types = {
        "column_name": "HHTENURE",
        "column_values": [
            {
                "name": "HHT_OWN_MARRIED",
                "value": 1,  # "HHT_OWN_FAMILY_MARRIED"
                "filter": [("HHT", "==", "1"), ("TEN", ".", "isin([1,2])")],
            },
            {
                "name": "HHT_OWN_FAMILY_MALE",
                "value": 2,
                "filter": [("HHT", "==", "2"), ("TEN", ".", "isin([1,2])")],
            },
            {
                "name": "HHT_OWN_FAMILY_FEMALE",
                "value": 3,
                "filter": [("HHT", "==", "3"), ("TEN", ".", "isin([1,2])")],
            },
            {
                "name": "HHT_OWN_NONFAMILY_SINGLE",
                "value": 4,
                "filter": [("HHT", ".", "isin([4,6])"), ("TEN", ".", "isin([1,2])")],
            },
            {
                "name": "HHT_OWN_NONFAMILY_NOTALONE",
                "value": 5,  # "HHT_OWN_NONFAMILY_OTHER"
                "filter": [("HHT", ".", "isin([5,7])"), ("TEN", ".", "isin([1,2])")],
            },
            {
                "name": "HHT_RENT_MARRIED",
                "value": 6,  # "HHT_RENT_FAMILY_MARRIED"
                "filter": [("HHT", "==", "1"), ("TEN", "==", "3")],
            },
            {
                "name": "HHT_RENT_FAMILY_MALE",
                "value": 7,
                "filter": [("HHT", "==", "2"), ("TEN", "==", "3")],
            },
            {
                "name": "HHT_RENT_FAMILY_FEMALE",
                "value": 8,
                "filter": [("HHT", "==", "3"), ("TEN", "==", "3")],
            },
            {
                "name": "HHT_RENT_NONFAMILY_SINGLE",
                "value": 9,
                "filter": [("HHT", ".", "isin([4,6])"), ("TEN", "==", "3")],
            },
            {
                "name": "HHT_RENT_NONFAMILY_NOTALONE",
                "value": 10,  # "HHT_RENT_NONFAMILY_OTHER"
                "filter": [("HHT", ".", "isin([5,7])"), ("TEN", "==", "3")],
            },
            {
                "name": "HHT_GQ",
                "value": 11,
                "filter": [("HHT", ".", "isnull()")],
            },
        ],
    }

    hu_types = {
        "column_name": "HU_TYPE",
        "column_values": [
            {
                "name": "HU_SINGLE_FAMILY",
                "value": 1,
                "filter": [("BLD", ".", "isin([2,3])")],
            },
            {
                "name": "HU_SMALL_APT_BLD",
                "value": 2,
                "filter": [("BLD", ".", "isin([4,5,6])")],
            },
            {
                "name": "HU_LARGE_APT_BLD",
                "value": 3,
                "filter": [("BLD", ".", "isin([7,8,9])")],
            },
            {
                "name": "HU_OTHER",
                "value": 4,
                "filter": [("BLD", ".", "isin([1,10])")],
            },
            {
                "name": "HU_GROUP_QUARTERS",
                "value": 5,
                "filter": [("BLD", ".", "isnull()")],
            },
        ],
    }

    derived_fields = [hh_types, hu_types]
    for field in derived_fields:
        hh = create_derived_fields(hh, field)

    return hh


def create_derived_ppl_fields(ppl: pd.DataFrame) -> pd.DataFrame:
    ppl_race = {
        "column_name": "RACE",
        "column_values": [
            {
                "name": "RACE_WHITE",
                "value": 1,
                "filter": [("RAC1P", "==", "1"), ("HISP", "==", "1")],
            },
            {
                "name": "RACE_BLACK",
                "value": 2,
                "filter": [("RAC1P", "==", "2"), ("HISP", "==", "1")],
            },
            {
                "name": "RACE_INDIAN",
                "value": 3,
                "filter": [("RAC1P", ".", "isin([3,4,5,7])"), ("HISP", "==", "1")],
            },
            {
                "name": "RACE_ASIAN",
                "value": 4,
                "filter": [("RAC1P", "==", "6"), ("HISP", "==", "1")],
            },
            {
                "name": "RACE_OTHER",
                "value": 5,
                "filter": [("RAC1P", ".", "isin([8,9])"), ("HISP", "==", "1")],
            },
            {
                "name": "RACE_HISPANIC",
                "value": 6,
                "filter": [("HISP", "!=", "1")],
            },
        ],
    }
    edu_by_emp = {
        "column_name": "EDUCATION_EMPLOYMENT",
        # note SCHL nan means age<3, which is covered by age filter for value: 13
        "column_values": [
            {
                "name": "EDUC_LESSHS_EMPLOYED",
                "value": 1,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", ".", "isin([1,2,4,5])"),
                    ("SCHL", "<=", "15"),
                ],
            },
            {
                "name": "EDUC_LESSHS_UNEMPLOYED",
                "value": 2,
                "filter": [("AGEP", ">=", "25"), ("AGEP", "<", "65"), ("ESR", "==", "3"), ("SCHL", "<=", "15")],
            },
            {
                "name": "EDUC_LESSHS_NILF",
                "value": 3,
                "filter": [("AGEP", ">=", "25"), ("AGEP", "<", "65"), ("ESR", "==", "6"), ("SCHL", "<=", "15")],
            },
            {
                "name": "EDUC_HS_EMPLOYED",
                "value": 4,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", ".", "isin([1,2,4,5])"),
                    ("SCHL", ".", "isin([16, 17])"),
                ],
            },
            {
                "name": "EDUC_HS_UNEMPLOYED",
                "value": 5,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", "==", "3"),
                    ("SCHL", ".", "isin([16, 17])"),
                ],
            },
            {
                "name": "EDUC_HS_NILF",
                "value": 6,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", "==", "6"),
                    ("SCHL", ".", "isin([16, 17])"),
                ],
            },
            {
                "name": "EDUC_SOMECOLLEGE_EMPLOYED",
                "value": 7,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", ".", "isin([1,2,4,5])"),
                    ("SCHL", ".", "isin([18, 19, 20])"),
                ],
            },
            {
                "name": "EDUC_SOMECOLLEGE_UNEMPLOYED",
                "value": 8,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", "==", "3"),
                    ("SCHL", ".", "isin([18, 19, 20])"),
                ],
            },
            {
                "name": "EDUC_SOMECOLLEGE_NILF",
                "value": 9,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", "==", "6"),
                    ("SCHL", ".", "isin([18, 19, 20])"),
                ],
            },
            {
                "name": "EDUC_COLLEGE_EMPLOYED",
                "value": 10,
                "filter": [
                    ("AGEP", ">=", "25"),
                    ("AGEP", "<", "65"),
                    ("ESR", ".", "isin([1,2,4,5])"),
                    ("SCHL", ">", "20"),
                ],
            },
            {
                "name": "EDUC_COLLEGE_UNEMPLOYED",
                "value": 11,
                "filter": [("AGEP", ">=", "25"), ("AGEP", "<", "65"), ("ESR", "==", "3"), ("SCHL", ">", "20")],
            },
            {
                "name": "EDUC_COLLEGE_NILF",
                "value": 12,
                "filter": [("AGEP", ">=", "25"), ("AGEP", "<", "65"), ("ESR", "==", "6"), ("SCHL", ">", "20")],
            },
            {"name": "EDUC_UNDER25", "value": 13, "filter": [("AGEP", "<", "25")]},
            {"name": "EDUC_65PLUS", "value": 14, "filter": [("AGEP", ">=", "65")]},
        ],
    }

    derived_fields = [ppl_race, edu_by_emp]
    for field in derived_fields:
        ppl = create_derived_fields(ppl, field)

    return ppl


def create_derived_fields(df: pd.DataFrame, field: Dict) -> pd.DataFrame:
    assert field["column_name"] not in df.columns

    for component in field["column_values"]:
        filter_str = " & ".join([f"(df['{x[0]}']{x[1]}{x[2]})" for x in component["filter"]])
        logging.info(f"Setting {field['column_name']} to {component['value']} where {filter_str}")
        df.loc[eval(filter_str), field["column_name"]] = component["value"]

    logging.info("Resulting distribution: ")
    logging.info(df[field["column_name"]].value_counts(dropna=False).sort_index().to_frame().T)

    filter_condition = df[field["column_name"]].isnull()
    if filter_condition.sum() > 0:
        logging.info(
            f"Removing {filter_condition.sum()} ({filter_condition.sum() / df.shape[0]:.1%})"
            + f" records that do not fit {field['column_name']} type definition."
        )
        if (filter_condition.sum() / df.shape[0]) > 0.1:
            logging.warning("More than 10% of data removed because it doesn't fit field definition")
        df = df.loc[~filter_condition].copy()

    return df


def get_and_clean_household_data(
    working_dir: Path, state: us.states, asc_year: int, filter_to_single_year: bool
) -> pd.DataFrame:
    hh = get_pums_data(asc_year, state, "household", working_dir)

    def filter_hh(hh, cond, reason):
        if cond.sum() > 0:
            remove_abs = cond.sum()
            remove_perc = remove_abs / hh.shape[0]
            logging.info(f"Removing {remove_abs} ({remove_perc:.1%}) households not {reason}")
            hh = hh.loc[~cond].copy()
        if hh.empty:
            raise RuntimeError(f"There were no households left after filtering for {reason}")
        return hh

    if filter_to_single_year:
        # filter to valid records for the desired year
        num_hh_before_filtering = hh.shape[0]
        hh = filter_hh(hh, hh["SERIALNO"].str[0:4].astype(int) != int(asc_year), "in desired survey year")
        fraction_of_hh_removed = (num_hh_before_filtering - hh.shape[0]) / num_hh_before_filtering
        if (fraction_of_hh_removed < 0.1) or (fraction_of_hh_removed > 0.3):
            logging.warning(
                f"Filtering to survey year left {fraction_of_hh_removed:.2%} of households, expected around 20%"
            )

    # DO NOT remove 0 weight! this removes GQ households with valid people attached
    # hh = filter_hh(hh, (hh['WGTP'] == 0) | hh['WGTP'].isnull(), "valid weight")
    hh = filter_hh(hh, hh["WGTP"].isnull(), "valid weight")

    # set group quarter households to single person households - they are zero in here by definition
    hh.loc[hh["HHT"].isnull(), "NP"] = 1

    hh = create_derived_hh_fields(hh)

    return hh


def get_and_clean_person_data(
    working_dir: Path, state: us.states.State, asc_year: int, hh: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    ppl = get_pums_data(asc_year, state, "people", working_dir)

    if hh is None:
        return ppl

    # make ppl consistent with HH: remove people corresponding to removed households
    filter_condition = ~ppl.SERIALNO.isin(hh.SERIALNO.unique())
    if filter_condition.sum() > 0:
        logging.info(
            f"Removing {filter_condition.sum()} ({filter_condition.sum() / ppl.shape[0]:.1%}) people corresponding"
            + " to excluded households"
        )
        ppl = ppl.loc[~filter_condition]

    ppl = create_derived_ppl_fields(ppl)

    return ppl


def integerise_ids(hh: pd.DataFrame, ppl: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # keep original serialno so we can tie to survey data if needed
    hh.loc[:, "SERIALNO_PUMS"] = hh["SERIALNO"]
    ppl.loc[:, "SERIALNO_PUMS"] = ppl["SERIALNO"]

    assert hh.SERIALNO.is_unique
    hh.loc[:, "SERIALNO"] = np.arange(1, hh.shape[0] + 1)
    hh["SERIALNO"] = hh["SERIALNO"].astype(np.int64)

    ppl = ppl.drop(columns=["SERIALNO"]).merge(
        hh[["SERIALNO", "SERIALNO_PUMS"]], on="SERIALNO_PUMS", how="left", validate="m:1"
    )

    return hh, ppl


# # this seems to break on windows - it's appending 0s instead of prepending them
# def attach_state_puma_id(hh: pd.DataFrame, ppl: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
#     # We concatenate state id and puma id and use these instead of puma ids, probably to be able to deal with cross-border models
#     hh["STPUMA"] = hh.apply(lambda x: f"{x.ST:02}{x.PUMA:05}", axis=1)
#     ppl["STPUMA"] = ppl.apply(lambda x: f"{x.ST:02}{x.PUMA:05}", axis=1)
#     return hh, ppl
def attach_state_puma_id(df: pd.DataFrame) -> pd.DataFrame:
    # We concatenate state id and puma id and use these instead of puma ids, probably to be able to deal with cross-border models
    df["STPUMA"] = (df["ST"].astype(str).str.zfill(2) + df["PUMA"].astype(str).str.zfill(5)).astype(int)
    return df


def filter_data_to_counties(
    data: pd.DataFrame, state: us.states.State, year: int, county_fips: Optional[Union[str, list, np.ndarray]]
) -> pd.DataFrame:
    # figure out pumas to restrict to from counties
    geo_crosswalk = get_tract_to_puma_crosswalk(state, county_fips)
    filter_condition = ~data["STPUMA"].isin(geo_crosswalk["STPUMA"].unique())
    if filter_condition.sum() > 0:
        logging.info(
            f"Removing {filter_condition.sum()} ({filter_condition.sum() / data.shape[0]:.1%})"
            + " datapoints outside PUMAs overlapping with model region"
        )
        data = data.loc[~filter_condition]
    return data


def filter_seed_columns(hh: pd.DataFrame, ppl: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    current_hh_cols = [
        "SERIALNO",
        "PUMA",
        "ST",
        "ADJHSG",
        "ADJINC",
        "WGTP",
        "NP",
        "TYPE",
        "ACR",
        "BLD",
        "TEN",
        "VEH",
        "FES",
        "HHT",
        "WIF",
        "HINCP",
        "HHTENURE",
        "HU_TYPE",
        "STPUMA",
        "SERIALNO_PUMS",
    ]
    columns_not_present = [col for col in current_hh_cols if col not in hh.columns]
    assert len(columns_not_present) == 0, f"Missing the following HH columns: {columns_not_present}"

    # jw mode is named JWTRNS from 2019 onwards, was JWTR before.
    #  Once more of these start to show up we need to generalise this, but for now just check for name here
    jw_mode_col = "JWTRNS"
    if "JWTRNS" not in ppl.columns:
        assert "JWTR" in ppl.columns
        jw_mode_col = "JWTR"

    current_ppl_cols = [
        "SERIALNO",
        "SPORDER",
        "PUMA",
        "ST",
        "ADJINC",
        "PWGTP",
        "AGEP",
        "COW",
        "JWMNP",
        "JWRIP",
        jw_mode_col,
        "MAR",
        "SCH",
        "SCHG",
        "SCHL",
        "SEX",
        "WAGP",
        "WKHP",
        "DRIVESP",
        "ESR",
        "HISP",
        "INDP",
        "JWAP",
        "JWDP",
        "PAOC",
        "POWPUMA",
        "RAC1P",
        "RACE",
        "STPUMA",
        "SERIALNO_PUMS",
        "PINCP",
        "DIS",
        "EDUCATION_EMPLOYMENT",
    ]
    columns_not_present = [col for col in current_ppl_cols if col not in ppl.columns]
    assert len(columns_not_present) == 0, f"Missing the following PERSON columns: {columns_not_present}"

    # We keep all columns after all, but re-order such the above columns come first. This guarantees position in
    #  linker_file.txt
    hh_cols = current_hh_cols + [col for col in hh.columns if col not in current_hh_cols]
    ppl_cols = current_ppl_cols + [col for col in ppl.columns if col not in current_ppl_cols]

    return hh[hh_cols], ppl[ppl_cols]


def make_hh_and_ppl_consistent(hh: pd.DataFrame, ppl: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """ensure that data is consistent - we want households with all persons"""

    id_field = "SERIALNO"
    number_peoplpe_field = "NP"

    ppl_without_households = list(set(ppl[id_field].unique()) - set(hh[id_field].unique()))
    if len(ppl_without_households) > 0:
        logging.info(f"Removing {len(ppl_without_households)} people without household in survey data")
        ppl = ppl.loc[~ppl[id_field].isin(ppl_without_households)]

    # now remove entries where not all people are present
    ppl_df = ppl.groupby(id_field).size().to_frame("num_people_in_survey").reset_index()  # type: ignore
    t_ = hh[[id_field, number_peoplpe_field]].merge(ppl_df, on=id_field, how="left")
    hh_to_remove = t_.loc[t_[number_peoplpe_field] != t_["num_people_in_survey"]].SERIALNO.unique()
    if hh_to_remove.shape[0] > 0:
        logging.info(f"Removing {hh_to_remove.shape[0]} households without all people in survey data")
        hh = hh.loc[~hh[id_field].isin(hh_to_remove)]
        ppl = ppl.loc[~ppl[id_field].isin(hh_to_remove)]

    # for GQ, hh weights are zero - assign person weights instead
    weight_column_name = "WGTP"
    person_weight_column_name = "PWGTP"
    if not (hh.loc[hh.HHT.isnull(), weight_column_name] == 0).all():
        logging.warning("Not all GQ households have weight 0, something changed in PUMS data")

    gq_ppl_weigths = hh.loc[hh.HHT.isnull()].merge(ppl[[id_field, person_weight_column_name]], how="left")[
        person_weight_column_name
    ]
    assert (gq_ppl_weigths > 0).all()

    hh.loc[hh.HHT.isnull(), weight_column_name] = gq_ppl_weigths.values
    assert (hh[weight_column_name] > 0).all()

    return hh, ppl


def create_seed_data(
    working_dir: Path,
    year: int,
    states_and_counties: List[Tuple[us.states.State, Optional[Union[str, list, np.ndarray]]]],
    filter_to_single_year: bool,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    households = []
    people = []
    for state, county_fips in states_and_counties:
        hh = get_and_clean_household_data(working_dir, state, year, filter_to_single_year)
        ppl = get_and_clean_person_data(working_dir, state, year, hh)

        hh, ppl = make_hh_and_ppl_consistent(hh, ppl)

        hh = attach_state_puma_id(hh)
        ppl = attach_state_puma_id(ppl)

        if county_fips is not None:
            hh = filter_data_to_counties(hh, state, year, county_fips)
            ppl = filter_data_to_counties(ppl, state, year, county_fips)
        households.append(hh)
        people.append(ppl)

    logging.info("Concatenating households.")
    hh = pd.concat(households, ignore_index=True)
    del households
    logging.info("Concatenating people.")
    ppl = pd.concat(people, ignore_index=True)
    del people

    logging.info("Integerising household ids.")
    hh, ppl = integerise_ids(hh, ppl)

    logging.info("Ordering columns for default linker file.")
    hh, ppl = filter_seed_columns(hh, ppl)

    logging.warning("Replacing nan values with 0 - make sure this is the desired behavior.")
    hh = hh.fillna(0)
    ppl = ppl.fillna(0)

    return hh, ppl
