# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd


def initialize_seed(
    dist_df: pd.DataFrame, target_df: pd.DataFrame, zone_df: pd.DataFrame, codes_df: pd.DataFrame, default_values: dict
):
    # add any missing values which are required by target
    # i.e. Standard initialization of all values to guarantee that IPF converges

    ddf = dist_df[dist_df.PROPORTION > 0]

    target_data = target_df[target_df["value"] > 0].drop(columns=["value"])

    for k, v in default_values.items():
        if k not in target_data.index.names:
            target_data[k] = v
    target_data = target_data.reset_index().set_index(codes_df.index.names).join(codes_df).reset_index()
    target_data = target_data.assign(PROPORTION=ddf.PROPORTION.min() / 1000)
    app = pd.concat([target_data.assign(TRACT=tract) for tract in zone_df.index.values])

    app.set_index(["TRACT"] + target_df.index.names, inplace=True)

    ddf = ddf.set_index(["TRACT"] + target_df.index.names)
    app = app[~app.index.isin(ddf.index)]

    return pd.concat([app, ddf]).reset_index()
