# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from os import PathLike

from polaris.network.ie.gmns.exporter.export_links import export_links_to_gmns
from polaris.network.ie.gmns.exporter.export_locations import export_locations_to_gmns
from polaris.network.ie.gmns.exporter.export_movements import export_connection_to_gmns
from polaris.network.ie.gmns.exporter.export_nodes import export_nodes_to_gmns
from polaris.network.ie.gmns.exporter.export_pockets import export_pockets_to_gmns
from polaris.network.ie.gmns.exporter.export_zones import export_zones_to_gmns
from polaris.network.ie.gmns.exporter.signal_control import export_sig_ctrl_to_gmns
from polaris.utils.optional_deps import check_dependency


def export_to_gmns(gmns_folder: str, crs: str, conn, path_to_file: PathLike):
    check_dependency("pyproj")

    functions = [
        export_links_to_gmns,
        export_nodes_to_gmns,
        export_zones_to_gmns,
        export_connection_to_gmns,
        export_pockets_to_gmns,
        export_sig_ctrl_to_gmns,
        export_locations_to_gmns,
    ]
    for func in functions:
        func(gmns_folder, crs, conn, path_to_file)
