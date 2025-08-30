# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import shutil
import subprocess
from datetime import datetime, timezone
from os.path import exists
from pathlib import Path

from polaris.network.create.triggers import delete_triggers, create_triggers
from polaris.network.utils.srid import get_srid
from polaris.scenario_management.assemble_model_files import assemble_scenario_files
from polaris.runs.scenario_file import get_scenario_value
from polaris.utils.database.database_loader import load_database_from_csvs, GeoInfo
from polaris.utils.database.db_utils import commit_and_close, write_about_model_value
from polaris.utils.database.migration_manager import MigrationManager
from polaris.utils.database.spatialite_utils import get_spatialite_version
from polaris.utils.database.standard_database import StandardDatabase, DatabaseType
from polaris.utils.dir_utils import mkdir_p
from polaris.utils.signals import SIGNAL


def restore_project_from_git(target_dir, git_dir, project_name, overwrite, scenario_name=None):
    target_dir, git_dir = Path(target_dir), Path(git_dir)
    mkdir_p(target_dir)

    if target_dir != git_dir:
        if overwrite:
            shutil.rmtree(target_dir)
        shutil.copytree(git_dir, target_dir, ignore=_ignore_files, dirs_exist_ok=True)

    restore_from_csv(target_dir, city=project_name, overwrite=overwrite, scenario_name=scenario_name)


def restore_from_csv(data_dir, city=None, dbtype=None, upgrade=False, overwrite=False, scenario_name=None):
    data_dir = Path(data_dir)

    if scenario_name:
        assemble_scenario_files(data_dir, scenario_name, full_warnings=True)

    city = city if city is not None else get_scenario_value(data_dir / "scenario_abm.json", "database_name")

    signal = SIGNAL(object)
    dbs = ["supply", "demand", "freight"] if dbtype is None else [dbtype]
    supply_file = data_dir / f"{city}-Supply.sqlite"
    for db in [DatabaseType.from_str(s) for s in dbs]:
        csv_dir = data_dir / str(db).lower()
        if db == DatabaseType.Freight and not csv_dir.exists():
            continue  # Skip freight if no csv directory exists

        db_file = data_dir / f"{city}-{db}.sqlite"
        if overwrite and db_file.exists():
            db_file.unlink()

        geo_i = GeoInfo.from_fixed(get_srid(supply_file)) if db == DatabaseType.Freight else None
        create_db_from_csv(db_file, csv_dir, db, signal, overwrite, geo_info=geo_i)

        if upgrade:
            MigrationManager.upgrade(db_file, db, False)

    if scenario_name:
        from polaris.scenario_management.building_procedures import run_required_rebuilds

        scenario_file = data_dir / "scenario_files" / "model_scenarios.json"
        with scenario_file.open() as file_:
            run_required_rebuilds(Path(data_dir), supply_file, json.load(file_)[scenario_name], scenario_name)


def _ignore_files(directory, contents):
    return contents if ".git" in directory else []


def create_db_from_csv(db_name, csv_dir, db_type, signal=None, overwrite=False, jumpstart=True, geo_info=None):
    if exists(db_name) and not overwrite:
        raise RuntimeError(f"DB [{db_name}] already exists and overwrite = False")

    geo_info = geo_info or GeoInfo.from_folder(csv_dir)
    db = StandardDatabase.for_type(db_type)
    db.create_db(db_name, geo_info, jumpstart=jumpstart)

    with commit_and_close(db_name, spatial=True) as conn:
        delete_triggers(db, conn)
        load_database_from_csvs(csv_dir, conn, db.default_values_directory, signal)

    MigrationManager.upgrade(db_name, db_type, redo_triggers=False)
    with commit_and_close(db_name, spatial=True) as conn:
        create_triggers(db, conn)

        write_about_model_value(conn, "Build time", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ"))
        write_about_model_value(conn, "Files source", str(csv_dir))
        write_about_model_value(conn, "spatialite_version", get_spatialite_version(conn))
        try:
            git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(Path(csv_dir).parent))
        except Exception:
            git_sha = "not found"
        finally:
            write_about_model_value(conn, "Git SHA", git_sha)
