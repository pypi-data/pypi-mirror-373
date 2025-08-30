# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from typing import List, Any

from .active_network_link import ActiveTransportLink

get_walk_links_qry = """Select walk_link, from_node, to_node, "length", ref_link, asbinary(geo) from Transit_Walk
                       where ref_link>0 AND ref_link not NULL"""


class WalkLink(ActiveTransportLink):
    def __init__(self, data: List[Any]):
        super().__init__(data)

        self.walk_link = self.id
        self.__table_name__ = "Transit_Walk"
        self.__field_name__ = "walk_link"

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key in ["walk_link", "id"]:
            self.__dict__["walk_link"] = value
            self.__dict__["id"] = value
