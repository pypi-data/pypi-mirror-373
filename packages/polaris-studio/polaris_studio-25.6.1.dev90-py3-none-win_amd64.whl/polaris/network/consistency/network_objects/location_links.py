# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging

import geopandas as gpd
import numpy as np
import pandas as pd

link_types_for_ext = ["EXPRESSWAY", "FREEWAY", "EXTERNAL"]


def location_links_builder(lnks: gpd.GeoDataFrame):
    # First we will create the main direction for each location

    # We only need one record per location, so we get the closest link for each location that
    # allows for both cars and pedestrians and the closest link that allow cars if no link allows for both
    closest_both = lnks[(lnks.is_auto) & (lnks.is_walk)]
    closest_cars = lnks[lnks.is_auto & (~lnks.location.isin(closest_both.location))]
    closest = pd.concat([closest_both, closest_cars])
    closest = closest.sort_values("distance").drop_duplicates("location").reset_index(drop=True)

    # We get the closest link and its projection and return the projection point
    logging.debug("Location_Links - Getting projection points")
    vectors = closest.loc_geo.shortest_line(closest.geometry)
    coords = vectors.get_coordinates()
    coords = coords[coords.index.duplicated(keep="first")]

    prj_p = gpd.GeoSeries.from_xy(coords["x"], coords["y"], crs=closest.crs)

    # We will now compute the vector connecting each location to its closest link
    # and rotate it by 45 degrees to get a proper coverage around the location
    alpha_ = np.arctan2(prj_p.y - closest.loc_geo.y, prj_p.x - closest.loc_geo.x)
    x_ = closest.loc_geo.x
    y_ = closest.loc_geo.y

    # The closest link will always be included
    loc_links = [closest[["location", "link"]]]

    # Now we loop through all angles at 45 degree intervals to get all surrounding links
    rotated = []
    for rot in range(45, 360, 45):
        logging.debug(f"Location_Links - Rotating vector by {rot} degrees")
        alpha = alpha_ + np.radians(rot)
        x = x_ + closest.dist_thresh * np.cos(alpha)
        y = y_ + +closest.dist_thresh * np.sin(alpha)
        prj_p = gpd.GeoSeries.from_xy(x, y, crs=closest.crs)
        vector = closest.loc_geo.shortest_line(prj_p)
        # Bring the vector to the location link dataframe
        gdf = lnks.merge(
            pd.DataFrame({"location": closest.location, "vec_geo": vector, "angle": rot}), on="location", how="inner"
        )
        rotated.append(gdf)
    gdf = pd.concat(rotated, ignore_index=True)
    gdf = gdf[gdf.geometry.intersects(gdf.vec_geo)]

    # We update the distance to be the distance from the location to the link in that SPECIFIC direction
    gdf.distance = gdf.loc_geo.distance(gdf.vec_geo.intersection(gdf.geometry))
    gdf = gdf.sort_values("distance").drop_duplicates(subset=["location", "angle"])
    loc_links.append(gdf[["location", "link"]])

    # There are rare cases where the candidates are just at the limit of the distance threshold
    # And imprecision, as well
    return pd.concat(loc_links).drop_duplicates(ignore_index=True).sort_values(by=["location", "link"])


def loc_link_candidates(locs, links_layer, maximum_distance):
    # We search all link candidates for all locations at once
    # This is MUCH faster than going blind for each location
    dt = maximum_distance

    links_layer = links_layer.assign(
        is_auto=links_layer.use_codes.str.contains("AUTO"), is_walk=links_layer.use_codes.str.contains("WALK")
    )

    all_loc_links = []
    locs = locs.rename_geometry("loc_geo")
    while locs.shape[0] > 0 and dt < 50000:
        loc_buff = gpd.GeoDataFrame(locs[["location"]], geometry=locs.buffer(dt), crs=locs.crs)
        loc_links = links_layer.sjoin(loc_buff, how="inner", predicate="intersects")
        loc_links = loc_links.merge(locs[["location", "land_use", "loc_geo"]], on="location")
        loc_links = loc_links.assign(distance=loc_links.geometry.distance(loc_links.loc_geo))
        loc_links = loc_links[((loc_links.is_auto & loc_links.is_walk) | (loc_links.land_use == "EXTERNAL"))]
        loc_links = loc_links.assign(dist_thresh=dt)
        locs = locs[~locs.location.isin(loc_links.location)]
        dt *= 1.2
        all_loc_links.append(loc_links)

    if not all_loc_links:
        # No records?  Let's get out of here
        return pd.DataFrame(columns=["location", "link"])

    loc_links_table = pd.concat(all_loc_links)
    if "EXTERNAL" not in loc_links_table.land_use.unique():
        # No external locations to pay special attention to?  Let's get out of here
        return loc_links_table

    other_loc_links = loc_links_table[loc_links_table.land_use != "EXTERNAL"]
    ext_loc_links = loc_links_table[loc_links_table.land_use == "EXTERNAL"]

    # Let's only get the closest link (and others VERY close to it, say 1500m) for external locations
    all_candidates = [] if other_loc_links.empty else [other_loc_links]
    for loc, df_ in ext_loc_links.groupby("location"):
        ext_single_loc_link = df_[df_["distance"] < df_["distance"].min() + 1500]

        df = ext_single_loc_link[ext_single_loc_link["type"].isin(link_types_for_ext)]
        if df.empty:
            logging.warning(f"We could not connect location {loc} with a link of any of the types {link_types_for_ext}")
        else:
            ext_single_loc_link = df

        if ext_single_loc_link.empty:
            raise Exception("We got an empty set of location links for external locations")

        all_candidates.append(ext_single_loc_link)

    return pd.concat(all_candidates)
