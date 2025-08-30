# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from typing import List

import pandas as pd


class BasicPTElement:
    def from_row(self, data: pd.Series):
        for key, value in data.items():
            if key not in self.__dict__.keys():
                logging.error(f"{key} Field does not exist")
                continue
            self.__dict__[key] = value  # type: ignore
        return self

    @property
    def available_fields(self) -> List[str]:
        return [key for key in self.__dict__.keys() if not key.startswith("_")]
