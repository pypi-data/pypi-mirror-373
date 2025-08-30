# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from math import floor, ceil, log10
from os import PathLike
from typing import Dict

import numpy as np
import pandas as pd

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.starts_logging import logger
from polaris.utils.database.db_utils import read_sql, read_and_close


class CheckConnectionTable:
    def __init__(self, supply_db: PathLike):
        """Analyzes the connection table in search of links that don't have all its lanes connected at either end

        It currently analyses five items:

         * If there are no repeated connections between any two links
         * If all lanes are connected in both the start and end of a link
         * If all pockets used in the connection table are in the pockets table
         * If all pockets in the pockets table are used in the connection table
         * If all necessary connections exist

         Args:
                 *data_tables* (:obj:`DataTableAccess`): Network's data table storage

         Returns:
                 *errors* (:obj:`dict`): Dictionary with all the errors found

         ::

             from polaris.network.network import Network
             from polaris.network.checker.checks import check_connection_table

             net = Network()
             net.open('path/to/my/network/file.sqlite')

             errors = check_connection_table(net)
             if 'repeated_connections' in errors:
                 repeated_connections = errors['repeated_connections']

             if 'link_start_connection' in errors:
                 disconnected_start = errors['link_start_connection']

             if 'link_end_connection' in errors:
                 disconnected_end = errors['link_end_connection']

             if 'unused_pockets' in errors:
                 unused_pockets = errors['unused_pockets']

             if 'missing_pockets' in errors:
                 missing_pockets = errors['missing_pockets']

             if 'missing_connections' in errors:
                 missing_connections = errors['missing_connections']

             net.close()
        """
        self.tables = DataTableAccess(supply_db)
        self.supply_db = supply_db
        self.errors: Dict[str, pd.DataFrame] = {}

    def full_check(self, complete_connectivity=True):
        self.repeated_connections()
        self.pockets()
        self.lane_connection(complete_connectivity)

        if not self.errors:
            logger.info("No issues found with the connections and pocket table")

    def repeated_connections(self):
        df = read_sql("select conn, node, link, to_link from Connection", self.supply_db)

        df = df.groupby(["node", "link", "to_link"]).count().reset_index()
        df = df[df.conn > 1][["node", "link", "to_link"]]
        if not df.empty:
            msg = f"There are {df.shape[0]} pairs of links with more than one connection of records between them"
            logger.error(msg)
            self.errors["repeated_connections"] = df

    def pockets(self):
        # We check for both link directions at the same time
        sql = """select DISTINCT(lanes) clanes, link * 100 + 10 * "dir" + 1 link, lanes from Connection where lanes like "%R%"
                 UNION ALL
                 select DISTINCT(lanes) clanes, link * 100 + 10 * "dir" + 2 link, lanes from Connection where lanes like "%L%"
                 UNION ALL
                 select DISTINCT(to_lanes) clanes, to_link * 100 + 10 * "to_dir" + 3 link, to_lanes from Connection
                 where to_lanes like "%R%"
                 UNION ALL
                 select DISTINCT(to_lanes) clanes, to_link * 100 + 10 * "to_dir" + 4 link, to_lanes from Connection
                 where to_lanes like "%L%"
                 """
        pocket_sql = 'Select pocket, lanes lane,link * 100 + 10 * "dir" links, "type" from Pocket'

        cpocket = read_sql(sql, self.supply_db)
        pockets = read_sql(pocket_sql, self.supply_db)

        # We first check the existence of all pockets
        pckts = cpocket[cpocket.lanes.str.contains("R") | cpocket.lanes.str.contains("L")]
        if not pckts.empty:
            pckts = pd.DataFrame(pckts.lanes.str.split(",").tolist(), index=pckts.link).stack()
            pckts = pckts.reset_index()[[0, "link"]]
            pckts.columns = ["lanes", "link"]
            pckts = pckts[pckts.lanes.str.contains("R") | pckts.lanes.str.contains("L")]
            pckts = pckts.assign(clanes=pckts.lanes)
        pckts.loc[:, "clanes"] = pckts.clanes.str.replace("R", "")
        pckts.loc[:, "clanes"] = pckts.clanes.str.replace("L", "")
        pckts = pckts.assign(key=pckts.link * 10 + pckts.clanes.astype(int))

        pockets.loc[:, "pocket"] = pockets.pocket.astype(int)[:]
        pockets.loc[pockets.type == "RIGHT_TURN", "links"] += 1
        pockets.loc[pockets.type == "LEFT_TURN", "links"] += 2
        pockets.loc[pockets.type == "RIGHT_MERGE", "links"] += 3
        pockets.loc[pockets.type == "LEFT_MERGE", "links"] += 4

        if not pockets.empty:
            index = [pockets.pocket, pockets.links, pockets.type]
            pockets = pd.DataFrame(pockets.lane.apply(np.arange).tolist(), index=index).stack()
            pockets = pockets.reset_index()
            pockets.columns = ["pocket", "links", "type", "lane", "1"]
            pockets = pockets[["pocket", "links", "type", "lane"]]
            pockets.loc[:, "lane"] += 1
        pockets = pockets.assign(key=pockets.links * 10 + pockets.lane)

        pocket_df = pckts.merge(pockets, on="key", how="outer")
        useless_pockets = pocket_df.loc[pocket_df.clanes.isna(), :]
        missing_pockets = pocket_df.loc[pocket_df.pocket.isna(), :]

        if not useless_pockets.empty:
            logger.error(f"There are {useless_pockets.shape[0]} unused pockets in the supply model")
            self.errors["unused_pockets"] = useless_pockets

        if not missing_pockets.empty:
            missing_pockets = missing_pockets.assign(link_id=missing_pockets.link / 100)
            missing_pockets = missing_pockets.assign(dir=0)
            missing_pockets.link_id = missing_pockets.link_id.apply(floor).astype(int)
            missing_pockets.dir = (missing_pockets.link / 10).apply(floor) - missing_pockets.link_id * 10
            logger.error(f"There are {missing_pockets.shape[0]} missing pockets in the pocket table")
            self.errors["missing_pockets"] = missing_pockets[["link_id", "dir", "lanes"]]

    def lane_connection(self, complete_connectivity=False):
        # Check to see if all lanes leaving and arriving a node are connected

        # Now we check lane connection
        sql1 = "select DISTINCT(lanes) conn_lanes, link * 10 + dir link from Connection"

        sql2 = "select DISTINCT(to_lanes) conn_lanes, to_link * 10 + to_dir link from Connection"

        lanes_sql = """select l.link * 10 link, l.lanes_ab lanes from Link l
                          INNER JOIN link_type lt on l.type=lt.link_type
                          where l.lanes_ab>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')
                       UNION ALL
                       select l.link * 10 + 1 link, l.lanes_ba lanes from Link l
                          INNER JOIN link_type lt on l.type=lt.link_type
                          where l.lanes_ba>0 AND (lt.use_codes like '%AUTO%' or lt.use_codes like '%TRUCK%' or
                                lt.use_codes like '%BUS%' or lt.use_codes like '%HOV%' or lt.use_codes like '%TAXI%')"""

        sql_lanes_exist = "select node, link, to_link from Connection"

        with read_and_close(self.supply_db) as conn:
            pairs = [
                [pd.read_sql_query(sql1, conn), "Departing from link"],
                [pd.read_sql_query(sql2, conn), "Arriving at link"],
            ]
            lanes = pd.read_sql_query(lanes_sql, conn)
            all_nodes = pd.read_sql("select node from Node order by node", conn)
            ln_exist = pd.read_sql_query(sql_lanes_exist, conn)

        for df, item_message in pairs:
            connections = pd.DataFrame(df.conn_lanes.str.split(",").tolist(), index=df.link).stack().reset_index()

            connections.columns = ["link", "trash", "conn_lanes"]
            connections = connections[~connections.conn_lanes.isin(["R1", "L1"])]
            aug_connections = pd.DataFrame(connections[["link", "conn_lanes"]])
            aug_connections["conn_lanes"] = aug_connections.conn_lanes.astype(int)[:]
            aug_connections.drop_duplicates(["link", "conn_lanes"], inplace=True)
            tot_per_link = aug_connections.groupby(["link"]).count()[["conn_lanes"]].reset_index()

            df = tot_per_link.merge(lanes, on="link", how="outer")
            df.fillna(0, inplace=True)
            df = df.assign(lane_diff=df.lanes - df.conn_lanes)
            df = df[df.lane_diff != 0]
            problematic_count = df.shape[0]

            if problematic_count:
                df = df.assign(link_id=df.link / 10)
                df.link_id = df.link_id.apply(floor).astype(int)
                df = df.assign(dir=df.link - df.link_id * 10)
                df = df[["link_id", "dir", "lane_diff"]]
                df.set_index(["link_id", "dir"], inplace=True)
                df = df.assign(issue=item_message)
                logger.error(f"{problematic_count} link/directions have lanes not connected for {item_message}")
                if "lane_connection" in self.errors:
                    self.errors["lane_connection"] = pd.concat([self.errors["lane_connection"], df])
                else:
                    self.errors["lane_connection"] = df

        if complete_connectivity:
            self.__complete_connectivity(all_nodes, ln_exist)

    def __complete_connectivity(self, all_nodes, ln_exist):
        from polaris.network.traffic.intersec import Intersection

        # Tests for complete connectivity
        nodes_fully_connected = []
        all_pairs = []
        with read_and_close(self.supply_db, spatial=True) as conn:
            for node in all_nodes.node.values:
                intersec = Intersection(self.tables, self.supply_db)
                intersec.load(node, conn)
                if intersec.intersection_type not in ["disconnected", "freeway"]:
                    nodes_fully_connected.append(node)
                    allowed = intersec.allowed_turns()
                    all_pairs.extend([[node] + item for item in allowed])
        must_have = pd.DataFrame(all_pairs, columns=["nod", "link_from", "link_to"])
        power2 = int(ceil(log10(must_have.link_from.max())))
        power1 = pow(10, int(ceil(log10(must_have.nod.max())) + power2))
        power2 = pow(10, power2)
        must_have = must_have.assign(key=must_have.nod * power1 + must_have.link_from * power2 + must_have.link_to)
        ln_exist.drop_duplicates(ignore_index=True, inplace=True)
        ln_exist = ln_exist.assign(key=ln_exist.node * power1 + ln_exist.link * power2 + ln_exist.to_link)
        df = must_have.merge(ln_exist, on="key", how="left")
        missed = df.loc[df.isna().nod, :][["node", "link_from", "link_to"]]
        if not missed.empty:
            logger.error(f"There are {missed.shape[0]} required connections missing")
            self.errors["missing_connections"] = missed
