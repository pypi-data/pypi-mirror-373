# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from typing import Dict, Optional

import pandas as pd

from polaris.demand.checker.demand_checker import DemandChecker
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.database_loader import GeoInfo
from polaris.utils.database.db_utils import commit_and_close, read_and_close


class Demand:
    """Polaris Demand Class"""

    def __init__(self, demand_file):
        """Instantiates the network"""
        if not os.path.isfile(demand_file):
            raise FileNotFoundError
        self.path_to_file = demand_file
        self.modes: Optional[Dict[int, str]] = None

    @staticmethod
    def from_file(demand_file: os.PathLike) -> "Demand":
        return Demand(demand_file)

    def connect(self):
        return commit_and_close(self.path_to_file)

    @staticmethod
    def create(demand_file: str) -> "Demand":
        """Creates new empty demand file. Fails if file exists
        Args:
            *demand_file* (:obj:`str`): Full path to the demand file to be created.
        """
        from polaris.utils.database.standard_database import StandardDatabase, DatabaseType

        if os.path.isfile(demand_file):
            raise FileExistsError

        geo_info = GeoInfo(False, pd.DataFrame([]), [], None)
        StandardDatabase.for_type(DatabaseType.Demand).create_db(demand_file, geo_info, add_defaults=True)

        return Demand(demand_file)

    def upgrade(self) -> None:
        """Updates the network to the latest version available"""
        from polaris.utils.database.migration_manager import MigrationManager
        from polaris.utils.database.standard_database import DatabaseType

        MigrationManager.upgrade(self.path_to_file, DatabaseType.Demand, redo_triggers=False)

    @property
    def tables(self) -> DataTableAccess:
        if not self.__checks_valid():
            raise Exception("Not a valid network")
        return DataTableAccess(self.path_to_file)

    @property
    def checker(self) -> DemandChecker:
        return DemandChecker(self.path_to_file)

    @property
    def mode_lookup(self):
        self.modes = self.modes or Demand.load_modes(self.path_to_file)
        return self.modes

    @staticmethod
    def load_modes(path_to_file):
        with read_and_close(path_to_file) as conn:
            return pd.read_sql("SELECT * FROM mode;", conn).set_index("mode_id").mode_description.to_dict()

    def __checks_valid(self) -> bool:
        if not os.path.isfile(self.path_to_file):
            logging.error("You don't have a valid project open. Fix that and try again")
            return False
        return True
