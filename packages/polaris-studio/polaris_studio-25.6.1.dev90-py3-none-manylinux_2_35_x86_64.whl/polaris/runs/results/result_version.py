# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
def get_version_from_handle(h5file):
    rv = {"link_moe": False, "paths": False}
    for group in h5file.list_nodes("/"):
        if group._v_pathname == "/link_moe":
            rv["link_moe"] = True
        if group._v_pathname == "/paths":
            rv["paths"] = True
    return rv
