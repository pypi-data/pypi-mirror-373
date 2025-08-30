# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
from pathlib import Path

from polaris.network.ie.gmns.export_gmns import export_to_gmns
from polaris.network.ie.gmns.import_gmns import import_from_gmns
from polaris.network.utils.network_dump_loader import LoadNetworkDump
from polaris.utils.database.database_dumper import dump_database_to_csv
from polaris.utils.database.db_utils import read_and_close


class ImportExport:
    """
    This class allows for importing and exporting to the GMNS format.
    """

    def __init__(self, supply_database_path: os.PathLike):
        self.supply_database = Path(supply_database_path)

    def dump(self, folder_name: str, tables=None, include_patterns=None, target_crs=None, extension="csv") -> None:
        """Creates a folder and dumps all tables in the database to CSV files

        Args:
            *folder_name* (:obj:`str`): Folder where the dump files are to be placed

            *tables* (:obj:`list`, `Optional`): List of tables to be dumped. If None, all tables are dumped. Defaults to None

            *include_patterns* (:obj:`list`, `Optional`): List of table name patterns to be dumped. If None, no patterns will be enforced. Defaults to None. Cannot be provided when providing a list of *tables* to dump

            *target_crs* (:obj:`int`, `Optional`): The desired CRS for the dumped files. If None, the original CRS is used. Defaults to None

            *extension* (:obj:`str`, `Optional`): The extension of the dumped files. Defaults to 'csv'. The preferred alternative is "parquet"
        """

        folder = Path(folder_name)
        folder = folder if folder.is_absolute() else (self.supply_database.parent / folder).resolve()
        # self.__run_consistency()
        with read_and_close(self.supply_database, spatial=True) as conn:
            dump_database_to_csv(
                conn,
                folder,
                table_list=tables,
                include_patterns=include_patterns,
                target_crs=target_crs,
                ext=extension,
            )

    def restore(self, folder_name: os.PathLike, jumpstart=False) -> None:
        """Reloads the network from a previous dump to csv

        Args:
            *folder_name* (:obj:`str`): Folder where the dump files are located
            *jumpstart* (:obj:`bool`): Copies base sql already initialized with spatialite base tables. It saves about
                                       a minute of runtime.
        """

        if not os.path.isdir(folder_name):
            raise FileNotFoundError
        network_loader = LoadNetworkDump(folder_name, jumpstart)
        network_loader.doWork()

    def from_gmns(self, gmns_folder: str, crs: str):
        """Imports the network data from the GMNS format

        Args:
            *gmns_folder* (:obj:`str`): Folder where the GMNS files are located
            *crs* (:obj:`str`): CRS of the exported dataset in readable format by PyProj (e.g. 'epsg:4326')"""
        import_from_gmns(gmns_folder, crs, self.supply_database)

    def to_gmns(self, gmns_folder: str, crs: str):
        """Exports the network data to the GMNS format

        Args:
            *gmns_folder* (:obj:`str`): Folder where the GMNS files are to be placed
            *crs* (:obj:`str`): CRS of the exported dataset in readable format by PyProj (e.g. 'epsg:4326')"""
        with read_and_close(self.supply_database, spatial=True) as conn:
            export_to_gmns(gmns_folder, crs, conn, self.supply_database)

    def __run_consistency(self):
        from polaris.network.consistency.consistency import Consistency

        Consistency(self.supply_database).enforce()
