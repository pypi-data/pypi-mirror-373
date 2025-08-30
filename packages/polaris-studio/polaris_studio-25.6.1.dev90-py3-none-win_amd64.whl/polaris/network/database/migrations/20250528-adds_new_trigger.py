# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md


def migrate(conn):
    sql = """create trigger if not exists polaris_sign_on_delete_record after delete on Sign
              begin
                UPDATE Node SET control_type = '' WHERE node=old.nodes;
              end;"""
    conn.execute(sql)
