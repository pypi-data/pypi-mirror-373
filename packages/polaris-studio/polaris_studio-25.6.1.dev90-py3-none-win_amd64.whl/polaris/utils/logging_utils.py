# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import inspect
import logging
import sys
from datetime import datetime
from functools import wraps
from os.path import dirname
from pathlib import Path
from typing import Optional

from polaris.utils.dir_utils import mkdir_p


class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Delay loading until all machines have had a chance to install
        from tzlocal import get_localzone

        tz = get_localzone()
        time_with_tz = datetime.fromtimestamp(record.created, tz=tz)

        return time_with_tz.strftime("%Y-%m-%d %H:%M:%S %Z%z")


FORMATTER = TimezoneFormatter("%(asctime)s - %(message)s")


def function_logging(msg):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            # format all arguments into a dictionary by argument name, including default arguments
            args_dict = inspect.getcallargs(function, *args, **kwargs)
            formatted_msg = msg.format(**args_dict)
            start_time = datetime.now()
            logging.info(formatted_msg)
            rv = function(*args, **kwargs)
            logging.info(f"{formatted_msg}: Done in {datetime.now() - start_time} seconds")
            return rv

        return wrapper

    return decorator


def add_file_handler(logger, logging_level, log_path: Optional[Path]):
    if log_path is None:
        return
    remove_file_handler(logger, "LOGFILE")

    mkdir_p(dirname(log_path))
    ch = logging.FileHandler(log_path)
    ch.setFormatter(FORMATTER)
    ch.set_name("LOGFILE")
    ch.setLevel(logging_level)
    logger.addHandler(ch)
    Path(log_path).parent.mkdir(exist_ok=True, parents=True)


def remove_file_handler(logger=None, handler_name="LOGFILE"):
    logger = logger or logging.getLogger()
    for h in [h for h in logger.handlers if h.name and handler_name == h.name]:
        h.close()
        logger.removeHandler(h)


def has_named_handler(logger: logging.Logger, handler_name: str):
    return len([h for h in logger.handlers if h.name and handler_name == h.name]) > 0


def ensure_stdout_handler(logger, logging_level):
    if has_named_handler(logger, "stdout"):
        return

    def add_it():
        logger.addHandler(h := logging.StreamHandler(sys.stdout))
        return h

    # Get or add a stdout handler
    handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and h.stream == sys.stdout]
    stdout_handler = handlers[0] if handlers else add_it()

    # Configure it to our liking
    stdout_handler.setLevel(logging_level)
    stdout_handler.setFormatter(FORMATTER)
    stdout_handler.set_name("stdout")

    logger.propagate = False


def polaris_logging(logfile: Optional[Path] = None):
    logger = logging.getLogger()  # just use the root logger
    logger.level = logging.INFO
    ensure_stdout_handler(logger, logging.INFO)
    add_file_handler(logger, logging.INFO, logfile)
    # debug_logger(logger)
    return logger


def level_to_string(level):
    return {logging.INFO: "INFO", logging.WARNING: "WARNING", logging.DEBUG: "DEBUG"}[level]


def debug_logger(logger):
    print(f"{logger.name} (level={level_to_string(logger.level)}, {len(logger.handlers)} handlers)")
    for i, h in enumerate(logger.handlers):
        debug_handler(h, i)


def debug_handler(h, i):
    level = level_to_string(h.level)
    if isinstance(h, logging.FileHandler):
        print(f"  Handler {i}: {h.name} (level={level}, file={h.baseFilename})")
    else:
        print(f"  Handler {i}: {h.name} (level={level})")
