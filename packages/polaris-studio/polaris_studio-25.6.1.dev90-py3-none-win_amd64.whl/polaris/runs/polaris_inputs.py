# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import dataclasses
import shutil
from pathlib import Path


@dataclasses.dataclass
class PolarisInputs:
    supply_db: Path
    demand_db: Path
    freight_db: Path
    result_db: Path
    result_h5: Path
    highway_skim: Path
    transit_skim: Path
    summary: Path
    gap: Path
    db_name: str

    @staticmethod
    def from_dir(dir, db_name=None, use_parent_supply=False):
        dir = Path(dir)
        if not dir.exists():
            raise FileNotFoundError(f"No such directory {dir}")
        if db_name is None:
            db_name = PolarisInputs.guess_db_name(dir)
        if use_parent_supply:
            supply = dir.parent / f"{db_name}-Supply.sqlite"
        else:
            supply = dir / f"{db_name}-Supply.sqlite"
        demand = dir / f"{db_name}-Demand.sqlite"
        freight = dir / f"{db_name}-Freight.sqlite"
        result = dir / f"{db_name}-Result.sqlite"
        result_h5 = dir / f"{db_name}-Result.h5"
        highway_skim = dir / "highway_skim_file.omx"
        transit_skim = dir / "transit_skim_file.omx"
        gap = dir / "gap_calculations.csv"
        summary = dir / "summary.csv"
        return PolarisInputs(
            supply, demand, freight, result, result_h5, highway_skim, transit_skim, summary, gap, db_name
        )

    def copy_to_dir(self, target_dir, copy_skims):
        shutil.copy(self.supply_db, target_dir)
        shutil.copy(self.demand_db, target_dir)
        shutil.copy(self.highway_skim, target_dir)
        if copy_skims:
            self.transit_skim.exists() and shutil.copy(self.transit_skim, target_dir)
        # The results files might not exist yet
        self.result_db.exists() and shutil.copy(self.result_db, target_dir)
        self.result_h5.exists() and shutil.copy(self.result_h5, target_dir)

    def restore_from_dir(self, backup_dir, restore_skims):
        shutil.copy(backup_dir / self.supply_db.name, self.supply_db)
        shutil.copy(backup_dir / self.demand_db.name, self.demand_db)
        shutil.copy(backup_dir / self.highway_skim.name, self.highway_skim)
        if restore_skims:
            shutil.copy(backup_dir / self.transit_skim.name, self.transit_skim)
        shutil.copy(backup_dir / self.result_db.name, self.result_db)
        shutil.copy(backup_dir / self.result_h5.name, self.result_h5)

    @staticmethod
    def guess_db_name(dir: Path):
        for pattern in ["*-Supply.sqlite", "*-Supply.sqlite.tar.gz", "*-Demand.sqlite", "*-Demand.sqlite.tar.gz"]:
            files = list(dir.glob(pattern))
            if len(files) == 1:
                return files[0].name.split("-")[0]
        raise RuntimeError(f"Couldn't guess dbname for directory: {dir}")
