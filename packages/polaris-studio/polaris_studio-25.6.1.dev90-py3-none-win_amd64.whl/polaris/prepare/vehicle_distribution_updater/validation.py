# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

import pandas as pd


def validate(df: pd.DataFrame, target_df: pd.DataFrame, zone_df: pd.DataFrame, model_dir, out_veh_file: Path):
    # Proportions for vehicle type
    sample = df.groupby(target_df.index.names).sum()[["VEH_TOT"]]
    sample.VEH_TOT /= sample.VEH_TOT.sum()

    sample = sample.join(target_df).rename(columns={"value": "target", "VEH_TOT": "result"})
    match_veh_type = sample.target.corr(sample.result)
    # sample.to_csv(Path(model_dir) / (str(Path(out_veh_file).stem) + "_share_proportions.csv"))
    ax1 = sample.plot.scatter("target", "result")
    ax1.set_title("Proportions for vehicle types")
    ax1.get_figure().savefig(str(Path(model_dir) / (str(Path(out_veh_file).stem) + "_share_proportions.png")))

    # Fleet per zone
    sample = df.groupby(zone_df.index.names).sum()[["VEH_TOT"]]

    sample = sample.join(zone_df).rename(columns={"veh_count": "target", "VEH_TOT": "result"})
    match_zone = sample.target.corr(sample.result)
    # sample.to_csv(Path(model_dir) / (str(Path(out_veh_file).stem) + "_zone_totals.csv"))
    ax2 = sample.plot.scatter("target", "result")
    ax2.set_title("Zone totals")
    ax2.get_figure().savefig(str(Path(model_dir) / (str(Path(out_veh_file).stem) + "_zone_totals.png")))
    return match_veh_type, match_zone
