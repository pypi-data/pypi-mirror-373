# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from dateutil.parser import parse

from polaris.utils.file_utils import readlines

PROGRESS_PATTERN = "departed="
TIME_PATTERN = "([0-9][0-9]):([0-9][0-9]):([0-9][0-9])"


def parse_timing_line(l):
    tokens = l.split(" ")
    dt = parse(f"{tokens[0]} {tokens[1]}")
    xs = [(x, re.search(TIME_PATTERN, x)) for x in tokens[2:]]
    xs = [x for x, y in xs if y]
    x = datetime.strptime(xs[0], "%H:%M:%S,")
    return (dt, x)


def read_timing(output_dir):
    log_file = Path(output_dir) / "log" / "polaris_progress.log"
    with open(log_file, "r") as f:
        lines = [l.strip() for l in f.readlines() if re.search(PROGRESS_PATTERN, l.strip())]
    lines = [parse_timing_line(l) for l in lines]
    return pd.DataFrame(lines, columns=["timestamp", "simulation_time"])


def read_total_duration(output_dir):
    log_file = Path(output_dir) / "log" / "polaris_progress.log"
    lines = [l.strip() for l in readlines(log_file) if "Main loop duration" in l]
    if not lines:
        return None
    m = re.search(rf"Main loop duration: *{TIME_PATTERN}", lines[0])
    return timedelta(hours=int(m[1]), minutes=int(m[2]), seconds=int(m[3])).total_seconds()
