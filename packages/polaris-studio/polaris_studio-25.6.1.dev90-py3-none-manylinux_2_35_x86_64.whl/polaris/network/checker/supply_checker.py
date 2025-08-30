# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from pathlib import Path
from typing import List, Any, Optional

from polaris.network.checker.checks.connection_table import CheckConnectionTable
from polaris.network.checker.checks.connectivity_auto import connectivity_auto
from polaris.utils.database.standard_database import DatabaseType
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.model_checker import ModelChecker
from polaris.utils.signals import SIGNAL


class SupplyChecker(ModelChecker):
    """Network checker

    ::

        # We open the network
        from polaris.network.network import Network
        n = Network()
        n.open(source)

        # We get the checker for this network
        checker = n.checker

        # We can run the critical checks (those that would result in model crashing)
        checker.critical()

        # The auto network connectivity
        checker.connectivity_auto()

        # The connections table
        checker.connections_table()

    """

    checking = SIGNAL(object)

    def __init__(self, database_path: os.PathLike):
        ModelChecker.__init__(self, DatabaseType.Supply, Path(__file__).parent.absolute(), database_path)

        self._path_to_file = database_path
        self.__networks: Optional[Any] = None

        self.checks_completed = 0
        self.errors: List[Any] = []
        self._network_file = database_path
        self._test_list.extend(["connectivity_auto", "connections_table"])
        polaris_logging()

    def _other_critical_tests(self):
        self.connectivity_auto()

    def connectivity_auto(self) -> None:
        """Checks auto network connectivity

        It computes paths between nodes in the network or between every single link/direction combination
        in the network
        """

        errors = connectivity_auto(self._path_to_file)
        if errors:
            self.errors.append(errors)
            logging.warning("There are locations in the auto network that are not fully connected")

    def connections_table(self, basic=True):
        """Includes
        * search for pockets that are not used in the connection table
        * search for pockets missing from the pockets table
        * search for lanes not connected to any other link at an intersection
        """

        checker = CheckConnectionTable(self._path_to_file)

        if basic:
            checker.lane_connection(False)
        else:
            checker.full_check()
        errors = checker.errors

        for key, val in errors.items():
            logging.error(key)
            logging.error(val)
