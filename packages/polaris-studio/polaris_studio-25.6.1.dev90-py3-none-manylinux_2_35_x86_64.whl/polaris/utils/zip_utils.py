# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import subprocess
import time
from polaris.utils.env_utils import is_windows


def fast_compress(tar_gz_file, files, base_dir):
    tar_gz_file.parent.mkdir(parents=True, exist_ok=True)
    files_str = " ".join(str(f) for f in files)
    if not is_windows():
        cmd = f'tar --use-compress-program="pigz -k " -cf {tar_gz_file} {files_str}'
    else:
        cmd = f"tar -czf {tar_gz_file} {files_str}"
    start = time.time()
    subprocess.check_output(cmd, shell=True, cwd=base_dir, encoding="utf-8")
    end = time.time()
    print(f"Compress Time: {end - start}")
