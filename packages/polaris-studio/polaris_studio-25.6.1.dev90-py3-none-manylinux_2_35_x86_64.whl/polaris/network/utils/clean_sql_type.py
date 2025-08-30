# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.utils.database.sqlite_types_afinity import type_dict


def clean_sql_type(col_type, table_name, raise_error=True):
    col_type = col_type if "(" not in col_type else col_type[: col_type.find("(")].strip()
    if col_type.upper() not in type_dict:
        if raise_error:
            raise TypeError(f"I don't know how to add column with type {col_type} for table {table_name}")
        else:
            return None
    return type_dict[col_type.upper()]
