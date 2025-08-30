# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import List, Tuple
from pydantic import BaseModel

from polaris.runs.convergence.convergence_iteration import ConvergenceIteration


class IncrementalLoadingConfig(BaseModel):
    """Configuration class for the POLARIS Incremental Loading"""

    enabled: bool = False
    """Flag which controls if any incremental loading should be undertaken during the model run"""

    profile: List[Tuple[int, float]] = None
    """Piecewise linear definition of the loading profile to be used.
    This should be a list of pairs (iteration, percentage of demand to load) e.g. [(1,0.5),(6,1.0)]."""

    # What is the
    def percentage_at_iteration(self, iteration: ConvergenceIteration):
        if not self.enabled or not self.profile:
            return 1.0
        assert isinstance(iteration, ConvergenceIteration) or isinstance(iteration, int)
        if isinstance(iteration, ConvergenceIteration):
            iteration_number = iteration.iteration_number if iteration.is_standard else 0
        else:
            iteration_number = iteration

        # Sort profile by iteration, just in case
        profile = sorted(self.profile)

        # Handle before the first point
        if iteration_number <= profile[0][0]:
            return profile[0][1]

        # Handle after the last point
        if iteration_number >= profile[-1][0]:
            return profile[-1][1]

        # Find the interval that contains the current iteration
        for i in range(len(profile) - 1):
            x0, y0 = profile[i]
            x1, y1 = profile[i + 1]
            if x0 <= iteration_number <= x1:
                # Linear interpolation
                fraction = (iteration_number - x0) / (x1 - x0)
                return y0 + fraction * (y1 - y0)

        # Fallback (should never hit)
        return 1.0
