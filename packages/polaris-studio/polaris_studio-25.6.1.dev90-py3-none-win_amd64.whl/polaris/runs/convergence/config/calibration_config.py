# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from pydantic import BaseModel

from polaris.utils.config_utils import from_dict
from polaris.utils.iteration_schedule import IterationSchedule


class CalibrationSchedule(BaseModel):
    destination: IterationSchedule
    mode: IterationSchedule
    activity: IterationSchedule
    timing: IterationSchedule

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            kwargs = {"first_iteration": 1, "last_iteration": 21, "every_x_iter": 5}
        if "last_iteration" in kwargs:
            # User was lazy and doesn't want to type a schedule for each type of cal, just repeat the same one
            super().__init__(
                destination=from_dict(IterationSchedule, kwargs),
                mode=from_dict(IterationSchedule, kwargs),
                timing=from_dict(IterationSchedule, kwargs),
                activity=from_dict(IterationSchedule, kwargs),
            )
        else:
            super().__init__(**kwargs)


class CalibrationConfig(BaseModel):
    """Configuration class for the POLARIS calibration procedure.

    Calibration in POLARIS occurs by determining a delta from observed counts for key models (activity generation,
    mode choice, destination choice, timing choice) and using this to adjust the Alternative Specific Constants
    (ASC) of that model. This is done by modifying the JSON files in the root of the project at specified
    'calibration' iterations and then allowing the model to stabilise before re-evaluating.
    """

    enabled: bool = False
    """Flag that defines whether the calibation is used or not in a model run"""

    target_csv_dir: Path = "calibration_targets"
    """Directory where the calibration target files are located (mode_choice_targets.csv, 
    destination_choice_targets.csv, timing_choice_targets.csv, activity_generation_targets.csv)
    """

    calibration_schedule: CalibrationSchedule = CalibrationSchedule()
    """A schedule for when to do each type of calibration {activity, destination, mode, timing}
    """

    destination_vot_max_adj: float = 0.2
    """The maximum percentage change to adjust destination choice distance multiplier in a single step."""

    num_planned_activity_iterations: int = 0
    """Number of activity-generation only iterations that should be run for warm-starting the ASCs in the 
       abm_init iteration
    """

    step_size: float = 2.0
    """The rate at which the calibrated ASCs are changed during each calibration iteration (e.g., 2 means calibrated values are increased/decreased by 2x the value they should be based on the gap in model outputs and targets)"""

    def normalise_paths(self):
        self.target_csv_dir = Path(self.target_csv_dir).resolve()
