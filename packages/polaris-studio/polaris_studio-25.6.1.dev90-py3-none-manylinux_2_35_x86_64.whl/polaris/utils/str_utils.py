# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import re
from textwrap import dedent


def outdent(in_str: str) -> str:
    if in_str.startswith("\n"):
        in_str = in_str[1:]
    return dedent(in_str.rstrip())


def trim_heredoc(str, n):
    return re.sub("\n *$", "", re.sub("^\n", "", re.sub(rf"\n {{{n}}}", "\n", str)))
