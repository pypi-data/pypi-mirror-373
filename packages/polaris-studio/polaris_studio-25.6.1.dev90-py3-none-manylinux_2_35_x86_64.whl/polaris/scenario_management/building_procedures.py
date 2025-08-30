# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from polaris.network.network import Network


def run_required_rebuilds(project_dir, network_file_name, scenario_configs, scenario_name):
    logging.info(
        f"Running required rebuilds for scenario: {scenario_name}",
    )
    network = Network.from_file(network_file_name)

    # Run all custom scripts
    custom_scripts = [x.lower() for x in scenario_configs.get("custom_scripts", [])]
    scenario_files = project_dir / "scenario_files" / scenario_name
    for script in custom_scripts:
        logging.info(f"Running custom script: {script}")
        custom_procedure = scenario_files / script
        spec = spec_from_file_location(Path(custom_procedure).stem, custom_procedure)
        loaded_module = module_from_spec(spec)
        spec.loader.exec_module(loaded_module)
        loaded_module.scenario_process(project_dir)

    consistency_procedures = [x.lower() for x in scenario_configs.get("run_on_build", [])]

    approved_rebuilds = ["active", "location_links", "location_parking", "intersections", "geoconsistency"]
    not_found = set(consistency_procedures) - set(approved_rebuilds)
    assert all(x in approved_rebuilds for x in consistency_procedures), f"Invalid consistency procedures: {not_found}"

    logging.info(f"Consistency procedures selected: {consistency_procedures}")
    if "active" in consistency_procedures:
        active = network.active
        active.__do_update_associations__ = "geoconsistency" not in consistency_procedures
        active.build()

    # Location Links if we didn't have them
    if "location_links" in consistency_procedures:
        network.tools.rebuild_location_links()

    # Location parking if we didn't have them
    if "location_parking" in consistency_procedures:
        network.tools.rebuild_location_parking()

    # Connections and intersection rebuilds if we need them
    if "intersections" in consistency_procedures:
        network.tools.rebuild_intersections(signals="osm", signs=[])

    # Full geo-consistency
    if "geoconsistency" in consistency_procedures:
        network.geo_consistency.update_all()
