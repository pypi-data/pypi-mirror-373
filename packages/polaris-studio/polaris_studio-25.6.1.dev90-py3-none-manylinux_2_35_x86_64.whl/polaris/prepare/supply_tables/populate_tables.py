# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import warnings
from typing import Optional

import geopandas as gpd

from polaris.network.utils.srid import get_table_srid
from polaris.prepare.supply_tables.ev_chargers.ev_charging import ev_chargers
from polaris.prepare.supply_tables.network.net_constructor import NetworkConstructor
from polaris.prepare.supply_tables.utils.state_county_candidates import get_state_counties, counties_for_model
from polaris.prepare.supply_tables.zones.popsyn import add_popsyn_regions
from polaris.prepare.supply_tables.zones.zoning import add_zoning
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import commit_and_close
from polaris.utils.user_configs import UserConfig


class Populator:
    def __init__(self, supply_path) -> None:
        self.supply_path = supply_path
        self._state_counties = gpd.GeoDataFrame()

    def add_zoning_system(
        self, model_area: gpd.GeoDataFrame, zone_level: str, census_api_key: Optional[str] = None, year: int = 2021
    ):
        """Create zoning system based on census subdivisions. Population data is extracted from The ACS 5 year. For
        mode details see https://github.com/datamade/census

        Args:
            model_area (GeoDataFrame): GeoDataFrame containing polygons with the model area
            zone_level (str): Census subdivision level to use for zoning -> tracts or block_groups
            year (int): Year of the population data. Defaults to 2021
            census_api_key (`Optional`: str): API key for the census. If not provided we will attempt to retrieve from
            the user configuration file.
        """

        assert zone_level in ["tracts", "block_groups"]

        key = census_api_key or UserConfig().census_api
        if not key:
            raise ValueError("No Census API found. Please obtain one at https://api.census.gov/data/key_signup.html")
        warnings.warn(key)
        self._state_counties = get_state_counties(model_area, year=year)
        add_zoning(model_area, self.state_counties(year), zone_level, self.supply_path, year, key)

    def add_popsyn_regions(self, model_area: gpd.GeoDataFrame, census_type: str, year: int = 2021, replace=False):
        """Populate the Population Synthesis Region geography table based on census subdivisions.

        Args:
            model_area (GeoDataFrame): GeoDataFrame containing polygons with the model area
            census_type (str): Census subdivision level to import -> tracts or block_groups
            year (int): Year of the population data. Defaults to 2021
        """

        assert census_type in ["tracts", "block_groups"]

        self._state_counties = get_state_counties(model_area, year=year)
        add_popsyn_regions(model_area, self.state_counties(year), census_type, self.supply_path, year, replace)

    def add_counties(self, year=2022):
        logging.warning(
            f"You have imported counties for {year}. Make sure the data is consistent with the data used for the freight model component"
        )

        model_area = DataTableAccess(self.supply_path).get("Zone")

        counties = counties_for_model(model_area, year).to_crs(model_area.crs)
        counties["county"] = counties["GEOID"].astype(int)

        sql = (
            'Insert into Counties("county", "x", "y", "name", "statefp", "state", "geo")'
            + "VALUES(?, ?, ?, ?, ?, ?, CastToMulti(GeomFromText(?, ?)))"
        )

        with commit_and_close(self.supply_path, spatial=True) as conn:
            assert sum(conn.execute("SELECT count(*) from Counties").fetchone()) == 0

            srid = get_table_srid(conn, "zone")
            counties = counties.to_crs(srid)
            counties = counties.assign(
                x=counties.geometry.centroid.x,
                y=counties.geometry.centroid.y,
                geo_wkt=counties.geometry.to_wkt(rounding_precision=6),
                srid=srid,
            )

            data = counties[["county", "x", "y", "name", "statefp", "state", "geo_wkt", "srid"]].to_records(index=False)
            conn.executemany(sql, data)

    def add_ev_chargers(self, nrel_api_key: Optional[str] = None, max_dist=100, clustering_attempts=5):
        """Adds EV Chargers

        Args:
            nrel_api_key (str): API key for the NREL API to retrieve location of EV chargers. If not provided it will be
            read from the user configuration file.
            max_dist (float):
            clustering_attempts (int):
        """
        key = nrel_api_key or UserConfig().nrel_api

        if not key:
            raise ValueError("No NREL API key provided. Please obtain one at https://developer.nrel.gov/signup/")

        assert max_dist > 0, "Minimum clustering must be non-negative. Use 0.1 if you must. That's in meters"

        model_area = DataTableAccess(self.supply_path).get("Zone")
        ev_chargers(model_area, self.supply_path, key, max_dist, clustering_attempts)

    def add_parking(
        self,
        facility_types: tuple = ("surface", "underground", "multi-storey", "rooftop"),
        sample_rate: float = 1.0,
    ):
        """Adds Parking facilities from data coming from OpenStreetMap

        Args:
           facility_types (str): Facility type according to OSM
        """
        from polaris.prepare.supply_tables.park.parking import add_parking

        add_parking(self.supply_path, facility_types, sample_rate)

    def add_locations(
        self,
        control_totals: gpd.GeoDataFrame,
        census_api_key: Optional[str] = None,
        residential_sample_rate=0.05,
        other_sample_rate=1.0,
    ):
        from polaris.prepare.supply_tables.locations.locations import add_locations

        key = census_api_key or UserConfig().census_api
        if not key:
            raise ValueError("No Census API found. Please obtain one at https://api.census.gov/data/key_signup.html")

        add_locations(
            supply_path=self.supply_path,
            state_counties=self.state_counties(),
            control_totals=control_totals,
            census_api_key=key,
            residential_sample_rate=residential_sample_rate,
            other_sample_rate=other_sample_rate,
        )

    def create_network(
        self,
        simplification_parameters={  # noqa: B006
            "simplify": True,
            "keep_transit_links": True,
            "accessibility_level": "zone",
            "maximum_network_capacity": False,
        },
        imputation_parameters={"algorithm": "knn", "max_iter": 10},  # noqa: B006
        year: int = 2021,
    ) -> NetworkConstructor:
        """ """
        if self._state_counties.empty:
            self._state_counties = get_state_counties(DataTableAccess(self.supply_path).get("Zone"), year)

        return NetworkConstructor(
            polaris_network_path=self.supply_path,
            simplification_parameters=simplification_parameters,
            imputation_parameters=imputation_parameters,
            state_counties=self._state_counties,
        )

    def state_counties(self, year: int = 2021):
        if self._state_counties.empty:
            model_area = DataTableAccess(self.supply_path).get("Zone")
            self._state_counties = get_state_counties(model_area, year=year)
        return self._state_counties
