# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from os import PathLike

from polaris.network.ie.gmns.importer.import_links import import_gmns_links
from polaris.network.ie.gmns.importer.import_locations import import_gmns_locations
from polaris.network.ie.gmns.importer.import_nodes import import_gmns_nodes
from polaris.network.ie.gmns.importer.import_zones import import_gmns_zones
from polaris.network.utils.srid import get_srid
from polaris.utils.database.db_utils import commit_and_close


def import_from_gmns(gmns_folder: str, source_crs: str, path_to_file: PathLike):
    proj_crs = get_srid(path_to_file)

    with commit_and_close(path_to_file, spatial=True) as conn:
        import_gmns_nodes(gmns_folder, source_crs, proj_crs, conn)
        import_gmns_links(gmns_folder, source_crs, proj_crs, conn, path_to_file)
        import_gmns_zones(gmns_folder, source_crs, proj_crs, conn)
        import_gmns_locations(gmns_folder, source_crs, proj_crs, conn, path_to_file)
        logging.info("Finished GMNS import")
