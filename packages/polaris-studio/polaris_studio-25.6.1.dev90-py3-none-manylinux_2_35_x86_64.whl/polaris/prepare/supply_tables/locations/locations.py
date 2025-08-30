# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import random
import sqlite3
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pygris
from census import Census

from polaris.utils.database.data_table_access import DataTableAccess
from polaris.network.utils.srid import get_srid
from polaris.network.network import Network
from polaris.utils.database.db_utils import commit_and_close, read_and_close
from polaris.utils.signals import SIGNAL
from polaris.prepare.supply_tables.utils.overture_data import get_building_locations


def add_locations(
    supply_path: Path,
    state_counties: gpd.GeoDataFrame,
    control_totals: gpd.GeoDataFrame,
    census_api_key: str,
    residential_sample_rate=0.25,
    other_sample_rate=1.0,
) -> None:
    """ """

    net = Network.from_file(supply_path, False)
    zone_layer = DataTableAccess(supply_path).get("Zone")

    all_buildings = get_building_locations(model_area=zone_layer, srid=get_srid(database_path=supply_path))
    all_buildings.reset_index(drop=True, inplace=True)

    # # We add all locations from OSM that we KNOW are very good from previous research
    # # "SYNTHESIZING ACTIVITY LOCATIONS IN THE CONTEXT OF INTEGRATED ACTIVITY-BASED MODELS", Zuniga-Garcia & Camargo, 2023
    # added = add_from_osm(net, other_sample_rate)

    # We then remove anything that is too close to those buildings, say a buffer of 10 meters
    # added.geometry = added.to_crs(3857).geometry.buffer(10).to_crs(all_buildings.crs)
    # joined = gpd.sjoin(all_buildings, added, how="left", predicate="intersects")
    # all_buildings = joined[joined.index_right.isnull()][all_buildings.columns]

    # We can now use these buildings to add residential and commercial locations
    remaining_buildings = add_residential(
        net, state_counties, zone_layer, residential_sample_rate, all_buildings, census_api_key
    )
    add_commercial(net, zone_layer, control_totals, other_sample_rate, remaining_buildings)
    net.close(False)


def add_residential(
    net: Network,
    state_counties: gpd.GeoDataFrame,
    zone_layer: gpd.GeoDataFrame,
    residential_sample_rate: float,
    all_buildings: gpd.GeoDataFrame,
    census_api_key: str,
) -> gpd.GeoDataFrame:
    logging.info("pre-processing residential locations")
    with read_and_close(net.path_to_file) as conn:
        max_loc = conn.execute("Select coalesce(max(location) + 1, 1) from Location").fetchone()[0]
        srid = get_srid(conn=conn)

    # We filter out non-residential buildings
    buildings = all_buildings[(all_buildings.land_use == "residential") | (all_buildings.land_use.isna())]

    # Roughly decide those that may or may not be small or large
    buildings = buildings.assign(is_large=1, is_small=1)
    buildings.loc[((buildings.floor_area < 1000) | (buildings.height < 6)), "is_large"] = 0
    buildings.loc[((buildings.floor_area > 1000) | (buildings.height > 9)), "is_small"] = 0
    location_candidates = buildings.to_crs(srid)

    # Let's compute the percentage of single and multi-family households in our area
    c = Census(census_api_key)

    # Get the number of housing units as distributed throughout the modeling area
    census_data = []
    for _, rec in state_counties.iterrows():
        census_data.extend(c.sf1.state_county_tract("H001001", rec["STATEFP"], rec["COUNTYFP"], Census.ALL))
    hholds = pd.DataFrame([[dt["tract"], dt["H001001"]] for dt in census_data], columns=["TRACTCE10", "housing_units"])
    hholds.housing_units = np.ceil(hholds.housing_units * residential_sample_rate).astype(int)

    geographies = []
    for state in state_counties.state_name.unique():
        gdf = pygris.tracts(state=state, year=2010, cache=True).rename(columns={"COUNTYFP10": "COUNTYFP"})
        gdf = gdf[gdf.COUNTYFP.isin(state_counties[state_counties.state_name == state].COUNTYFP)]
        geographies.append(gdf)
    tracts = pd.concat(geographies)

    ctrl_tot = tracts.merge(hholds, on="TRACTCE10")
    ctrl_tot = ctrl_tot.assign(density=ctrl_tot.housing_units / ctrl_tot.geometry.to_crs(3857).area)
    ctrl_tot = ctrl_tot.assign(prob_multi=0.1 + (ctrl_tot.density / ctrl_tot.density.max()) * 0.9)
    ctrl_tot = ctrl_tot.assign(prob_single=1 - ctrl_tot.prob_multi)
    ctrl_tot = ctrl_tot.to_crs(srid)

    # It turns out that this overlay is impossibly time-consuming for large models, but no much way around it
    # # We guarantee that there are locations in every zone by overlaying the zones with the tracts
    # # And later generating locations for each one of the sub-polygons
    ctrl_tot = gpd.overlay(zone_layer, ctrl_tot, how="intersection", keep_geom_type=False)
    ctrl_tot.loc[:, "housing_units"] = np.ceil(ctrl_tot.density * ctrl_tot.geometry.to_crs(3857).area)

    # Get the total number of households in the area by building size
    fields = {
        "total": "DP04_0001E",
        "single_family": "DP04_0007E",
        "single_family_attached": "DP04_0008E",
        "two_units": "DP04_0009E",
        "three_to_four_units": "DP04_0010E",
        "five_to_nine_units": "DP04_0011E",
        "ten_to_nineteen_units": "DP04_0012E",
        "twenty_or_more_units": "DP04_0013E",
        "mobile_homes": "DP04_0014E",
        "boat_rv_van_etc": "DP04_0015E",
    }

    hh_data = dict.fromkeys(fields.keys(), 0)
    for _, state_fips, county_fips in state_counties[["STATEFP", "COUNTYFP"]].drop_duplicates().to_records():
        for k, x in fields.items():
            hh_data[k] += c.acs5dp.state_county(("NAME", x), state_fips, county_fips)[0][x]

    multi_distribution = np.array(
        [
            hh_data["two_units"],
            hh_data["three_to_four_units"],
            hh_data["five_to_nine_units"],
            hh_data["ten_to_nineteen_units"],
            hh_data["twenty_or_more_units"],
        ]
    )
    multi_distribution = np.cumsum(multi_distribution) / multi_distribution.sum()
    multi_multipliers = np.array([2, 3.5, 7, 14.5, 40])

    # Randomly distribute locations for each tract in the modeling region, picking them from buildings
    np.random.seed(1)
    all_locations = []
    tot_elements = 0
    ctrl_tot.reset_index(drop=True, inplace=True)

    signal = SIGNAL(object)
    signal.emit(["start", "master", ctrl_tot.shape[0], "Adding residential locations"])  # type: ignore

    for idx, rec in ctrl_tot.iterrows():
        signal.emit(["update", "master", idx + 1, "Adding residential locations"])  # type: ignore
        if not rec.geometry.area:
            continue
        tot = 0
        sizes = []
        while tot < rec.housing_units:
            if np.random.rand() <= rec.prob_single:
                tot += 1
                sizes.append(1)
            else:
                # We find the size of the multi-family in a random fashion
                # considering that the probability of each size is always the same for the entire region
                size_index = np.nonzero(multi_distribution > np.random.rand())[0][0]
                found_size = multi_multipliers[size_index]
                if np.floor(tot + found_size) > rec.housing_units:
                    tot += 1
                    sizes.append(1)
                    continue
                tot += found_size
                sizes.append(found_size)

        tot_elements += len(sizes)
        locs = location_candidates[location_candidates.intersects(rec.geometry)]
        small = min(locs.is_small.sum(), len([x for x in sizes if x == 1]))
        large = min(locs.is_large.sum(), len([x for x in sizes if x > 1]))
        loc_add = [
            locs[locs.is_small == 1].sample(n=small).assign(luse="RESIDENTIAL-SINGLE"),
            locs[locs.is_large == 1].sample(n=large).assign(luse="RESIDENTIAL-MULTI"),
        ]
        all_locations.extend(loc_add)
    signal.emit(["update", "master", ctrl_tot.shape[0], "Adding residential locations"])  # type: ignore
    locs = pd.concat(all_locations)
    remaining_buildings = all_buildings[~all_buildings.index.isin(locs.index)]
    locs = locs.assign(
        loc_id=1 + np.arange(max_loc, max_loc + locs.shape[0]), geo_wkb=locs.geometry.to_wkb(), srid=srid
    )
    lu_base = "INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary) VALUES(?,1,0,0,1);"
    with commit_and_close(net.path_to_file, spatial=True) as conn:
        remove_constraints(conn)
        conn.executemany(lu_base, [["RESIDENTIAL-SINGLE"], ["RESIDENTIAL-MULTI"]])

        zones = DataTableAccess(net.path_to_file).get("Zone", conn)[["zone", "geo"]]
        links = DataTableAccess(net.path_to_file).get("Link", conn)[["link", "geo"]]
        locs = locs.sjoin_nearest(zones)[["loc_id", "luse", "zone", "geo_wkb", "srid", "geometry"]]
        locs = locs.drop_duplicates(subset="loc_id")
        if links.empty:
            locs = locs.assign(link=-1)
        else:
            locs = locs.sjoin_nearest(links, how="left")
            locs = locs.drop_duplicates(subset="loc_id")

        res_locations = locs[["loc_id", "luse", "link", "zone", "geo_wkb", "srid"]]
        conn.executemany(
            "INSERT INTO Location (location, land_use, link, zone, geo) VALUES (?, ?, ?, ?, GeomFromWKB(?, ?))",
            res_locations.to_records(index=False),
        )
    return remaining_buildings


def add_commercial(
    net: Network,
    zone_layer: gpd.GeoDataFrame,
    control_totals: gpd.GeoDataFrame,
    sample_rate: float,
    buildings: gpd.GeoDataFrame,
):
    logging.info("pre-processing non-residential locations")
    with read_and_close(net.path_to_file) as conn:
        max_loc = conn.execute("Select coalesce(max(location) + 1, 1) from Location").fetchone()[0]
        srid = get_srid(conn=conn)

    buildings = buildings[buildings.land_use != "residential"]

    zone_layer = zone_layer.to_crs(srid)
    buildings = buildings.to_crs(srid)
    control_totals = control_totals.to_crs(srid)

    geo_col = control_totals._geometry_column_name
    lu_cols = [col for col in control_totals.columns if col != geo_col]

    # This overlay is extremely time-consuming, but there is no way around it if we want to guarantee that
    # there are locations generated for all zones
    control_totals = control_totals.assign(tot_area_ctrl_tot__=control_totals.geometry.to_crs(3857).area)
    control_totals = gpd.overlay(control_totals, zone_layer, how="intersection", keep_geom_type=False)
    areas = control_totals.geometry.to_crs(3857).area
    for col in lu_cols:
        control_totals[col] = np.ceil(control_totals[col] * areas / control_totals.tot_area_ctrl_tot__)
    control_totals = control_totals[lu_cols + [geo_col]]

    def create_repeated_strings(strings, repetitions):
        return [s for s, r in zip(strings, repetitions) for _ in range(r) if r > 0]

    control_totals = control_totals.reset_index(drop=True)
    all_data = []

    signal = SIGNAL(object)
    signal.emit(["start", "master", control_totals.shape[0], "Adding Adding non-residential locations"])  # type: ignore

    np.random.seed(1)
    for idx, rec in control_totals.iterrows():
        signal.emit(["update", "master", idx + 1, "Adding Adding non-residential locations"])  # type: ignore
        totals = rec[lu_cols].astype(int).tolist()
        total = sum(totals)
        if not total:
            continue
        sample_gdf = buildings[buildings.intersects(rec.geometry)]
        locs = sample_gdf.sample(n=min(total, sample_gdf.shape[0]), replace=False, random_state=idx)
        lus = create_repeated_strings(lu_cols, totals)
        random.shuffle(lus)
        total = locs.shape[0]
        temp_df = pd.DataFrame({"luse": lus[:total], "geometry": locs.geometry})
        all_data.append(gpd.GeoDataFrame(temp_df).set_geometry("geometry"))

    signal.emit(["update", "master", control_totals.shape[0], ""])  # type: ignore
    locs = pd.concat(all_data)
    locs = locs.assign(geo_wkb=locs.geometry.to_wkb(), srid=srid, loc_id=np.arange(max_loc, max_loc + locs.shape[0]))

    lu_base = "INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES(?,0,1,0,0,'');"
    sql_qry = "INSERT INTO Location (location, land_use, link, zone, geo) VALUES (?, ?, ?, ?, GeomFromWKB(?, ?))"
    with commit_and_close(net.path_to_file, spatial=True) as conn:
        remove_constraints(conn)
        conn.executemany(lu_base, [[x] for x in lu_cols])

        zones = (DataTableAccess(net.path_to_file).get("Zone", conn)[["zone", "geo"]]).to_crs(srid)
        links = DataTableAccess(net.path_to_file).get("Link", conn)[["link", "geo"]].to_crs(srid)
        locs = locs.sjoin_nearest(zones, how="left")[["loc_id", "luse", "zone", "geo_wkb", "srid", "geometry"]]
        if links.empty:
            locs = locs.assign(link=-1)
        else:
            locs = locs.sjoin_nearest(links, how="left")
            locs = locs.drop_duplicates(subset="loc_id")
        conn.executemany(sql_qry, locs[["loc_id", "luse", "link", "zone", "geo_wkb", "srid"]].to_records(index=False))


def remove_constraints(conn: sqlite3.Connection):
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("PRAGMA ignore_check_constraints=1")
