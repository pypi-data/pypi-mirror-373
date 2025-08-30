# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import re
from functools import total_ordering
from importlib.util import spec_from_file_location, module_from_spec
from os import listdir
from os.path import exists, isfile, join
from pathlib import Path

from polaris.utils.database.db_utils import run_sql_file
from polaris.utils.str_utils import outdent

migration_file_pattern = re.compile(r"^([0-9]+(_[0-9\.]+)?)(-.*)?\.(py|sql)$")


@total_ordering
class Migration:
    def __init__(self, migration_id, description, type, file):
        self.migration_id = migration_id
        self.description = description
        self.type = type
        self.file = file

    def __eq__(self, other):
        return self.migration_id == other.migration_id

    def __lt__(self, other):
        return self.migration_id < other.migration_id

    def __hash__(self):
        return int(self.migration_id)

    def __repr__(self):
        return f"Migration({self.migration_id} - {self.description})"

    @classmethod
    def from_file(cls, file):
        if not exists(file):
            raise RuntimeError(f"No such migration: {file}")
        match = migration_file_pattern.match(Path(file).name)
        if not match:
            raise RuntimeError(f"Not a validly named migration file: {Path(file).name}")
        descr = match[3][1:] if match[3] else None  # drop the leading '-' that will be matched by the regex
        return cls(match[1], descr, match[4], file)

    @classmethod
    def from_id(cls, migration_id, migrations_dir):
        files = [s for s in listdir(migrations_dir) if isfile(join(migrations_dir, s)) if s.startswith(migration_id)]
        if len(files) == 1:
            return cls.from_file(join(migrations_dir, files[0]))
        msg = f"Can't find migration definition file for {migration_id} in {migrations_dir}: possibilities are {files}"
        raise FileNotFoundError(msg)

    def run(self, conn):
        applied_migration_ids = Migration.find_applied_migrations(conn)
        if self.migration_id in applied_migration_ids:
            logging.warning(f"  Applying migration [{self.migration_id}] for a second time")
        if self.file.endswith(".sql"):
            run_sql_file(self.file, conn)
        elif self.file.endswith(".py"):
            Migration._run_py(self.file, conn)
        else:
            raise RuntimeError(f"Unsupported migration type for file {self.file}")

        description = "NULL" if self.description is None else f"'{self.description}'"
        with conn:
            sql = outdent(
                f"""
                INSERT INTO Migrations VALUES ('{self.migration_id}', {description}, DATETIME('now'))
                ON CONFLICT(migration_id) DO UPDATE SET applied_at=DATETIME('now');"""
            )
            conn.execute(sql)
        conn.commit()

    @staticmethod
    def _run_py(migration_file, conn):
        spec = spec_from_file_location(Path(migration_file).stem, migration_file)
        loaded_module = module_from_spec(spec)
        spec.loader.exec_module(loaded_module)
        loaded_module.migrate(conn)

    @staticmethod
    def find_applied_migrations(conn):
        return [e[0] for e in conn.execute("SELECT migration_id from Migrations").fetchall()]
