# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
def migrate(conn):
    from polaris.network.active.active_networks import ActiveNetworks

    ActiveNetworks.update_bearing(conn)
