# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from contextlib import contextmanager
import logging
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from polaris.utils.logging_utils import function_logging


class ScenarioCompression:
    DEFAULT_NAME = "content.tar.gz"

    def __init__(self, target_folder, target_file_name=None, split_individual_files=True):
        self.target_folder = Path(target_folder)
        self.target_file_name = Path(target_file_name or self.DEFAULT_NAME)
        self.split_individual_files = split_individual_files
        self.files_added = {}

    @function_logging("        ~   Compressing files")
    def compress(self):
        try:
            self.create_tar_files()
            if self.check_created_compress_file():
                self.delete_files()
            else:
                return False
            return True
        except Exception:
            logging.error("Error while compressing:")
            logging.error(sys.exc_info())
            return False

    @function_logging("        ~   Decompressing files")
    def decompress(self):
        try:
            files_to_decompress = Path(self.target_folder).glob("*.tar.gz")
            for f in files_to_decompress:
                orig_file = f.parent / f.name.replace(".tar.gz", "")
                ScenarioCompression.maybe_extract(orig_file)
        except Exception:
            logging.error("Error while decompressing:")
            logging.error(sys.exc_info())
            return False

    @staticmethod
    def maybe_extract(file: Path):
        if file.exists():
            return file
        tar_file = file.with_suffix(file.suffix + ".tar.gz")
        if tar_file.exists():
            if not shutil.which("pigz"):
                logging.error("Please install pigz (sudo apt install pigz)")
                ScenarioCompression.python_decompress(tar_file, file.parent)
            else:
                ScenarioCompression.pigz_decompress(tar_file, file.parent)

        # If the file still doesn't exist, we've run out of things to try
        if not file.exists():
            raise FileNotFoundError(f"Couldn't find (or extract) file: {file}")
        return file

    def create_tar_files(self):
        exts_to_compress = [".sqlite"]
        filter = lambda ff: ff != self.target_file_name and any(ff.endswith(e) for e in exts_to_compress)
        files_to_compress = [ff for ff in os.listdir(str(self.target_folder)) if filter(ff)]

        if not self.split_individual_files:
            self.create_single_tar_file(files_to_compress)
        else:
            self.create_many_tar_files(files_to_compress)

    def create_single_tar_file(self, files_to_compress):
        self.files_added[self.target_file_name] = files_to_compress
        tar_filename = self.target_folder / self.target_file_name
        logging.info(f"        ~     Compressing {files_to_compress} into {tar_filename}")
        self.compress_things(files_to_compress, tar_filename)

    def create_many_tar_files(self, files_to_compress):
        logging.info(f"        ~     Compressing {files_to_compress} in dir {self.target_folder}")

        for f in files_to_compress:
            logging.info(f"        ~       - {f}")
            tar_gz_file = self.target_folder / f"{f}.tar.gz"
            self.files_added[f"{f}.tar.gz"] = [self.target_folder / f]
            self.compress_things([f], tar_gz_file)

    def compress_things(self, files, tar_gz_file):
        if shutil.which("pigz"):
            self.fast_pigz_compress(files, tar_gz_file)
        else:
            self.slow_python_compression(files, tar_gz_file)

    def fast_pigz_compress(self, files, tar_gz_file):
        files_str = " ".join(files)
        cmd = f'tar --use-compress-program="pigz -k " -cf {tar_gz_file} {files_str}'
        subprocess.check_output(cmd, shell=True, cwd=self.target_folder, encoding="utf-8")

    @staticmethod
    def pigz_decompress(tar_gz_file, target_dir):
        cmd = f" pigz -dc '{tar_gz_file}' | tar xf - -m -C '{target_dir}'"
        subprocess.check_output(cmd, shell=True, cwd=target_dir, encoding="utf-8")

    @staticmethod
    def python_decompress(tar_gz_file, target_dir):
        with tarfile.TarFile.gzopen(tar_gz_file, mode="r") as tar_file:
            tar_file.extractall(target_dir)

    def slow_python_compression(self, files, tar_gz_file):
        with tarfile.TarFile.gzopen(tar_gz_file, mode="w", compresslevel=9) as tar_file:
            for f in files:
                tar_file.add(self.target_folder / f, arcname=f, recursive=False)

    def check_created_compress_file(self):
        logging.info("        ~   Checking that compressed files were created cleanly")
        for k, v in self.files_added.items():
            filename = Path(self.target_folder, k)
            tar_file = tarfile.TarFile.open(filename, mode="r")
            members = tar_file.getmembers()
            if len(members) != len(v):
                logging.warning(f"Number of files didn't match for {filename}")
                return False
        logging.info("        ~   All tar.gz files pass sanity checking")
        return True

    def delete_files(self):
        logging.info("        ~   Deleting files which were compressed")
        delete_it = lambda f: shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)
        [delete_it(f) for tar_f in self.files_added for f in self.files_added[tar_f]]


@contextmanager
def extract_read_and_close(file: Path, keep_extracted: bool = False, **kwargs):
    """
    A context manager for reading from a potentially compressed SQLite file.
    The manager will handle, extracting the file if required, establishing the connection. After the
    block completes it will close the connection and delete any extracted sqlite file.

    :param file: Path to the SQLite file (compressed or uncompressed).
    :param keep_extracted: If False, deletes the extracted file after use.
    :param kwargs: Additional arguments passed to `commit_and_close`.
    :yield: The SQLite connection.
    """

    try:
        from polaris.utils.database.db_utils import commit_and_close

        extracted_file = maybe_extract(file) if not file.exists() else None

        with commit_and_close(file, **kwargs) as conn:
            yield conn  # Pass the connection back to the caller
    finally:
        if extracted_file is not None and not keep_extracted and extracted_file.exists():
            os.remove(extracted_file)


maybe_extract = ScenarioCompression.maybe_extract
