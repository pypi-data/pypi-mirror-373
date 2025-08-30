# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

from polaris.runs.polaris_inputs import PolarisInputs
from .tnc_metrics import TNCMetrics
from .transit_demand_metrics import TransitDemandMetrics
from .transit_supply_metrics import TransitSupplyMetrics
from ..runs.convergence.convergence_iteration import ConvergenceIteration


class SpatialMetrics:
    """Spatial metrics class that provides access to metrics associated with spatially-enabled elements of the model.

    ::

        from polaris.runs.polaris_inputs import PolarisInputs
        from Polaris.analyze.spatial_metrics import SpatialMetrics

        inputs = PolarisInputs.from_dir('path/to/model_dir')

        metrics_object = SpatialMetrics(inputs)
    """

    def __init__(self, inputs: PolarisInputs):
        self.__supply_file__ = inputs.supply_db
        self.__demand_file__ = inputs.demand_db
        self.__result_file__ = inputs.result_db
        self.__result_h5 = inputs.result_h5

    @classmethod
    def from_iteration(cls, iteration: ConvergenceIteration):
        """Create a KPI object from a ConvergenceIteration object."""
        if iteration.files is None:
            raise RuntimeError("Given iteration doesn't have defined input files")
        return cls(iteration.files)

    @classmethod
    def from_dir(cls, iteration_dir: Path):
        """Create a Spatial metrics object from a given directory."""
        return cls(PolarisInputs.from_dir(iteration_dir))

    def transit_supply_metrics(self) -> TransitSupplyMetrics:
        """Returns a class of :func:`~Polaris.analyze.transit_supply_metrics.TransitSupplyMetrics`"""
        return TransitSupplyMetrics(self.__supply_file__)

    def transit_demand_metrics(self) -> TransitDemandMetrics:
        """Returns a class of :func:`~Polaris.analyze.transit_demand_metrics.TransitDemandMetrics`"""
        return TransitDemandMetrics(self.__supply_file__, self.__result_h5)

    def tnc_metrics(self) -> TNCMetrics:
        """Returns a class of :func:`~Polaris.analyze.tnc_metrics.TNCMetrics`"""
        return TNCMetrics(self.__supply_file__, self.__demand_file__, self.__result_file__, self.__result_h5)
