# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import os
from typing import Dict

import pandas as pd
import geopandas as gpd

from polaris.network.traffic.hand_of_driving import get_driving_side
from polaris.network.utils.srid import get_srid
from polaris.network.osm.osm import OSM
from polaris.network.starts_logging import logger
from polaris.network.traffic.intersection_control.stop_sign import StopSign
from polaris.network.utils.worker_thread import WorkerThread
from polaris.utils.database.data_table_access import DataTableAccess
from polaris.utils.database.db_utils import commit_and_close, read_and_close
from polaris.utils.logging_utils import polaris_logging
from polaris.utils.signals import SIGNAL


class CreateConnections(WorkerThread):
    connecting = SIGNAL(object)

    def __init__(self, data_tables, path_to_file: os.PathLike, signals, signs, missing_only):
        WorkerThread.__init__(self, None)
        self.tables = data_tables
        polaris_logging()
        self.do_all_signs = False
        self.missing_only = missing_only

        sql = """select distinct(node_a) node from Link l
                                inner join link_type lt on l.type=lt.link_type
                                where lt.use_codes like "%AUTO%"
                         union all
                         select distinct(node_b) node from Link l
                                inner join link_type lt on l.type=lt.link_type
                                where lt.use_codes like "%AUTO%" """
        with read_and_close(path_to_file) as conn:
            self.all_nodes = sorted({node[0] for node in conn.execute(sql)})

            if missing_only:
                covered = sorted({node[0] for node in conn.execute("SELECT DISTINCT(node) from Connection")})
                self.all_nodes = [node for node in self.all_nodes if node not in covered]

            self.signals = [x[0] for x in conn.execute("Select nodes from Signal")] if signals is None else signals
            self.signs = [x[0] for x in conn.execute("Select nodes from Sign")] if signs is None else signs

            if signs is not None:
                self.do_all_signs = len(self.signs) == 0

        self.osm = OSM(path_to_file)
        self.__path_to_file = path_to_file

    def doWork(self):
        """Alias for execute"""
        self.execute()

    def finish(self):
        """Kills the progress bar so others can be generated"""
        self.connecting.emit(["finished_connections_procedure"])

    def execute(self) -> None:
        """Rebuilds all connections in the network after clearing all existing connections and signals

        Args:
            *signals* (:obj:`List[int]`): List of nodes that should have signals rebuilt after connections are done
        """
        logger.info("Starting connection rebuild")
        self.tables.refresh_cache("Connection")
        with commit_and_close(self.__path_to_file, spatial=True) as conn:
            self.__processer(conn)
        logger.info("Finishing connection rebuild")

    def __processer(self, conn):
        from polaris.network.traffic.intersec import Intersection

        driving_side = get_driving_side(conn=conn)
        logger.info("Removing existing connections, signals and stop signs")

        tables = ["Signal", "Signal_Nested_Records", "Phasing", "Phasing_Nested_Records", "Timing", "Sign"]
        tables.extend(["Timing_Nested_Records"])
        sig_tables = tables + ["Connection", "Pocket"]

        if not self.missing_only:
            for table in sig_tables:
                conn.execute(f"delete from {table};")
            conn.commit()
            conn.execute("update Node set control_type = '';")

        txt = "Rebuilding connections"
        self.connecting.emit(["start", "master", 1, txt])
        self.connecting.emit(["start", "secondary", len(self.all_nodes), txt, txt])

        connection_sets = []
        pocket_sets = []
        signal_sets: Dict[str, list] = {x: [] for x in tables}

        logging.info("      Recreating intersections")
        portions = max(1, len(self.all_nodes) // 20)
        for counter, node in enumerate(self.all_nodes):
            if counter % portions == 0:
                logging.debug(f"      Processed {counter}/{len(self.all_nodes)} intersections")
            self.connecting.emit(["update", "secondary", counter + 1, txt, txt])

            inter = Intersection(self.tables, self.__path_to_file, conn, self.osm, driving_side)
            inter.__bulk_loading__ = True
            inter.load(node, conn)

            c = inter._creates_connections(conn)
            connection_sets.append(c)
            pocket_sets.append(inter._builds_pockets)

            add_signal = self.__signal_decision(conn, inter, node)

            if (node in self.signs or self.do_all_signs) and not add_signal:
                ss = StopSign(inter)
                ss.re_compute()
                if ss.stop_signs:
                    signal_sets["Sign"].append(ss.data)
            elif add_signal:
                if inter.connections(conn).link.nunique() > 1:
                    sig = inter.create_signal(conn, compute_and_save=False)
                    sig.re_compute(conn)
                    for table_name, data in sig.data.items():
                        signal_sets[table_name].append(data)

            logger.debug(f"node {node}")
        # saves the data into the database
        conn_sets = pd.concat(connection_sets)
        conn_sets["geo"] = gpd.GeoSeries(conn_sets.geo).to_wkb()
        cols = [x for x in conn_sets.columns if str(x).lower() != "geo"]
        conn_sets[cols].to_sql("Connection", conn, if_exists="append", index=False)
        geos = conn_sets[["geo", "link", "to_link"]].assign(srid=get_srid(conn=conn))
        npgeos = geos[["geo", "srid", "link", "to_link"]].to_records(index=False)
        conn.executemany("Update Connection set Geo=GeomFromWKB(?,?) where link=? and to_link=?", npgeos)
        df = pd.concat(pocket_sets).drop_duplicates(subset=["link", "dir", "type"])
        if not df.empty:
            if self.missing_only:
                pkt = DataTableAccess(self.__path_to_file).get("Pocket", conn, False).set_index(["link", "dir", "type"])
                df = df[~df.set_index(["link", "dir", "type"]).index.isin(pkt).index]
            df.to_sql("Pocket", conn, if_exists="append", index=False)

        for table_name, data in signal_sets.items():
            if data:
                pd.concat(data).to_sql(table_name, conn, if_exists="append", index=False)

        self.connecting.emit(["finished_create_connections_procedure"])

        for table in sig_tables:
            self.tables.refresh_cache(table)

    def __signal_decision(self, conn, inter, node):
        add_signal = False
        if isinstance(self.signals, list) and node in self.signals:
            add_signal = inter.supports_signal(conn)
        elif self.signals in ["osm", "geometric"] and node not in self.signs:
            if inter.supports_signal(conn):
                if self.signals in ["osm", "geometric"]:
                    if self.signals == "osm":
                        add_signal = inter.osm_signal()
                    elif self.signals == "geometric":
                        add_signal = inter.determine_geometric_need_for_signal(conn)
        return add_signal
