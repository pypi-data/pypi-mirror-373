# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from polaris.network.create.triggers import recreate_freight_triggers


def migrate(conn):

    to_del = [
        "airport_populates_geo_enabled_fields_on_new_record",
        "airport_enforces_x_field_Airports",
        "airport_enforces_y_field_Airports",
        "airport_updates_fields_on_geo_change",
        "national_ports_populates_geo_enabled_fields_on_new_record",
        "national_ports_enforces_x_field_National_Portss",
        "national_ports_enforces_y_field_National_Portss",
        "national_ports_updates_fields_on_geo_change",
        "railport_populates_geo_enabled_fields_on_new_record",
        "railport_enforces_x_field_Railports",
        "railport_enforces_y_field_Railports",
        "railport_updates_fields_on_geo_change",
    ]

    for trigger in to_del:
        conn.execute(f"DROP TRIGGER IF EXISTS {trigger}")
    recreate_freight_triggers(conn)
