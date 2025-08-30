# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import hashlib
import logging
import os
from tempfile import gettempdir

import duckdb
import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon

overture_url = "s3://overturemaps-us-west-2/release/2025-05-21.0"


def get_building_locations(model_area: gpd.GeoDataFrame, srid: int) -> gpd.GeoDataFrame:
    transformed_ma = model_area.to_crs(4326)

    tempfile_name = os.path.join(gettempdir(), tempfile_cache(transformed_ma.union_all()) + "_locs.parquet")
    if os.path.exists(tempfile_name):
        return gpd.read_parquet(tempfile_name)
    else:
        buildings = get_buildings(transformed_ma)
        buildings = gpd.GeoDataFrame(buildings, geometry=buildings.geometry.to_crs(3857).centroid.to_crs(srid))
        buildings.to_parquet(tempfile_name)
        return buildings


def get_pois(model_area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return get_overture_elements(model_area, theme="places")


def get_buildings(model_area: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return get_overture_elements(model_area, theme="buildings")


def get_overture_elements(model_area: gpd.GeoDataFrame, theme="buildings") -> gpd.GeoDataFrame:
    transformed_ma = model_area.to_crs(4326)
    unary_union = transformed_ma.union_all()

    file_stub = tempfile_cache(unary_union)
    tempfile_name = os.path.join(gettempdir(), file_stub + f"_{theme}.parquet")
    tempfile_name_filtered = os.path.join(gettempdir(), file_stub + f"_{theme}_filtered.parquet")

    if os.path.exists(tempfile_name_filtered):
        # If the filtered file exists, we return it
        return gpd.read_parquet(tempfile_name_filtered)

    # Otherwise let's get through the motions
    if os.path.exists(tempfile_name):
        # If the downloaded and converted file exists, we load it
        gdf = gpd.read_parquet(tempfile_name)
    else:
        # Otherwise we download it
        minx, miny, maxx, maxy = unary_union.bounds
        conn = duckdb.connect()
        c = conn.cursor()

        c.execute("""INSTALL spatial; INSTALL httpfs; INSTALL parquet;""")
        c.execute("""LOAD spatial; LOAD parquet; SET s3_region='us-west-2';""")

        logging.info(f"Downloading {theme} from Overture maps. Sit tight! This may take a while.")
        qrys = {
            "buildings": f"""COPY (
                        SELECT id, height, class as land_use, geometry
                        FROM read_parquet('{overture_url}/theme=buildings/type=*/*', filename=true, hive_partitioning=1, union_by_name = true)
                        WHERE bbox.xmin BETWEEN {minx} AND {maxx} AND bbox.ymin BETWEEN {miny} AND {maxy}
                        ) TO '{tempfile_name}'
                    WITH (FORMAT 'parquet', COMPRESSION 'ZSTD');""",
            "places": f"""COPY (
                        SELECT id, names.primary AS name, categories.primary as main_category, categories.alternate as other_categories, confidence, geometry
                        FROM read_parquet('{overture_url}/theme=places/type=*/*')
                        WHERE bbox.xmin BETWEEN {minx} AND {maxx} AND bbox.ymin BETWEEN {miny} AND {maxy}
                        ) TO '{tempfile_name}'
                    WITH (FORMAT 'parquet', COMPRESSION 'ZSTD');""",
            "land_use": f"""COPY (
                        SELECT subtype, class AS land_use_class, names.primary AS name, surface, geometry
                        FROM read_parquet('{overture_url}/theme=base/type=land_use/*')
                        WHERE bbox.xmin BETWEEN {minx} AND {maxx} AND bbox.ymin BETWEEN {miny} AND {maxy}
                        ) TO '{tempfile_name}'
                    WITH (FORMAT 'parquet', COMPRESSION 'ZSTD');""",
        }

        _ = c.execute(qrys[theme])

        logging.info(f"{theme} data downloaded. Basic geo-processing")
        df = pd.read_parquet(tempfile_name)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkb(df.geometry, crs=4326))
        gdf.to_parquet(tempfile_name)

    joined = gdf.sjoin(transformed_ma)
    gdf = gdf[gdf.index.isin(joined.index.unique())]

    if theme == "buildings":
        # Add floor area to buildings
        gdf = gdf.assign(floor_area=gdf.geometry.to_crs(3857).area)

    gdf.to_parquet(tempfile_name_filtered)
    return gdf


def tempfile_cache(unary_union: MultiPolygon) -> str:
    # Create the hash object
    hash_object = hashlib.md5(str(round(sum(unary_union.bounds), 5)).encode())
    return hash_object.hexdigest()
