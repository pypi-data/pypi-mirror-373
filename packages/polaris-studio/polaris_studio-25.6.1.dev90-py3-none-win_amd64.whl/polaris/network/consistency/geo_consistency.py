# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import sqlite3
from typing import Optional, List

import pandas as pd
from pandas.api.types import is_string_dtype

from polaris.network.starts_logging import logger
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import (
    read_and_close,
    commit_and_close,
    without_triggers,
)
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.signals import SIGNAL


class GeoConsistency(WorkerThread):
    """Geo-consistency enforcement/rebuilding

    Overall geo-consistency for the database should be automatically enforced
    when opening and closing the database in Python or QGIS, so the tools in
    this submodule are not expected to be relevant other than during database
    migrations or large scale changes where the automatic consistency enforcement
    might be too time consuming.

        ::

            from polaris.network.network import Network
            net = Network()
            net.open(path/to/network)

            # We get the submodule we want to work with in good polaris.network fashion
            geo_consistency = net.geo_consistency

            # We can update all geo consistency fields the package is capable of
            geo_consistency.update_all()

            # You can also choose to update only specific items
            geo_consistency.update_zone_association()
            geo_consistency.update_link_association()
            geo_consistency.update_active_network_association()
            geo_consistency.update_location_association()

    """

    parking_distance_from_location = 250
    geoconsistency = SIGNAL(object)

    def __init__(self, geotool, data_tables: DataTableAccess):
        WorkerThread.__init__(self, None)
        from polaris.network.tools.geo import Geo

        polaris_logging()

        self.geotool: Geo = geotool
        self.__data_storage = data_tables
        self.messages: List[str] = []

        self.__mt = "Geo-Consistency"
        self._network_path = geotool._network_file

    def doWork(self):
        """Alias for update_all"""
        self.update_all()

    def update_all(self):
        """Updates references to zones, links and walk_links to guarantee geo-consistency for all tables"""
        sig = ["start", "master", 9, self.__mt]
        self.geoconsistency.emit(sig)

        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_zone_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            self.__data_storage.refresh_cache()

            logging.info("Updating link and walk_link for Location Table")
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            self.__data_storage.refresh_cache()

            for tbl_nm in ["Location", "Parking"]:
                logging.info(f"Updating bike_link and walk_link for {tbl_nm} Table")
                self.__update_active_and_net_links_for_park_loc(tbl_nm, conn=conn, do_link=False)
                self.geoconsistency.emit(["update", "master", 1, self.__mt])

            self.__update_link_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            self.__data_storage.refresh_cache()

            self.__update_location_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            self.__data_storage.refresh_cache()

            self.__update_areatype_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])

            self.__update_county_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])

            self.__update_popsyn_region_association(conn=conn)
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
        self.finish()

    def update_location_association(self):
        """Ensures geo-consistent references to **Location** for all tables

        The field "location" is updated for tables 'ev_charging_stations'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])
        logging.info("Updating Location geo-association throughout the database")
        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_location_association(conn=conn)
        for message in self.messages:
            logging.warning(message)
        self.finish()

    def update_zone_association(self):
        """Ensures geo-consistent references to the **zone system** for all tables

        The field "zone" is updated for tables 'ev_charging_stations', 'Location', 'Parking', 'Node',
        'Transit_Stops'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])

        logging.info("Updating Zone geo-association throughout the database")
        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_zone_association(conn=conn)
        for message in self.messages:
            logging.warning(message)
        self.finish()
        self.__data_storage.refresh_cache()

    def update_popsyn_region_association(self):
        """Ensures geo-consistent references to the **PopSyn Region** for all tables

        The field "zone" is updated for table 'Location'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])

        logging.info("Updating PopSyn Region geo-association throughout the database")
        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_popsyn_region_association(conn=conn)
        for message in self.messages:
            logging.warning(message)
        self.finish()
        self.__data_storage.refresh_cache()

    def update_area_type_association(self):
        """Ensures geo-consistent references to the **area types** for all tables

        The field "area_type" is updated for tables 'Link'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])

        logging.info("Updating area_type geo-association throughout the database")
        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_areatype_association(conn=conn)
        for message in self.messages:
            logging.warning(message)
        self.finish()
        self.__data_storage.refresh_cache()

    def update_county_association(self):
        """Ensures geo-consistent references to **counties** for all tables

        The field "county" is updated for the table 'Location'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])

        logging.info("Updating County geo-association throughout the database")
        with commit_and_close(self._network_path, spatial=True) as conn:
            self.__update_county_association(conn=conn)
        for message in self.messages:
            logging.warning(message)
        self.finish()
        self.__data_storage.refresh_cache()

    def update_link_association(self):
        """Ensures geo-consistent references to **network links** for all tables

        The field "link" is updated for tables 'Location', 'Parking' & 'Micromobility_Docks'

        Links are only eligible to be associated with locations & parking facilities if
        said link is accessible by AUTO mode. Association with micromobility_docks only
        requires that the link is accessible by any mode"""

        self.geoconsistency.emit(["start", "master", 3, self.__mt])
        with commit_and_close(self._network_path, commit=True, spatial=True) as conn:
            logging.info("Updating Link geo-association throughout the database")
            self.__update_link_association(conn)

        for message in self.messages:
            logging.warning(message)
        self.messages.clear()
        self.finish()

    def update_active_network_association(self):
        """Ensures geo-consistent references to **active links** system for all tables

        The fields "walk_link"  and "bike_link" are updated for tables 'Location' & 'Parking'"""

        self.geoconsistency.emit(["start", "master", 1, self.__mt])
        with commit_and_close(self._network_path, commit=True, spatial=True) as conn:
            trigger_names = [
                "polaris_location_on_bike_link_change",
                "polaris_location_on_bike_offset_change",
                "polaris_location_on_walk_link_change",
                "polaris_location_on_walk_offset_change",
                "polaris_parking_on_bike_link_change",
                "polaris_parking_on_bike_offset_change",
                "polaris_parking_on_walk_link_change",
                "polaris_parking_on_walk_offset_change",
            ]
            with without_triggers(conn, trigger_names):
                for table in ["Location", "Parking"]:
                    self.__update_active_and_net_links_for_park_loc(table, conn, False, True, True)

        for message in self.messages:
            logging.warning(message)
        self.messages.clear()
        self.finish()

    def finish(self):
        self.geoconsistency.emit(["finished_geoconsistency_procedure"])

    def __update_link_association(self, conn: sqlite3.Connection):

        trigger_names = [
            "polaris_location_on_link_change",
            "polaris_location_on_setback_change",
            "polaris_location_on_offset_change",
            "polaris_parking_on_link_change",
            "polaris_parking_on_setback_change",
            "polaris_parking_on_offset_change",
            "polaris_micromobility_docks_on_link_change",
            "polaris_micromobility_docks_on_offset_change",
            "polaris_micromobility_docks_on_setback_change",
        ]
        with without_triggers(conn, trigger_names):
            self.__update_active_and_net_links_for_park_loc("Location", conn, True, False, False)
            self.__update_active_and_net_links_for_park_loc("Parking", conn, True, False, False)
            self.__update_link_micromobility_table(conn)
            conn.execute('DELETE FROM Geo_Consistency_Controller WHERE table_name="Link" and field_changed="geo"')

    def __update_zone_association(self, conn: sqlite3.Connection):
        list_jobs = [
            ["Ev_charging_Stations", "ID"],
            ["Location", "location"],
            ["Parking", "parking"],
            ["Node", "node"],
            ["Micromobility_Docks", "dock_id"],
            ["Transit_Stops", "stop_id"],
        ]

        trigger_names = [
            "polaris_location_on_zone_change",
            "polaris_micromobility_docks_on_zone_change",
            "polaris_network_changes_on_zone_node",
            "polaris_parking_on_zone_change",
            "polaris_transit_stops_on_zone_change",
            "polaris_ev_charging_stations_on_zone_change",
        ]
        with without_triggers(conn, trigger_names):
            self.messages.clear()
            zones = self.__get_layer("Zone").reset_index().rename(columns={"zone": "new_data"})[["new_data", "geo"]]

            self.__update_simple_element(conn, list_jobs, zones, "zone")
            self.geoconsistency.emit(["update", "master", 1, self.__mt])

        conn.execute("DELETE FROM Geo_Consistency_Controller WHERE table_name='Zone' and field_changed='geo'")

        conn.commit()

    def __update_county_association(self, conn: sqlite3.Connection):
        list_jobs = [["Location", "location"]]

        self.messages.clear()
        cnty = self.__get_layer("Counties").reset_index().rename(columns={"county": "new_data"})

        with without_triggers(conn, ["polaris_location_on_county_change"]):
            self.__update_simple_element(conn, list_jobs, cnty, "county")
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            # Set to NULL for EXTERNAL locations
            conn.execute("UPDATE Location SET county = NULL WHERE land_use = 'EXTERNAL'")
            conn.execute("DELETE FROM Geo_Consistency_Controller WHERE table_name='Counties'")
            conn.commit()

    def __update_popsyn_region_association(self, conn: sqlite3.Connection):
        list_jobs = [["Location", "location"]]

        self.messages.clear()
        cz = self.__get_layer("PopSyn_Region").reset_index().rename(columns={"popsyn_region": "new_data"})

        with without_triggers(conn, ["polaris_location_on_popsyn_region_change"]):
            self.__update_simple_element(conn, list_jobs, cz[["new_data", "geo"]], "popsyn_region")
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
            conn.execute("DELETE FROM Geo_Consistency_Controller WHERE table_name='PopSyn_Region'")
            conn.commit()

    def __update_areatype_association(self, conn: sqlite3.Connection):

        self.messages.clear()
        zones = self.__get_layer("Zone").reset_index().rename(columns={"area_type": "new_data"})[["new_data", "geo"]]

        with without_triggers(conn, ["polaris_network_changes_on_link_area_type"]):
            self.__update_simple_element_with_overlay(conn, [["Link", "link"]], zones, "area_type")

        conn.execute("DELETE FROM Geo_Consistency_Controller WHERE table_name='Link' and field_changed='area_type'")
        self.geoconsistency.emit(["update", "master", 1, self.__mt])

        conn.commit()

    def __update_simple_element(self, conn, list_jobs, ref_layer, ref_field, function="nearest"):
        for table, field in list_jobs:
            logger.info(f"  {ref_field} geo association for {table}")
            data_orig = self.__data_storage.get(table_name=table, conn=conn)
            if data_orig.empty:
                continue
            data = data_orig[[field, ref_field, data_orig.geometry.name]]

            # Join to get the new locations
            if function == "nearest":
                data = data.sjoin_nearest(ref_layer, distance_col="distance")
            else:
                data = data.sjoin(ref_layer, how="left", predicate=function).assign(distance_col=0)

            # Then drop one if there are duplicates (equidistant elements)
            data.sort_values(by=[field, ref_field, "new_data"], inplace=True)
            data = data.drop_duplicates(subset=[field], keep="first")

            self.__update_data(data, ref_field, field, table, conn)

    def __update_simple_element_with_overlay(self, conn, list_jobs, ref_layer, ref_field):
        for table, field in list_jobs:
            logger.info(f"  {ref_field} geo association for {table}")
            data_orig = self.__data_storage.get(table_name=table, conn=conn)
            if data_orig.empty:
                continue
            data_layer = data_orig[[field, ref_field, data_orig.geometry.name]]

            # Join to get the new locations
            data = data_layer.overlay(ref_layer)

            if data_layer.union_all().area == 0:
                data = data.assign(metric=data.geometry.length)
            else:
                data = data.assign(metric=data.geometry.area)

            data = data.loc[data.groupby(field)["metric"].idxmax()].drop(columns=["metric"])

            # We get the closest when we don't have overlaps
            missing = data_orig[~data_orig[field].isin(data[field])][[field, ref_field, data_orig.geometry.name]]
            if not missing.empty:
                complement = missing.sjoin_nearest(ref_layer).drop(columns=["index_right"])
                data = pd.concat([data, complement])

            self.__update_data(data, ref_field, field, table, conn)

    def __update_data(self, data, ref_field, field, table, conn):
        altered = data[data[ref_field] != data.new_data][["new_data", field]]
        if altered.empty:
            return

        def int_if_not_nan(x):
            return int(x) if pd.notna(x) else x

        recs = altered.to_records(index=False)  # type: ignore
        if is_string_dtype(altered[field]):
            recs = [[int_if_not_nan(x[0]), x[1]] for x in recs]  # type: ignore
        else:
            recs = [[int_if_not_nan(x[0]), int(x[1])] for x in recs]  # type: ignore
        sql = f"Update {table} set {ref_field}=? where {field} = ?"

        # Turning foreign keys off also turns off triggers
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.executemany(sql, recs)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        self.__data_storage.refresh_cache(table)
        self.messages.append(f"   {ref_field} needed correction for {altered.shape[0]} records on {table}")

    def __update_location_association(self, conn: sqlite3.Connection):
        list_jobs = [["Ev_charging_Stations", "ID"]]
        locs = self.__get_layer("Location").reset_index().rename(columns={"location": "new_data"})

        with without_triggers(conn, ["polaris_ev_charging_stations_on_location_change"]):
            self.__update_simple_element(conn, list_jobs, locs, "location")
            self.geoconsistency.emit(["update", "master", 1, self.__mt])
        conn.execute('DELETE FROM Geo_Consistency_Controller WHERE table_name="Location" and field_changed="geo"')
        conn.commit()

    def __update_active_and_net_links_for_park_loc(
        self, table_name: str, conn: sqlite3.Connection, do_link=True, do_wlink=True, do_blink=True
    ):
        id_field = table_name.lower()
        gdf = self.__data_storage.get(table_name, conn)
        if gdf.empty:
            return
        altered_link, altered_walk, altered_bike = pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])
        # First we get the new links
        if do_link:
            gdf_ = gdf[[id_field, "link", "offset", "setback", "dir", gdf.geometry.name]]
            altered_link = self.__get_link_for_table("link", gdf_, id_field, "AUTO", True, conn)

        if do_wlink:
            # Then we get the new walk links
            gdf_ = gdf[[id_field, "walk_link", "offset", gdf.geometry.name]].assign(setback=0, dir=0)
            altered_walk = self.__get_link_for_table("walk", gdf_, id_field, "WALK", False)
            altered_walk.rename(columns={"link": "walk_link", "offset": "walk_offset"}, inplace=True)

        if do_blink:
            # Then we get the new bike links
            gdf_ = gdf[[id_field, "bike_link", "offset", gdf.geometry.name]].assign(setback=0, dir=0)
            altered_bike = self.__get_link_for_table("bike", gdf_, id_field, "BIKE", False)
            altered_bike.rename(columns={"link": "bike_link", "offset": "bike_offset"}, inplace=True)

        table_fields = [
            (altered_bike, ["bike_link", "bike_offset"]),
            (altered_walk, ["walk_link", "walk_offset"]),
            (altered_link, ["link", "dir", "offset", "setback"]),
        ]

        for df, fields in table_fields:
            if not df.empty:
                recs = df[fields + [id_field]].to_records(index=False)
                sql = ", ".join([f"{x}=?" for x in fields])
                conn.execute("PRAGMA foreign_keys = OFF;")
                conn.executemany(f"Update {table_name} set {sql} where {id_field}= ?", recs)
                conn.execute("PRAGMA foreign_keys = ON;")
                self.messages.append(f"   {fields[0]} records corrected for {df.shape[0]} records on {table_name}")
                conn.commit()
        for t in ("Transit_Bike", "Transit_Walk", "Transit_Stops"):
            conn.execute(f'DELETE FROM Geo_Consistency_Controller WHERE table_name="{t}" and field_changed="geo"')

        self.__data_storage.refresh_cache(table_name)

    def __update_link_micromobility_table(self, conn: sqlite3.Connection):
        gdf = self.__data_storage.get("Micromobility_Docks", conn)
        if not gdf.empty:
            gdf = gdf[["dock_id", "link", "offset", "setback", "dir", "geo"]]
            altered = self.__get_link_for_table("link", gdf, "dock_id", "AUTO", True, conn)

            if not altered.empty:
                fields = ["link", "offset", "setback", "dir"]
                recs = altered[fields + ["dock_id"]].to_records(index=False)

                sql = ", ".join([f"{x}=?" for x in fields])
                conn.executemany(f"Update Micromobility_Docks set {sql} where dock_id = ?", recs)
                conn.commit()
                self.__data_storage.refresh_cache("Micromobility_Docks")

        conn.commit()

    def __get_link_for_table(
        self, link_type, gdf, field, mode=None, do_direction=True, conn: Optional[sqlite3.Connection] = None
    ):
        if gdf.empty:
            return gdf
        if link_type == "link":
            links = self.__get_layer("Link").rename(columns={"link": "nlink"})
            if mode is not None and conn is not None:
                ltypes = self.__data_storage.get("Link_Type", conn)
                ltypes = ltypes[ltypes["use_codes"].str.contains("AUTO")]
                links = links[links["type"].isin(ltypes.link_type)]

        elif link_type == "walk":
            links = self.__get_layer("Transit_Walk").rename(columns={"walk_link": "nlink"})
            gdf = gdf.rename(columns={"walk_link": "link"})
        elif link_type == "bike":
            links = self.__get_layer("Transit_Bike").rename(columns={"bike_link": "nlink"})
            gdf = gdf.rename(columns={"bike_link": "link"})
        else:
            raise ValueError("Wrong link type")

        sz = gdf.shape[0]
        links = links[["nlink", "geo"]]
        gdf = gdf.sjoin_nearest(links, distance_col="nstbck").assign(nffst=gdf.offset, new_dir=gdf.dir)

        # sjoin_nearest may return more than one element, in which case we keep only one
        # arbitrarily set to the smallest ID of the matching elements
        gdf.sort_values(by=[field, "nstbck", "nlink"], inplace=True)
        gdf = gdf.drop_duplicates(subset=[field], keep="first")
        if sz != gdf.shape[0]:
            raise ValueError("Could not find a link close to every element. Maybe an issue with link types?")

        geo_name = gdf.geometry.name
        gdf = gdf.merge(links[["nlink", geo_name]].rename(columns={geo_name: "link_geo"}), on="nlink")

        gdf["nffst"] = gdf.link_geo.project(gdf[geo_name])
        if do_direction:
            gdf["new_dir"] = gdf.apply(
                lambda row: self.geotool.side_of_link_for_point(point=row[geo_name], link=row.link_geo), axis=1
            )

        df = pd.DataFrame(gdf[[field, "link", "nlink", "offset", "nffst", "setback", "nstbck", "new_dir", "dir"]])

        df.nffst = df.nffst.fillna(0).round(2)
        df.nstbck = df.nstbck.fillna(0).round(2)

        crit1 = df.nlink != df.link
        crit2 = df.offset.fillna(value=0.0).round(2) != df.nffst.fillna(value=0.0).round(2)
        crit3 = df.setback.fillna(value=0.0).round(2) != df.nstbck.fillna(value=0.0).round(2)
        crit4 = df.dir != df.new_dir

        df = df.loc[crit1 | crit2 | crit3 | crit4, ["nlink", "nffst", "nstbck", "new_dir", field]]  # type: ignore
        return df.rename(columns={"nlink": "link", "nffst": "offset", "nstbck": "setback", "new_dir": "dir"})

    def __get_layer(self, lyr_name):
        with read_and_close(self._network_path, spatial=True) as conn:
            return self.__data_storage.get(lyr_name, conn)
