# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from sqlite3 import Connection

from polaris.network.starts_logging import logger
from polaris.utils.database.db_utils import has_table
from polaris.utils.database.standard_database import StandardDatabase, DatabaseType


def recreate_network_triggers(conn: Connection) -> None:
    delete_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)
    create_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)


def recreate_freight_triggers(conn: Connection) -> None:
    delete_triggers(StandardDatabase.for_type(DatabaseType.Freight), conn)
    create_triggers(StandardDatabase.for_type(DatabaseType.Freight), conn)


def create_network_triggers(conn: Connection) -> None:
    create_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)


def create_triggers(db: StandardDatabase, conn: Connection) -> None:
    logger.info("  Creating triggers")
    trigger_list_file = db.base_directory / "triggers/list_triggers.txt"
    if not trigger_list_file.exists():
        return

    with open(trigger_list_file) as f:
        trigger_list = [line.rstrip() for line in f.readlines()]

    for table in trigger_list:
        logger.debug(f"     creating triggers for {table}")
        qry_file = db.base_directory / "triggers" / f"{table}.sql"

        with open(qry_file, "r") as sql_file:
            query_list = sql_file.read()

        # Running one query/command at a time helps debugging in the case a particular command fails
        for cmd in query_list.split("--##"):
            lines = [e.strip() for e in cmd.split("\n")]
            lines = [e for e in lines if not e.startswith("--") and e != ""]
            if not len(lines):
                continue

            if "create trigger if not exists" in lines[0].lower():
                # If the trigger operates on a table that does not exist, then we do not attept to add it
                table_name = lines[0].split(" on ")[1]
                if not has_table(conn, table_name):
                    logger.error(f"Could not find table {table_name}. Skipping trigger creation {cmd=}")
                    continue
            try:
                conn.execute(cmd)
            except Exception as e:
                logger.error(f"Failed adding triggers table - > {e.args}")
                logger.error(f"Point of failure - > {cmd}")
                raise e
        conn.commit()


def delete_network_triggers(conn: Connection) -> None:
    delete_triggers(StandardDatabase.for_type(DatabaseType.Supply), conn)


def delete_triggers(db: StandardDatabase, conn: Connection) -> None:
    logger.info("  Deleting triggers")
    trigger_list_file = db.base_directory / "triggers/list_triggers.txt"
    if not trigger_list_file.exists():
        return
    with conn:
        with open(trigger_list_file) as f:
            trigger_list = [line.rstrip() for line in f.readlines()]
        for table in trigger_list:
            qry_file = db.base_directory / "triggers" / f"{table}.sql"

            with open(qry_file, "r") as sql_file:
                query_list = sql_file.read()

            # Running one query/command at a time helps debugging in the case a particular command fails
            for cmd in query_list.split("--##"):
                for qry in cmd.split("\n"):
                    if qry[:2] == "--":
                        continue
                    if "create trigger if not exists " in qry:
                        qry = qry.replace("create trigger if not exists ", "")
                        qry = "DROP trigger if exists " + qry.split(" ")[0]
                        try:
                            conn.execute(qry)
                        except Exception as e:
                            logger.error(f"Failed removing triggers table - > {e.args}")
                            logger.error(f"Point of failure - > {qry}")
