# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
from pathlib import Path

import requests
from shapely import Polygon


def download_GTFS_feeds(poly: Polygon, project_path: Path, MOBILITY_DATABASE_API_KEY) -> int:
    """Downloads GTFS feeds from the Mobility Database API and saves them to the appropriate folder."""

    # First step is to download the token
    token_url = "https://api.mobilitydatabase.org/v1/tokens"
    headers = {"Content-Type": "application/json"}
    data = {"refresh_token": MOBILITY_DATABASE_API_KEY}

    response = requests.post(token_url, headers=headers, data=json.dumps(data))
    access_token = response.json()["access_token"]

    # Then we get the list of all GTFS for our modeling area
    min_long, min_lat, max_long, max_lat = poly.bounds
    overlap_type = "completely_enclosed"
    url = "https://api.mobilitydatabase.org/v1/gtfs_feeds"
    headers = {"accept": "application/json", "Authorization": "Bearer {}".format(access_token)}

    params = {
        "limit": 400,
        "offset": 0,
        "dataset_latitudes": f"{min_lat},{max_lat}",
        "dataset_longitudes": f"{min_long},{max_long}",
        "bounding_filter_method": overlap_type,
    }

    response2 = requests.get(url, headers=headers, params=params)  # type: ignore
    if response2.status_code != 200:
        return 0
    feed_list = response2.json()

    # We then download all the feeds to the appropriate folder
    tgt_pth = project_path / "supply" / "gtfs"

    counter = 0
    for feed in feed_list:
        urlk = feed.get("latest_dataset", None)
        if not urlk:
            continue
        url = urlk.get("hosted_url")
        bbox = urlk.get("bounding_box")
        if not url or not bbox:
            continue

        if bbox.get("minimum_latitude", -1000) < min_lat or bbox.get("maximum_latitude", 1000) > max_lat:
            continue
        if bbox.get("minimum_longitude", -1000) < min_long or bbox.get("maximum_longitude", 1000) > max_long:
            continue

        tgt_pth.mkdir(parents=True, exist_ok=True)
        counter += 1
        response = requests.get(url)
        with open(tgt_pth / f'{feed["id"]}.zip', "wb") as file:
            file.write(response.content)
    return counter
