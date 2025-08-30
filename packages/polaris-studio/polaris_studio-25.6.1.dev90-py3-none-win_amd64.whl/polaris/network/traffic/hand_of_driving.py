# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os
import sqlite3
from enum import Enum
from typing import Optional

from polaris.utils.database.db_utils import read_about_model_value, read_and_close


# Placeholder since enum.StrEnum requires >= Python 3.11
class StrEnum(str, Enum):
    pass


class DrivingSide(StrEnum):
    RIGHT = "R"
    LEFT = "L"

    # For compatibility with the previous driving side values
    def __int__(self):
        return 1 if self == DrivingSide.RIGHT else -1

    def other(self):
        return DrivingSide.LEFT if self == DrivingSide.RIGHT else DrivingSide.RIGHT

    def other_index(self, other):
        return 0 if self == other else -1  # where self/other are each a DrivingSide

    def long_name(self):
        return "RIGHT" if self == DrivingSide.RIGHT else "LEFT"

    def __str__(self):
        return self.RIGHT if self == DrivingSide.RIGHT else self.LEFT


def get_driving_side(
    database_path: Optional[os.PathLike] = None, conn: Optional[sqlite3.Connection] = None
) -> DrivingSide:
    if database_path is None and conn is None:
        raise Exception("To retrieve an hand of driving you must provide a database connection OR a database path")
    with conn or read_and_close(database_path) as conn:
        side = read_about_model_value(conn, "hand_of_driving", cast=str, default="RIGHT")
        return DrivingSide.LEFT if side.upper() == "LEFT" else DrivingSide.RIGHT
