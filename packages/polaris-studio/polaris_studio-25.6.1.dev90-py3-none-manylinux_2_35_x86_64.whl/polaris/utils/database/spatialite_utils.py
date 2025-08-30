# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from contextlib import closing
import logging
import os
import shutil
from os.path import join, basename
from pathlib import Path
from sqlite3 import Connection
from tempfile import gettempdir
from typing import Optional
from zipfile import ZipFile

from polaris.utils.dir_utils import mkdir_p
from polaris.utils.env_utils import WhereAmI, is_windows, inside_qgis, where_am_i_running
from polaris.utils.type_utils import AnyPath


def connect_spatialite(path_to_file: AnyPath, missing_ok: bool = False) -> Connection:
    if inside_qgis:
        import qgis  # type: ignore

        return qgis.utils.spatialite_connect(str(path_to_file))

    ensure_spatialite_binaries()
    return _connect_spatialite(path_to_file, missing_ok)


def _connect_spatialite(path_to_file: AnyPath, missing_ok: bool = False):
    from polaris.utils.database.db_utils import safe_connect

    conn = safe_connect(path_to_file, missing_ok)
    conn.enable_load_extension(True)

    # Load the version specified in the environment (if specified) or just attempt to find on the path otherwise
    conn.load_extension(os.environ.get("MOD_SPATIALITE_PATH", "mod_spatialite"))
    return conn


def is_spatialite(conn):
    from polaris.utils.database.db_utils import has_table

    return has_table(conn, "geometry_columns")


def ensure_spatialite_binaries(directory: Optional[AnyPath] = None) -> None:
    if is_windows():
        return ensure_spatialite_binaries_windows(directory)
    else:
        return ensure_spatialite_binaries_posix()


def ensure_spatialite_binaries_posix() -> None:
    try:
        conn = _connect_spatialite(":memory:")
        conn.close()
        return

    except Exception:
        pass

    dirs = []
    where_am_i = where_am_i_running()
    if where_am_i in [WhereAmI.BEBOP_CLUSTER, WhereAmI.CROSSOVER_CLUSTER, WhereAmI.IMPROV_CLUSTER]:
        dirs.append(f"/lcrc/project/POLARIS/{where_am_i}/.local/lib")
        dirs.append(f"/lcrc/project/POLARIS/{where_am_i}/.local/lib64")
    else:
        print("Not on bebop/crossover/improv, not adding /lcrc/project/POLARIS/... to search path")
    print("Looking for mod_spatialite in the following directories:", dirs)
    dirs.extend(["/usr/local/lib", "/usr/lib/x86_64-linux-gnu", "~/.local/lib", "~/.local/lib64"])
    so_files = [Path(d).expanduser() / "mod_spatialite.so" for d in dirs]
    so_files = [so for so in so_files if so.exists()]
    if so_files == []:
        raise Exception("I don't know where to find mod_spatialite I'm sorry")

    # We can't modify LD_LIBRARY_PATH dynamically, so we just use the full path to the so file
    os.environ["MOD_SPATIALITE_PATH"] = str(so_files[0]).replace(".so", "")


def ensure_spatialite_binaries_windows(directory: Optional[AnyPath] = None, raise_error=True) -> None:
    dir_path = directory or gettempdir()

    if not _dll_already_exists(Path(dir_path)):
        _download_and_extract_spatialite(Path(dir_path))

    dir_path = str(dir_path)
    if dir_path not in os.environ["PATH"] or "PROJ_LIB" not in os.environ:
        os.environ["PATH"] = dir_path + os.pathsep + os.environ["PATH"]
        os.environ["PROJ_LIB"] = dir_path

    # We need to have the proj.db file in place.
    # The easiest one on Windows is in the public user. On Linux it should not be necessary
    # See why: https://www.gaia-gis.it/fossil/libspatialite/wiki?name=PROJ.6
    projdb_dir = "C:/Users/Public/spatialite/proj"
    Path(projdb_dir).mkdir(parents=True, exist_ok=True)
    if os.path.isfile(join(projdb_dir, "proj.db")):
        return

    shutil.copyfile(join(dir_path, "proj.db"), join(projdb_dir, "proj.db"))


def _dll_already_exists(d: Path) -> bool:
    ext = "dll" if is_windows() else "so"
    return (d / f"mod_spatialite.{ext}").exists()


def _download_and_extract_spatialite(directory: AnyPath) -> None:
    mkdir_p(directory)

    import urllib
    import urllib.request

    # Pretend to be Firefox so we don't get bot-blocked
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)

    url = "http://polaris.taps.anl.gov/resources/spatialite/mod_spatialite-5.1.0-win-amd64.zip"
    zip_file = join(directory, basename(url))

    urllib.request.urlretrieve(url, zip_file)
    ZipFile(zip_file).extractall(directory)
    os.remove(zip_file)


def spatialize_db(conn, logger=None):
    logger = logger or logging
    logger.info("Adding Spatialite infrastructure to the database")
    if not is_spatialite(conn):
        try:
            conn.execute("SELECT InitSpatialMetaData();")
            conn.commit()
        except Exception as e:
            logger.error("Problem with spatialite", e.args)
            raise e
    if not is_spatialite(conn):
        raise RuntimeError("Something went wrong while spatializing the database")


def get_spatialite_version(conn):
    res = conn.execute("SELECT spatialite_version()").fetchone()
    return None if res is None else res[0]


def spatialite_available():
    try:
        with closing(connect_spatialite(":memory:")) as conn:

            spatialize_db(conn)
            assert conn.execute("SELECT 1;").fetchone() == (1,)

            splite_ver = conn.execute("SELECT spatialite_version();").fetchone()[0]
            major, minor, _patch = splite_ver.split(".")
            if int(major) < 5:
                logging.critical(f"Spatialite available but version ({splite_ver}) < 5.0.0 - ST_Azimuth missing.")
            elif int(minor) < 1:
                logging.critical(f"Spatialite available but version ({splite_ver}) is < 5.1.0 - knn functions missing.")
            else:
                logging.info(f"Spatialite is working with version {splite_ver}")
            return True

    except Exception as e:
        print(e)
        logging.info("Spatialite is not available!!")
        return False
