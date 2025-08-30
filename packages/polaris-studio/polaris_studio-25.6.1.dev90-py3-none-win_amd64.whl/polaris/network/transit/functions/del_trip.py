# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
def delete_trip(trip_id: int, conn, commit=True):
    """Deletes all information regarding one specific transit trip

    Args:
        *trip_id* (:obj:`str`): trip_id as present in the database
    """
    sqls = [
        """DELETE from transit_trips_schedule where trip_id=?""",
        "DELETE from Transit_Trips where trip_id=?",
    ]

    for sql in sqls:
        conn.execute(sql, [trip_id])
    if commit:
        conn.commit()
