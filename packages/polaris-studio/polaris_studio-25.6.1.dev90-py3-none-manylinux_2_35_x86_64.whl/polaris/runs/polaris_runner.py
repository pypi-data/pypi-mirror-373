# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import traceback
from pathlib import Path
from shutil import rmtree, which
from datetime import datetime

from polaris.runs.scenario_file import (
    apply_modification,
    get_desired_output_dir,
    find_next_available_filename,
)
from polaris.utils.cmd_runner import run_cmd, no_printer
from polaris.utils.logging_utils import function_logging
from polaris.utils.numa.numa import NumaHardware
from retry.api import retry_call


def do_nothing(*args, **kwargs):
    pass


def get_container_runtime():
    apptainer_path = which("apptainer")
    if apptainer_path:
        return "apptainer"
    singularity_path = which("singularity")
    if singularity_path:
        return "singularity"
    logging.error("Neither apptainer nor singularity is available on this system, cannot run apptainer image.")
    raise RuntimeError("Neither apptainer nor singularity is available on this system, cannot run apptainer image.")


@function_logging("  Running Polaris")
def run(
    project_dir: Path,
    polaris_exe: Path,
    base_scenario_file: str,
    scenario_modifiers,
    threads,
    printer=no_printer,
    clean_output_folder=True,
    crash_handler=do_nothing,
    run_command=run_cmd,
    numa_threads=None,
    result_evaluator=do_nothing,
    num_retries=1,
):
    base_scenario_file = str(project_dir / base_scenario_file)
    report_scenario_mods(scenario_modifiers, base_scenario_file)
    scenario_file = apply_modification(base_scenario_file, scenario_modifiers)

    # Figure out exactly what the expected output dir is
    output_dir = get_desired_output_dir(scenario_file, project_dir)
    if not clean_output_folder:
        output_dir = find_next_available_filename(output_dir)

    if str(polaris_exe).endswith(".sif"):
        # If we are running an apptainer image, we need to run it with the apptainer or singularity command
        container_runtime = get_container_runtime()
        # cmd = ["apptainer", "run", polaris_exe, scenario_file, str(threads)]
        cmd = [
            container_runtime,
            "run",
            "--pwd",
            str(project_dir),
            "-B",
            f"{project_dir}:{project_dir}",
            polaris_exe,
            scenario_file,
            str(threads),
        ]
    else:
        cmd = [polaris_exe, scenario_file, str(threads)]

    logging.info(f"       exe: {polaris_exe}")
    logging.info(f"      arg1: {scenario_file}")
    logging.info(f"      arg2: {threads}")
    logging.info(f"       dir: {project_dir}")

    # check for numa options, and if we aren't using them check if they are available
    if numa_threads:
        logging.info(f"      NUMA: enabled ({numa_threads=})")
    else:
        check_numa_status()

    buf = []

    # make sure that the directory we are targeting is removed
    def clean_output_and_run():
        buf.clear()  # reset the buffer
        if output_dir.exists():
            rmtree(output_dir)
        run_command(cmd, project_dir, printer, stderr_buf=buf, numa_threads=numa_threads)
        result_evaluator(output_dir)

    # define a cleanup function for failed attempts
    def clean_up_failed_run(*args):
        logging.error(f"Got an exception: {args=}")
        if not output_dir.exists():
            logging.error(f"{output_dir} was not created, not retrying")
            return True  # to stop further attempts

        # Call the user provided crash handler
        try:
            crash_handler(output_dir, buf)
        except:
            logging.error("Error while running crash handler")
            tb = traceback.format_exc()
            logging.error(tb, flush=True)

        # Move the iteration crash log into the project log folder so it doesn't get overwritten by retry
        log_file = output_dir / "log" / "polaris_progress.log"
        if log_file.exists():
            iter = output_dir.name
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_log_file = project_dir / "log" / f"polaris_progress_{iter}_{stamp}.log"
            log_file.rename(new_log_file)
            logging.error(f"POLARIS crashed, check logs in {new_log_file}")
            with open(new_log_file, "r") as f:
                for l in f.readlines()[-20:]:
                    logging.error(l.strip())

        else:
            logging.error(f"POLARIS crashed and log file [{log_file}] wasn't yet created")
            logging.error("Captured standard output:")
            for line in buf:
                logging.error(line)

    # Try running N+1 times
    # debug pro tip: set tries=1, as errors will then immediately bubble up instead of being caught by the retry_call
    retry_call(clean_output_and_run, logger=logging, tries=num_retries + 1, on_exception=clean_up_failed_run)

    if not output_dir.exists():
        logging.error("POLARIS run failed without generating an output directory or log file.")
        logging.error("Captured standard output:")
        for line in buf:
            logging.error(line)
        raise RuntimeError("POLARIS run failed without generating an output directory or log file.")

    # If after all that the finished flag still doesn't exist... throw our hands up and quit
    if not (output_dir / "finished").exists():
        logging.error("Captured standard output:")
        for line in buf:
            logging.error(line)
        raise RuntimeError(
            "This should never happen: POLARIS ran to completion, returned a successful error code but did not "
            f"generate a 'finished' file in the output director ({output_dir})"
        )

    return output_dir, scenario_file


def check_numa_status(numa_report=None):
    numa_report = numa_report or NumaHardware.from_cli()
    if not numa_report.available:
        return

    logging.info(f"!! NUMA is available but not being set (use_numa parameter for POLARIS runner) !!")
    logging.info(f"num nodes: {numa_report.num_nodes}")
    for i, n in enumerate(numa_report.nodes):
        logging.info(f"Node {i}:")
        logging.info(f"     Node Size: {n.total}")
        logging.info(f"    Free Space: {n.free}")


def report_scenario_mods(mods, scenario_file):
    if len(mods) == 0:
        logging.warning(f"No modifications to {scenario_file}?")
        return

    logging.info(f"  The following modifications will be applied to {scenario_file}:")
    pad_len = max([len(k.split(".")[-1]) for k in mods.keys()])
    for k, v in mods.items():
        k = k.split(".")[-1]
        logging.info(f"    {k:<{pad_len}} : {v}")
