# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pydantic import BaseModel


class STAInputs(BaseModel):
    assignment_algorithm: str = "bfw"
    max_iterations: int = 100
    rgap: float = 0.0001
    bpr_alpha: float = 0.15
    bpr_beta: float = 4.0
