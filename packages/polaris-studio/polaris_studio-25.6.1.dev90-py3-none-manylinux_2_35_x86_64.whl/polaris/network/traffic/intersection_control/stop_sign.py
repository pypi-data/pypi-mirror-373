# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from itertools import combinations
from sqlite3 import Connection

import numpy as np
import pandas as pd

from polaris.network.consistency.link_types_constants import RAMP, FREEWAY, EXPRESSWAY


class StopSign:
    def __init__(self, intersection):
        from polaris.network.traffic.intersec import Intersection

        self.inter: Intersection = intersection
        self.stop_signs = []

    def re_compute(self):
        # No stop signs if there are no conflicts
        no_sign = [RAMP, FREEWAY, EXPRESSWAY]

        self.stop_signs.clear()
        if len(self.inter.incoming) <= 1:
            return

        rnks = {x.link: x.link_rank for x in self.inter.incoming} | {x.link: x.link_rank for x in self.inter.outgoing}
        out_bearing = {x.link: x.bearing for x in self.inter.outgoing}
        in_bearing = {x.link: x.bearing for x in self.inter.incoming}

        connec = self.inter.connections()
        connec = connec.assign(
            in_bearing=connec.link.map(in_bearing),
            out_bearing=connec.to_link.map(out_bearing),
            in_rank=connec.link.map(rnks),
            out_rank=connec.to_link.map(rnks),
        )

        all_ranks = [lnk.link_rank for lnk in self.inter.incoming] + [lnk.link_rank for lnk in self.inter.outgoing]

        place_stops = []
        for _, df in connec.groupby(["to_link"]):
            threshold = (
                45.0 if any(x in no_sign for x in np.hstack([df.in_rank.to_numpy(), df.out_rank.to_numpy()])) else 22.5
            )
            if df.shape[0] <= 1:
                # Direct movement. No stop to even consider
                continue

            all_comb = list(combinations(df.in_bearing.tolist(), 2))
            differences = [abs(c[1] - c[0]) for c in all_comb]
            if not all(diff < threshold or threshold > 360 - diff for diff in differences):
                # This is not a merge, so a signal is needed
                place_stops.extend(df.link.tolist())

        place_stops = [x for x in set(place_stops) if rnks[x] not in no_sign]

        all_links = list(set([lnk.link for lnk in self.inter.incoming] + [lnk.link for lnk in self.inter.outgoing]))

        # This could be a T-junction, in which case we stop the leg of the T only
        if len(all_links) == 3:
            df = connec.query("type=='THRU'")
            if df.shape[0] <= 2:
                # Looking more like a T-junction
                # We need to check if the two links are the same
                links = list(set(np.hstack([df.link, df.to_link])))
                if len(links) == 2:
                    # This is a T-junction
                    # Now we need to check if the hyerarchies support that it is the T leg that must be stopped
                    if rnks[links[0]] <= max(all_ranks) and rnks[links[1]] <= max(all_ranks):
                        # The leg of the T is not a higher priority road than the top, so we can remove stops from the straight direction
                        for link in links:
                            if link in place_stops:
                                place_stops.remove(link)

        # if this is a regular intersection, we need to analyse right-of-way
        if len(all_links) == 4:
            df = connec.query("type=='THRU'")
            intersec_links = list(set(np.hstack([df.link, df.to_link])))
            if df.shape[0] <= 4 and len(intersec_links) == 4:
                # Looking more like a regular intersection
                # We need to check if they are two-and-two
                df1 = df.query("link==@all_links[0] or to_link==@all_links[0]")
                df2 = df[~df.isin(df1)]
                links1 = list(set(np.hstack([df1.link, df1.to_link])))
                links2 = list(set(np.hstack([df2.link, df2.to_link])))
                if len(links1) == 2 and len(links2) == 2:
                    # This IS a regular intersection
                    # Now we need to check if the hyerarchies sugest putting stops in only one or both directions
                    rankings1 = [rnks[x] for x in links1]
                    rankings2 = [rnks[x] for x in links2]
                    if min(rankings1) < max(rankings2):
                        # Only links2 have stops
                        for link in links1:
                            if link in place_stops:
                                place_stops.remove(link)
                    elif min(rankings2) < max(rankings1):
                        # Only links1 have stops
                        for link in links2:
                            if link in place_stops:
                                place_stops.remove(link)

        ALL_STOP = "ALL_STOP" if len(place_stops) == len(set(all_links)) else "STOP"

        stop_links = [lnk for lnk in self.inter.incoming if lnk.link in place_stops]
        self.stop_signs = [[lnk.link, lnk.direction, self.inter.node, ALL_STOP] for lnk in stop_links]

    def save(self, conn: Connection):
        if not self.stop_signs:
            return
        self.data.to_sql("Sign", conn, if_exists="append", index=False)

    @property
    def data(self):
        return pd.DataFrame(self.stop_signs, columns=["link", "dir", "nodes", "sign"])
