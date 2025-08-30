# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import os

os.environ["USE_PYGEOS"] = "0"

import warnings  # noqa: E402

warnings.filterwarnings(action="ignore", message="invalid value encountered in line_locate_point")
warnings.simplefilter("always", DeprecationWarning)


from polaris.project.polaris import Polaris  # noqa: E402, F401
from .version import __version__ as version  # noqa: E402, F401
