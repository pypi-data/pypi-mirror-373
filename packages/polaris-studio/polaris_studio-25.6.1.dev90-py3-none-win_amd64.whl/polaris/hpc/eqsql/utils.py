# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import inspect
import json
import logging
import re
from functools import wraps

from sqlalchemy import func, text


def clear_idle_pg_connection():
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            args_dict = inspect.getcallargs(function, *args, **kwargs)
            if "engine" in args_dict:
                try:
                    with args_dict["engine"].connect() as conn:
                        conn.execute(text("SELECT 1"))
                except Exception:
                    pass
            elif "conn" in args_dict:
                try:
                    args_dict["conn"].execute(text("SELECT 1"))
                except Exception as err:
                    logging.warning(
                        "Your database conn seems to have become idle - you can likely get around this problem by "
                        "re-running the cell of your notebook."
                    )
                    raise RuntimeError("Idle conn Object") from err

            return function(*args, **kwargs)

        return wrapper

    return decorator


def from_id(cls, engine, id):
    with engine.connect() as conn:
        return from_cursor_result(cls, conn.execute(cls.table().select().filter(cls.key_col() == id)))


def from_cursor_result(cls, result):
    row = result.fetchone()
    if row is None:
        return None
    return from_row(cls, row)


def from_row(cls, row):
    return cls(**dictify_dict_fields(row._asdict()))


def dictify_dict_fields(dct):
    if "input" in dct:
        dct["input"] = json.loads(dct["input"])
    if "definition" in dct:
        dct["definition"] = json.loads(dct["definition"])
    return dct


def update_from_db(obj, engine):
    with engine.connect() as conn:
        cursor_result = conn.execute(type(obj).table().select().filter(type(obj).key_col() == obj.primary_key))
        data = dict(cursor_result.fetchone()._asdict().items())
        return obj._replace(**dictify_dict_fields(data))


def update_to_db(obj, engine, **kwargs):
    from sqlalchemy.dialects.postgresql import insert

    if "updated_at" not in kwargs:
        kwargs["updated_at"] = func.now()
    if "worker_id" in kwargs:
        check_worker_regex(kwargs["worker_id"])
    for k, v in kwargs.items():
        if isinstance(v, dict):
            kwargs[k] = json.dumps(v)
    for k in obj._fields:
        if k not in kwargs:
            v = getattr(obj, k)
            kwargs[k] = json.dumps(v) if isinstance(v, dict) else v
    with engine.connect() as conn:
        obj_type = type(obj)
        insert_values = {**kwargs, obj_type.key_col().name: obj.primary_key}

        insert_stmt = insert(obj_type.table()).values(insert_values)

        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[obj_type.key_col()], set_={key: insert_stmt.excluded[key] for key in kwargs.keys()}
        ).returning(obj_type.table().c)

        return from_cursor_result(obj_type, conn.execute(upsert_stmt))


def check_worker_regex(worker_id: str):
    try:
        re.compile(worker_id)
    except Exception as e:
        raise ValueError(f"worker_id regex '{worker_id}' is invalid! re.compile returned {e}") from e
