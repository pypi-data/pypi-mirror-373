# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np
import openmatrix as omx


def export_transit_omx(matrices, path_file, modes, metrics, index, intervals):
    try:
        omx_export = omx.open_file(path_file, "w")
        for metric in metrics:
            for mode in modes:
                for interval in intervals:
                    data = matrices[metric][mode][interval]
                    nm = f"{mode}_{interval}_{metric}"
                    omx_export[nm] = data
                    omx_export[nm].attrs.timeperiod = interval
                    omx_export[nm].attrs.mode = mode
                    omx_export[nm].attrs.metric = metric

        omx_export.root._v_attrs["interval_count"] = np.array([len(intervals)]).astype("int32")
        omx_export.root._v_attrs["update_intervals"] = np.array(intervals).astype("float32")
        zones = np.array(index.zones.values.astype(np.int32))
        omx_export.create_mapping("taz", zones)
    finally:
        omx_export.close()
