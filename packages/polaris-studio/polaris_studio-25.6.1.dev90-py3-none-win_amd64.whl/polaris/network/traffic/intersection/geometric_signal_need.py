# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import sqlite3


def geom_need_for_signal(intersec, conn: sqlite3.Connection) -> bool:
    """Determines the need for a signal for an intersection based on its geometry"""
    num_links = len(set(intersec.connections(conn).link.to_list() + intersec.connections(conn).to_link.to_list()))
    if num_links < 3:
        # This is just a node with no real intersection
        return False

    if num_links > 4:
        # There are too many intersections to even think about it
        return True

    sql = 'Select "type" from Link where node_a=? union all Select "type" from Link where node_b=?'

    all_link_types = [x[0] for x in conn.execute(sql, [intersec.node, intersec.node])]

    if num_links == 3 and "RAMP" in all_link_types:
        # A ramp merging into a node should not have a signal
        return False

    major_types = ["FREEWAY", "EXPRESSWAY", "PRINCIPAL", "MAJOR", "MINOR", "COLLECTOR"]

    # We check if this is a minor with minor intersection
    exist_major = [x for x in all_link_types if x in major_types]
    if len(exist_major) < 3:
        return False

    cs = intersec.connection_data_records
    from_links = list(cs.link.unique())
    to_links = list(cs.to_link.unique())

    # For merges we do not use traffic lights
    if min([len(set(to_links)), len(set(from_links))]) < 2:
        return False
    # If all prior checks failed, then we need a signal
    return True
