# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import logging
from pathlib import Path

from polaris.scenario_management.list_scenario_files import list_scenario_files, list_supply
from polaris.utils.testing.repository_structure import check_supply_sources, check_file_places


def check_all_scenarios(model_path: Path):
    base_dir = Path(model_path)
    scenario_file = base_dir / "scenario_files" / "model_scenarios.json"

    if not scenario_file.exists():
        logging.info("model_scenarios.json file not found in scenario_files directory")
        return

    with scenario_file.open() as file_:
        configs = json.load(file_)

    for scenario_name in configs.keys():
        logging.info(f"Checking scenario {scenario_name}")

        check_scenario(base_dir, scenario_name)
        logging.info("-----------------------------------\n")


def check_scenario(base_dir, scenario_name):
    file_sources = list_scenario_files(base_dir, scenario_name)
    assert (base_dir / "scenario_files" / scenario_name).exists(), f"Scenario folder {scenario_name} does not exist"
    supply_sources = list_supply(file_sources)
    check_supply_sources(base_dir, supply_sources)
    check_file_places(base_dir, file_sources, scenario_name, False)

    # Checks that the specified custom scripts exist
    scenario_file = base_dir / "scenario_files" / "model_scenarios.json"
    with scenario_file.open() as file_:
        scenario_configs = json.load(file_)[scenario_name]

    custom_scripts = [x.lower() for x in scenario_configs.get("custom_scripts", [])]
    scenario_files = base_dir / "scenario_files" / scenario_name
    for script in custom_scripts:
        assert (scenario_files / script).exists(), f"Script {script} does not exist in scenario_files/{scenario_name}"
