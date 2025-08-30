# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
from pathlib import Path
from typing import List

from polaris.utils.database.database_dumper import get_table_data, EXCL_NAME_PAT
from polaris.utils.database.db_utils import read_and_close, list_tables_in_db
from polaris.utils.testing.model_comparison.compare_tables import compare_tables


def compare_databases(old_path: Path, new_path: Path, tables_to_compare=None) -> List[str]:
    report = []
    tables_to_compare = [e.lower() for e in tables_to_compare] if tables_to_compare else None

    def table_matcher(tn):
        excluded = any(x.match(tn) for x in EXCL_NAME_PAT)
        included = tables_to_compare is None or tn in tables_to_compare
        return included and not excluded

    with read_and_close(new_path, spatial=True) as conn_new:
        new_tables = [tn for tn in list_tables_in_db(conn_new) if table_matcher(tn)]
        with read_and_close(old_path, spatial=True) as conn_old:
            old_tables = [tn for tn in list_tables_in_db(conn_old) if table_matcher(tn)]

            dropped_tables = [x for x in old_tables if x not in new_tables]
            if dropped_tables:
                report.extend(["**Dropped tables**:\n", f"{', '.join(dropped_tables)}\n"])
            else:
                report.append("**No dropped tables**\n")

            added_tables = [x for x in new_tables if x not in old_tables]
            if added_tables:
                report.extend(["**New tables**:\n", f"{', '.join(added_tables)}\n"])
            else:
                report.append("**No new tables**\n")

            # Compares one table at a time
            no_change = []
            table_changes = []
            for table in new_tables:
                if table not in old_tables:
                    continue
                logging.info(table)
                table_report = compare_tables(get_table_data(conn_old, table), get_table_data(conn_new, table))
                if len(table_report):
                    table_changes.append(f"\n{table}:\n")
                    table_changes.extend(table_report)
                else:
                    no_change.append(table)

            if no_change:
                report.extend(["**Tables with no changes**:\n", f"{', '.join(no_change)}\n"])

            if table_changes:
                report.append("\n\n**Tables with changes**:")
                report.extend(table_changes)

    return report
