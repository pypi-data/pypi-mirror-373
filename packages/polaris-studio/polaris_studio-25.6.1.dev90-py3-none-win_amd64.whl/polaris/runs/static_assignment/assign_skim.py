# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path
from typing import Dict

import numpy as np
import openmatrix as omx
from aequilibrae.matrix.aequilibrae_matrix import AequilibraeMatrix
from tables import Filters

from polaris.analyze.activity_metrics import ActivityMetrics
from polaris.analyze.kpi_utils import KPITag
from polaris.analyze.result_kpis import ResultKPIs
from polaris.runs.convergence.convergence_callback_functions import copy_back_files
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.runs.static_assignment.intrazonals import fill_intrazonals
from polaris.runs.static_assignment.static_assign import assign_with_skim
from polaris.runs.static_assignment.static_assignment_inputs import STAInputs
from polaris.runs.static_assignment.static_graph import StaticGraph
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.logging_utils import add_file_handler, function_logging


@function_logging("  Assignment skimming")
def assignment_skimming(
    external_trips: Dict[int, AequilibraeMatrix],
    assig_pars: STAInputs,
    config: ConvergenceConfig,
    current_iteration: ConvergenceIteration,
    output_dir: Path,
    polaris_inputs: PolarisInputs,
    save_assignment_results: bool,
    pces,
):
    act_metr = ActivityMetrics(polaris_inputs.supply_db, output_dir / polaris_inputs.demand_db.name)
    graph = StaticGraph(polaris_inputs.supply_db).graph
    compression = Filters(complevel=0, complib="zlib")
    omx_export = omx.open_file(output_dir / polaris_inputs.highway_skim.name, "w", filters=compression)
    omx_export.create_mapping("taz", graph.centroids)
    omx_export.root._v_attrs["interval_count"] = np.array([len(config.skim_interval_endpoints)]).astype("int32")
    omx_export.root._v_attrs["update_intervals"] = np.array(config.skim_interval_endpoints).astype("float32")

    aeq_data = output_dir / "aequilibrae_data"
    aeq_data.mkdir(exist_ok=True)
    graph.network.to_parquet(aeq_data / "graph_network.parquet")

    logger = logging.getLogger("aequilibrae")
    add_file_handler(logger, logging.DEBUG, output_dir / "log" / "polaris_progress.log")

    if save_assignment_results:
        with commit_and_close(current_iteration.files.result_db, missing_ok=True) as conn:
            build_infrastructure(conn)

    graph.graph["hourly_capacity"] = graph.graph["capacity"]
    for prev_interv, interv in zip([0] + config.skim_interval_endpoints[:-1], config.skim_interval_endpoints):
        logger.info(f"      Skimming period: {interv}")

        graph.graph["capacity"] = graph.graph.hourly_capacity * ((interv - prev_interv) / 60)

        # We only have car trips among our activities, so no PCE conversion needed
        mat_ = act_metr.vehicle_trip_matrix(from_start_time=prev_interv * 60, to_start_time=interv * 60)
        matrix = mat_.to_aeq()
        ext_trips = external_trips.get(interv, None)

        if ext_trips is not None:
            if any(x not in matrix.names for x in ext_trips.names):
                all_names = list(set(set(matrix.names) | set(ext_trips.names)))
                mat = AequilibraeMatrix()
                zones = graph.centroids.shape[0]
                mat.create_empty(zones=zones, matrix_names=all_names, index_names=["taz"], memory_only=True)
                mat.index[:] = graph.centroids[:]
                for i in matrix.names:
                    mat.matrix[i][:, :] = matrix.matrix[i][:, :]
                matrix = mat

            for i in ext_trips.names:
                matrix.matrix[i][:, :] += ext_trips.matrix[i][:, :]

        assert len(matrix.names) > 0, "There is no demand to assign"

        for i, mat in enumerate(matrix.names):
            if mat in pces:
                matrix.matrices[:, :, i] *= pces[mat]
            else:
                logging.warning(f"  {mat} not in PCE dictionary, using 1.0")

        matrix.computational_view(matrix.names[0])
        matrix.export(str(aeq_data / f"demand_matrix_{interv}.omx"), cores=[matrix.names[0]])
        assig = assign_with_skim(graph, matrix, assig_pars)

        if save_assignment_results:
            results = assig.results().query("PCE_tot > 0")

            table_name = f"link_flows_static_{interv}"
            report = {"convergence": str(assig.assignment.convergence_report), "setup": str(assig.info())}

            data = [
                table_name,
                "traffic assignment",
                assig.procedure_id,
                str(report),
                assig.procedure_date,
                assig.description,
            ]

            if save_assignment_results:
                with commit_and_close(current_iteration.files.result_db) as conn:
                    results.to_sql(table_name, conn, if_exists="replace")
                    conn.execute(
                        "Insert into static_results(table_name, procedure, procedure_id, procedure_report, timestamp, description) Values(?,?,?,?,?,?)",
                        data,
                    )
        skims = {
            "distance": assig.classes[0].results.skims.distance.astype(np.float32),
            "time": assig.classes[0]._aon_results.skims.time.astype(np.float32),
            "cost": np.zeros_like(assig.classes[0]._aon_results.skims.time).astype(np.float32),
        }

        for metric, value in skims.items():
            slice_name = f"auto_{interv}_{metric}"
            omx_export[slice_name] = fill_intrazonals(value)
            omx_export[slice_name].attrs.timeperiod = interv
            omx_export[slice_name].attrs.metric = metric
            omx_export[slice_name].attrs.mode = "auto"
        del skims

    omx_export.root._v_attrs["interval_count"] = np.array([len(config.skim_interval_endpoints)]).astype("int32")
    omx_export.root._v_attrs["update_intervals"] = np.array(config.skim_interval_endpoints).astype("float32")
    del matrix
    del graph

    omx_export.close()
    copy_back_files(config, current_iteration)
    kpi_types = [KPITag.POPULATION, KPITag.ACTIVITIES_PLANNED, KPITag.VALIDATION, KPITag.CALIBRATION]
    ResultKPIs.from_iteration(current_iteration, include_kpis=kpi_types).cache_all_available_metrics()


def build_infrastructure(conn):
    sql = """
                create TABLE if not exists static_results(table_name       TEXT     NOT NULL PRIMARY KEY,
                                                          procedure        TEXT     NOT NULL,
                                                          procedure_id     TEXT     NOT NULL,
                                                          procedure_report TEXT     NOT NULL,
                                                          timestamp        DATETIME DEFAULT current_timestamp,
                                                          description      TEXT);
                """
    conn.execute(sql)
    conn.execute("DELETE FROM static_results")
