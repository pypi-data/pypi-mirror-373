# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from functools import wraps
from typing import Dict, Tuple, Union

from enum import IntEnum


class KPITag(IntEnum):
    """Enum defining KPI types"""

    SYSTEM = 0
    POPULATION = 1
    ACTIVITIES = 2
    ACTIVITIES_PLANNED = 3
    TRIPS = 4
    TNC = 5
    TRAFFIC = 6
    TRANSIT = 7
    VEHICLES = 8
    SKIMS = 9
    CALIBRATION = 10
    VALIDATION = 11
    CONVERGENCE = 12
    GLOBAL = 13

    SCALAR = 40
    HIGH_MEMORY = 50
    HIGH_CPU = 60

    BROKEN = 100

    @classmethod
    def all_values(cls):
        return tuple(member.value for member in cls)

    def __str__(self):
        return self.name


class KPIFilter(object):
    def __init__(self, include: Tuple[KPITag, ...], exclude: Tuple[KPITag, ...]):
        self.include = include
        self.exclude = exclude

    def allows(self, tags: Tuple[KPITag, ...]):
        if isinstance(tags, str):
            tags = get_kpi_tags_for_metric(tags)
        return any(t in self.include for t in tags) and not any(t in self.exclude for t in tags)


# This is the global registry storing the association between a given metric and its tags
KPITagRegistry: Dict[str, Tuple[KPITag, ...]] = {}


def get_kpi_tags_for_metric(metric_name: str) -> Tuple[KPITag, ...]:
    return KPITagRegistry.get(metric_name, ())


def kpi_type(kpi_types: Union[KPITag, tuple]):
    """
    Decorator to attach tag(s) to a given KPI metric method.
    """
    if not isinstance(kpi_types, tuple):
        kpi_types = (kpi_types,)

    def decorator(func):
        KPITagRegistry[func.__name__.replace("metric_", "")] = kpi_types

        # Return the original function unchanged
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


standard_kpis = (
    KPITag.SYSTEM,
    KPITag.POPULATION,
    KPITag.ACTIVITIES,
    KPITag.TRIPS,
    KPITag.TNC,
    KPITag.TRAFFIC,
    KPITag.TRANSIT,
    KPITag.VEHICLES,
    KPITag.CALIBRATION,
    KPITag.VALIDATION,
    KPITag.CONVERGENCE,
    KPITag.GLOBAL,
)

all_kpis = KPITag.all_values()

planning_kpis = (
    KPITag.SYSTEM,
    KPITag.POPULATION,
    KPITag.ACTIVITIES_PLANNED,
    KPITag.CALIBRATION,
    KPITag.CONVERGENCE,
    KPITag.GLOBAL,
)

no_kpis = ()
