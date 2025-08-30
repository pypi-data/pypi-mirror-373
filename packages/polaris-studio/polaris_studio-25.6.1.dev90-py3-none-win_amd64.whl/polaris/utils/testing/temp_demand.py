# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
import uuid
from os.path import join, isfile
from shutil import copyfile, rmtree
from tempfile import gettempdir

from polaris.demand.demand import Demand


class TempDemand:
    __empty_demand_file = join(gettempdir(), "polaris_empty_demand.sqlite")

    def __init__(self, from_demand_path=None):
        from_demand_path = from_demand_path or self.__create_empty_db()

        self.dir = join(gettempdir(), f"polaris_{uuid.uuid4().hex}")
        os.mkdir(self.dir)
        self.demand_db_file = join(self.dir, "polaris_demand.sqlite")
        copyfile(from_demand_path, self.demand_db_file)
        self.demand = Demand.from_file(self.demand_db_file)
        self.demand_methods = [f for f in dir(self.demand) if not f.startswith("_")]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self, clear_issues=False):
        self.demand.close(clear_issues=clear_issues)
        try:
            rmtree(self.dir)
        except Exception as e:
            print(e.args)  # Oh well, we tried

    def __getattr__(self, func):
        """Delegate all incoming method calls and attributes to the underlying demand object."""
        if func not in self.demand_methods:
            raise AttributeError
        return getattr(self.demand, func)

    @staticmethod
    def __create_empty_db():
        if not isfile(TempDemand.__empty_demand_file):
            Demand.create(TempDemand.__empty_demand_file)
        return TempDemand.__empty_demand_file
