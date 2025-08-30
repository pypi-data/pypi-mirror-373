# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import pandas as pd
from pathlib import Path
import requests
import zipfile
import io
import tempfile


class NHTSDataset:

    def __init__(self, hh_df, per_df, trip_df, veh_df):
        self.trip_df = trip_df.copy()
        self.per_df = per_df.copy()
        self.hh_df = hh_df.copy()
        self.veh_df = veh_df.copy()

    def filter_to_hh_state(self, statecode=None, statefips=None):
        if statecode is None and statefips is None:
            raise ValueError("Must provide either statecode or statefips")
        if statecode is not None and statefips is not None:
            raise ValueError("Must provide only one of statecode or statefips")

        if statecode is not None:
            filtervar = "HHSTATE"
            filterval = statecode
        else:
            filtervar = "HHSTFIPS"
            filterval = statefips

        hh_df = self.hh_df[self.hh_df[filtervar] == filterval]
        per_df = self.per_df[self.per_df[filtervar] == filterval]
        trip_df = self.trip_df[self.trip_df[filtervar] == filterval]
        veh_df = self.veh_df[self.veh_df[filtervar] == filterval]

        if len(trip_df) == 0 or len(per_df) == 0 or len(hh_df) == 0:
            raise ValueError(f"No data found for {filtervar} = {filterval}")

        return self.__class__(hh_df, per_df, trip_df, veh_df)

    def save(self, dir):
        dir = Path(dir)
        dir.mkdir(exist_ok=True, parents=True)
        self.hh_df.to_parquet(dir / "hhpub.parquet")
        self.per_df.to_parquet(dir / "perpub.parquet")
        self.trip_df.to_parquet(dir / "trippub.parquet")
        self.veh_df.to_parquet(dir / "vehpub.parquet")

    @classmethod
    def download(cls, csv_zip_url, unzip_dir=None):
        if unzip_dir is None:
            with tempfile.TemporaryDirectory() as temp_dir:
                cls.download(csv_zip_url, unzip_dir=temp_dir)
                return cls.from_dir(temp_dir)
        else:
            unzip_dir = Path(unzip_dir)
            response = requests.get(csv_zip_url)
            if response.status_code != 200:
                raise RuntimeError(f"Failed to download {csv_zip_url}")
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(unzip_dir)

            return cls.from_dir(unzip_dir)

    @classmethod
    def from_dir(cls, dir):
        dir = Path(dir)
        if (dir / "hhpub.csv").exists():
            return cls.from_csv_dir(dir)
        elif (dir / "hhpub.parquet").exists():
            return cls.from_parquet_dir(dir)
        else:
            raise FileNotFoundError(f"Couldn't find a hhold file in directory: {dir}")

    @classmethod
    def from_csv_dir(cls, dir):
        dir = Path(dir)
        hh = pd.read_csv(dir / "hhpub.csv")
        per = pd.read_csv(dir / "perpub.csv")
        trip = pd.read_csv(dir / "trippub.csv")
        veh = pd.read_csv(dir / "vehpub.csv")
        return cls(hh, per, trip, veh)

    @classmethod
    def from_parquet_dir(cls, dir):
        dir = Path(dir)
        hh = pd.read_parquet(dir / "hhpub.parquet")
        per = pd.read_parquet(dir / "perpub.parquet")
        trip = pd.read_parquet(dir / "trippub.parquet")
        veh = pd.read_parquet(dir / "vehpub.parquet")
        return cls(hh, per, trip, veh)
