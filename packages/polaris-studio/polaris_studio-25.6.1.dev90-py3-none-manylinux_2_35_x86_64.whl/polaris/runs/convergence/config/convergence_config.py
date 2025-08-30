# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import logging
import multiprocessing as mp
import uuid
from pathlib import Path
from typing import Any, Optional, Union, List, Tuple

import psutil
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator
from polaris.analyze.kpi_utils import KPITag, standard_kpis
from polaris.runs.convergence.config.calibration_config import CalibrationConfig
from polaris.runs.convergence.config.freight_config import FreightConfig
from polaris.runs.convergence.config.incremental_loading_config import IncrementalLoadingConfig
from polaris.runs.convergence.config.workplace_stabilization_config import WorkplaceStabilizationConfig
from polaris.runs.convergence.convergence_iteration import ConvergenceIteration
from polaris.runs.polaris_version import PolarisVersion
from polaris.utils.config_utils import from_file
from polaris.utils.dir_utils import mkdir_p, with_dir
from polaris.utils.env_utils import is_windows
from polaris.utils.func_utils import deprecated

default_config_filename = "convergence_control.yaml"


class KpiFilterConfig(BaseModel):
    include_tags: Tuple[KPITag, ...] = standard_kpis
    exclude_tags: Tuple[KPITag, ...] = (KPITag.HIGH_CPU, KPITag.HIGH_MEMORY, KPITag.BROKEN)


class ConvergenceConfig(BaseModel):
    """Configuration class for the POLARIS iterative convergence process"""

    # The following is here to avoid problems in the Cython compiled version of polaris.
    # When compiled, methods (including methods of this class) are no longer "function"s they become "cyfunctions".
    # We use type(mkdir_p) to get that type at runtime so that pydantic doesn't try to check the methods are annotated.
    model_config = ConfigDict(ignored_types=(type(mkdir_p),), validate_assignment=True)

    uuid: str = None
    """Unique identifier of the model run. Not normally specified and will be populated with a
    random UUID if not provided"""

    data_dir: Path = Path(".")
    """The root directory of the model, defaults to the directory in which the convergence_control.yaml
    is located"""

    backup_dir: Optional[Path] = None
    """Deprecated: Folder where backup of the model data is created before running the model"""

    archive_dir: Path = Path("archive")
    """Deprecated: Folder from where to retrive archived data"""

    results_dir: Path = Field(default=None, validate_default=True)
    """Deprecated: Folder to where the results of the model are saved"""

    db_name: str = None
    """The filename prefix used in each of the database filenames (i.e. Chicago => Chicago-Supply.sqlite, etc)"""

    polaris_exe: Optional[Path] = Field(default=None, validate_default=True)
    """Path to the POLARIS executable to use. Three special values are supported for this: "model" - the binary that
    is located at ${data_dir}/bin/Integrated_Model, "polaris-studio" - the binary that ships with polaris-studio and
    "ci" - the latest CI executable (if available from your machine). If not specified will default to "model" if such
    exists, or to "polaris-studio" otherwise.
    """

    scenario_skim_file: Path = "scenario_abm.json"
    """Deprecated: File with scenario configuration for skimming"""

    scenario_main_init: Path = "scenario_abm.json"
    """Deprecated: File with scenario configuration for model initialization"""

    scenario_main: Path = Field(default="scenario_abm.json", validate_default=True)
    """File containing the template scenario configuration which will be adapted based on the current iteration
    """

    async_inline: bool = False
    """Flag which controls if normally asynchronous post-processing steps (which aren't needed for subsequent iterations)
    should be processed "in-line" to minimize the memory footprint. Set to True if you are having "Out of Memory" issues
    """

    num_threads: int = mp.cpu_count()
    """Number of CPU threads to use during simulation"""

    num_abm_runs: int = 2
    """Number of normal runs (ABM + DTA) to perform"""

    num_dta_runs: int = 0
    """Number of DTA-only runs to perform for a fixed demand from a previous normal iteration"""

    num_outer_loops: int = 1
    """Number of times a sequence of ABM+DTA and DTA-only runs will take place. For each num_outer_loop, num_abm_runs of ABM+DTA runs and num_dta_runs of DTA-only runs are simulated"""

    start_iteration_from: Optional[Union[int, str]] = None
    """If a model run was interrupted, start_iteration_from can be set to restart a particular iteration (i.e. 5, iteration_5, 00_skim_iteration)"""

    num_retries: int = 1
    """Number of simulation crashes that are allowed before aborting the convergence process"""

    use_numa: bool = True
    """Flag that controls whether we apply numa options to the POLARIS executable when it is run"""

    do_skim: bool = Field(default=False, validate_default=True)
    """Flag which controls whether a freeflow skimming iteration is undertaken at the beginning of the process. Note that this is rarely a
    good idea (compared to starting from existing skims) as POLARIS can take a considerable number of iterations to converge from a
    freeflow state"""

    do_abm_init: bool = False
    """Flag which controls whether a model initialization iteration is run at the beginning of the process. This iteration will synthesize
    population, generates demand, and assigns demand to the network"""

    do_pop_synth: bool = Field(default=False, validate_default=True)
    """Flag which controls whether a separate population synthesis iteration is run at the beginning of the process"""

    workplace_stabilization: WorkplaceStabilizationConfig = WorkplaceStabilizationConfig(enabled=False)
    """Configuration related to the workplace stabilization process"""

    calibration: CalibrationConfig = CalibrationConfig(enabled=False)
    """Configuration related to the calibration process"""

    freight: FreightConfig = FreightConfig(enabled=False)
    """Configuration related to the freight modelling"""

    incremental_loading: IncrementalLoadingConfig = IncrementalLoadingConfig(enabled=False)

    do_routing_MSA: bool = False
    """Deprecated: Flag controlling the use of MSA averaging across routing iterations"""

    realtime_informed_vehicle_market_share: Optional[float] = None
    """Share of vehicles that have connectivity and receive realtime information about network (pass-through to scenario file)"""

    skim_averaging_factor: Optional[float] = None
    """The proportional weight given to skims observed in the current iteration as they are mixed with previous iteration skims
    to produce the output skims for this iteration. Output = (1-w) * previous + w * current."""

    capacity_expressway: Optional[float] = None
    """Capacity of the expressway functional class to be used for the convergence run (pass-through to scenario file)"""

    capacity_arterial: Optional[float] = None
    """Capacity of the arterial functional class to be used for the convergence run (pass-through to scenario file)"""

    capacity_local: Optional[float] = None
    """Capacity of the local functional class to be used for the convergence run (pass-through to scenario file)"""

    population_scale_factor: float = 1.0
    """Population scaling factor"""

    trajectory_sampling: float = 0.01
    """Proportion of trajectories that are written to the database in each simulation iteration (pass-through to scenario file)"""

    add_rsus: bool = False
    """Deprecated"""
    rsu_highway_pr: float = 0.0
    """Deprecated"""
    rsu_major_pr: float = 0.0
    """Deprecated"""
    rsu_minor_pr: float = 0.0
    """Deprecated"""
    rsu_local_pr: float = 0.0
    """Deprecated"""
    rsu_enabled_switching: bool = False
    """Deprecated"""

    fixed_connectivity_penetration_rates_for_cv: Optional[float] = None

    highway_skim_file_name: str = "highway_skim_file.omx"
    """Name of the highway skim file"""

    transit_skim_file_name: str = "transit_skim_file.omx"
    """Name of the transit skim file"""

    skim_interval_endpoints: List[int] = [240, 360, 420, 480, 540, 600, 720, 840, 900, 960, 1020, 1080, 1140, 1200] + [
        1320,
        1440,
    ]
    """An array of skimming intervals in minutes (since midnight) where each value denotes the end of the bin starting
    from the previous value or time 0"""

    seed: Optional[int] = None
    """Simulation seed for reproducible random number generator seeding. Note 0 evaluates to a random number."""

    skim_seed: Optional[int] = None
    """Simulation skim seed for reproducible selection of skim locations and times. Note 0 evaluates to a random number."""

    user_data: Optional[Any] = None
    """user_data is a general purpose storage location that can used to carry study-specific parameters which need
    to be accessible inside callback methods across multiple iterations"""

    scenario_mods: Optional[Any] = {}
    """Scenario modifications that should be automatically applied on each iteration."""

    kpis: KpiFilterConfig = KpiFilterConfig()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.uuid is None:
            self.uuid = uuid.uuid4().hex

    @classmethod
    def from_file(cls, file: Union[str, Path]):
        file_dir = Path(file).parent.resolve()
        return from_file(cls, file).normalise_paths(file_dir)

    @classmethod
    def from_dir(cls, dir: Union[str, Path]):
        config_in_this_dir = Path(dir) / default_config_filename
        config_in_parent_dir = Path(dir).parent / default_config_filename
        if config_in_this_dir.exists():
            return cls.from_file(config_in_this_dir)
        if config_in_parent_dir.exists():
            return cls.from_file(config_in_parent_dir)
        raise FileNotFoundError(f"Can't find {default_config_filename} in {dir} or its parent dir")

    def pretty_print(self, indent=""):
        max_key = max(len(str(k)) for k in self.model_dump().keys())
        return [f"{indent}{k.ljust(max_key)} = {v}" for k, v in self.model_dump().items()]

    def normalise_paths(self, relative_to):
        # print(self)
        with with_dir(relative_to):
            self.data_dir = self.data_dir.resolve()
        with with_dir(self.data_dir):
            self.backup_dir = self.backup_dir.resolve() if self.backup_dir is not None else None
            self.archive_dir = self.archive_dir.resolve()
            self.results_dir = self.results_dir.resolve()
            self.calibration.normalise_paths()

        if self.db_name is None:
            self.db_name = self.load_scenario_json()["General simulation controls"]["database_name"]

        # If we have less than 200GB lets do our async processing in-line to avoid memory issues
        if (psutil.virtual_memory().total < 200000000000) and self.db_name in ["Chicago", "Detroit", "Atlanta"]:
            self.async_inline = True

        return self

    def load_scenario_json(self):
        with open(self.data_dir / self.scenario_main, "r") as fl:
            return json.load(fl)

    def set_from_dict(self, _dict):
        """
        Set underlying properties using an input dictionary of values. This is very useful when applying
        a batch of overrides programatically (i.e. via EQ/SQL). The given dictionary should have keys that
        correspond to named members (i.e. { "num_abm_runs": 7 }) along with the desired state of that
        property. Nested members can be configured with nested dictionaries or using a.b syntax (i.e.
        {"workplace_stabilization.enabled": False} or {"workplace_stabilization": {"enabled": True}} ).
        """
        for k, v in _dict.items():
            # Transform any ("a.b", 7) into ("a", {"b": 7})
            if isinstance(k, str) and "." in k:
                k, key_inner = k.split(".")
                v = {key_inner: v}

            # Handle any sub-dictionaries (only 1 level supported for now)
            if isinstance(v, dict):
                inner_config = getattr(self, k)
                if isinstance(inner_config, dict):
                    # If the attribute is a dictionary, just merge them together
                    logging.info(f"{k} -> {v}")
                    setattr(self, k, inner_config | v)
                else:
                    # Otherwise assume that it's some type of pydantic model and set it's attributes
                    for kk, vv in v.items():
                        logging.info(f"{k}.{kk} -> {vv}")
                        setattr(inner_config, kk, vv)
            else:
                logging.info(f"{k} -> {v}")
                setattr(self, k, v)

    @deprecated
    def supply_file(self):
        return Path(f"{self.db_name}-Supply.sqlite")

    @deprecated
    def demand_file(self):
        return Path(f"{self.db_name}-Demand.sqlite")

    @deprecated
    def result_file(self):
        return Path(f"{self.db_name}-Result.sqlite")

    def iterations(self):
        setup_iterations = []
        if self.do_skim:
            setup_iterations.append(ConvergenceIteration(is_skim=True))
        if self.do_pop_synth:
            setup_iterations.append(ConvergenceIteration(is_pop_synth=True))
        if self.do_abm_init:
            setup_iterations.append(ConvergenceIteration(is_abm_init=True))

        iterations = []
        for _ in range(1, self.num_outer_loops + 1):
            iterations += [ConvergenceIteration() for _ in range(1, self.num_abm_runs + 1)]
            iterations += [ConvergenceIteration(is_dta=True) for _ in range(1, self.num_dta_runs + 1)]
        for i, it in enumerate(iterations):
            it.iteration_number = i + 1
        if iterations != []:
            iterations[-1].is_last = True

        return self.filter_based_on_start_iter(setup_iterations + iterations, self.start_iteration_from)

    def filter_based_on_start_iter(self, iterations, start_from=None):
        start_from = start_from or self.start_iteration_from

        if not start_from:
            return iterations

        # if it's an integer - create a string reprr of the corresponding normal iteration object
        if isinstance(start_from, int) or start_from.isdigit():
            start_from = str(ConvergenceIteration.of_type("normal", start_from))

        try:
            idx = [str(e) for e in iterations].index(str(start_from))
            return iterations[idx:]
        except:
            doing_str = ",".join([str(e) for e in iterations])
            raise RuntimeError(f"Couldn't start from {start_from}, it's not in the list we are doing {doing_str}")

    def check_exe(self):
        logging.info("POLARIS Executable:")
        ver = PolarisVersion.from_exe(self.polaris_exe)
        ver.log()

    # -------------------------------------------------------------------------------
    # Validators for populating default values (can be based on other defined values)
    # -------------------------------------------------------------------------------
    @field_validator("results_dir", mode="before")
    def val_results_dir(cls, v, info: ValidationInfo) -> Path:
        return v or (info.data["data_dir"] / "simulation_results")

    @field_validator("polaris_exe", mode="before")
    def default_polaris_exe(cls, v, info: ValidationInfo):
        exists = lambda x: Path(x).absolute() if x and Path(x).exists() else None
        extension = ".exe" if is_windows() else ""
        model_bin = info.data["data_dir"] / "bin" / f"Integrated_Model{extension}"
        polaris_bin = Path(__file__).parent.parent.parent.parent / "bin" / f"Integrated_Model{extension}"

        # if the user asks for a special binary figure out the correct path for it
        if v is not None:
            if str(v).lower() == "ci":
                v = get_bin_on_ci_server()
            elif str(v).lower() == "model":
                v = model_bin
            elif str(v).lower() == "polaris-studio":
                v = polaris_bin
        else:  # If not specified, try out some known executables that might exist
            return exists(model_bin) or exists(polaris_bin)

        # Otherwise the user specified an exe, so just figure out its full path and return that
        return Path(v).absolute()

    @field_validator("scenario_main", mode="before")
    def default_scenario_main(cls, v, info: ValidationInfo):
        return v or (info.data["data_dir"] / "scenario_abm.json")

    @field_validator("do_pop_synth", mode="before")
    def default_do_pop_synth(cls, v, info: ValidationInfo):
        return not not v

    @field_validator("do_skim", mode="before")
    def default_do_skim(cls, v, info: ValidationInfo):
        return v and "scenario_skim_file" in info.data

    # -------------------------------------------------------------------------------


def get_bin_on_ci_server():
    """returns the location of the latest POLARIS executable from ANL's CI infrastructure."""
    return (
        r"\\vms-cfs2.taps.anl.gov\Cluster2\POLARIS_CI_CD_ARTIFACTS\polaris-linux\develop\latest\windows\Integrated_Model.exe"
        if is_windows()
        else "/mnt/ci/polaris-linux/develop/latest/ubuntu-20.04/Integrated_Model"
    )
