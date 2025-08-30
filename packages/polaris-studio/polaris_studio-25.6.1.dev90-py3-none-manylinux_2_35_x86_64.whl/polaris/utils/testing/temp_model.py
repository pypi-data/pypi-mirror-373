# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from tempfile import gettempdir

from polaris import Polaris
from polaris.utils.env_utils import is_windows

# We can move these to being fixtures once we everything as pytests
test_file_cache = Path(gettempdir()) / "polaris_studio_testing" / "cache"


def new_temp_folder() -> Path:
    right_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir = test_file_cache.parent / f"{right_now}--{uuid.uuid4().hex[:4]}"
    while dir.exists():
        dir = test_file_cache.parent / f"{right_now}--{uuid.uuid4().hex[:4]}"
    dir.mkdir(parents=True)
    return dir


def TempModel(model_name):
    fldr = f"C:/temp_container/{model_name}" if is_windows() else f"/tmp/{model_name}"
    new_fldr = new_temp_folder()
    shutil.copytree(fldr, new_fldr, dirs_exist_ok=True)

    Polaris.from_dir(Path(new_fldr)).upgrade()
    return Path(new_fldr)
