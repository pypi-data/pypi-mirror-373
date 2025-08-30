# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os.path import isfile
from shutil import copyfile, rmtree

from polaris.network.network import Network
from polaris.utils.database.spatialite_utils import connect_spatialite
from polaris.utils.testing.temp_model import test_file_cache, new_temp_folder


class TempNetwork:
    __empty_network_file = test_file_cache / "polaris_empty_network.sqlite"

    def __init__(self, network_to_copy=None):
        network_to_copy = network_to_copy or self.__create_empty_network_db()

        self.dir = new_temp_folder()

        self.network_db_file = self.dir / "polaris_network.sqlite"
        copyfile(network_to_copy, self.network_db_file)
        self.network = Network.from_file(self.network_db_file, False)
        self.network_methods = [f for f in dir(self.network) if not f.startswith("_")]
        self.conn = connect_spatialite(self.network_db_file)
        self.conn.commit()
        self.loaded = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __gc__(self):
        """This is called when the object is garbage collected."""
        self.close()

    # def __del__(self):
    #     self.close()

    def close(self, clear_issues=False):
        try:
            if not self.loaded:
                return
            self.loaded = False
            self.conn.close()
            self.network.close(clear_issues=clear_issues)
            self.dir.exists() and rmtree(self.dir)
        except Exception as e:
            logging.error(f"Couldn't delete dir {dir}, reason: {e}")

    def __getattr__(self, func):
        """Delegate all incoming method calls and attributes to the underlying network object."""
        if func not in self.network_methods:
            raise AttributeError
        return getattr(self.network, func)

    @staticmethod
    def __create_empty_network_db():
        if not isfile(TempNetwork.__empty_network_file):
            TempNetwork.__empty_network_file.parent.mkdir(exist_ok=True, parents=True)
            Network.create(TempNetwork.__empty_network_file, srid=26916, jumpstart=True)
        return TempNetwork.__empty_network_file
