# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import json
import logging
from pathlib import Path
from tempfile import gettempdir
from typing import ClassVar

from appdirs import user_config_dir
from pydantic import BaseModel


class UserConfig(BaseModel):
    """Class to store user"""

    census_api: str = ""
    mobility_database_api: str = ""
    nrel_api: str = ""
    last_model_opened: Path = Path(gettempdir())
    osm_url: str = "http://overpass-api.de/api"

    _saving: ClassVar[bool] = True
    config_dir: ClassVar[Path] = Path(user_config_dir("polaris")).parent
    config_file: ClassVar[Path] = config_dir / "polaris_user_configs.json"
    osm_cache: ClassVar[Path] = config_dir / "osm_cache.sqlite"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if self.config_file.exists():
            type(self)._saving = False
            with open(self.config_file, "r") as f:
                for key, value in json.loads(f.read()).items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                    else:
                        logging.error(f"Invalid configuration found in user config file: {key}.  Ignoring it")
            type(self)._saving = True

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if self._saving:
            with open(self.config_file, "w") as f:
                f.write(self.model_dump_json())
                logging.warning(
                    f"Configurations, including API keys, are stored as plain text in {str(self.config_file)}"
                )

    @classmethod
    def del_config(cls):
        """Delete the user config file."""
        if cls.config_file.exists():
            cls.config_file.unlink()
            logging.warning(f"Deleted user config file: {cls.config_file}")
        else:
            logging.warning(f"User config file does not exist: {cls.config_file}")
