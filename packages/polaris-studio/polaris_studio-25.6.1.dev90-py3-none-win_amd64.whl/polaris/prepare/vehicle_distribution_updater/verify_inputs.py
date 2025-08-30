# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd


def verify_inputs(dist_df: pd.DataFrame, target_df: pd.DataFrame):
    source_headers = list(dist_df.columns)
    target_headers = list(target_df.index.names)

    # check that all of the control variables from target exist in source
    for x in target_headers:
        if x not in source_headers:
            raise ValueError("Target control {x} not in source vehicle distribution header: {source_headers}")
        vals = list(target_df.index.unique(level=x))
        source_vals = list(dist_df[x].unique())
        for v in vals:
            if v not in source_vals:
                raise ValueError(f"Target value {v} for column {x}, not in source vehicle distribution data.")
