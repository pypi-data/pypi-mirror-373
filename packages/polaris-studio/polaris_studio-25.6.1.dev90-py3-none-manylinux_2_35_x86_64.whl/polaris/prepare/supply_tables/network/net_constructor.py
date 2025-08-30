# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import warnings
from os.path import join
from pathlib import Path
from tempfile import gettempdir
from typing import Optional
from uuid import uuid4

import geopandas as gpd
import partridge as ptg
import yaml
from aequilibrae import Parameters
from aequilibrae.project import Project

from polaris.prepare.supply_tables.network.aeq_to_polaris import import_network_from_aequilibrae
from polaris.prepare.supply_tables.network.download_gtfs_feeds import download_GTFS_feeds
from polaris.prepare.supply_tables.network.parameter_imputation import impute_missing_attributes
from polaris.prepare.supply_tables.network.pedestrian_links import get_pedestrian_used_links
from polaris.prepare.supply_tables.network.traffic_links import get_car_used_links
from polaris.prepare.supply_tables.network.transit_links import get_transit_used_links
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.user_configs import UserConfig


class NetworkConstructor:
    def __init__(
        self,
        polaris_network_path: Path,
        simplification_parameters={  # noqa: B006
            "simplify": True,
            "keep_transit_links": True,
            "accessibility_level": "zone",
            "maximum_network_capacity": False,
        },
        imputation_parameters={  # noqa: B006
            "algorithm": "knn",
            "max_iter": 10,
        },
        state_counties: Optional[gpd.GeoDataFrame] = None,
    ) -> None:
        """
        Args:
            polaris_network_path (Path): Path to a Polaris Network object where the network will be saved to
            imputation_parameters (dict): dictionary with imputation parameters, which are
                algorithm (str): imputation algorithm to be used between 'knn' or 'iterative' imputation. Defaults to 'knn'
                max_iter (int): if algorithm='iterative', sets the number of maximum iterations. Defaults to 10
                save_changes (bool): if True, writes imputed attributes into database. Defaults to False.
                fields_to_impute (tuple(str)): Fields for which do data imputation ("speed_ab", "speed_ba", "lanes_ab", "lanes_ba")
        """
        from polaris.network.network import Network

        imputation_parameters["save_changes"] = True
        imputation_parameters["fields_to_impute"] = ("speed_ab", "speed_ba", "lanes_ab", "lanes_ba")
        self.state_counties = gpd.GeoDataFrame([]) if state_counties is None else state_counties
        self.polaris_network = Network.from_file(polaris_network_path, run_consistency=False)
        self.aeq_project = Project()

        # Path to correct AequilibraE importer parameters

        self.simplification_parameters = simplification_parameters
        self.imputation_parameters = imputation_parameters

    def download_gtfs(self, mobility_database_api_key: Optional[str] = None) -> int:

        key = mobility_database_api_key or UserConfig().mobility_database_api
        if not key:
            raise ValueError("No Census API found. Please obtain one at https://mobilitydatabase.org/sign-in")

        zns = DataTableAccess(self.polaris_network.path_to_file).get("Zone").to_crs("EPSG:4326")
        pth = Path(self.polaris_network.path_to_file).parent
        feed_number = download_GTFS_feeds(zns.union_all(), pth, mobility_database_api_key)
        logging.info(f"Downloaded {feed_number} GTFS feeds")
        return feed_number

    def build_network(self):
        self._import_network_from_osm()
        self._impute_missing_attributes()
        self._simplify_network()
        import_network_from_aequilibrae(self.aeq_project, self.polaris_network)
        warnings.warn("Speed units are those found in the OSM network. Please transform them to m/s.")

    def import_transit(self, map_match=False, date=""):
        tgt_pth = Path(self.polaris_network.path_to_file).parent / "supply" / "gtfs"
        gtfs_feeds = list(tgt_pth.glob("*.zip"))
        if len(gtfs_feeds) == 0:
            logging.warning("No GTFS feeds downloaded yet. Call the download_gtfs method first")
            return

        transit = self.polaris_network.transit
        for feed in gtfs_feeds:
            # Grab the agency name
            agency_df = ptg.load_feed(str(feed)).agency
            agency = feed.stem
            if agency_df.shape[0] > 0:
                agency = agency_df.agency_name.values[0] if len(agency_df.agency_name.values[0]) > 0 else agency

            # Get the date we want to import the feed for
            if date == "":
                busy_date, _ = ptg.read_busiest_date(str(feed))
                date = f"{busy_date.year}-{str(busy_date.month).zfill(2)}-{str(busy_date.day).zfill(2)}"

            pt_feed = transit.new_gtfs(agency=agency, file_path=feed)
            pt_feed.set_allow_map_match(map_match)
            pt_feed.load_date(date)
            pt_feed.set_do_raw_shapes(True)
            pt_feed.doWork()

        transit.fix_connections_table()

    def _import_network_from_osm(self):
        self.aeq_project.new(join(gettempdir(), uuid4().hex))

        # TODO: Get rid of this patch when a new version of AequilibraE is available > 1.1.1
        # This PR fixes it: https://github.com/AequilibraE/aequilibrae/pull/565
        with open(Path(__file__).parent / "link_specs.yml", "r") as yml:
            pars = yaml.load(yml, Loader=yaml.SafeLoader)
        par = Parameters(self.aeq_project)
        par.parameters["network"]["osm"] = pars["osm"]
        par.parameters["osm"]["overpass_endpoint"] = UserConfig().osm_url
        par.write_back()

        zns = DataTableAccess(self.polaris_network.path_to_file).get("Zone").to_crs("EPSG:4326")
        self.aeq_project.network.create_from_osm(model_area=zns.union_all().convex_hull)

    def _impute_missing_attributes(self) -> None:
        """Imputes missing attributes on a network based on attributes similarity and distance"""

        impute_missing_attributes(
            self.aeq_project, self.imputation_parameters, Path(self.polaris_network.path_to_file).parent
        )

    def _simplify_network(self):
        """Simplifies the network by keeping only used links
        Args:
            car_links (tuple): a list of link ids to keep for cars
            transit_links (tuple): a list of link ids to keep for transit
            walk_links (tuple): a list of link ids to keep for walk
        """
        if not self.simplification_parameters.get("simplify", False):
            return

        # list_DELETE = ["centroid_connector", "steps", "razed", "planned"]
        max_capacity = self.simplification_parameters.get("maximum_network_capacity", False)
        access_level = self.simplification_parameters["accessibility_level"]

        walk_links = get_pedestrian_used_links(
            self.polaris_network, self.aeq_project, access_level, self.state_counties
        )
        car_links = get_car_used_links(
            self.polaris_network, self.aeq_project, access_level, self.state_counties, max_capacity
        )

        transit_links = self._get_transit_used_links()

        logging.info("Simplifying network")
        df_links = self.aeq_project.network.links.data[["link_id", "modes"]]

        keep_links = list(car_links) + list(transit_links) + list(walk_links)
        all_links = df_links.link_id.values
        links_to_remove = list(set(all_links) - set(keep_links))
        if links_to_remove:
            with self.aeq_project.db_connection as conn:
                conn.executemany("DELETE FROM links WHERE link_id=?;", zip(links_to_remove))

    def _get_transit_used_links(self):
        if not self.simplification_parameters.get("keep_transit_links", False):
            return []

        tgt_pth = Path(self.polaris_network.path_to_file).parent / "supply" / "gtfs"
        if len(list(tgt_pth.glob("*.zip"))) == 0:
            return []
        return get_transit_used_links(self.polaris_network, self.aeq_project)
