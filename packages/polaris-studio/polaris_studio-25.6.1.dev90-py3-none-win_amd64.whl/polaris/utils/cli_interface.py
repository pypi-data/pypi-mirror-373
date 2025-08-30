# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
# !/usr/bin/env python

import logging
import os
import shutil
from pathlib import Path

import click

from polaris.project.polaris import Polaris  # noqa: E402
from polaris.runs import summary
from polaris.utils.checker_utils import check_critical
from polaris.utils.file_utils import download_and_extract
from polaris.utils.logging_utils import polaris_logging


@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("You can only invoke commands run, upgrade or build_from_git")


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
@click.option(
    "--config_file",
    required=False,
    help="Convergence control file override. Defaults to convergence_control.yaml",
    default=None,
)
@click.option("--num_threads", required=False, help="Number of threads to use for model run", type=int)
@click.option(
    "--population_scale_factor", required=False, help="Population sampling factor", type=click.FloatRange(0.0001, 1.0)
)
@click.option(
    "--do_upgrade/--no_upgrade",
    required=False,
    help="Whether we want to upgrade the model to the latest structure before running it",
)
@click.option(
    "--do_pop_synth/--no_pop_synth",
    required=False,
    default=None,
    help='Override the "should run population sythesizer" flag from convergence_control.yaml',
)
@click.option(
    "--do_skim/--no_skim",
    required=False,
    default=None,
    help='Override the "should run skimming" flag from convergence_control.yaml',
)
@click.option(
    "--do_abm_init/--no_abm_init",
    default=None,
    required=False,
    help="Override the 'should run abm_init iteration' flag from convergence_control.yaml ",
)
@click.option(
    "--polaris_exe",
    required=False,
    help="Path to the polaris executable to be used. Defaults to the executable shipped with polaris",
)
@click.option(
    "--num_abm_runs",
    required=False,
    help="Number of ABM runs to be run. Defaults to the value in convergence_control.yaml",
    type=int,
)
@click.option(
    "--num_dta_runs",
    required=False,
    help="Number of DTA runs to be run. Defaults to the value in convergence_control.yaml",
    type=int,
)
@click.option(
    "--start_iteration_from",
    required=False,
    help="Start running from this iteration. Defaults to the value in convergence_control.yaml",
    type=int,
)
def run(
    data_dir,
    config_file,
    do_upgrade,
    num_threads,
    population_scale_factor,
    do_pop_synth,
    do_skim,
    do_abm_init,
    polaris_exe,
    num_abm_runs,
    num_dta_runs,
    start_iteration_from,
):
    model = Polaris.from_dir(data_dir, config_file=config_file)

    if do_upgrade:
        model.upgrade()

    args = {
        "num_threads": num_threads,
        "do_pop_synth": do_pop_synth,
        "do_skim": do_skim,
        "do_abm_init": do_abm_init,
        "polaris_exe": polaris_exe,
        "num_abm_runs": num_abm_runs,
        "num_dta_runs": num_dta_runs,
        "start_iteration_from": start_iteration_from,
        "population_scale_factor": population_scale_factor,
    }
    args = {k: v for k, v in args.items() if v is not None}
    model.run(**args)


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
@click.option("--force", required=False, help="Force the application of the given migration ID", multiple=True)
def upgrade(data_dir, force):
    model = Polaris.from_dir(data_dir)
    model.upgrade(force_migrations=force)


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
def check(data_dir):
    model = Polaris.from_dir(data_dir)

    logging.info("Consistency Checks")
    model.network.checker.consistency_tests()

    logging.info("Critical Checks")
    if check_critical(model) != []:
        exit(1)


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
@click.option("--city", required=True, help="City model to build - corresponds to the git repository")
@click.option("--db_name", required=False, help="DB name. Defaults to the value in abm_scenario.json", default=None)
@click.option(
    "--overwrite",
    required=False,
    help="Overwrite any model in the target directory. Defaults to False",
    default=False,
)
@click.option(
    "--inplace",
    required=False,
    help="Build in place or a sub-directory. Defaults to subdirectory",
    is_flag=True,
    default=True,
)
@click.option("--upgrade", required=False, help="Whether we should upgrade the model after building it")
@click.option("--branch", required=False, help="Branch to build from", default="main")
@click.option("--scenario", required=False, help="Scenario to be built. Defaults to the base one", default=None)
def build_from_git(data_dir, city, db_name, overwrite, inplace, upgrade, branch, scenario):
    polaris_logging()
    model = Polaris.build_from_git(
        model_dir=data_dir,
        city=city,
        db_name=db_name,
        overwrite=overwrite,
        inplace=inplace,
        git_dir=data_dir,
        branch=branch,
        scenario_name=scenario,
    )
    polaris_logging(Path(data_dir) / "log" / "polaris-studio.log")
    if upgrade:
        model.upgrade()


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
@click.option("--city", required=False, help="City model to build")
@click.option("--upgrade", required=False, help="Whether we should upgrade the model after building it")
@click.option("--dbtype", required=False, help="Which DB to build, defaults to all")
@click.option("--overwrite/--no-overwrite", default=False, help="Overwrite the file(s) if exists")
@click.option("--scenario", required=False, help="Scenario to be built. Defaults to the base one", default=None)
def build(data_dir, city, upgrade, dbtype, overwrite, scenario):
    Polaris.restore(
        data_dir=Path(data_dir), city=city, dbtype=dbtype, upgrade=upgrade, overwrite=overwrite, scenario_name=scenario
    )


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
@click.option("--overwrite/--no-overwrite", default=False, help="Overwrite the file(s) if exists")
def get_demo(data_dir, overwrite):
    data_dir = Path(data_dir)
    if data_dir.exists() and overwrite:
        print(f"Overwriting existing data in {data_dir}")
        shutil.rmtree(data_dir)
    elif data_dir.exists():
        print(f"Data directory {data_dir} already exists. Use --overwrite to overwrite it.")
        return

    polaris_logging(data_dir / "log" / "polaris-studio.log")

    download_and_extract("https://polaris.taps.anl.gov/models/bloomington-demo-latest.tar.gz", data_dir)

    data_dir = list(data_dir.glob("Bloomington-*"))
    if len(data_dir) == 0:
        raise FileNotFoundError(f"There was an error while downloading to{data_dir}")
    data_dir = data_dir[0]
    logging.info("Bloomington demo model downloaded and extracted")
    logging.info(f"   Model:        {data_dir}/Model")
    logging.info(f"   Instructions: {data_dir}/Setup and Run Polaris.pptx")
    logging.info("   ")
    logging.info("Start a run with:")
    logging.info(f"   polaris run --data_dir {data_dir}/Model --do_upgrade --num_threads 4")


@cli.command()  # type: ignore
@click.option("--data_dir", required=True, help="Model directory", default=os.getcwd)
def aggregate_summaries(data_dir):
    summary.aggregate_summaries(Path(data_dir), save=True)


@cli.command()  # type: ignore
@click.option("--license_path", required=True, help="Adds the license to the Python installation folder")
def add_license(license_path):
    from shutil import copy

    if not Path(license_path).exists():
        raise FileNotFoundError(f"License file not found: {license_path}")

    bin_folder = Path(__file__).parent.parent / "bin"
    copy(license_path, bin_folder)


@cli.command()  # type: ignore
def test_spatialite():
    from polaris.utils.database.spatialite_utils import spatialite_available

    spatialite_available()


if __name__ == "__main__":
    cli()  # type: ignore
