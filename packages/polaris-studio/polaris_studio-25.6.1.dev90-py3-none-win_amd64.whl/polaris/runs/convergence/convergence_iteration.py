# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
import uuid
import dataclasses
from pathlib import Path
from typing import Optional

from polaris.runs.polaris_inputs import PolarisInputs


@dataclasses.dataclass
class ConvergenceIteration:
    uuid: str = None
    is_skim: bool = False
    is_pop_synth: bool = False
    is_abm_init: bool = False
    is_dta: bool = False
    is_last: bool = False
    iteration_number: int = -1
    runtime: float = 0
    output_dir: Optional[Path] = None
    scenario_file: Optional[Path] = None
    files: Optional[PolarisInputs] = None

    previous_iteration: Optional["ConvergenceIteration"] = None
    next_iteration: Optional["ConvergenceIteration"] = None

    @property
    def is_standard(self):
        return not any([self.is_pop_synth, self.is_abm_init, self.is_skim, self.is_dta])

    @classmethod
    def of_type(cls, iteration_type, iteration_number):
        if iteration_type is None or iteration_type == "normal":
            return ConvergenceIteration(iteration_number=iteration_number)
        if iteration_type == "skim":
            return ConvergenceIteration(is_skim=True, iteration_number=iteration_number)
        elif iteration_type == "abm_init":
            return ConvergenceIteration(is_abm_init=True, iteration_number=iteration_number)
        elif iteration_type == "pop_synth":
            return ConvergenceIteration(is_pop_synth=True, iteration_number=iteration_number)
        elif iteration_type == "dta":
            return ConvergenceIteration(is_dta=True, iteration_number=iteration_number)
        raise RuntimeError(f"Unknown iteration type: {iteration_type}")

    @classmethod
    def from_dir(cls, dir, db_name=None, it_type=None, it_num=None):
        # If they aren't specified we can parse these props from the dirname
        if db_name is None or it_type is None or it_num is None:
            db_name, it_type, it_num = cls.parse_dirname(dir)
        iteration = cls.of_type(it_type, it_num)
        iteration.output_dir = Path(dir)
        iteration.files = PolarisInputs.from_dir(Path(dir), db_name)
        return iteration

    def type(self):
        if self.is_skim:
            return "skim"
        if self.is_pop_synth:
            return "pop_synth"
        if self.is_abm_init:
            return "abm_init"
        if self.is_dta:
            return "dta"
        return "normal"

    def __str__(self):
        base_str = self._get_base_str()
        if self.iteration_number is not None and self.iteration_number >= 0:
            return f"{base_str}_{self.iteration_number}"
        return base_str

    def _get_base_str(self):
        if self.is_skim:
            return "00_skim_iteration"
        elif self.is_abm_init:
            return "01_abm_init_iteration"
        elif self.is_pop_synth:
            return "02_pop_synth_iteration"
        elif self.is_dta:
            return f"dta_iteration"
        return f"iteration"

    def __format__(self, *args, **kwargs):
        return str(self).__format__(*args, **kwargs)

    def set_output_dir(self, output_dir: Path, scenario_file: Path, db_name: str):
        """
        This method is called when an iteration has actually been run. It sets the actual paths to the output folder
        and scenario file that was used to run the iteration as well as storing the auto-generated uuid in that folder.
        """
        self.output_dir = output_dir
        self.files = PolarisInputs.from_dir(output_dir, db_name)
        self.scenario_file = output_dir / "model_files" / scenario_file.name
        uuid_file = output_dir / "uuid"
        if uuid_file.exists():
            with open(output_dir / "uuid", "r") as f:
                self.uuid = f.read()
        else:
            self.uuid = uuid.uuid4().hex
            with open(output_dir / "uuid", "w") as f:
                f.write(self.uuid)

    @staticmethod
    def parse_dirname(dirname):
        dirname = Path(dirname).name

        # Get the type and iteration number first
        type = ConvergenceIteration.parse_type(dirname)
        it_num = int(dirname.split("_iteration_")[-1]) if "iteration_" in dirname else None

        # Use the type/it_number to get a base string...
        #         ... the bit before the base_str is the db_name
        base_str = ConvergenceIteration.of_type(type, it_num)._get_base_str()
        m = re.match(rf"(.*)_{base_str}.*", dirname)
        if not m:
            raise RuntimeError(f"Can't find {base_str} in {dirname}")

        return m[1], type, it_num

    @staticmethod
    def parse_type(dirname):
        for pattern in {"skim", "abm_init", "cristal", "dta", "pop_synth"}:
            if pattern in dirname:
                return pattern
        return "normal"
