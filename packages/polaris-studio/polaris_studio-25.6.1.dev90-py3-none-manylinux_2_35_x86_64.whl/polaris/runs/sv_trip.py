# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import multiprocessing

import numpy as np
from polaris.runs.polaris_inputs import PolarisInputs
from polaris.utils.logging_utils import function_logging


@function_logging("    Exporting SV Trips")
def export_sv_trip(inputs: PolarisInputs, output_dir):
    from SVTrip.svtrip import SVTrip

    svtrip = SVTrip()
    svtrip.parameters.load_default()

    # svtrip.parameters.execution.run_parallel = False
    svtrip.parameters.execution.n_workers = multiprocessing.cpu_count()
    svtrip.parameters.execution.jobs_per_thread = 15

    svtrip.parameters.output.export_folder = output_dir

    svtrip.read_polaris_trajectories(inputs.demand_db, inputs.supply_db)
    # svtrip.load_trips_from_csv(pth)
    np.random.seed(123)
    svtrip.set_logging_level(60)  # turn off any logging - it's WAY too verbose
    svtrip.run()
    svtrip.logger.critical("FINISHED")
