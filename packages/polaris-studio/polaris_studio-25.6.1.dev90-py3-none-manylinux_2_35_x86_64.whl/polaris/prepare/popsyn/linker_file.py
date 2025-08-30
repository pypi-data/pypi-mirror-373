# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from functools import partial
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from polaris.utils.list_utils import first_and_only

# c++ code has optional TESTPERSON, haven't seen this one in any models though, so will leave out for now
ALL_POPSYN_CONTROL_VARIABLE_TYPES = ["HH", "PERSON", "TESTHH"]


class ControlVariable:
    def __init__(self, type, variable_index, dimension, seed_index_column, marg_vars):
        assert (
            type in ALL_POPSYN_CONTROL_VARIABLE_TYPES
        ), f"Demand type {type} not in {ALL_POPSYN_CONTROL_VARIABLE_TYPES}"
        self.type = type
        self.variable_index = variable_index
        self.dimension = dimension
        self.seed_index_column = seed_index_column
        self.marg_vars = marg_vars


class LinkerFile:
    def __init__(self, linker_file, project_dir):
        linker_file = Path(linker_file)
        linker_file = LinkerFile.find_relative(linker_file.name, project_dir, linker_file.parent)
        if not linker_file.exists():
            raise FileNotFoundError(f"Linker file {linker_file} does not exist.")
        self.linker_file_contents = self.load_linker_file(linker_file)
        self.file = self.extract_file_names(self.linker_file_contents, project_dir, linker_file.parent)
        self.data_types = self.extract_data_types(self.linker_file_contents)
        self.dimensions = {type: self.get_keyword_value(f"{type}DIMS", True) for type in self.data_types}
        self.control_variables = {t: self.extract_control_variables_for_type(t) for t in self.data_types}

        self.region_id = self.extract_region_ids(self.linker_file_contents)
        self.seed_id = self.extract_seed_ids(self.linker_file_contents)
        self.zone_id = {"CONTROL": self.get_keyword_value("ZONE", True)[0]}

        # Make test copies of file/region
        if "TESTHH" in self.data_types:
            self.file["TESTHH"] = self.file["HH"]
            self.region_id["TESTHH"] = self.region_id["HH"]
            self.seed_id["TESTHH"] = self.seed_id["HH"]

        self.puma_id_contains_state_id = False

        self.control_data = {}
        self.extract_control_data()

    @staticmethod
    def extract_data_types(linker_file_contents):
        comments_and_blanks = lambda x: (not x.startswith("#")) and (not x == "")  # noqa: E731
        all_entries = {x.split("\t")[0] for x in filter(comments_and_blanks, linker_file_contents)}
        data_types_in_linker_file = list(
            {x[: -len("MARGVAR")] for x in set(filter(lambda x: x.endswith("MARGVAR"), all_entries))}
        )
        unrecognised_data_types = list(
            filter(lambda x: x not in ALL_POPSYN_CONTROL_VARIABLE_TYPES, data_types_in_linker_file)
        )
        if len(unrecognised_data_types) > 0:
            logging.critical(
                f"Unrecognised data type in linker file {unrecognised_data_types} not in"
                f" {ALL_POPSYN_CONTROL_VARIABLE_TYPES}. Continuing without these, but they will be missing from"
                " this analysis."
            )

        return data_types_in_linker_file

    def extract_control_data(self):
        control_data_full = pd.read_csv(self.file["CONTROL"], sep=",|\t", engine="python")
        control_geo_columns = [self.zone_id["CONTROL"], self.region_id["CONTROL"]]

        # determine if puma column uses 5-diget PUMA code or state_id + PUMA code, our models do either
        max_puma_id_length = control_data_full.iloc[:, self.region_id["CONTROL"]].astype(str).apply(len).max()
        if max_puma_id_length <= 5:
            self.puma_id_contains_state_id = False
        else:
            self.puma_id_contains_state_id = True

        self.control_data = {k: {dim: {} for dim in range(len(self.dimensions[k]))} for k in self.data_types}

        for type in self.data_types:
            seed_data_full = pd.read_csv(self.file[type], sep=",|\t", engine="python")
            for variable_index in range(len(self.dimensions[type])):
                control_variable = self.control_variables[type][variable_index]

                # seed data info
                seed_data_column_name = seed_data_full.columns[control_variable.seed_index_column]

                # for each control variable, extract data
                for control_var_data in control_variable.marg_vars.iterrows():
                    col_offset = control_var_data[1]["col_offset"]
                    col_name = control_data_full.columns[col_offset]
                    if control_data_full[col_name].dtype != np.int64:
                        control_data_full[col_name] = (
                            pd.to_numeric(control_data_full[col_name], "coerce").fillna(0).astype(np.int64)
                        )

                    ## 0th column is zone_id, 1st column is regionid, rest is data in order
                    control_data = control_data_full.iloc[:, [*control_geo_columns, col_offset]].astype(float)
                    control_variable_name = control_data_full.columns[col_offset]

                    self.control_data[type][variable_index][control_variable_name] = {
                        "control_data": control_data,
                        "seed_column_name": seed_data_column_name,
                        "seed_data_min_val": control_var_data[1]["low_val"],
                        "seed_high_val_excl": control_var_data[1]["high_val_excl"],
                        "control_idx": control_var_data[1]["control_idx"],
                    }

    @staticmethod
    def extract_region_ids(contents):
        return {
            "HH": LinkerFile.parse_line_for_keyword(contents, "REGION", True)[0],
            "PERSON": LinkerFile.parse_line_for_keyword(contents, "PERSON", True)[0],
            "CONTROL": LinkerFile.parse_line_for_keyword(contents, "ZONE", True)[1],
        }

    @staticmethod
    def extract_seed_ids(contents):
        # hh and ppl id column index
        return {
            "HH": LinkerFile.parse_line_for_keyword(contents, "REGION", True)[1],
            "PERSON": LinkerFile.parse_line_for_keyword(contents, "PERSON", True)[1],
        }

    @staticmethod
    def find_relative(file_name, project_dir, linker_dir):
        """Find relative file name in project_dir or linker_dir"""
        if (project_dir / file_name).exists():
            return project_dir / file_name
        elif (linker_dir / file_name).exists():
            return linker_dir / file_name
        else:
            raise FileNotFoundError(f"File {file_name} not found in {project_dir} or {linker_dir}")

    @staticmethod
    def extract_file_names(contents: list, project_dir: Path, linker_dir: Path):
        find_relative = partial(LinkerFile.find_relative, project_dir=project_dir, linker_dir=linker_dir)

        return {
            "HH": find_relative(LinkerFile.parse_line_for_keyword(contents, "HHFILE")[0]),
            "PERSON": find_relative(LinkerFile.parse_line_for_keyword(contents, "PERSONFILE")[0]),
            "CONTROL": find_relative(LinkerFile.parse_line_for_keyword(contents, "ZONEFILE")[0]),
        }

    @staticmethod
    def load_linker_file(linker_file):
        with open(linker_file) as f:
            return [x.strip() for x in f.readlines()]

    @staticmethod
    def parse_line_for_keyword(lines, keyword, make_values_numeric=False):
        matching_ling = first_and_only(filter(lambda x: x.startswith(f"{keyword}\t"), lines))
        data = matching_ling.split("\t")[1:]
        assert len(data) > 0
        if make_values_numeric:
            data = [int(x) for x in data]
        return data

    def get_keyword_value(self, keyword, make_numeric):
        return LinkerFile.parse_line_for_keyword(self.linker_file_contents, keyword, make_numeric)

    def extract_seed_file_index_for_variable(self, type, variable_index):
        ### extract index in file  - xx_var;
        keyword = f"{type}VAR"
        line_data = list(filter(lambda x: x.startswith(f"{keyword}\t"), self.linker_file_contents))
        assert len(line_data) == len(self.dimensions[type])
        only_once = 0
        for line in line_data:
            d = self.parse_line_for_keyword([line], keyword, True)
            if d[0] != variable_index:
                continue
            only_once += 1
            seed_index_this_var = d[1]
        assert only_once == 1, (
            f"{type} seed file index column for variable id {variable_index} found {only_once} values"
            + " - only one allowed."
        )
        return seed_index_this_var

    def extract_control_info_for_variable(self, type, variable_index):
        ### extract controls for this variable  -  xx_marg_var;
        keyword = f"{type}MARGVAR"
        line_data = list(filter(lambda x: x.startswith(f"{keyword}\t"), self.linker_file_contents))
        assert len(line_data) == np.sum(self.dimensions[type])
        marg_vars = []
        for line in line_data:
            d = self.parse_line_for_keyword([line], keyword, True)
            assert len(d) == 5
            if d[0] != variable_index:
                continue
            marg_vars.append(d[1:])
        assert len(marg_vars) == self.dimensions[type][variable_index]
        return pd.DataFrame(data=marg_vars, columns=["control_idx", "low_val", "high_val_excl", "col_offset"])

    def extract_control_variables_for_type(self, type):
        control_vars = []
        for variable_index in range(len(self.dimensions[type])):
            seed_index_this_var = self.extract_seed_file_index_for_variable(type, variable_index)
            mag_vars = self.extract_control_info_for_variable(type, variable_index)

            c = ControlVariable(
                type=type,
                variable_index=variable_index,
                dimension=self.dimensions[type][variable_index],
                seed_index_column=seed_index_this_var,
                marg_vars=mag_vars,
            )
            control_vars.append(c)
        assert len(control_vars) == len(self.dimensions[type]), f"Couldn't find all control variables for {type}"
        return control_vars
