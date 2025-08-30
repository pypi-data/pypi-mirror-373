# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import List

import pandas as pd


def verify_veh_dist_input(dist_df: pd.DataFrame, controls: List[str], fleet_mode=False) -> pd.DataFrame:
    # check required fields
    req_fields = ["POLARIS_ID", "VINTAGE", "PROPORTION"] + controls
    if not fleet_mode:
        req_fields.append("TRACT")
    for r in req_fields:
        found = False
        for c in dist_df.columns:
            if r in c.upper():
                found = True
                dist_df.rename({c: r}, axis=1, inplace=True)
                break
        if not found:
            raise ValueError(f"Error, missing field '{r}' in source vehicle distribution data file.")
    return dist_df
