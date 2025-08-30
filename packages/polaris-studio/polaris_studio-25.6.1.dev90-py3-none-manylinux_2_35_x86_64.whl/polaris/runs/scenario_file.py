# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import io
import json
import re
from os import PathLike
from os.path import exists
from pathlib import Path
from typing import Dict, Tuple, Optional

import yaml


def get_scenario_value(filename: Path, key: str):
    """Utility function to quickly get the value of a given (potentially nested) key from the scenario_abm.json.
    Returns None if key can't be found.
    """
    full_dict = load_dict_from_file(filename)
    dic, key = find_containing_dic(full_dict, key)
    return dic.get(key, None)


def apply_modification(input_filename: Path, modifications: Dict, output_filename: Optional[Path] = None) -> Path:
    input_filename = Path(input_filename)
    if output_filename:
        output_filename = Path(output_filename)

    if modifications is None:
        return input_filename

    output_filename = modified_name(input_filename, output_filename)
    json_tree = load_dict_from_file(input_filename)

    json_tree = apply_modifications_to_dict(json_tree, modifications)

    save_dict_to_file(output_filename, json_tree)

    return output_filename


def apply_modifications_to_dict(json_tree, modifications):
    for key, value in modifications.items():
        dic, key = find_containing_dic(json_tree, key)
        dic[key] = value
    return json_tree


def modified_name(input_filename: Path, output_filename: Optional[Path]) -> Path:
    return output_filename or input_filename.with_suffix(f".modified{input_filename.suffix}")


def load_dict_from_file(filename: Path):
    filename = Path(filename)
    with open(filename, "r") as f:
        if filename.suffix == ".json":
            return json.load(f)
        if filename.suffix == ".yaml":
            return yaml.load(f, Loader=yaml.FullLoader)


def save_dict_to_file(filename, dic):
    filename = Path(filename)
    with open(filename, "w") as f:
        if filename.suffix == ".json":
            json.dump(dic, f, indent=4)
        if filename.suffix == ".yaml":
            yaml.dump(dic, f)


def get_desired_output_dir(scenario_file_or_dict, root_dir):
    if isinstance(scenario_file_or_dict, str) or isinstance(scenario_file_or_dict, PathLike):
        dict_ = load_json(scenario_file_or_dict)
    else:
        dict_ = scenario_file_or_dict

    return Path(root_dir) / dict_["Output controls"]["output_directory"]


def guess_next_output_dir(scenario_file_or_dict, root_dir):
    # This replicates the logic that will be used in Polaris to find a suitable (non-existing) output folder
    base = get_desired_output_dir(scenario_file_or_dict, root_dir)
    return find_next_available_filename(base)


def find_next_available_filename(base, separator=""):
    temp = base
    if re.search(r"\d+$", str(base)):
        base = base + "_"
    counter = 1
    while exists(temp):
        temp = base.parent / Path(f"{base.stem}{separator}{counter}{base.suffix}")
        counter += 1
    return temp


def split_key(key):
    tokens = key.split(".")
    if len(tokens) < 2:
        return None, key
    return tokens[0:-1], tokens[-1]


def find_containing_dic(dic: dict, key: str) -> Tuple[dict, str]:
    """Finds the dictionary that contains the given key and returns a reference to it
    so that modifications can be made to it.
    """
    if key in dic:
        return dic, key  # it is a top level key

    # Check if the user specified it as a nested key syntax (eg. a.b.c)
    outer, inner = split_key(key)
    if outer is None:
        # If not, see if any of the sub-dictionaries have a key with the given name
        sub_dict = find_recursively_dic_with_key(dic, key)
        # If so, return that, otherwise just return the original
        return (sub_dict or dic, key)

    # If the user specified the exact key - generate that structure if it doesn't exist
    for i in outer:
        if i not in dic:
            dic[i] = {}
        dic = dic[i]
    return dic, inner


def find_recursively_dic_with_key(dic, key_to_find):
    for key, value in dic.items():
        if key == key_to_find:
            return dic
        elif isinstance(value, dict):
            ret_val = find_recursively_dic_with_key(value, key_to_find)
            if ret_val is not None:
                return ret_val


def write_json(filename, d):
    with open(filename, "w", newline="") as f:
        json.dump(d, f, indent=4, separators=(",", ": "))


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


def load_yaml(filename):
    with open(filename, "r") as stream:
        return yaml.safe_load(stream)


def save_yaml(filename, data):
    # Write YAML file
    with io.open(filename, "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
