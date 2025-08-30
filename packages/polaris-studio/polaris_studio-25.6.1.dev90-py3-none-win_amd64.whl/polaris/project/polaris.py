# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
import warnings
from copy import deepcopy
from os import PathLike
from pathlib import Path
from typing import List, Optional

from polaris.network.utils.srid import get_srid
from polaris.project.project_from_git import clone_and_build
from polaris.project.project_restorer import restore_from_csv
from polaris.runs.convergence.config.convergence_config import ConvergenceConfig, default_config_filename
from polaris.runs.convergence.convergence_runner import run_polaris_convergence
from polaris.runs.run_utils import get_latest_polaris_output
from polaris.utils.database.database_loader import GeoInfo
from polaris.utils.database.migration_manager import DatabaseType, MigrationManager
from polaris.utils.database.standard_database import StandardDatabase
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.optional_deps import check_dependency


class Polaris:
    """Python interface for all things Polaris

    Running polaris models with this interface is trivial

    ::
        model = Polaris().from_dir("D:/src/argonne/MODELS/bloomington")
        model.run()

    """

    def __init__(self, project_folder=None, config_file=None):
        self.__project_folder: Path = None
        self.__database_name = ""
        self.__network = None
        self.__demand = None
        self.__freight = None
        self.__analyze = None
        self.__router = None
        self.__router_lib = None
        self.run_config: ConvergenceConfig

        if config_file is not None and project_folder is None:
            raise ValueError("Must provide a project folder if providing a config_file")

        if project_folder is not None:
            self.open(project_folder, config_file)

    @classmethod
    def add_license(cls, license_file: PathLike):
        """Copies the license file to a place where the Polaris binary can find it

        :param license_file: Path to the license file

        ::

            from polaris import Polaris
            Polaris.add_license("path/to/license.txt")
        """
        from shutil import copy

        if not Path(license_file).exists():
            raise FileNotFoundError(f"License file not found: {license_file}")

        bin_folder = Path(__file__).parent.parent / "bin"
        copy(license_file, bin_folder)

    @classmethod
    def from_dir(cls, project_folder, config_file=None):
        return Polaris(project_folder, config_file)

    @classmethod
    def from_config_file(cls, config_file):
        config_file = Path(config_file)
        if not config_file.is_absolute():
            raise ValueError(f"Config file must be absolute: {config_file}")
        return Polaris(config_file.parent, config_file)

    @classmethod
    def build_from_git(
        cls,
        model_dir,
        city,
        db_name=None,
        overwrite=False,
        inplace=False,
        branch="main",
        git_dir=None,
        scenario_name=None,
    ):
        """Clones a polaris project from git and builds it into a runnable model

        ::

            from polaris import Polaris
            Polaris.from_dir(Polaris.build_from_git("e:/models/from_git", "atlanta"))
        """
        return cls(clone_and_build(model_dir, city, db_name, overwrite, inplace, branch, git_dir, scenario_name))

    @classmethod
    def restore(cls, data_dir, city=None, dbtype=None, upgrade=False, overwrite=False, scenario_name=None):
        """Builds a polaris project from directory into a runnable model

        ::

            from polaris import Polaris
            Polaris.restore("e:/models/from_git/Atlanta", "Atlanta")
        """
        polaris_logging(data_dir / "log" / "polaris-studio.log")
        restore_from_csv(data_dir, city, dbtype, upgrade, overwrite, scenario_name)
        return cls(data_dir)

    @property
    def is_open(self) -> bool:
        if self.__project_folder is None:
            return False
        return self.__project_folder.exists()

    def open(self, model_path: PathLike, config_file: Optional[str] = None) -> None:
        """Opens a Polaris model in memory.  When  a config file is provided, the model tries to load it

        :param model_path: Complete path for the folder containing the Polaris model.
        :param config_file: `Optional`, Name of the convergence control yaml we want to work with. Defaults to *convergence_control.yaml*

        ::

            from polaris import Polaris

            model = Polaris()
            model.open('path/to/model', 'convergence_control_modified.yaml')
        """
        self.__project_folder = Path(model_path).resolve()
        self._load_config(self._handle_config_filename(config_file))

        polaris_logging(self.__project_folder / "log" / "polaris-studio.log")

    def _handle_config_filename(self, config_file):
        if config_file is None:
            return (self.__project_folder / default_config_filename).resolve()
        config_file = Path(config_file)
        if config_file.is_absolute():
            return config_file
        return (self.__project_folder / config_file).resolve()

    @property
    def model_path(self) -> Path:
        """Path to the loaded project"""
        return Path(self.__project_folder)

    @property
    def supply_file(self) -> Path:
        """Path to the supply file in project"""
        return Path(self.__project_folder) / f"{self.__database_name}-Supply.sqlite"

    @property
    def demand_file(self) -> Path:
        """Path to the demand file in project"""
        return self.run_config.data_dir / f"{self.__database_name}-Demand.sqlite"

    @property
    def freight_file(self) -> Path:
        """Path to the freight file in project"""
        return self.run_config.data_dir / f"{self.__database_name}-Freight.sqlite"

    @property
    def result_file(self) -> Path:
        """Path to the result sqlite file in project"""
        return self.run_config.data_dir / f"{self.__database_name}-Result.sqlite"

    @property
    def result_h5_file(self) -> Path:
        """Path to the result h5 file in project"""
        return self.run_config.data_dir / f"{self.__database_name}-Result.h5"

    @property
    def network(self):
        for dep in ["geopandas", "aequilibrae", "networkx"]:
            check_dependency(dep, raise_error=True)
        from polaris.network.network import Network

        self.__network = self.__network or Network.from_file(self.supply_file)
        return self.__network

    @property
    def demand(self):
        from polaris.demand.demand import Demand

        self.__demand = self.__demand or Demand.from_file(self.demand_file)
        return self.__demand

    @property
    def freight(self):
        from polaris.freight.freight import Freight

        self.__freight = self.__freight or Freight.from_file(self.freight_file)
        return self.__freight

    @property
    def latest_output_dir(self) -> Path:
        return get_latest_polaris_output(self.__project_folder, self.__database_name)

    @property
    def router(self):
        from polaris.runs.router import BatchRouter

        if self.__router is None:
            self.__router = BatchRouter(self.run_config, self.supply_file, self.__router_lib)
        else:
            warnings.warn("Using router cached in memory")
        return self.__router

    def set_router_lib(self, router_lib):
        if self.__router_lib == router_lib:
            return
        self.__router_lib = Path(router_lib)
        self.__router = None

    @property
    def skims(self):
        from polaris.skims.skims import Skims

        hwy_name = self.run_config.highway_skim_file_name
        pt_name = self.run_config.transit_skim_file_name
        iter_dir = self.run_config.data_dir
        hwy = iter_dir if os.path.exists(iter_dir / hwy_name) else self.model_path
        pt = iter_dir if os.path.exists(iter_dir / pt_name) else self.model_path
        return Skims(hwy / hwy_name, pt / pt_name)

    def upgrade(self, max_migration: Optional[str] = None, force_migrations: Optional[List[str]] = None):
        """Upgrade the underlying databases to the latest / greatest schema version.

        :param max_migration: a string (date) defining the latest migration id that should be applied. Useful if
                              working with an older version of the POLARIS executable which isn't compatible with
                              the latest schema.

        ::
         model.upgrade("202402")  # only apply upgrades (migrations) from before February 2024.
        """

        def foo(file, dbtype, redo_triggers):
            MigrationManager.upgrade(file, dbtype, redo_triggers, max_migration, force_migrations)

        # We have some extra protection for non-existent freight databases as they are just being introduced.
        # And we make sure to create it before upgrading the demand and supply databases as we need to move data from
        # them to this newly created db
        if not self.freight_file.exists():
            geo_info = GeoInfo.from_fixed(get_srid(self.supply_file))
            StandardDatabase.for_type(DatabaseType.Freight).create_db(self.freight_file, geo_info=geo_info)

        foo(self.freight_file, DatabaseType.Freight, False)
        foo(self.demand_file, DatabaseType.Demand, False)
        foo(self.supply_file, DatabaseType.Supply, True)

    def run(self, **kwargs) -> None:
        # Move keywords args that the ConvergenceConfig class knows how to handle into a temp config for this run
        config = deepcopy(self.run_config)
        for k in [k for k in kwargs.keys() if k in config.__dict__]:
            config.__setattr__(k, kwargs[k])
            del kwargs[k]

        # all remaining keyword args passed directly to the run method
        run_polaris_convergence(config, **kwargs)

    def close(self):
        """Eliminates all data from memory

        ::
         model.close()
        """
        del self.__project_folder
        del self.__router
        self.__database_name = ""
        self.__close_all()

    def __close_all(self):
        self.__database_name = ""
        self.__router = None

    def _load_config(self, config_file: PathLike) -> None:
        """
        :param config_file: Name of the YAML/JSON file with the full model run configuration

        ::

            model._load_config('my_config.json')
        """
        config_file = Path(config_file)

        if not config_file.is_absolute():
            raise ValueError(f"config_file must be an absolute path, got: {config_file}")

        if not config_file.exists():
            raise FileNotFoundError(f"{config_file} not found")

        self.run_config = ConvergenceConfig.from_file(config_file)
        self.__database_name = self.run_config.db_name
