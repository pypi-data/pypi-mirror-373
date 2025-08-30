# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import shutil

import pandas as pd
from polaris.utils.database.db_utils import add_column_unless_exists, filename_from_conn
from polaris.utils.list_utils import first_and_only


def migrate(conn):
    add_column_unless_exists(conn, "Person", "disability", "INT", "DEFAULT 2")
    add_column_unless_exists(conn, "Person", "escooter_use_level", "INT", "DEFAULT 0")

    try:
        try_to_patch_linker_file(conn)
    except Exception:
        logging.warning("Something went wrong updating linker file with disability")
        logging.warning("You will likely have to update files by hand.")


def try_to_patch_linker_file(conn):
    data_dir = filename_from_conn(conn).parent
    linker_file = data_dir / "linker_file.txt"
    with open(linker_file) as f:
        contents = f.readlines()

    def get_line(tag):
        return first_and_only([e for e in contents if e.startswith(tag)]).strip().split("\t")

    # Looks for pums person file and make sure it has some kind of disability data in it (or make it up)
    _, person_file = get_line("PERSONFILE")
    person_file = data_dir / person_file

    sep = "," if person_file.name.endswith("csv") else "\t"
    df = pd.read_csv(person_file, sep=sep)
    if "DIS" not in df.columns:
        logging.warning(f"Disability column missing from {person_file}, adding default value")
        df["DIS"] = 2  # assign a new col with default data
        shutil.move(person_file, person_file.with_suffix(person_file.suffix + ".backup"))
        df.to_csv(person_file, sep=sep, index=False)

    # Make sure that the PERSONDATA record in the linker file has the correct DIS index in the 17th position
    col_index = list(df.columns).index("DIS")
    _, *person_data = get_line("PERSONDATA")
    if len(person_data) == 17:
        if int(person_data[-1]) != col_index:
            logging.warning(
                "There are already 17 records in PERSONDATA, but the last one isn't disbility."
                "You'll need to update by hand"
            )
        else:
            logging.info("PERSONDATA looks good")
        return
    if len(person_data) != 16:
        logging.warning("Wrong number of args in linker file - you'll need to update PERSONDATA by hand")
        return

    # we just need to add this column as the 17th entry
    shutil.move(linker_file, linker_file.with_suffix(".txt.backup"))
    with open(linker_file, "w") as f:
        for e in contents:
            if e.startswith("PERSONDATA"):
                row = ["PERSONDATA", *person_data] + [str(col_index)]
                f.write("\t".join(row))
            else:
                f.write(e)


# if __name__ == "__main__":
#     demand_db = "/mnt/q/FY23/2308 - EScooter Study/base-model/chicago_new_abm_base/Chicago-Demand.sqlite"
#     with read_and_close(demand_db) as conn:
#         migrate(conn)
