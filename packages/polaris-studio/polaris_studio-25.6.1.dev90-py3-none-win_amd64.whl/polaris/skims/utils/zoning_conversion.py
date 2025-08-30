# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import importlib.util as iutil
import itertools
from pathlib import Path

import numpy as np
import openmatrix as omx
import pandas as pd
from scipy.sparse import coo_matrix
from tables import Filters

if iutil.find_spec("geopandas") is not None:
    import geopandas as gpd


def convert_zoning_systems(src_skim, src_zone: gpd.GeoDataFrame, tgt_zone: gpd.GeoDataFrame, output_path: Path):
    """Converts the zoning system of the skims

    Args:
        *src_zone* (:obj:`gpd.GeoDataFrame`): GeoDataFrame with the source zoning system
        *tgt_zone* (:obj:`gpd.GeoDataFrame`): GeoDataFrame with the target zoning system
        *output_path* (:obj:`Path`): Path to the output file
    """

    src_zone = src_zone[["zone", "geo"]].rename(columns={"zone": "source_zone"})
    tgt_zone = tgt_zone[["zone", "geo"]].rename(columns={"zone": "tgt_zn"})

    ovrl = src_zone.overlay(tgt_zone, how="intersection", keep_geom_type=False)
    ovrl = ovrl.assign(ovrl_a=ovrl.area)
    ovrl = ovrl[ovrl["ovrl_a"] > 0]

    # Factor the overlay areas up and down
    ovrl_areas = ovrl.groupby("tgt_zn")["ovrl_a"].sum().reset_index()
    ovrl_areas = tgt_zone.assign(orig_a=tgt_zone.area).merge(ovrl_areas, on="tgt_zn")

    ovrl_factor = ovrl_areas.assign(factor=ovrl_areas["orig_a"] / ovrl_areas["ovrl_a"])[["tgt_zn", "orig_a", "factor"]]
    ovrl = ovrl.merge(ovrl_factor, on="tgt_zn")
    ovrl.ovrl_a *= ovrl.factor
    ovrl.drop(columns=["factor"], inplace=True)
    ovrl = ovrl.assign(fraction=ovrl.ovrl_a / ovrl.orig_a)
    cnvtr = ovrl[["source_zone", "tgt_zn", "fraction"]]

    src_index = src_skim.index.zones.to_numpy()
    tgt_index = tgt_zone.sort_values(by="tgt_zn")["tgt_zn"].to_numpy()

    rev_idx = np.zeros(tgt_index.max() + 1).astype(np.int64)
    rev_idx[tgt_index] = np.arange(tgt_index.shape[0])[:]

    metrics = src_skim.metrics
    modes = src_skim.modes if hasattr(src_skim, "modes") else ["auto"]
    intervals = src_skim.intervals
    combinations = list(itertools.product(metrics, modes, intervals))
    combinations_dicts = [{"metric": metr, "mode": md, "interval": interv} for metr, md, interv in combinations]

    with omx.open_file(str(output_path), "w", filters=Filters(complevel=4, complib="zlib")) as omx_export:
        omx_export.create_mapping("taz", tgt_index)
        omx_export.root._v_attrs["interval_count"] = np.array(len(intervals)).astype("int32")
        omx_export.root._v_attrs["update_intervals"] = np.array(intervals).astype("float32")

        for comb in combinations_dicts:
            src_skim_data = src_skim.get_skims(**comb)
            array = compress_array(cnvtr, rev_idx, src_index, src_skim_data, tgt_index)

            slice_name = f"{comb['mode']}_{comb['interval']}_{comb['metric']}"
            # Add values and all its attributes
            omx_export[slice_name] = array
            omx_export[slice_name].attrs.timeperiod = comb["interval"]
            omx_export[slice_name].attrs.metric = comb["metric"]
            omx_export[slice_name].attrs.mode = comb["mode"]


def compress_array(cnvtr, rev_idx, src_index, src_skim_data, tgt_index):
    coo_ = coo_matrix(src_skim_data)
    src_skim_df = pd.DataFrame({"origin": src_index[coo_.row], "destination": src_index[coo_.col], "metric": coo_.data})
    x1 = cnvtr.rename(columns={"source_zone": "origin", "tgt_zn": "tgt_orig", "fraction": "fraction1"})
    x2 = cnvtr.rename(columns={"source_zone": "destination", "tgt_zn": "tgt_dest", "fraction": "fraction2"})
    src_skim_df2 = src_skim_df.merge(x1, how="inner", on="origin").merge(x2, how="inner", on="destination")
    src_skim_df2.metric *= src_skim_df2.fraction1 * src_skim_df2.fraction2
    src_skim_df2.drop(columns=["fraction1", "fraction2", "origin", "destination"], inplace=True)
    tgt_skm_df = src_skim_df2.groupby(["tgt_orig", "tgt_dest"])["metric"].sum().reset_index()
    tgt_skm_df.head()
    return coo_matrix(
        (tgt_skm_df.metric, (rev_idx[tgt_skm_df.tgt_orig], rev_idx[tgt_skm_df.tgt_dest])),
        shape=(tgt_index.shape[0], tgt_index.shape[0]),
        dtype=np.float32,
    ).toarray()
