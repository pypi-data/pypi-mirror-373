# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import os
from pathlib import Path
from typing import List


def list_scenario_files(base_dir: Path, scenario_name):
    scenario_files_root = base_dir / "scenario_files"
    scenario_sequence = scenario_inheritance_sequence(base_dir, scenario_name)
    # Let's list all files we need to copy, following the scenario inheritance chain
    # This way, files that are present in two scenarios will only show as the top one
    file_sources = []
    for scen in scenario_sequence:
        scenario_path = scenario_files_root / scen
        main_root = str(scenario_path)
        for root, _, files in os.walk(scenario_path):
            subfolder = root.replace(main_root, "")
            new_fldr = base_dir / subfolder.lstrip(r"\/")

            # Records lists of files and the place they should go to
            for file in files:
                file_sources.append((Path(root) / file, scen, new_fldr / file))
    return file_sources


# This function returns the sequence of scenarios from the base scenario to the bottom of the inheritance chain for a given scenario.
def scenario_inheritance_sequence(git_dir: Path, scenario_name: str):
    scenario_file = git_dir / "scenario_files" / "model_scenarios.json"
    with scenario_file.open() as file_:
        configs = json.load(file_)

    scenario_sequence = []
    while scenario_name != "base":
        assert scenario_name in configs, f"Scenario {scenario_name} not found in model_scenarios.json"
        scenario_sequence.append(scenario_name)
        scenario_name = configs[scenario_name]["based_on"]
    return scenario_sequence[::-1]  # Return in the order from base to the bottom of the inheritance chain


def list_supply(file_sources: List[tuple]):
    return [source for source, _, _ in file_sources if source.parts[-2] == "supply"]
