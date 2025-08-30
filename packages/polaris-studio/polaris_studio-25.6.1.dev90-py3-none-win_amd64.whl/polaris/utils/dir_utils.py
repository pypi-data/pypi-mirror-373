# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import contextlib
import os
import shutil
from pathlib import Path
from time import sleep

BIG_FILE_THRESHOLD = 100000000  # 100MB


def mkdir_p(dir):
    Path(dir).mkdir(exist_ok=True, parents=True)


@contextlib.contextmanager
def with_dir(chdir):
    current_dir = os.getcwd()
    os.chdir(chdir)
    try:
        yield
    finally:
        os.chdir(current_dir)


def slow_rmtree(dir: Path):
    """Work around the WSL bug that causes system failure when deleting too much
    data at once.
    """
    for x in dir.glob("*"):
        if x.is_dir():
            slow_rmtree(x)
        else:
            is_big = x.stat().st_size > BIG_FILE_THRESHOLD
            x.unlink()
            if is_big:
                sleep(1)  # put in a small pause after big files
    shutil.rmtree(dir)
