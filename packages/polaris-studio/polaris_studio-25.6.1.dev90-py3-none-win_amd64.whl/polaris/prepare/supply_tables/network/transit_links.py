# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path

import pandas as pd
from aequilibrae.transit import Transit
from aequilibrae.utils.db_utils import read_and_close

from polaris.network.transit.feed_tester import test_feed


def get_transit_used_links(polaris_net, aeq_project):
    """Obtains a list of links being used by the transit mode.
    Args:
        polaris_net (Network): Polaris network
        aeq_project (Project): AequilibraE project we are working with
    Return:
        a list with of link ids
    """
    tgt_pth = Path(polaris_net.path_to_file).parent / "supply" / "gtfs"
    transit = Transit(aeq_project)
    for feed_path in tgt_pth.glob("*.zip"):
        if not test_feed(feed_path):
            continue
        feed = transit.new_gtfs_builder(agency=feed_path.stem, file_path=feed_path)
        date = feed.dates_available()[0]
        for service in feed.gtfs_data.services.values():
            service.monday = 1
            service.tuesday = 1
            service.wednesday = 1
            service.thursday = 1
            service.friday = 1
            service.saturday = 1
            service.sunday = 1
        feed.load_date(date)
        feed.set_allow_map_match(True)
        feed.map_match()
        feed.save_to_disk()

    pth = Path(str(aeq_project.path_to_file).replace("project_database", "public_transport"))
    if not pth.exists():
        return []
    with read_and_close(pth) as conn:
        df_links = pd.read_sql_query("SELECT * FROM pattern_mapping", conn)
    return df_links.link.tolist()
