# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shlex
from subprocess import Popen, PIPE, STDOUT

from polaris.utils.env_utils import is_windows
from polaris.utils.numa.numa import get_numa_nodes_to_use, get_numactl_opts, write_nodes_in_use


def run_cmd(cmd, working_dir, printer=print, ignore_errors=False, stderr_buf=None, numa_threads=None):
    if isinstance(cmd, str):
        cmd = shlex.split(cmd, posix=not is_windows())

    # On windows we get problems with file not found when running an exe with backslashes in
    cmd[0] = str(cmd[0]).replace("\\", "/")

    # NUMA: prefix our invokation with the numactl opts and store them in a temp file for others to discover
    numa_options_file = None
    if numa_threads:
        numa_nodes = get_numa_nodes_to_use(numa_threads)
        numa_options_file = write_nodes_in_use(numa_nodes, numa_threads)

        cmd = get_numactl_opts(numa_nodes) + cmd

    logging.info(f"{cmd=}")
    with Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=working_dir, bufsize=0, universal_newlines=True) as p:
        exit_code = None
        blank_line_buffer = []
        while True:
            line = p.stdout.readline().strip()
            if not line:
                blank_line_buffer.append(line)
                exit_code = p.poll()
            else:
                if stderr_buf is not None:
                    [stderr_buf.append(e) for e in blank_line_buffer]
                    stderr_buf.append(line)
                [printer(e) for e in blank_line_buffer]
                blank_line_buffer.clear()
                printer(line)

            if exit_code is not None:
                break

    if numa_options_file is not None and numa_options_file.exists():
        logging.info(f"    Deleting {numa_options_file} at end of cmd_runner")
        numa_options_file.unlink()

    if exit_code != 0:
        cmd_str = " ".join([str(e) for e in cmd])
        logging.critical(f"Non-zero exit code ({exit_code}) returned for cmd: {cmd_str}")
        if ignore_errors:
            logging.critical("Ignoring failure - good luck")
            return exit_code
        raise RuntimeError(f"Command failed with exit_code {exit_code}")

    return exit_code


def run_cmd_and_capture(cmd, **kwargs):
    rv = []

    def foo(msg):
        rv.append(msg)

    run_cmd(cmd, working_dir=None, printer=foo, **kwargs)
    return rv


def no_printer(_):
    pass
