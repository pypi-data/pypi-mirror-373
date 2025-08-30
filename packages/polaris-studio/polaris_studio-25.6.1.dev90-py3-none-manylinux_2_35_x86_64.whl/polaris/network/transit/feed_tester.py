# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import zipfile
from pathlib import Path


def test_feed(src: Path) -> bool:
    # Test is GTFS feed has everything we need from it
    zip_archive = zipfile.ZipFile(src)

    files = ["routes.txt", "calendar.txt", "stop_times.txt"]

    if not all(f in zip_archive.namelist() for f in files):
        return False
    return True
