# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from contextlib import contextmanager
from packaging import version
import logging
import re
import sqlite3
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from sqlite3 import connect, sqlite_version
from typing import Dict, List, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import sqlalchemy.engine

# import sqlalchemy
from polaris.runs.scenario_compression import ScenarioCompression
from polaris.utils.database.spatialite_utils import connect_spatialite
from polaris.utils.time_utils import time_function
from polaris.utils.type_utils import AnyPath


def list_tables_in_db(conn: sqlite3.Connection):
    sql = "SELECT name FROM sqlite_master WHERE type ='table'"
    table_list = sorted([x[0].lower() for x in conn.execute(sql).fetchall() if "idx_" not in x[0].lower()])
    return table_list


def safe_connect(filepath: AnyPath, missing_ok=False) -> sqlite3.Connection:
    if Path(filepath).exists() or missing_ok or str(filepath) == ":memory:":
        return connect(filepath)
    raise FileNotFoundError(f"Attempting to open non-existent SQLite database: {filepath}")


def normalise_conn(conn: Union[sqlite3.Connection, AnyPath]) -> sqlite3.Connection:
    return conn if isinstance(conn, sqlite3.Connection) else safe_connect(conn)


def filename_from_conn(conn):
    return Path(conn.execute("PRAGMA database_list").fetchall()[0][2])


class commit_and_close:
    """A context manager for sqlite connections which closes and commits."""

    def __init__(
        self,
        db: Union[AnyPath, sqlite3.Connection, "sqlalchemy.engine.Connection"],
        commit=True,
        missing_ok=False,
        spatial=False,
    ):
        """
        :param db: The database (filename or connection) to be managed
        :param commit: Boolean indicating if a commit/rollback should be attempted on closing
        :param missing_ok: Boolean indicating that the db is not expected to exist yet
        :param spatial: Boolean indicating that a spatialite connection is desired
        """

        def get_conn() -> Union[sqlite3.Connection, "sqlalchemy.Connection"]:
            if spatial:
                if not isinstance(db, (str, PathLike)):
                    raise Exception("You must provide a database path to connect to spatialite")
                return connect_spatialite(db, missing_ok)
            elif isinstance(db, (str, PathLike)):
                return safe_connect(db, missing_ok)
            else:
                return db

        self.conn = get_conn()
        self.commit = commit

    def __enter__(self):
        return self.conn

    def __exit__(self, err_typ, err_value, traceback):
        if self.commit:
            if err_typ is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        self.conn.close()


def read_and_close(filepath, **kwargs):
    """A context manager for sqlite connections (alias for `commit_and_close(db,commit=False))`."""
    return commit_and_close(filepath, commit=False, **kwargs)


def read_sql(sql, filepath, **kwargs):
    import pandas as pd

    with read_and_close(filepath) as conn:
        return pd.read_sql(sql, conn, **kwargs)


def read_table(tablename, filepath, **kwargs):
    import pandas as pd

    with read_and_close(filepath) as conn:
        return pd.read_sql(f"SELECT * FROM {tablename};", conn, **kwargs)


def table_to_csv(conn, table_name, csv_file):
    import pandas as pd

    df = pd.read_sql(sql=f"SELECT * from {table_name};", con=conn)
    df.to_csv(csv_file, index=False)


def sql_to_csv(conn, sql, csv_file):
    import pandas as pd

    pd.read_sql(sql=sql, con=conn).to_csv(csv_file, index=False)


def run_sql_file(
    qry_file: PathLike, conn: Union[sqlite3.Connection, PathLike], replacements=None, attach=None, query_sep=";"
):
    with open(qry_file, "r") as sql_file:
        contents = sql_file.read()
    try:
        return run_sql(contents, normalise_conn(conn), replacements, attach, query_sep)
    except Exception as e:
        logging.error(f"While processing file: {qry_file}")
        raise e


def run_sql(contents: str, db: Union[sqlite3.Connection, PathLike], replacements=None, attach=None, query_sep=";"):
    import pandas as pd

    if replacements:
        for from_str, to_str in replacements.items():
            contents = contents.replace(from_str, str(to_str))
    contents = re.sub("--.*\n", "", contents, count=0, flags=0)

    # Running one query/command at a time helps debugging in the case a particular command fails, but is hard to do
    # for triggers which can use ; inside a single query
    query_list = [x.strip() for x in contents.split(query_sep)]
    query_list = [x for x in query_list if x != ""]

    conn = normalise_conn(db)
    if attach:
        attach_to_conn(conn, attach)

    rv = []
    for cmd in query_list:
        try:
            duration = time_function(lambda: conn.execute(cmd))  # noqa: B023
            rv.append((duration, cmd))
        except Exception as e:
            print(f"Failed running sql: {cmd}")
            logging.error(f"Failed running sql: {cmd}")
            logging.error(e.args)
            raise e

    return pd.DataFrame(data=rv, columns=["duration", "sql"])


def attach_to_conn(conn: sqlite3.Connection, attachments: dict) -> None:
    try:
        for alias, file in attachments.items():
            conn.execute(f'ATTACH DATABASE "{file}" as {alias};')

    except Exception as e:
        logging.error(f"Failed attaching external databases {attachments}")
        logging.error(e.args)
        raise e


def drop_table(conn, table_name):
    normalise_conn(conn).execute(f"DROP TABLE IF EXISTS {table_name};")


def has_table(conn: sqlite3.Connection, table_name: str) -> bool:
    sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name like '{table_name}';"
    return len(normalise_conn(conn).execute(sql).fetchall()) > 0


def count_table(conn: sqlite3.Connection, table_name: str) -> bool:
    sql = f"SELECT COUNT(*) FROM {table_name};"
    return normalise_conn(conn).execute(sql).fetchone()[0]


def remove_table(conn: sqlite3.Connection, table_name: str, missing_okay=False):
    missing_okay = "IF EXISTS" if missing_okay else ""
    sql = f"DROP TABLE {missing_okay} {table_name};"
    return normalise_conn(conn).execute(sql)


sqlite_system_tables = ["schema_version", "sqlite_sequence"]


def get_tables(conn, skip_system_tables=True):
    sql = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = [e[0] for e in normalise_conn(conn).execute(sql).fetchall()]
    return [e for e in tables if e not in sqlite_system_tables] if skip_system_tables else tables


@dataclass
class ColumnDef:
    idx: int
    name: str
    type: str
    not_null: bool
    default: str
    is_pk: bool


def get_schema(conn: sqlite3.Connection, table_name: str) -> Dict[str, ColumnDef]:
    rv = [ColumnDef(*e) for e in conn.execute(f"PRAGMA table_info({table_name});").fetchall()]
    return {e.name: e for e in rv}


def get_trigger_sql(conn: sqlite3.Connection, name: str):
    res = conn.execute(f"select sql from sqlite_master where type = 'trigger' and name = '{name}';").fetchone()
    return None if res is None else res[0]


def drop_trigger(conn, trigger_name):
    conn.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")


def has_column(conn: sqlite3.Connection, table_name: str, col_name: str):
    return col_name.lower() in [k.lower() for k in get_schema(conn, table_name).keys()]


def add_column_unless_exists(conn: sqlite3.Connection, table_name: str, col_name: str, col_type: str, constraints=""):
    if not has_column(conn, table_name, col_name):
        add_column(conn, table_name, col_name, col_type, constraints)


def drop_column_if_exists(conn: sqlite3.Connection, table_name: str, col_name: str):
    if has_column(conn, table_name, col_name):
        drop_column(conn, table_name, col_name)


def add_column(conn: sqlite3.Connection, table_name, col_name, col_type, constraints=""):
    conn.execute(f"ALTER TABLE {table_name} ADD {col_name} {col_type} {constraints};")


def drop_column(conn: sqlite3.Connection, table_name, col_name):
    check_version("3.35.0", "dropping columns")
    triggers = ["ISO_metadata_reference_row_id_value_update", "ISO_metadata_reference_row_id_value_insert"]
    with without_triggers(conn, triggers):
        conn.execute(f"ALTER TABLE {table_name} DROP {col_name};")


def check_version(minimum, operation):
    if version.parse(sqlite_version) < version.parse(minimum):
        logging.error(f"Support for {operation} requires sqlite3 version >= {minimum}, you have {sqlite_version}")
        logging.error("You can upgrade your version by upgrading your python installation version >= 3.10")
        raise RuntimeError(f"Support for {operation} requires sqlite3 version >= {minimum}, found {sqlite_version}")


def rename_column(conn: sqlite3.Connection, table_name, old_name, new_name):
    check_version("3.25.0", "renaming columns")
    sql = f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name};"
    conn.execute(sql)


@contextmanager
def without_triggers(conn: sqlite3.Connection, trigger_names: List[str]):
    sqls = []
    try:

        for trigger in trigger_names:
            if sql := get_trigger_sql(conn, trigger):
                sqls.append(sql)
                drop_trigger(conn, trigger)
        conn.commit()

        yield

    finally:
        for sql in sqls:
            conn.execute(sql)
        conn.commit()


def read_about_model_value(supply_db, variable_name, cast=None, default=None):
    sql = "SELECT infovalue from about_model WHERE infoname = ?;"
    row = supply_db.execute(sql, [variable_name]).fetchone()
    if row is None:
        return default
    return cast(row[0]) if cast is not None else row[0]


def write_about_model_value(supply_db, variable_name, variable_value):
    sql = """
      INSERT INTO about_model VALUES (?,?)
      ON CONFLICT(infoname) DO
        UPDATE set infovalue = excluded.infovalue;
    """
    supply_db.execute(sql, (variable_name, variable_value))


def load_link_types(supply_db):
    import pandas as pd

    with safe_connect(ScenarioCompression.maybe_extract(supply_db)) as conn:

        def sql(linknr, lanes):
            return f"""
                SELECT {linknr},type,z.zone
                FROM link l, node n, zone z
                WHERE {lanes}
                AND l.node_a = n.node AND n.zone = z.zone and l.type not in ('LIGHTRAIL', 'HEAVYRAIL', 'WALKWAY')
                """

        linknr_ab, lanes_ab = "2*link     as linknr", "lanes_ab>0"
        linknr_ba, lanes_ba = "(2*link+1) as linknr", "lanes_ba>0"
        return pd.read_sql(
            f"{sql(linknr_ab, lanes_ab)} UNION {sql(linknr_ba, lanes_ba)} ORDER BY linknr", conn
        ).set_index("linknr")
