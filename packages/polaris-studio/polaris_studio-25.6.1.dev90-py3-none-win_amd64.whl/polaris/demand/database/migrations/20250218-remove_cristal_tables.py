# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.migration_utils import move_table_to_other_db


def migrate(conn):

    move_table_to_other_db(conn, "Establishments", "Demand", "Freight")
    move_table_to_other_db(conn, "Establishments_Attributes", "Demand", "Freight")
    move_table_to_other_db(conn, "Firms", "Demand", "Freight")
    move_table_to_other_db(conn, "Freight_Delivery", "Demand", "Freight")
    move_table_to_other_db(conn, "Freight_Shipment", "Demand", "Freight")
    move_table_to_other_db(conn, "Freight_Shipment_Delivery", "Demand", "Freight")
    move_table_to_other_db(conn, "Industry_Make_Use", "Demand", "Freight")
