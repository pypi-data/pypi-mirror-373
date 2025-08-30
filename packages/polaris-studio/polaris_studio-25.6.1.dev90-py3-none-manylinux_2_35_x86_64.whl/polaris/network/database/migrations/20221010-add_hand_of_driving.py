# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.db_utils import write_about_model_value


def migrate(conn):
    write_about_model_value(conn, "hand_of_driving", "RIGHT")
