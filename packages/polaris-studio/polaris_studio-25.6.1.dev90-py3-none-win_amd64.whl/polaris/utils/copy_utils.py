# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import contextlib
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Union
import json

from polaris.utils.env_utils import WhereAmI, where_am_i_running

globus_logger = logging.getLogger("globus_sdk")
globus_logger.setLevel(logging.WARN)
CLIENT_ID = "082f7169-7ffe-41b2-be4b-8337fb606ce2"


def magic_copy(src, dest, recursive=True):
    r"""Copy to/from a network location that may require globus for transfer. If not required, copy will be done
    via shutil.

    Note that if running on bebop/crossover, globus will be automatically used.

    Standard globus bindings are available in `GlobusLocation.vms_endpoint_lookup` and addditional endpoints can be
    added through the `GlobusLocation.additional_endpoints = {"/local/path": "endpoint-uuid"}`
    """

    src, dest = normalise_path(src), normalise_path(dest)
    src.copy_to(dest, recursive=recursive)


def globus_copy(src, dest, recursive=True):
    r"""Copy to/from a network location using globus for transfer.

    Standard globus bindings are available in `GlobusLocation.vms_endpoint_lookup` and addditional endpoints can be
    added through the `GlobusLocation.additional_endpoints = {"/local/path": "endpoint-uuid"}`
    """

    src, dest = GlobusLocation.from_path(src), GlobusLocation.from_path(dest)
    src.copy_to(dest, recursive=recursive)


@contextlib.contextmanager
def without_statcopy():
    """A simple context manager to remove the shutil copystat behaviour that breaks on our windows fileshares."""
    _orig_copystat = shutil.copystat
    shutil.copystat = lambda x, _: x  # type: ignore
    yield
    shutil.copystat = _orig_copystat


class FileLocation(object):
    pass


class ShutilLocation(FileLocation):  # pragma: no cover
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)

    def copy_to(self, destination: "ShutilLocation", recursive: bool = True):
        with without_statcopy():
            if self.path.is_dir():
                shutil.copytree(self.path, destination.path, copy_function=shutil.copyfile, dirs_exist_ok=True)
            else:
                dst = destination.path / self.path.name if destination.path.is_dir() else destination.path
                shutil.copyfile(self.path, dst)


class GlobusLocation(FileLocation):  # pragma: no cover
    def __init__(self, endpoint, relative_path, abs_path, lcrc=False) -> None:
        self.endpoint: str = endpoint
        self.relative_path: Path = relative_path
        self.abs_path: Path = abs_path
        self.lcrc = lcrc

    lcrc_endpoint = "15288284-7006-4041-ba1a-6b52501e49f1"
    additional_endpoints: Dict[str, str] = {}
    vms_endpoint_lookup = {
        "/mnt/r/": "11519a30-abe2-11ed-adfd-bfc1a406350a",
        "/mnt/cfs2/": "5f357028-e63d-11ee-a2dd-51e3263d68d3",
        "/mnt/cfs/": "8637d35c-e3f3-11ed-9a61-83ef71fbf0ae",
        "/mnt/q/FY24/2409 - GPRA_Study/": "43fad83c-2470-11ee-80c1-a3018385fcef",
        "/mnt/q/FY25/2503 - C2C Chicago Runs/": "4f3b2b5e-fd4c-11ef-9207-0affeb6b961d",
        "/mnt/p/ShareAndFileTransfer/": "4f5782ec-ff82-11ed-ba4c-09d6a6f08166",
        "/mnt/p/VMS_Software/15-CI-CD-Artifacts/": "3643bc1a-ea3f-11ed-9ba5-c9bb788c490e",
        "/mnt/gpra24_results/": "17f7261a-3ae0-11ee-9209-5b20905a64b1",
        "/mnt/s/VMS_POLARIS/2 - PROJECTS & TASKS/14 - TNC-Related": "3973606c-3af2-11ee-87bc-4dfadf03ac7e",
    }

    @classmethod
    def set_additional_endpoints(cls, additional_endpoints):
        logging.info("Setting additional endpoints")
        cls.additional_endpoints = additional_endpoints

    @classmethod
    def from_path(cls, path):
        if "GLOBUS_ADD_ENDPOINTS" in os.environ and len(cls.additional_endpoints) == 0:
            endpoints_to_add: Dict[str, str] = json.loads(os.environ["GLOBUS_ADD_ENDPOINTS"])
            cls.set_additional_endpoints(endpoints_to_add)

        # Check if additional end points are defined and merge them into the list
        endpoint_lookup = cls.vms_endpoint_lookup | cls.additional_endpoints
        for path_prefix, endpoint in endpoint_lookup.items():
            if str(path).startswith(path_prefix):
                return GlobusLocation(endpoint, str(path).replace(path_prefix, "/"), Path(path))
        if str(path).startswith("/lcrc/"):
            return GlobusLocation(cls.lcrc_endpoint, str(path), Path(path), lcrc=True)
        raise RuntimeError(f"Can't figure out a globus endpoint for {path}")

    def __repr__(self) -> str:
        return f"{self.endpoint}:{self.relative_path}"

    # Note the use of "forward-declared" type for the dest, see:
    #   https://stackoverflow.com/questions/40049016/using-the-class-as-a-type-hint-for-arguments-in-its-methods
    def copy_to(self, dest: "GlobusLocation", recursive=True):
        from globus_sdk import TransferClient, TransferData

        if self.can_do_locally(dest):
            self.local_copy_to(dest)
            return

        tc = TransferClient(authorizer=get_globus_auth())

        logging.info(f"MAGIC_COPY\n src: {self}\ndest: {dest}")

        tdata = TransferData(tc, self.endpoint, dest.endpoint, sync_level="checksum")
        tdata.add_item(str(self.relative_path), str(dest.relative_path), recursive=recursive)
        transfer_result = tc.submit_transfer(tdata)
        task_id = transfer_result["task_id"]

        count = 0
        while not tc.task_wait(task_id, timeout=10):
            print(".", end="", flush=True)
            count += 1
            if count % 6 == 0:
                print(" ", end="", flush=True)
        print("")

    def can_do_locally(self, dest):
        return self.lcrc and dest.lcrc

    def local_copy_to(self, dest: "GlobusLocation"):
        ShutilLocation(self.relative_path).copy_to(ShutilLocation(dest.relative_path))


def get_globus_auth(force_reauth: bool = False):  # pragma: no cover
    from globus_sdk import RefreshTokenAuthorizer, NativeAppAuthClient
    from globus_sdk.tokenstorage import SQLiteAdapter

    client = NativeAppAuthClient(CLIENT_ID)
    token_storage_file = Path(os.path.expanduser("~/.globus/cli/storage.db"))
    token_storage_file.parent.mkdir(parents=True, exist_ok=True)  # make sure dir exists

    adapter = SQLiteAdapter(token_storage_file, namespace="eqsql")
    token_data = adapter.get_token_data("transfer.api.globus.org")
    scopes = [
        "urn:globus:auth:scope:transfer.api.globus.org:all",
        "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/15288284-7006-4041-ba1a-6b52501e49f1/data_access]",
    ]

    if not token_data or force_reauth:
        client.oauth2_start_flow(refresh_tokens=True, requested_scopes=scopes)

        print(f"Please go to this URL and login: {client.oauth2_get_authorize_url()}")

        get_input = getattr(__builtins__, "raw_input", input)
        auth_code = get_input("Please enter the code here: ").strip()
        adapter.store(client.oauth2_exchange_code_for_tokens(auth_code))
        token_data = adapter.get_token_data("transfer.api.globus.org")

    if not token_data:
        raise RuntimeError("Could not obtain a globus token")

    return RefreshTokenAuthorizer(
        token_data["refresh_token"],
        client,
        access_token=token_data["access_token"],
        expires_at=token_data["expires_at_seconds"],
    )


def normalise_path(path) -> FileLocation:
    where_am_i = where_am_i_running()
    if (
        where_am_i == WhereAmI.BEBOP_CLUSTER
        or where_am_i == WhereAmI.CROSSOVER_CLUSTER
        or where_am_i == WhereAmI.IMPROV_CLUSTER
    ):
        return GlobusLocation.from_path(path)
    else:
        return ShutilLocation(path)
