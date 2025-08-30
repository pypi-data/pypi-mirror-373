# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import time
from contextlib import contextmanager
from math import floor


def function_timing(func, return_value_from="block"):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        retval = func(*args, **kwargs)
        end_time = time.time()
        duration = start_time - end_time
        logging.info(f"duration: {seconds_to_str(duration)}")
        return retval if return_value_from == "block" else duration

    return wrapper


def time_function(fn):
    start_time = time.time()
    fn()
    return time.time() - start_time


@contextmanager
def time_block():
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logging.info(f"duration: {seconds_to_str(duration)}")


def seconds_to_str(seconds):
    h = floor(seconds / 3600)
    m = floor((seconds % 3600) / 60)
    s = round(seconds % 60)
    return f"{h:>02}:{m:>02}:{s:>02}"
