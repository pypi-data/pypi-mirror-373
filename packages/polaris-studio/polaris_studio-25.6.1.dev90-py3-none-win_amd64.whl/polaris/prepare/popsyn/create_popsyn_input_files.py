# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
#!/usr/bin/env python

import logging
import shutil
from os import PathLike
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy as np
import us

from polaris.prepare.popsyn.control_totals import create_control_totals
from polaris.prepare.popsyn.seed import create_seed_data

# List of years synpop input file generation has successfully run before.
# Note there are three main areas where this process might break:
#  1. seed data column names and values
#  2. control total field names and values
#  3. geo crosswalk (associating pumas with census tracts)
# Regarding 1., we test for mandatory column names however we currently do not validate numeric values so a change in
#  definition of a variable could lead to a mismatch with control data, as defined in the {}MARGVAR part of the linker
#  file.
# Regarding 2., we define a control field that represents the sum of all sub-fields, which should catch a name change
#  when variables are added/removed from 5-year ACS data.
# Regarding 3., PUMAs can change during census years, the latest of which was 2020. Tose definitions will make their
#  way into this data at some point and could result in mismatches between tract ids and data.
#  get_tract_to_puma_crosswalk takes a url to the puma-tract mapping, which currently defaults to 2010.
YEARS_SUCCESSFULLY_RUN = [2016, 2017, 2019]


def parse_state(state_name: Union[str, int]) -> us.states.State:
    """Given a state name or state abbreviaton or state fips code, returns a us.states object"""
    # DC needs special treatment, cannot rely on DC_STATEHOOD here so force inclusion in states list
    if us.states.DC not in us.states.STATES:
        us.states.STATES_AND_TERRITORIES.append(us.states.DC)
        us.states.STATES.append(us.states.DC)
    state = us.states.lookup(str(state_name))
    if state is None:
        logging.critical(
            f"Couldn't figure out state from provided input {state_name},"
            + " please use either full name, abbreveation or fips code."
        )
        raise ValueError()
    return state


def run_file_generation(
    year: int,
    states_and_counties: List[Tuple[Union[str, int], Optional[Union[str, list, np.ndarray]]]],
    dir: Optional[PathLike] = None,
    filter_to_single_year: bool = False,
    control_total_file_name: str = "sf1.csv",
    household_file_name: str = "pums_hh.csv",
    person_file_name: str = "pums_person.csv",
) -> None:
    """states_and counties is a list of tuples, each with a state and sub-selection of counties; the latter can be None"""
    if dir is None:
        dir = Path.cwd()
    dir = Path(dir)

    states_and_counties = [(parse_state(x[0]), x[1]) for x in states_and_counties]
    year = int(year)

    if year not in YEARS_SUCCESSFULLY_RUN:
        logging.warning(
            f"File generation process for year {year} has not been tested yet, keep an eye out for warnings and"
            + " make sure column names and values have not changed and geometries have not been updated to 2020 census."
        )

    hh, ppl = create_seed_data(dir, year, states_and_counties, filter_to_single_year)
    hh.to_csv(Path(dir) / household_file_name, index=False)  # type: ignore
    ppl.to_csv(Path(dir) / person_file_name, index=False)  # type: ignore

    control_totals = create_control_totals(dir, states_and_counties, year)
    control_totals.to_csv(dir / control_total_file_name, index=False)

    # copy default linker file to working dir
    linker_file = Path(__file__).absolute().parent / "linker_file.txt"
    shutil.copy(linker_file, dir)

    logging.info(
        f"Successfully ran seed and control generation for state(s) {[x[0].name for x in states_and_counties]} and "  # type: ignore
        + f" year {year} to output directory {dir}. Sub-selection of counties: {[x[1] for x in states_and_counties]}."
    )
