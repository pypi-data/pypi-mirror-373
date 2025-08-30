# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
node_field_translation = {
    "node_id": "node",
    "x_coord": "x",
    "y_coord": "y",
    "z_coord": "z",
    "ctrl_type": "ctrl_type_osm",
    "zone_id": "zone",
}

link_field_translation = {
    "link_id": "link",
    "from_node_id": "node_a",
    "to_node_id": "node_b",
    "facility_type": "type",
    "capacity": "cap",
    "free_speed": "fspd",
    "allowed_uses": "use",
    "geometry": "geo",
    "link_type_name": "type",
}

zone_field_translation = {"zone_id": "zone", "boundary": "geo"}

location_field_translation = {
    "loc_id": "location",
    "link_id": "link",
    "lr": "offset",
    "x_coord": "x",
    "y_coord": "y",
    "z_coord": "z",
    "loc_type": "land_use",
    "zone_id": "zone",
}
