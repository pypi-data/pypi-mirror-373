# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from os.path import join, isfile
from typing import List

import pandas as pd
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.db_utils import commit_and_close, has_table
from polaris.utils.database.standard_database import DatabaseType
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.signals import SIGNAL


class ModelChecker(WorkerThread):
    """Database Checker"""

    checking = SIGNAL(object)

    def __init__(self, database_type: DatabaseType, tests_folder: os.PathLike, database_path: os.PathLike):
        WorkerThread.__init__(self, None)

        self._path_to_file = database_path
        polaris_logging()

        self.checks_completed = 0
        self.errors: List[str] = []
        self._test_list = ["critical"]

        self.master_message_name = "Running checking suite"

        self.__database_type = database_type
        self.__test_folder = tests_folder

    def doWork(self):
        """Alias for execute"""
        self.execute()
        self.finish()

    def finish(self):
        """Kills the progress bar so others can be generated"""
        self.checking.emit(["finished_checking_procedure"])

    def execute(self):
        """Runs the complete network testing suite on the network file

        If runs critical analysis, connectivity tests, database structure analysis and
        other secondary tests that may indicate structure issues in the network.
        List of tests can be overloaded by *set_test_list*"""

        self._emit_master_start(len(self._test_list))
        for test in self._test_list:
            getattr(self, test)()

    def critical(self):
        """Runs set of tests for issues known to crash Polaris"""

        self._emit_start(1, "Critical tests")
        self.__binary_tests("crashing_queries.sql", "error")
        self._foreign_key_tests()
        self._other_critical_tests()
        self._emit_end("Critical tests")
        return self.errors

    def _other_critical_tests(self):
        pass

    def consistency_tests(self):
        """Basic consistency checks"""
        self._emit_start(1, "Basic consistency")
        self.__binary_tests("check_queries.sql", "warn")
        self._emit_end("Basic consistency")

    def set_test_list(self, test_list):
        """Set the list of tests that constitute a complete analysis"""
        self._test_list = test_list

    def __binary_tests(self, test_file: str, log_type: str) -> None:
        """Runs all tests built as simple SQL queries

        Due to its implementation, all these tests have a binary nature"""

        fn = join(self.__test_folder, test_file)
        if not isfile(fn):
            logging.warning("Test suite not available")
            raise NotImplementedError(fn)

        with open(fn, "r") as file:
            lines = file.readlines()
        lines = "".join(lines).split(";")

        with commit_and_close(self._path_to_file, commit=False) as conn:
            for sql in lines:
                data = [x[0] for x in conn.execute(sql).fetchall()]
                if not sum(data):
                    continue
                dt = ", ".join([str(x) for x in data])
                msg = sql.lstrip().split("\n")[0]
                m = msg.format(dt)
                self.errors.append(m)
                if log_type == "error":
                    logging.error(m)
                elif log_type == "warn":
                    logging.warning(m)
                else:
                    logging.info(m)

    def _foreign_key_tests(self):
        from polaris.utils.database.standard_database import StandardDatabase

        with commit_and_close(self._path_to_file) as conn:
            for tbl in StandardDatabase.for_type(self.__database_type).tables():
                if not has_table(conn, tbl):
                    logging.warning(f"Missing table {tbl}, skipping FK check")
                    continue
                df = pd.read_sql(f"PRAGMA foreign_key_check({tbl});", conn)
                if not df.empty:
                    m = f"Table {tbl} has {df.shape[0]} foreign key inconsistencies"
                    self.errors.append(m)
                    logging.error(m)

    def _log_warn(self, msg: str):
        self.errors.append(msg)
        logging.warning(msg)

    def _emit_start(self, total: int, running: str):
        self.checking.emit(["start", "secondary", total, running, self.master_message_name])

    def _emit_master_start(self, total: int):
        self.checking.emit(["start", "master", total, self.master_message_name])

    def _emit_end(self, running: str):
        self.checks_completed += 1
        self.checking.emit(["update", "secondary", self.checks_completed, running, self.master_message_name])
