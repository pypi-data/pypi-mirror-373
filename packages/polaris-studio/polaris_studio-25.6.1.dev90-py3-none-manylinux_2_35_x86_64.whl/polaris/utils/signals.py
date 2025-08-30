# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md

from polaris.utils.env_utils import inside_qgis


def noop(_):
    pass


if inside_qgis:
    from qgis.PyQt.QtCore import pyqtSignal as SIGNAL  # type: ignore

    noop(SIGNAL.__class__)  # This should be no-op but it stops PyCharm from "optimising" the above import
else:
    from polaris.utils.python_signal import PythonSignal as SIGNAL  # type: ignore

    noop(SIGNAL.__class__)  # This should be no-op but it stops PyCharm from "optimising" the above import
