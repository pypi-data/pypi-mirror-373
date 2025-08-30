# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd


def verify_polaris_codes(codes_df: pd.DataFrame) -> pd.DataFrame:
    # check required fields
    rq_flds = ["POLARIS_ID", "VEHICLE_CLASS", "POWERTRAIN", "FUEL", "AUTOMATION", "CONNECTIVITY", "VINTAGE"]
    for r in rq_flds:
        found = False
        for c in codes_df.columns:
            if r in c.upper():
                found = True
                codes_df.rename({c: r}, axis=1, inplace=True)
                break
        if not found:
            raise ValueError(f"Error, missing field '{r}' in source vehicle code file. File must have fields {rq_flds}")
    pcode_names = [str(x) for x in codes_df.columns[1:]]
    codes_df.set_index(pcode_names, inplace=True)
    codes_df.index.set_names(pcode_names, inplace=True)
    return codes_df
