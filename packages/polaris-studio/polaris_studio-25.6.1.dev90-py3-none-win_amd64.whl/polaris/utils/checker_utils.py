# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from polaris.demand.checker.demand_checker import DemandChecker
from polaris.freight.checker.freight_checker import FreightChecker
from polaris.network.checker.supply_checker import SupplyChecker
from polaris.utils.global_checker import GlobalChecker


def check_critical(model):
    """Runs all the checks on the model and returns a list of errors"""
    errors = []
    errors.extend(GlobalChecker(model).critical())
    errors.extend(SupplyChecker(model.supply_file).critical())
    errors.extend(DemandChecker(model.demand_file).critical())

    if model.freight_file.exists():
        errors.extend(FreightChecker(model.freight_file).critical())

    if len(errors) > 0:
        logging.error("There are critical errors in the model:")
        for error in errors:
            logging.error("    " + str(error))

    return errors
