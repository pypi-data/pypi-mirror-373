# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import warnings

from polaris.utils.env_utils import is_on_ci


def can_fail(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.warning(f"Function {func.__name__} failed, but we're going to press on anyway", exc_info=True)
            logging.warning(e.args, exc_info=True)
            if is_on_ci():
                raise e

    return inner_function


def deprecated(func):
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{func.__name__} is deprecated and will be removed in a future version.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return func(*args, **kwargs)

    return wrapper
