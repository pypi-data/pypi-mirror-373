# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike
from os.path import join

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess


def export_sig_ctrl_to_gmns(gmns_folder: str, target_crs, conn, path_to_file: PathLike):
    # Controller
    controller_sql = "select signal controller_id from Signal"
    pd.read_sql(controller_sql, conn).to_csv(join(gmns_folder, "signal_controller.csv"), index=False)

    # signal_phase_mvmt
    conn_sql = "Select conn mvmt_id, link value_link, dir value_dir, to_link value_to_link from Connection"
    connections = pd.read_sql(conn_sql, conn)

    pnr = DataTableAccess(path_to_file).get("Phasing_Nested_Records", conn=conn)

    pnr = pnr.merge(connections, on=["value_link", "value_dir", "value_to_link"], how="left")
    pnr = pnr.assign(protection="permitted")
    pnr.loc[pnr.value_protect == "PROTECTED", "protection"] = "protected"

    pnr.loc[:, "value_link"] = 2 * pnr.value_link + pnr.value_dir

    pnr.drop(columns=["value_dir", "value_to_link", "value_movement", "value_protect", "index"], inplace=True)
    pnr.rename(columns={"value_link": "link_id", "object_id": "signal_phase_mvmt_id"}, inplace=True)

    ph_sql = "Select phasing_id signal_phase_mvmt_id, signal controller_id, phase signal_phase_num from Phasing"
    ph = pd.read_sql(ph_sql, conn)

    pnr = pnr.merge(ph, on="signal_phase_mvmt_id")
    pnr["signal_phase_mvmt_id"] = np.arange(pnr.shape[0]) + 1

    pnr.to_csv(join(gmns_folder, "signal_phase_mvmt.csv"), index=False)

    # signal_timing_plan
    st = DataTableAccess(path_to_file).get("Timing", conn=conn)
    st.rename(columns={"timing_id": "timing_plan_id", "signal": "controller_id", "cycle": "cycle_length"}, inplace=True)
    st.drop(columns=["timing", "type", "offset", "phases"], inplace=True)
    st.to_csv(join(gmns_folder, "signal_timing_plan.csv"), index=False)

    # signal_timing_phase
    tnr = DataTableAccess(path_to_file).get("Timing_Nested_Records", conn=conn)
    tnr.rename(
        columns={
            "object_id": "timing_plan_id",
            "value_ring": "ring",
            "value_phase": "signal_phase_num",
            "value_extend": "extension",
            "value_barrier": "barrier",
            "value_minimum": "min_green",
            "value_maximum": "max_green",
            "value_position": "position",
        },
        inplace=True,
    )
    tnr = tnr.assign(clearance=tnr.value_yellow + tnr.value_red)
    tnr.drop(columns=["index", "value_yellow", "value_red"], inplace=True)
    tnr = tnr.assign(timing_phase_id=np.arange(tnr.shape[0]) + 1)
    tnr.to_csv(join(gmns_folder, "signal_timing_phase.csv"), index=False)
