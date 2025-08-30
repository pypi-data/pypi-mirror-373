# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import numpy as np

INTEGER = ["INT", "INTEGER", "TINYINT", "SMALLINT", "MEDIUMINT", "BIGINT", "UNSIGNED BIG INT", "INT2", "INT8"]
TEXT = ["CHARACTER", "VARCHAR", "VARYING CHARACTER", "NCHAR", "NATIVE CHARACTER", "NVARCHAR", "TEXT", "CLOB"]
REAL = ["REAL", "DOUBLE", "DOUBLE PRECISION", "FLOAT"]
NUMERIC = ["NUMERIC", "DECIMAL", "BOOLEAN", "DATE", "DATETIME"]

type_dict = {
    **dict.fromkeys(INTEGER, "INTEGER"),
    **dict.fromkeys(TEXT, "TEXT"),
    **dict.fromkeys(REAL, "REAL"),
    **dict.fromkeys(NUMERIC, "NUMERIC"),
}

sql_to_numpy = {"INTEGER": int, "TEXT": np.str_, "REAL": float, "NUMERIC": float}
