# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# from datetime import datetime, date
import logging
import subprocess
from pathlib import Path

previous_year_release = 2025
previous_month_release = 6

year_release = 2025
month_release = 6
day_release = 1
alpha = 90

__version__ = f"{str(year_release)[-2:]}.{str(month_release).zfill(2)}.{str(day_release).zfill(3)}.dev{alpha}"

try:
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(Path(__file__).parent.parent))
except:  # noqa: E722

    recorded = Path(__file__).parent / "sha.txt"
    if recorded.exists():
        with open(recorded, "r") as f:
            git_sha = recorded.read_text().strip()  # type: ignore
    else:
        git_sha = "NO GIT SHA FOUND"  # type: ignore
        logging.error("NO GIT SHA FOUND")
