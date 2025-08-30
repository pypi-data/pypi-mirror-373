# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path


def check_supply_sources(base_dir: Path, scenario_sources: list, scenario_name: str = "base"):
    # Let's collect the files from the base and start the analysis
    scenario_tables = [x.stem for x in scenario_sources]
    base_supply_files = (base_dir / "supply").glob("*.*")
    files_from_base = [x for x in base_supply_files if x.is_file() and x.stem not in scenario_tables]

    scenario_sources.extend(files_from_base)

    # We need to have exactly two of each file name, one of them being the schema
    source_files = {}  # type: dict[str, list[Path]]
    table_sources = {}
    extensions = [".schema", ".csv", ".parquet"]

    for x in scenario_sources:
        if x.stem != "srids" and x.suffix in extensions:
            source_files[x.stem.lower()] = source_files.get(x.stem.lower(), []) + [x]
        if x.suffix.lower() == ".schema":
            table_sources[x.stem.lower()] = x.parent

    check_number_of_files = all(len(items) == 2 for items in source_files.values())
    if not check_number_of_files:
        for k, v in source_files.items():
            if len(v) != 2:
                print(k, v)
    assert check_number_of_files, "There should be two of each, check above!"

    # Asserts we have exactly two files for each table, one of them being the schema
    for f1, f2 in source_files.values():
        sfx1 = f1.suffix.lower()
        sfx2 = f2.suffix.lower()
        msg = f"ERROR on scenario {scenario_name}"
        assert all(x in extensions for x in (sfx1, sfx2)), f"{msg}. Unexpected file type for {f1.stem}"
        assert ".schema" in [sfx1, sfx2], f"{msg}. Schema file not found for {f1.stem}"
        assert f1.parent == f2.parent, f"{msg}. Files {f1.stem} and {f2.stem} are not coming from the same scenario"

    # Checks sets of tables that MUST come from the same place if they are present
    table_sets = [
        ["link", "node"],
        [
            "transit_links",
            "transit_agencies",
            "transit_pattern_links",
            "transit_patterns",
            "transit_routes",
            "transit_stops",
        ],
        [
            "connection",
            "signal",
            "phasing",
            "timing",
            "phasing_nested_records",
            "timing_nested_records",
            "signal_nested_records",
            "sign",
        ],
        ["turn_overrides", "link"],
    ]

    for table_set in table_sets:
        table_set = [table_name.lower() for table_name in table_set if table_name in table_sources]
        msg = f"ERROR on scenario {scenario_name}. Tables [{', '.join(table_set)}] MUST come from the same source"
        assert len({table_sources.get(table_name) for table_name in table_set}) <= 1, msg


def check_file_places(base_dir, file_sources, scenario_name, full_warnings):
    from rapidfuzz import fuzz

    scenario_files_root = base_dir / "scenario_files"
    # Let's list the base files that we will compare against to try to detect files that might be in the wrong place
    exclude = [".git", str(scenario_files_root), str(base_dir / "supply")]
    base_files = [x for x in base_dir.glob("**/*") if x.is_file() and not any(excl in str(x) for excl in exclude)]
    similar_matches = []
    very_similar_matches = []
    exact_matches = []
    wrong_places = []
    for source, scen, _ in file_sources:
        subfolder = str(source).replace(str(scenario_files_root / scen), "")
        # Analysis to see if there is anything weird / wrong places / etc.
        # For each scenario file, we go through all files in the base directory to see if there
        # are any files that seem to have the wrong name (very similar names) or that seem to be in the wrong place
        for fl in base_files:
            simil1 = fuzz.ratio(source.name, fl.name)
            if 70 < simil1 < 90:
                # Roughly similar file names
                similar_matches.append((source.name, fl.name, subfolder))
            elif 90 < simil1 < 100:
                # Extremely similar file names - Not something we would expect
                very_similar_matches.append((source.name, fl.name, subfolder))
            elif simil1 == 100:
                new_fldr = str(source.parent)
                # Same file -> Same name
                for x in ["scenario_files", scenario_name]:
                    new_fldr = new_fldr.replace(f"{x}/", "").replace(rf"\{x}", "")
                if new_fldr != str(fl.parent):
                    # Would be placed in different folders, so it seems wrong
                    wrong_places.append((source.name, new_fldr, fl.parent, scen))
                else:
                    exact_matches.append(fl.name)
    if exact_matches:
        logging.info("Files found to be replaced in the correct folder. Copy NOT executed")
        logging.info("     " + ", ".join(exact_matches))
    if similar_matches and full_warnings:
        logging.info("VAGUELY similar files were found")
        for sm in similar_matches:
            logging.info(f"      {sm[0]} is vaguely similar to {sm[1]} in folder {sm[2]}")
    if very_similar_matches:
        logging.warning("VERY similar files were found")
        for sm in very_similar_matches:
            logging.warning(f"      {sm[0]} is very similar to {sm[1]} in folder {sm[2]}")
    if wrong_places:
        logging.critical("FILES APPARENTLY IN THE WRONG PLACE")
        for sm in wrong_places:
            msg = f"      {sm[0]} from scenario {sm[3]} appears to be in the wrong place. {sm[1]} instead of {sm[2]}."
            logging.critical(msg)
