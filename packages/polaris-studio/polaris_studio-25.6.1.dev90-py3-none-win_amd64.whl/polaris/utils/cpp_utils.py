# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
import pyparsing as pp
from collections import defaultdict


def find_enums_in_file(filename):
    with open(filename, "r") as f:
        filecontents = f.read()
    return find_enums_in_str(filecontents)


def find_enums_in_str(s: str):
    enums = defaultdict(lambda: {})  # type: ignore
    docs = categorize_comments(s)
    for item, _, _ in get_enum_parser().scan_string(s):
        idx = 0
        for entry in item.names:
            if entry.value != "":
                if not check_int(entry.value):
                    # This is an identifier to a previous value in the enum
                    # We will just ignore these
                    continue
                idx = int(entry.value)
            comments = [v.rstrip().strip() for k, v in docs.items() if entry.name in k]
            comment = comments[0] if len(comments) > 0 else ""
            enums[item.enum][idx] = [entry.name, comment]
            idx += 1
    return enums


def check_int(s):
    # Adapted from https://stackoverflow.com/a/1265696
    s = str(s)
    if s[0] in ("-", "+"):
        return s[1:].isdigit()
    return s.isdigit()


def categorize_comments(s: str):
    pattern = r"\s*([a-zA-Z_]*).*//(.*)$"
    rv = {}
    for x in s.split("\n"):
        m = re.match(pattern, x)
        if not m or m[1].strip() == "":
            continue
        rv[m[1].strip()] = m[2].replace("@", "").replace("[HIDDEN]", "").strip()

    return rv


def get_enum_parser():
    # syntax we don't want to see in the final parse tree
    LBRACE, RBRACE, EQ, COMMA = pp.Suppress.using_each("{}=,")
    _enum = pp.Suppress("enum") + pp.Suppress(pp.Optional("class"))
    identifier = pp.Word(pp.alphas + "_", pp.alphanums + "_")
    integer = pp.Word(pp.nums + "-")
    value = integer | identifier
    enumValue = pp.Group(identifier("name") + pp.Optional(EQ + value("value")))
    enumList = pp.Group(enumValue + (COMMA + enumValue)[...])
    parser = _enum + identifier("enum") + LBRACE + enumList("names") + RBRACE
    return parser.ignore("//" + pp.rest_of_line).ignore(pp.c_style_comment)
