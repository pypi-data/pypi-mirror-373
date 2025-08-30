# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pydantic import BaseModel

from polaris.utils.iteration_schedule import IterationSchedule


class WorkplaceStabilizationConfig(BaseModel):
    """Configuration class for the POLARIS workplace stabilization process.

    Workplace stabilization in POLARIS is the process by which long-term decisions regarding work location
    are introduced to an overall iterative process. Work places are allowed to be updated based on current
    congestion conditions on specified iterations, a number of iterations are then run using those updated
    choices to allow the congestion to stabilize before repeating the process.
    """

    enabled: bool = False
    """Flag which controls if any workplace stabilization will be undertaken during the model run"""

    schedule: IterationSchedule = IterationSchedule(first_iteration=1, last_iteration=31, every_x_iter=5)

    def should_choose_workplaces(self, iteration):
        return self.enabled and self.schedule.at_iteration(iteration)

    def number_of_prior_workplaces_iteration(self, i: int) -> float:
        return float(sum([self.should_choose_workplaces(e) for e in range(1, i)]))
