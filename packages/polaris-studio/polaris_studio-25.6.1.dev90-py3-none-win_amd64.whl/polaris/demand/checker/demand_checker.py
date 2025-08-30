# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
from pathlib import Path

from polaris.utils.database.standard_database import DatabaseType
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.model_checker import ModelChecker
from polaris.utils.signals import SIGNAL


class DemandChecker(ModelChecker):
    """Demand checker

    ::

        # We open the network
        from polaris.demand import Demand
        n = Demand(demand_file_path)

        # We get the checker for this network
        checker = n.checker

        # We can run the critical checks (those that would result in model crashing)
        checker.critical()
    """

    checking = SIGNAL(object)

    def __init__(self, database_path: os.PathLike):
        ModelChecker.__init__(self, DatabaseType.Demand, Path(__file__).parent.absolute(), database_path)

        self._path_to_file = database_path
        polaris_logging()
