# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pydantic import BaseModel

from polaris.utils.iteration_schedule import IterationSchedule


class FreightConfig(BaseModel):
    """Configuration class for the POLARIS Freight module

    Freight currently has b2b demand synthesis, b2b/b2c delivery simulation and tour chaining of fixed trips.
    More functionality is being added across the mid 2025 period.
    """

    enabled: bool = False
    """Flag which controls if any freight modelling will be undertaken during the model run"""

    b2b_demand_synthesis_schedule: IterationSchedule = IterationSchedule(
        first_iteration=1, last_iteration=0, every_x_iter=1, on_abm_init=True
    )
    """Controls if B2B demand synthesis is run (default is to only run during the abm init iteration)
       but any schedule can be configured
    """

    simulate_deliveries_schedule: IterationSchedule = IterationSchedule(
        first_iteration=5, last_iteration=31, every_x_iter=5, on_abm_init=True
    )

    # Are we doing anything that would generate outputs into the Freight database at this iteration?
    def should_do_anything(self, iteration):
        return self.should_synthesize_b2b_demand(iteration) or self.should_model_deliveries(iteration)

    def should_synthesize_b2b_demand(self, iteration):
        return self.enabled and self.b2b_demand_synthesis_schedule.at_iteration(iteration)

    def should_model_deliveries(self, iteration):
        # We always have to model deliveries if we are synthesizing b2b demand
        return self.enabled and (
            self.simulate_deliveries_schedule.at_iteration(iteration)
            or self.b2b_demand_synthesis_schedule.at_iteration(iteration)
        )
