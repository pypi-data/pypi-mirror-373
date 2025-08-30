# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import dataclasses
from datetime import datetime, timezone
import logging
import re
from pathlib import Path
from tempfile import gettempdir

from retry.api import retry_call

from polaris.runs.run_utils import seconds_to_str
from polaris.utils.cmd_runner import run_cmd


@dataclasses.dataclass
class PolarisVersion:
    exe_path: Path
    build_date: str
    git_branch: str
    git_sha: str

    @classmethod
    def from_exe(cls, polaris_exe):
        polaris_exe = Path(polaris_exe)
        if polaris_exe.exists():
            output = []
            work_dir = str(polaris_exe.parent)
            work_dir = gettempdir()

            def fn():
                run_cmd(f"{polaris_exe} --version", working_dir=work_dir, printer=output.append)

            try:
                retry_call(fn, logger=logging, tries=6)
            except Exception:
                logging.error(f"Can't run {polaris_exe} to determine version, check output for hints")
                logging.error(f"working dir = {work_dir}")
                for l in output:
                    logging.error(l)
                raise

            if output == []:
                logging.error(f"Can't run {polaris_exe} to determine version")
                return cls(polaris_exe, None, None, None)

            branch, sha, build_date = parse_polaris_version("\n".join(output))
            return cls(polaris_exe, build_date, branch, sha)
        else:
            return cls(polaris_exe, None, None, None)

    def log(self):
        logging.info(f"    path: {self.exe_path}")
        if self.exe_path.exists():
            logging.info("  exists: ✔")
            logging.info(f"   built: {build_date_str(self.build_date)}")
            logging.info(f"  branch: {self.git_branch}")
            logging.info(f"     SHA: {self.git_sha}")
            logging.info(f"     url: https://git-out.gss.anl.gov/polaris/code/polaris-linux/-/commit/{self.git_sha}")

        else:
            logging.info("  exists: ✘")


def build_date_str(build_date):
    if build_date is None:
        return "Couldn't determine build time"
    delta = seconds_to_str((datetime.now(timezone.utc) - build_date).total_seconds())
    return f"{build_date.strftime('%Y/%m/%d %H:%M:%S %Z')} ({delta} ago)"


def parse_polaris_version(exe_output):
    branch, sha, build_date = None, None, None
    m = re.search("Built with git branch: (.*)", exe_output)
    if m is not None:
        branch = m[1].strip()
    m = re.search("Git commit hash: (.*)", exe_output)
    if m is not None:
        sha = m[1].strip()

    m = re.search(r"Compiled at:* (.*) \(UTC\)", exe_output)
    m2 = re.search("This source file was compiled on date (.*) and at the time (.*)", exe_output)
    if m is not None:
        build_date = datetime.strptime(m[1].strip(), "%Y%m%d-%H%M%S")
    elif m2 is not None:
        a = m2[1].strip()
        b = m2[2].strip()
        build_date = datetime.strptime(f"{a}-{b}", "%b %d %Y-%H:%M:%S")

    # assume that old (m2 matching) dates were in UTC (prove me wrong!)
    build_date = build_date.replace(tzinfo=timezone.utc)

    return branch, sha, build_date
