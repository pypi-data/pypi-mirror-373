# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import csv
import glob
import logging
import math
import shutil
import sqlite3
import sys
import time
from contextlib import closing
from itertools import groupby
from pathlib import Path
from polaris.utils.database.db_utils import run_sql_file

from pyomo.environ import (
    ConcreteModel,
    Var,
    Binary,
    NonNegativeReals,
    Constraint,
    SolverFactory,
    Objective,
    maximize,
    SolverStatus,
    TerminationCondition,
)

import yaml
from polaris.utils.database.db_utils import read_about_model_value, write_about_model_value


def copy_transit_files(base_dir, run_dir):
    files_to_copy = glob.glob(f"{base_dir}/output_*.csv")
    files_to_copy += glob.glob(f"{base_dir}/transit_optimization_settings*")
    logging.info(f"Copying {len(files_to_copy)} files matching pattern into {run_dir}")
    if not run_dir.exists():
        logging.warning(f"Something isn't right target dir ({run_dir}) doesn't exist")
        return
    for i in files_to_copy:
        shutil.copy(i, str(run_dir))


#################################################################################################
############################# BEGIN DEFINING PREREQUISITE FUNCTIONS #############################
#################################################################################################
def Clean_DB(Sqdb, printer_off):
    """This function takes Sqdb name cleans the DB."""
    conn = sqlite3.connect(Sqdb)
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    c = conn.cursor()
    if printer_off != True:
        logger.info("Started cleaning the DB...")
    c.executescript(
        """
    -- drop table if exists activity;
    -- drop table if exists path;
    -- drop table if exists path_multimodal;
    -- drop table if exists path_multimodal_links;
    -- drop table if exists Person_Gaps;
    -- drop table if exists trip;
    -- drop table if exists household;
    -- drop table if exists person;
    -- drop table if exists ev_charging;
    -- drop table if exists vehicle;
    drop table if exists boardings_by_agency_and_trip_mode;
    drop table if exists boardings_by_agency_mode_route_stop_time;
    drop table if exists boardings_by_agency_mode_route_time;
    drop table if exists individual_boardings;
    drop table if exists individual_transfers;
    -- drop table if exists tnc_trip;
    -- drop table if exists traveler;"""
    )

    if printer_off != True:
        logger.info("Finished cleaning the DB...")
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.commit()
    conn.close()
    if printer_off != True:
        logger.info("Closed %s." % (Sqdb))


def Input_to_Optimizer(
    Sqdb,
    period_seconds,
    period_minutes,
    time_frame,
    traffic_scale_factor_adjusted,
    FixedOpCostTram,
    FixedOpCostMetro,
    FixedOpCostComm,
    FixedOpCostBus,
    FixedOpCostFerry,
    FixedOpCostCable,
    FixedOpCostLift,
    FixedOpCostFunicular,
    FixedOpCostTrolley,
    FixedOpCostMono,
    printer_off,
    Attached_Sqdb,
    first_opt_itr,
):
    """This function runs input_to_optimizer script."""
    conn = sqlite3.connect(Sqdb)
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    c = conn.cursor()
    if printer_off != True:
        logger.info("Started running the input_to_optimizer...")
    c.executescript(
        """
    ATTACH DATABASE "{Attached_Sqdb}" as a;
    drop table if exists pattern_stop_counter;
    CREATE TEMP TABLE pattern_stop_counter as
    SELECT
        pattern_id,
        count(*) + 1 as stop_count
    FROM
        a.Transit_pattern_links
    GROUP BY
        pattern_id
    ;

    update a.transit_patterns
    set
        seated_capacity = (select seated_capacity from a.transit_routes where a.transit_patterns.route_id = a.transit_routes.route_id),
        design_capacity = (select design_capacity from a.transit_routes where a.transit_patterns.route_id = a.transit_routes.route_id),
        total_capacity = (select total_capacity from a.transit_routes where a.transit_patterns.route_id = a.transit_routes.route_id)
    where exists (select * from a.transit_routes where a.transit_patterns.route_id = a.transit_routes.route_id);


    update a.transit_trips
    set
        seated_capacity = (select seated_capacity from a.transit_patterns where a.transit_trips.pattern_id = a.transit_patterns.pattern_id),
        design_capacity = (select design_capacity from a.transit_patterns where a.transit_trips.pattern_id = a.transit_patterns.pattern_id),
        total_capacity = (select total_capacity from a.transit_patterns where a.transit_trips.pattern_id = a.transit_patterns.pattern_id)
    where exists (select * from a.transit_patterns where a.transit_trips.pattern_id = a.transit_patterns.pattern_id);

    drop table if exists patterns_for_optimizer;
    CREATE TABLE patterns_for_optimizer(
      pattern_id INTEGER,
      departure_hh_bin INTEGER,
      route_of_pattern INTEGER,
      agency_of_pattern INTEGER,
      agency_name TEXT,
      route_type INTEGER,
      crt_freq INTEGER,
      triptime REAL,
      pattern_cap REAL,
      stop_count INTEGER,
      primary key (pattern_id, departure_hh_bin)
    );

    INSERT INTO patterns_for_optimizer
    SELECT
        tp.pattern_id as pattern_id,
        case
            when (ts.departure/{period_seconds}) + 1 <= {time_frame} then (ts.departure/{period_seconds})
            else (ts.departure/{period_seconds}) - {time_frame} end
        as departure_hh_bin,
        tp.route_id as route_of_pattern,
        tr.agency_id as agency_of_pattern,
        ta.agency as agency_name,
        tr.type as route_type,
        count(*) as crt_freq,
        avg(cast(ts2.departure - ts.departure as real)) as triptime,
        avg(cast(tt.total_capacity as real))  as pattern_cap,
        psc.stop_count as stop_count
    FROM
        a.transit_agencies ta,
        a.transit_routes tr,
        a.transit_patterns tp,
        a.transit_trips tt,
        a.transit_trips_schedule ts,
        a.transit_trips_schedule ts2,
        pattern_stop_counter as psc
    WHERE
        ta.agency_id = tr.agency_id and
        tr.route_id = tp.route_id and
        tp.pattern_id = tt.pattern_id and
        tt.trip_id = ts.trip_id and
        tt.trip_id = ts2.trip_id and
        tp.pattern_id = psc.pattern_id and
        ts."index" = 0 and
        ts2."index" = psc.stop_count - 1
    GROUP BY
        tt.pattern_id,
        departure_hh_bin
    ORDER BY
        tt.pattern_id,
        departure_hh_bin
    ;

    drop table if exists ridership_for_optimizer;
    CREATE TABLE ridership_for_optimizer(
      pattern_id INT,
      departure_hh_bin INT,
      stop_index INT,
      stop_id INT,
      crt_ridership INT,
      crt_flow INT,
      PRIMARY KEY (pattern_id, departure_hh_bin, stop_index)
    );

    insert into ridership_for_optimizer
    SELECT
        pfo.pattern_id as pattern_id,
        pfo.departure_hh_bin as departure_hh_bin,
        tpl."index" as stop_index,
        tl.from_node as stop_id,
        0.0 as crt_ridership,
        0.0 as crt_flow
    FROM
        patterns_for_optimizer as pfo,
        a.transit_pattern_links as tpl,
        a.transit_links as tl
    WHERE
        pfo.pattern_id = tpl.pattern_id and
        tpl.transit_link = tl.transit_link
    GROUP BY
        pfo.pattern_id,
        pfo.departure_hh_bin,
        tpl."index"
    ;

    drop table if exists ridership_for_optimizer_temp;
    CREATE temp TABLE ridership_for_optimizer_temp(
      pattern_id INT,
      departure_hh_bin INT,
      stop_index INT,
      crt_ridership INT,
      crt_flow INT,
      PRIMARY KEY (pattern_id, departure_hh_bin, stop_index)
    );

    insert into ridership_for_optimizer_temp
    SELECT
        pfo.pattern_id as pattern_id,
        pfo.departure_hh_bin as departure_hh_bin,
        tvl."index" as stop_index,
        {traffic_scale_factor_adjusted}*sum(tvl.value_Boardings) as crt_ridership,
        {traffic_scale_factor_adjusted}*sum(tvl.value_Seated_Load + tvl.value_Standing_Load) as crt_flow
    FROM
        patterns_for_optimizer as pfo,
        a.transit_trips tt,
        transit_vehicle_links as tvl,
        a.transit_trips_schedule as tts
    WHERE
        pfo.pattern_id = tt.pattern_id and
        tt.trip_id = tvl.value_transit_vehicle_trip and
        tt.trip_id = tts.trip_id and
        pfo.departure_hh_bin = cast((tts.departure)/{period_seconds} as int) and
        tts."index" = 0
    GROUP BY
        pfo.pattern_id,
        pfo.departure_hh_bin,
        tvl."index"
    ORDER BY
        pfo.pattern_id,
        pfo.departure_hh_bin,
        tvl."index"
    ;

    update ridership_for_optimizer
    set
        (crt_ridership, crt_flow) = (select a.crt_ridership, a.crt_flow
                            from ridership_for_optimizer_temp as a
                            where
                                a.pattern_id = ridership_for_optimizer.pattern_id AND
                                a.departure_hh_bin = ridership_for_optimizer.departure_hh_bin AND
                                a.stop_index = ridership_for_optimizer.stop_index)
    where exists (select *
                            from ridership_for_optimizer_temp as a
                            where
                                a.pattern_id = ridership_for_optimizer.pattern_id AND
                                a.departure_hh_bin = ridership_for_optimizer.departure_hh_bin AND
                                a.stop_index = ridership_for_optimizer.stop_index);


    drop table if exists route_cost_ridership;
    CREATE TABLE route_cost_ridership(
      route_id INT,
      route TEXT,
      agency_id INT,
      agency TEXT,
      route_type INT,
      oper_cost REAL,
      crt_ridership INT,
      cost_per_rider REAL,
      crt_freq INT,
      PRIMARY KEY (route_id)
    );

    insert into route_cost_ridership
    SELECT
        p.route_of_pattern as route_id,
        sr.route as route,
        sr.agency_id as agency_id,
        sa.agency as agency,
        p.route_type as route_type,
        sum(case
            when p.route_type = 0 and r.stop_index = 0 then {FixedOpCostTram}*triptime*crt_freq/{period_minutes}
            when p.route_type = 1 and r.stop_index = 0 then {FixedOpCostMetro}*triptime*crt_freq/{period_minutes}
            when p.route_type = 2 and r.stop_index = 0 then {FixedOpCostComm}*triptime*crt_freq/{period_minutes}
            when p.route_type = 3 and r.stop_index = 0 then {FixedOpCostBus}*triptime*crt_freq/{period_minutes}
            when p.route_type = 4 and r.stop_index = 0 then {FixedOpCostFerry}*triptime*crt_freq/{period_minutes}
            when p.route_type = 5 and r.stop_index = 0 then {FixedOpCostCable}*triptime*crt_freq/{period_minutes}
            when p.route_type = 6 and r.stop_index = 0 then {FixedOpCostLift}*triptime*crt_freq/{period_minutes}
            when p.route_type = 7 and r.stop_index = 0 then {FixedOpCostFunicular}*triptime*crt_freq/{period_minutes}
            when p.route_type = 11 and r.stop_index = 0 then {FixedOpCostTrolley}*triptime*crt_freq/{period_minutes}
            when p.route_type = 12 and r.stop_index = 0 then {FixedOpCostMono}*triptime*crt_freq/{period_minutes}
            else 0
        end) as oper_cost,
        sum(r.crt_ridership) as crt_ridership,
        0.0 as cost_per_rider,
        sum(case
            when r.stop_index = 0 then p.crt_freq
            else 0
        end) as crt_freq
    FROM
        patterns_for_optimizer p,
        ridership_for_optimizer r,
        a.transit_routes sr,
        a.transit_agencies sa
    WHERE
        p.pattern_id = r.pattern_id and
        p.route_of_pattern = sr.route_id and
        p.departure_hh_bin = r.departure_hh_bin and
        sr.agency_id = sa.agency_id
    group by
        p.route_of_pattern
    order by
        sa.agency_id,
        p.route_type,
        p.route_of_pattern
    ;

    update route_cost_ridership
    set cost_per_rider = case
        when crt_ridership = 0 then 1000000
        else oper_cost/crt_ridership
    end;

    drop table if exists route_cost_ridership_for_optimizer;
    CREATE TABLE route_cost_ridership_for_optimizer(
      route_id INT,
      agency_id INT,
      route_type INT,
      oper_cost REAL,
      crt_ridership INT,
      cost_per_rider REAL,
      crt_freq INT,
      PRIMARY KEY (route_id)
    );

    insert into route_cost_ridership_for_optimizer
    SELECT
        p.route_of_pattern as route_id,
        p.agency_of_pattern as agency_id,
        p.route_type as route_type,
        sum(case
            when p.route_type = 0 and r.stop_index = 0 then {FixedOpCostTram}*triptime*crt_freq/{period_minutes}
            when p.route_type = 1 and r.stop_index = 0 then {FixedOpCostMetro}*triptime*crt_freq/{period_minutes}
            when p.route_type = 2 and r.stop_index = 0 then {FixedOpCostComm}*triptime*crt_freq/{period_minutes}
            when p.route_type = 3 and r.stop_index = 0 then {FixedOpCostBus}*triptime*crt_freq/{period_minutes}
            when p.route_type = 4 and r.stop_index = 0 then {FixedOpCostFerry}*triptime*crt_freq/{period_minutes}
            when p.route_type = 5 and r.stop_index = 0 then {FixedOpCostCable}*triptime*crt_freq/{period_minutes}
            when p.route_type = 6 and r.stop_index = 0 then {FixedOpCostLift}*triptime*crt_freq/{period_minutes}
            when p.route_type = 7 and r.stop_index = 0 then {FixedOpCostFunicular}*triptime*crt_freq/{period_minutes}
            when p.route_type = 11 and r.stop_index = 0 then {FixedOpCostTrolley}*triptime*crt_freq/{period_minutes}
            when p.route_type = 12 and r.stop_index = 0 then {FixedOpCostMono}*triptime*crt_freq/{period_minutes}
            else 0
        end) as oper_cost,
        sum(r.crt_ridership) as crt_ridership,
        0.0 as cost_per_rider,
        sum(case
            when r.stop_index = 0 then p.crt_freq
            else 0
        end) as crt_freq
    FROM
        patterns_for_optimizer p,
        ridership_for_optimizer r
    WHERE
        p.pattern_id = r.pattern_id and
        p.departure_hh_bin = r.departure_hh_bin
    group by
        p.route_of_pattern
    order by
        p.route_of_pattern
    ;

    update route_cost_ridership_for_optimizer
    set cost_per_rider = case
        when crt_ridership = 0 then 1000000
        else oper_cost/crt_ridership
    end;

    drop table if exists trip_departure;
    create temp table trip_departure(
        trip_id INTEGER,
        pattern_id INTEGER,
        departure_hh_bin INTEGER,
        PRIMARY KEY (trip_id)
    );

    insert into trip_departure
    select
        t.trip_id as trip_id,
        t.pattern_id as pattern_id,
        case
            when (ts.departure/{period_seconds}) + 1 <= {time_frame} then (ts.departure/{period_seconds})
            else (ts.departure/{period_seconds}) - {time_frame} end
        as departure_hh_bin
    FROM
        a.transit_trips t,
        a.transit_trips_schedule ts
    WHERE
        t.trip_id = ts.trip_id and
        ts."index" = 0
    group by
        t.trip_id;


    drop table if exists rts_pt_freq;
    CREATE temp TABLE rts_pt_freq(
      route_id INTEGER,
      stop_hh_bin integer,
      stop_id INTEGER,
      pattern_id INTEGER,
      departure_hh_bin integer,
      rts_pt_overlap INTEGER,
      PRIMARY KEY (route_id, stop_hh_bin, stop_id, pattern_id, departure_hh_bin)
    );

    insert into rts_pt_freq
    SELECT
        p.route_id as route_id,
        case
            when (ts.departure/{period_seconds}) + 1 <= {time_frame} then (ts.departure/{period_seconds})
            else (ts.departure/{period_seconds}) - {time_frame} end
        as stop_hh_bin,
        r.stop_id as stop_id,
        p.pattern_id as pattern_id,
        t.departure_hh_bin as departure_hh_bin,
        count (*) as rts_pt_overlap
    FROM
        a.transit_patterns p,
        trip_departure t,
        a.transit_trips_schedule ts,
        ridership_for_optimizer r
    WHERE
        p.pattern_id = t.pattern_id AND
        p.pattern_id = r.pattern_id AND
        t.trip_id = ts.trip_id and
        t.departure_hh_bin = r.departure_hh_bin and
        ts."index" = r.stop_index
    group BY
        p.route_id,
        stop_id,
        stop_hh_bin,
        p.pattern_id,
        t.departure_hh_bin
    ;

    drop table if exists rts_pt_freq_ratio;
    CREATE TABLE rts_pt_freq_ratio(
      route_id INTEGER,
      stop_hh_bin integer,
      stop_id INTEGER,
      pattern_id INTEGER,
      departure_hh_bin integer,
      rts_pt_ratio INTEGER,
      PRIMARY KEY (route_id, stop_hh_bin, stop_id, pattern_id, departure_hh_bin)
    );

    insert into rts_pt_freq_ratio
    SELECT
        r.route_id as route_id,
        r.stop_hh_bin as stop_hh_bin,
        r.stop_id as stop_id,
        r.pattern_id as pattern_id,
        r.departure_hh_bin as departure_hh_bin,
        cast(r.rts_pt_overlap as real)/cast(p.crt_freq as real) as rts_pt_ratio
    FROM
        patterns_for_optimizer p,
        rts_pt_freq r
    WHERE
        p.pattern_id = r.pattern_id AND
        p.departure_hh_bin = r.departure_hh_bin
    group by
        r.route_id,
        r.stop_hh_bin,
        r.stop_id,
        r.pattern_id,
        r.departure_hh_bin
    ;

    drop table if exists sanity_check_1;
    CREATE temp TABLE sanity_check_1(
      route_id INTEGER,
      stop_id INTEGER,
      pattern_id INTEGER,
      departure_hh_bin integer,
      summed_ratio INTEGER,
      PRIMARY KEY (route_id, stop_id, pattern_id, departure_hh_bin)
    );

    insert into sanity_check_1
    SELECT
        route_id,
        stop_id,
        pattern_id,
        departure_hh_bin,
        sum(rts_pt_ratio) as summed_ratio
    FROM
        rts_pt_freq_ratio
    group by
        route_id,
        stop_id,
        pattern_id,
        departure_hh_bin
    ;

    drop table if exists sanity_check_2;
    CREATE temp TABLE sanity_check_2(
      pattern_id INTEGER,
      "index" INTEGER,
      stop_id INTEGER,
      stop_count integer,
      PRIMARY KEY (pattern_id, stop_id)
    );

    insert into sanity_check_2
    SELECT
        p.pattern_id as pattern_id,
        p."index" as "index",
        l.from_node as stop_id,
        count(*) as stop_count
    FROM
        a."Transit_Pattern_Links" p,
        a.transit_links l
    where
        p.transit_link = l.transit_link
    group by
        p.pattern_id,
        l.from_node
    order by
        p.pattern_id,
        p."index"
    ;

    DROP table if exists pattern_departure_index_link_durations;
    CREATE table pattern_departure_index_link_durations as
    SELECT
        tt.pattern_id as patternid,
        case
            when cast(tts.departure/{period_seconds} as int) < {time_frame} then cast(tts.departure/{period_seconds} as int)
            else cast(tts.departure/{period_seconds} as int) - {time_frame} end as pattern_time_index,
        tts2."index" as link_index,
        (avg(tts3.departure)-avg(tts2.departure)) as avg_duration,
        count(*) as trip_count
    FROM
        "Transit_Trips" as tt,
        "Transit_Trips_Schedule" as tts,
        "Transit_Trips_Schedule" as tts2,
        "Transit_Trips_Schedule" as tts3
    WHERE
        tt.trip_id = tts.trip_id
        and tt.trip_id = tts2.trip_id
        and tt.trip_id = tts3.trip_id
        and tts."index" = 0
        and tts2."index" + 1 = tts3."index"
    GROUP BY
        patternid,
        pattern_time_index,
        link_index
    ;
    """.format(
            period_seconds=period_seconds,
            period_minutes=period_minutes,
            time_frame=time_frame,
            traffic_scale_factor_adjusted=traffic_scale_factor_adjusted,
            FixedOpCostTram=FixedOpCostTram,
            FixedOpCostMetro=FixedOpCostMetro,
            FixedOpCostComm=FixedOpCostComm,
            FixedOpCostBus=FixedOpCostBus,
            FixedOpCostFerry=FixedOpCostFerry,
            FixedOpCostCable=FixedOpCostCable,
            FixedOpCostLift=FixedOpCostLift,
            FixedOpCostFunicular=FixedOpCostFunicular,
            FixedOpCostTrolley=FixedOpCostTrolley,
            FixedOpCostMono=FixedOpCostMono,
            Attached_Sqdb=Attached_Sqdb,
        )
    )
    if printer_off != True:
        logger.info("Finished running the input_to_optimizer...")
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.commit()
    conn.close()

    if printer_off != True:
        logger.info("Closed %s." % (Sqdb))

    if first_opt_itr:
        conn = sqlite3.connect(Attached_Sqdb)
        conn.execute("pragma foreign_keys = off")
        if printer_off != True:
            logger.info("SQLite Foreign_keys are unlocked...")
        if printer_off != True:
            logger.info("Connected to %s." % (Sqdb))
        c = conn.cursor()
        if printer_off != True:
            logger.info("Started running the input_to_optimizer...")
        c.executescript(
            """
        ATTACH DATABASE "{Sqdb}" as a;

        drop table if exists agency_cost_original;
        CREATE TABLE agency_cost_original(
          agency_name TEXT,
          route_type TEXT,
          oper_cost REAL,
          PRIMARY KEY (agency_name, route_type)
        );

        insert into agency_cost_original
        SELECT
            ta.agency as agency_name,
            case
                when p.route_type = 0 then 'TRAM'
                when p.route_type = 1 then 'METRO'
                when p.route_type = 2 then 'COMM'
                when p.route_type = 3 then 'BUS'
                when p.route_type = 4 then 'FERRY'
                when p.route_type = 5 then 'CABLE'
                when p.route_type = 6 then 'LIFT'
                when p.route_type = 7 then 'FUNICULAR'
                when p.route_type = 11 then 'TROLLEY'
                when p.route_type = 12 then 'MONO'
            end as route_type,
            sum(case
                when p.route_type = 0 then {FixedOpCostTram}*triptime*crt_freq/{period_minutes}
                when p.route_type = 1 then {FixedOpCostMetro}*triptime*crt_freq/{period_minutes}
                when p.route_type = 2 then {FixedOpCostComm}*triptime*crt_freq/{period_minutes}
                when p.route_type = 3 then {FixedOpCostBus}*triptime*crt_freq/{period_minutes}
                when p.route_type = 4 then {FixedOpCostFerry}*triptime*crt_freq/{period_minutes}
                when p.route_type = 5 then {FixedOpCostCable}*triptime*crt_freq/{period_minutes}
                when p.route_type = 6 then {FixedOpCostLift}*triptime*crt_freq/{period_minutes}
                when p.route_type = 7 then {FixedOpCostFunicular}*triptime*crt_freq/{period_minutes}
                when p.route_type = 11 then {FixedOpCostTrolley}*triptime*crt_freq/{period_minutes}
                when p.route_type = 12 then {FixedOpCostMono}*triptime*crt_freq/{period_minutes}
                else 0
            end) as oper_cost
        FROM
            a.patterns_for_optimizer p,
            transit_agencies ta
        where
            p.agency_of_pattern = ta.agency_id
        group by
            p.agency_name,
            p.route_type
        order by
            agency_name,
            route_type
        ;

        drop table if exists agency_cost_for_optimizer_original;
        CREATE TABLE agency_cost_for_optimizer_original(
          agency INT,
          route_type INT,
          oper_cost REAL,
          PRIMARY KEY (agency, route_type)
        );

        insert into agency_cost_for_optimizer_original
        SELECT
            agency_of_pattern,
            route_type,
            sum(case
                when route_type = 0 then {FixedOpCostTram}*triptime*crt_freq/{period_minutes}
                when route_type = 1 then {FixedOpCostMetro}*triptime*crt_freq/{period_minutes}
                when route_type = 2 then {FixedOpCostComm}*triptime*crt_freq/{period_minutes}
                when route_type = 3 then {FixedOpCostBus}*triptime*crt_freq/{period_minutes}
                when route_type = 4 then {FixedOpCostFerry}*triptime*crt_freq/{period_minutes}
                when route_type = 5 then {FixedOpCostCable}*triptime*crt_freq/{period_minutes}
                when route_type = 6 then {FixedOpCostLift}*triptime*crt_freq/{period_minutes}
                when route_type = 7 then {FixedOpCostFunicular}*triptime*crt_freq/{period_minutes}
                when route_type = 11 then {FixedOpCostTrolley}*triptime*crt_freq/{period_minutes}
                when route_type = 12 then {FixedOpCostMono}*triptime*crt_freq/{period_minutes}
                else 0
            end) as oper_cost
        FROM
            a.patterns_for_optimizer
        group by
            agency_name,
            route_type
        order by
            agency_name,
            route_type desc
        ;
        """.format(
                period_seconds=period_seconds,
                period_minutes=period_minutes,
                time_frame=time_frame,
                traffic_scale_factor_adjusted=traffic_scale_factor_adjusted,
                FixedOpCostTram=FixedOpCostTram,
                FixedOpCostMetro=FixedOpCostMetro,
                FixedOpCostComm=FixedOpCostComm,
                FixedOpCostBus=FixedOpCostBus,
                FixedOpCostFerry=FixedOpCostFerry,
                FixedOpCostCable=FixedOpCostCable,
                FixedOpCostLift=FixedOpCostLift,
                FixedOpCostFunicular=FixedOpCostFunicular,
                FixedOpCostTrolley=FixedOpCostTrolley,
                FixedOpCostMono=FixedOpCostMono,
                Sqdb=Sqdb,
            )
        )
        if printer_off != True:
            logger.info("Finished running the input_to_optimizer...")
        conn.execute("pragma foreign_keys = on")
        if printer_off != True:
            logger.info("SQLite Foreign_keys are locked...")
        conn.commit()
        conn.close()

    if printer_off != True:
        logger.info("Closed %s." % (Attached_Sqdb))


def Sqdb_value_updater(Sqdb, Tablename, Column, Condition, printer_off):
    """This function reads an SQL table with a given condition."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    c.execute(
        """update {table}
    set {column} = {column} {condition}""".format(
            table=Tablename, column=Column, condition=Condition
        )
    )
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()
    if printer_off != True:
        logger.info("Disconnected from %s." % (Sqdb))


def Sqdb_table_exists_check(Sqdb, tablename, printer_off):
    """This function returns True if a table exists in a given SQL DB; False, otherwise."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    c = conn.cursor()
    c.execute(
        """ SELECT count(name) FROM sqlite_master
                  WHERE type='table' AND name='{tablename}' """.format(
            tablename=tablename
        )
    )
    if c.fetchone()[0] == 1:
        exists = True
    else:
        exists = False
    conn.commit()
    conn.close()
    if printer_off != True:
        logger.info("Closed %s." % (Sqdb))
    return exists


def Sqdb_reader(Sqdb, Tablename, Columns, printer_off):
    """This function reads an SQL table with a given condition."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    if printer_off != True:
        logger.info("Importing columns: %s in table %s from %s." % (Columns, Tablename, Sqdb))
    c.execute(
        """SELECT {columns}
                 FROM {table}""".format(
            table=Tablename, columns=Columns
        )
    )
    Sql_headers = [description[0].upper() for description in c.description]
    Sql_columns = [list(sublist) for sublist in list(zip(*c.fetchall()))]
    if printer_off != True:
        logger.info("Importing completed...")
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()
    if printer_off != True:
        logger.info("Disconnected from %s." % (Sqdb))
    return Sql_headers, Sql_columns


def Conditional_Sqdb_reader(Sqdb, Tablename, Columns, Condition, printer_off):
    """This function reads an SQL table with a given condition."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    if printer_off != True:
        logger.info("Importing columns: %s in table %s from %s." % (Columns, Tablename, Sqdb))
    c.execute(
        """SELECT {columns}
                 FROM {table}
                 {condition}""".format(
            table=Tablename, columns=Columns, condition=Condition
        )
    )
    Sql_headers = [description[0] for description in c.description]
    Sql_columns = c.fetchall()
    if printer_off != True:
        logger.info("Importing completed...")
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()
    if printer_off != True:
        logger.info("Disconnected from %s." % (Sqdb))
    return Sql_headers, Sql_columns


def Sqdb_writer(Sqdb, Tablename, Headers, Data, printer_off):
    """This function creates a new table with data into a given SQL file."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    if printer_off != True:
        logger.info("Inserting the table into the SQLite Database...")
    c.execute("DROP table if exists {tablename}".format(tablename=Tablename))
    c.execute("CREATE TABLE {tablename} {headers}".format(tablename=Tablename, headers=Headers))
    c.executemany(
        "INSERT INTO {tablename} {headers} VALUES ({entry})".format(
            tablename=Tablename, headers=Headers, entry=",".join(["?"] * len(Headers))
        ),
        Data,
    )
    if printer_off != True:
        logger.info("Finished inserting the table into the SQLite Database...")
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()


def Sqdb_insert(Sqdb, Tablename, Headers, Data, printer_off):
    """This function inserts data into an existing table in a given SQL file."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    if printer_off != True:
        logger.info("Inserting the table into the SQLite Database...")
    c.executemany(
        "INSERT INTO {tablename} {headers} VALUES ({entry})".format(
            tablename=Tablename, headers=Headers, entry=",".join(["?"] * len(Headers))
        ),
        Data,
    )
    if printer_off != True:
        logger.info("Finished inserting the table into the SQLite Database...")
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()


def Sqdb_updater(Sqdb, Tablename, Headers, Data, printer_off):
    """This function reads an SQL table, keeps its key features but erases all data,
    and replaces them with the new input Data."""
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    conn.execute("pragma foreign_keys = off")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are unlocked...")
    c = conn.cursor()
    if printer_off != True:
        logger.info("Inserting the table into the SQLite Database...")
    c.execute("Delete from {tablename}".format(tablename=Tablename))
    c.executemany(
        "INSERT INTO {tablename} {headers} VALUES ({entry})".format(
            tablename=Tablename, headers=Headers, entry=",".join(["?"] * len(Headers))
        ),
        Data,
    )
    if printer_off != True:
        logger.info("Finished inserting the table into the SQLite Database...")
    conn.commit()
    conn.execute("pragma foreign_keys = on")
    if printer_off != True:
        logger.info("SQLite Foreign_keys are locked...")
    conn.close()


def Sqdb_script_runner(Sqdb, sql_script_file, printer_off):
    """This function takes Sqdb name and script file names as inputs,
    connects to the DB, runs the given script, and closes the DB."""
    with open(sql_script_file, "r") as sql_file:
        sql_script = sql_file.read()
    conn = sqlite3.connect(Sqdb)
    if printer_off != True:
        logger.info("Connected to %s." % (Sqdb))
    c = conn.cursor()
    if printer_off != True:
        logger.info("Started running the script in the SQLite Database...")
    c.executescript(sql_script)
    if printer_off != True:
        logger.info("Finished running the script in the SQLite Database...")
    conn.commit()
    conn.close()
    if printer_off != True:
        logger.info("Closed %s." % (Sqdb))


def isfloat(value):
    """This function checks if a given value is float; returns True if yes."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def printfile(outlist, fname):
    """This function writes a given list into a csv as a row."""
    csv.writer(fname).writerow(outlist)
    fname.flush()


#################################################################################################
############################## END DEFINING PREREQUISITE FUNCTIONS ##############################
#################################################################################################


def setup_logging():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(name)s - %(levelname)s - %(message)s"
    )


def copy_default_settings():
    pass


def modify_settings(settings_file, mods):
    pass


def run_transit_optimization(optimization_settings_file, supply_path, demand_path, first_opt_itr=False):
    logger.info("Running Transit Optimization")
    with open(optimization_settings_file) as file:
        optimization_settings = yaml.load(file, Loader=yaml.FullLoader)

    for i, j in optimization_settings.items():
        if isfloat(j) == True:
            if float(j).is_integer() == True:
                globals()[i] = int(j)
            else:
                globals()[i] = float(j)
        else:
            globals()[i] = j

    start = time.time()
    period_seconds = period_minutes * 60
    time_frame = int(1440 / period_minutes)
    period_seconds2 = period_minutes2 * 60
    time_frame2 = int(1440 / period_minutes2)
    traffic_scale_factor_adjusted = 1 / traffic_scale_factor

    logger.info("  Cleaning demand db.")
    Clean_DB(demand_path, printer_off)
    logger.info("  Preprocessing input parameters.")
    Input_to_Optimizer(
        demand_path,
        period_seconds,
        period_minutes,
        time_frame,
        traffic_scale_factor_adjusted,
        FixedOpCostTram,
        FixedOpCostMetro,
        FixedOpCostComm,
        FixedOpCostBus,
        FixedOpCostFerry,
        FixedOpCostCable,
        FixedOpCostLift,
        FixedOpCostFunicular,
        FixedOpCostTrolley,
        FixedOpCostMono,
        printer_off,
        supply_path,
        first_opt_itr,
    )

    #############################################################################################
    ################################ BEGIN READING SQLITE FILES #################################
    #############################################################################################
    Transit_Patterns = dict(zip(*Sqdb_reader(supply_path, "Transit_Patterns", "*", printer_off)))
    Transit_Pattern_Links = dict(zip(*Sqdb_reader(supply_path, "Transit_Pattern_Links", "*", printer_off)))
    Transit_Links = dict(zip(*Sqdb_reader(supply_path, "Transit_Links", "*", printer_off)))
    Patterns_for_Optimizer = dict(zip(*Sqdb_reader(demand_path, "Patterns_for_Optimizer", "*", printer_off)))
    Route_Cost_Ridership_for_Optimizer = dict(
        zip(*Sqdb_reader(demand_path, "Route_Cost_Ridership_for_Optimizer", "*", printer_off))
    )
    Agency_Cost_for_Optimizer = dict(
        zip(*Sqdb_reader(supply_path, "Agency_Cost_for_Optimizer_Original", "*", printer_off))
    )
    Ridership_for_Optimizer = dict(zip(*Sqdb_reader(demand_path, "Ridership_for_Optimizer", "*", printer_off)))
    Rts_Pt_Freq_Ratio = dict(zip(*Sqdb_reader(demand_path, "Rts_Pt_Freq_Ratio", "*", printer_off)))
    Pattern_Departure_Index_Link_Durations = dict(
        zip(*Sqdb_reader(demand_path, "Pattern_Departure_Index_Link_Durations", "*", printer_off))
    )
    #############################################################################################
    ################################# END READING SQLITE FILES ##################################
    #############################################################################################

    #############################################################################################
    ################################## BEGIN PREPARING INPUTS ###################################
    #############################################################################################
    seated_cap = dict(zip(Transit_Patterns["PATTERN_ID"], Transit_Patterns["SEATED_CAPACITY"]))
    design_cap = dict(zip(Transit_Patterns["PATTERN_ID"], Transit_Patterns["DESIGN_CAPACITY"]))
    total_cap = dict(zip(Transit_Patterns["PATTERN_ID"], Transit_Patterns["TOTAL_CAPACITY"]))

    unique_a = list(sorted(set(Patterns_for_Optimizer["AGENCY_OF_PATTERN"])))
    unique_p = list(sorted(set(Patterns_for_Optimizer["PATTERN_ID"])))
    unique_r = list(sorted(set(Patterns_for_Optimizer["ROUTE_OF_PATTERN"])))
    unique_pd = list(
        sorted(
            set(
                [
                    (Patterns_for_Optimizer["PATTERN_ID"][i], Patterns_for_Optimizer["DEPARTURE_HH_BIN"][i])
                    for i in range(len(Patterns_for_Optimizer["PATTERN_ID"]))
                ]
            )
        )
    )
    unique_ad_type_cap = list(
        sorted(
            set(
                [
                    (
                        Patterns_for_Optimizer["AGENCY_OF_PATTERN"][i],
                        Patterns_for_Optimizer["DEPARTURE_HH_BIN"][i],
                        Patterns_for_Optimizer["ROUTE_TYPE"][i],
                        Patterns_for_Optimizer["PATTERN_CAP"][i],
                    )
                    for i in range(len(Patterns_for_Optimizer["AGENCY_OF_PATTERN"]))
                ]
            )
        )
    )

    name_of_a = dict(zip(Patterns_for_Optimizer["AGENCY_OF_PATTERN"], Patterns_for_Optimizer["AGENCY_NAME"]))
    route_of_p = dict(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["ROUTE_OF_PATTERN"]))
    agency_of_p = dict(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["AGENCY_OF_PATTERN"]))
    route_type_of_p = dict(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["ROUTE_TYPE"]))
    crt_freq_of_pd = dict(
        zip(
            tuple(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["DEPARTURE_HH_BIN"])),
            Patterns_for_Optimizer["CRT_FREQ"],
        )
    )
    triptime_of_pd = dict(
        zip(
            tuple(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["DEPARTURE_HH_BIN"])),
            Patterns_for_Optimizer["TRIPTIME"],
        )
    )
    cap_of_pd = dict(
        zip(
            tuple(zip(Patterns_for_Optimizer["PATTERN_ID"], Patterns_for_Optimizer["DEPARTURE_HH_BIN"])),
            Patterns_for_Optimizer["PATTERN_CAP"],
        )
    )

    temp_agency_types = {i: [] for i in unique_a}
    for i in range(len(Patterns_for_Optimizer["AGENCY_OF_PATTERN"])):
        temp_agency_types[Patterns_for_Optimizer["AGENCY_OF_PATTERN"][i]].append(
            Patterns_for_Optimizer["ROUTE_TYPE"][i]
        )
    agency_types = {i: list(sorted(set(j))) for i, j in temp_agency_types.items()}

    unique_cap = list(sorted(set((cap_of_pd.values()))))

    unique_ra_type = list(
        sorted(
            set(
                [
                    (
                        Route_Cost_Ridership_for_Optimizer["ROUTE_ID"][i],
                        Route_Cost_Ridership_for_Optimizer["AGENCY_ID"][i],
                        Route_Cost_Ridership_for_Optimizer["ROUTE_TYPE"][i],
                    )
                    for i in range(len(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"]))
                ]
            )
        )
    )
    agency_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["AGENCY_ID"])
    )
    route_type_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["ROUTE_TYPE"])
    )
    crt_cost_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["OPER_COST"])
    )
    crt_ridership_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["CRT_RIDERSHIP"])
    )
    cost_per_rider_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["COST_PER_RIDER"])
    )
    crt_freq_of_r = dict(
        zip(Route_Cost_Ridership_for_Optimizer["ROUTE_ID"], Route_Cost_Ridership_for_Optimizer["CRT_FREQ"])
    )

    unique_a_type = list(
        sorted(
            set(
                [
                    (Agency_Cost_for_Optimizer["AGENCY"][i], Agency_Cost_for_Optimizer["ROUTE_TYPE"][i])
                    for i in range(len(Agency_Cost_for_Optimizer["AGENCY"]))
                ]
            )
        )
    )

    budget_of_a_type = dict(
        zip(
            tuple(zip(Agency_Cost_for_Optimizer["AGENCY"], Agency_Cost_for_Optimizer["ROUTE_TYPE"])),
            Agency_Cost_for_Optimizer["OPER_COST"],
        )
    )

    unique_type = list(sorted(set(Agency_Cost_for_Optimizer["ROUTE_TYPE"])))

    unique_s = list(sorted(set(Ridership_for_Optimizer["STOP_ID"])))
    unique_pdi = list(
        sorted(
            set(
                (
                    Ridership_for_Optimizer["PATTERN_ID"][i],
                    Ridership_for_Optimizer["DEPARTURE_HH_BIN"][i],
                    Ridership_for_Optimizer["STOP_INDEX"][i],
                )
                for i in range(len(Ridership_for_Optimizer["PATTERN_ID"]))
            )
        )
    )
    unique_pds = list(
        sorted(
            set(
                (
                    Ridership_for_Optimizer["PATTERN_ID"][i],
                    Ridership_for_Optimizer["DEPARTURE_HH_BIN"][i],
                    Ridership_for_Optimizer["STOP_ID"][i],
                )
                for i in range(len(Ridership_for_Optimizer["PATTERN_ID"]))
            )
        )
    )

    i_of_pd = {(p, d): [] for p, d in unique_pd}
    for p, d, i in unique_pdi:
        i_of_pd[p, d].append(i)

    s_of_pd = {(p, d): [] for p, d in unique_pd}
    for p, d, s in unique_pds:
        s_of_pd[p, d].append(s)

    r_of_a_type = {(a, ty): [] for r, a, ty in unique_ra_type}
    for r, a, ty in unique_ra_type:
        r_of_a_type[a, ty].append(r)

    crt_cost_of_ra_type, crt_ridership_of_ra_type = {}, {}
    cost_per_rider_of_ra_type, crt_freq_of_ra_type = {}, {}
    for a, ty in unique_a_type:
        temp_query = Conditional_Sqdb_reader(
            demand_path,
            "route_cost_ridership_for_optimizer",
            "route_id, oper_cost, crt_ridership, cost_per_rider, crt_freq",
            """where agency_id = %s and route_type = %s
            ORDER BY cost_per_rider desc"""
            % (a, ty),
            printer_off,
        )[1:][0]
        crt_cost_of_ra_type[a, ty] = {i[0]: i[1] for i in temp_query}
        crt_ridership_of_ra_type[a, ty] = {i[0]: i[2] for i in temp_query}
        cost_per_rider_of_ra_type[a, ty] = {i[0]: i[3] for i in temp_query}
        crt_freq_of_ra_type[a, ty] = {i[0]: i[4] for i in temp_query}

    stop_id_of_pdi = dict(
        zip(
            tuple(
                zip(
                    Ridership_for_Optimizer["PATTERN_ID"],
                    Ridership_for_Optimizer["DEPARTURE_HH_BIN"],
                    Ridership_for_Optimizer["STOP_INDEX"],
                )
            ),
            Ridership_for_Optimizer["STOP_ID"],
        )
    )
    crt_ridership_of_pdi = dict(
        zip(
            tuple(
                zip(
                    Ridership_for_Optimizer["PATTERN_ID"],
                    Ridership_for_Optimizer["DEPARTURE_HH_BIN"],
                    Ridership_for_Optimizer["STOP_INDEX"],
                )
            ),
            Ridership_for_Optimizer["CRT_RIDERSHIP"],
        )
    )
    crt_flow_of_pdi = dict(
        zip(
            tuple(
                zip(
                    Ridership_for_Optimizer["PATTERN_ID"],
                    Ridership_for_Optimizer["DEPARTURE_HH_BIN"],
                    Ridership_for_Optimizer["STOP_INDEX"],
                )
            ),
            Ridership_for_Optimizer["CRT_FLOW"],
        )
    )
    crt_ridership_of_pds, crt_flow_of_pds, counter_of_pds = {}, {}, {}
    for p, d, s in unique_pds:
        crt_ridership_of_pds[p, d, s] = 0
        crt_flow_of_pds[p, d, s] = 0
        counter_of_pds[p, d, s] = 0
        for i in i_of_pd[p, d]:
            if stop_id_of_pdi[p, d, i] == s:
                counter_of_pds[p, d, s] += 1
                crt_ridership_of_pds[p, d, s] = crt_ridership_of_pds[p, d, s] + (
                    (crt_ridership_of_pdi[p, d, i] - crt_ridership_of_pds[p, d, s]) / counter_of_pds[p, d, s]
                )
                crt_flow_of_pds[p, d, s] = crt_flow_of_pds[p, d, s] + (
                    (crt_flow_of_pdi[p, d, i] - crt_flow_of_pds[p, d, s]) / counter_of_pds[p, d, s]
                )

    unique_rts_pd = list(
        sorted(
            set(
                [
                    (
                        Rts_Pt_Freq_Ratio["ROUTE_ID"][i],
                        Rts_Pt_Freq_Ratio["STOP_HH_BIN"][i],
                        Rts_Pt_Freq_Ratio["STOP_ID"][i],
                        Rts_Pt_Freq_Ratio["PATTERN_ID"][i],
                        Rts_Pt_Freq_Ratio["DEPARTURE_HH_BIN"][i],
                    )
                    for i in range(len(Rts_Pt_Freq_Ratio["ROUTE_ID"]))
                ]
            )
        )
    )
    unique_rts = list(
        sorted(
            set(
                [
                    (
                        Rts_Pt_Freq_Ratio["ROUTE_ID"][i],
                        Rts_Pt_Freq_Ratio["STOP_HH_BIN"][i],
                        Rts_Pt_Freq_Ratio["STOP_ID"][i],
                    )
                    for i in range(len(Rts_Pt_Freq_Ratio["ROUTE_ID"]))
                ]
            )
        )
    )
    unique_ts = list(
        sorted(
            set(
                [
                    (Rts_Pt_Freq_Ratio["STOP_HH_BIN"][i], Rts_Pt_Freq_Ratio["STOP_ID"][i])
                    for i in range(len(Rts_Pt_Freq_Ratio["STOP_HH_BIN"]))
                ]
            )
        )
    )
    rts_pd_ratio = dict(
        zip(
            tuple(
                zip(
                    Rts_Pt_Freq_Ratio["ROUTE_ID"],
                    Rts_Pt_Freq_Ratio["STOP_HH_BIN"],
                    Rts_Pt_Freq_Ratio["STOP_ID"],
                    Rts_Pt_Freq_Ratio["PATTERN_ID"],
                    Rts_Pt_Freq_Ratio["DEPARTURE_HH_BIN"],
                )
            ),
            Rts_Pt_Freq_Ratio["RTS_PT_RATIO"],
        )
    )

    r_to_be_removed = []
    for a, ty in unique_a_type:
        if ty == 3:  # if only bus
            my_saving = 0
            r_index = 0
            while my_saving < cost_reduction_target * budget_of_a_type[a, ty]:
                r, oper_cost = list(crt_cost_of_ra_type[a, ty].items())[r_index]
                my_saving += oper_cost
                if my_saving < cost_reduction_target * budget_of_a_type[a, ty]:
                    r_to_be_removed.append(r)
                r_index += 1

    unique_rts_with_eliminated_r = [(r, t, s) for r, t, s in unique_rts if r not in r_to_be_removed]
    unique_rts_pd_with_eliminated_r = [(r, t, s, p, d) for r, t, s, p, d in unique_rts_pd if r not in r_to_be_removed]

    r_of_ts = {(t, s): [] for t, s in unique_ts}
    for r, t, s in unique_rts_with_eliminated_r:
        r_of_ts[t, s].append(r)

    Period = list(range(time_frame))
    #############################################################################################
    ################################### END PREPARING INPUTS ####################################
    #############################################################################################

    #############################################################################################
    ############################## BEGIN PRE-PROCESSING PARAMETERS ##############################
    #############################################################################################
    triptimesurrogate_of_pd = {(p, d): min(triptime_of_pd[p, d] / 60, period_minutes) for p, d in unique_pd}

    p_of_ad_type_cap = {(a, d, ty, cap): [] for a, d, ty, cap in unique_ad_type_cap}
    for p, d in unique_pd:
        a = agency_of_p[p]
        ty = route_type_of_p[p]
        cap = cap_of_pd[p, d]
        p_of_ad_type_cap[a, d, ty, cap].append((p))

    FleetAvail_of_ad_type_cap = {}
    for a, d, ty, cap in unique_ad_type_cap:
        FleetAvail_of_ad_type_cap[(a, d, ty, cap)] = sum(
            int(triptimesurrogate_of_pd[p, d] * crt_freq_of_pd[p, d] / period_minutes) + 1
            for p in p_of_ad_type_cap[a, d, ty, cap]
        )

    pd_of_rts = {(r, t, s): [] for r, t, s in unique_rts_with_eliminated_r}
    for r, t, s, p, d in unique_rts_pd_with_eliminated_r:
        pd_of_rts[r, t, s].append((p, d))

    crt_ridership_of_rts = {}
    flag_of_rts = {}
    for r, t, s in unique_rts_with_eliminated_r:
        crt_ridership_of_rts[r, t, s] = sum(
            rts_pd_ratio[r, t, s, p, d] * crt_ridership_of_pds[p, d, s] for p, d in pd_of_rts[r, t, s]
        )
        flag_of_rts[r, t, s] = 0
        if crt_ridership_of_rts[r, t, s] >= 1.0:
            flag_of_rts[r, t, s] = 1

    crt_flow_of_rts = {}
    for r, t, s in unique_rts_with_eliminated_r:
        crt_flow_of_rts[r, t, s] = sum(
            rts_pd_ratio[r, t, s, p, d] * crt_flow_of_pds[p, d, s] for p, d in pd_of_rts[r, t, s]
        )

    unit_cost_of_p = {}
    for p in unique_p:
        if route_type_of_p[p] == 0:
            unit_cost_of_p[p] = FixedOpCostTram
        elif route_type_of_p[p] == 1:
            unit_cost_of_p[p] = FixedOpCostMetro
        elif route_type_of_p[p] == 2:
            unit_cost_of_p[p] = FixedOpCostComm
        elif route_type_of_p[p] == 3:
            unit_cost_of_p[p] = FixedOpCostBus
        elif route_type_of_p[p] == 4:
            unit_cost_of_p[p] = FixedOpCostFerry
        elif route_type_of_p[p] == 5:
            unit_cost_of_p[p] = FixedOpCostCable
        elif route_type_of_p[p] == 6:
            unit_cost_of_p[p] = FixedOpCostLift
        elif route_type_of_p[p] == 7:
            unit_cost_of_p[p] = FixedOpCostFunicular
        elif route_type_of_p[p] == 11:
            unit_cost_of_p[p] = FixedOpCostTrolley
        elif route_type_of_p[p] == 12:
            unit_cost_of_p[p] = FixedOpCostMono
        else:
            raise TypeError

    crt_cost_of_pd = {
        (p, d): unit_cost_of_p[p] * triptime_of_pd[p, d] * crt_freq_of_pd[p, d] / 60 for p, d in unique_pd
    }

    crt_fleet_of_pd = {
        (p, d): triptimesurrogate_of_pd[p, d] * crt_freq_of_pd[p, d] / period_minutes for p, d in unique_pd
    }

    crt_ridership_of_pd = {(p, d): sum(crt_ridership_of_pdi[p, d, i] for i in i_of_pd[p, d]) for p, d in unique_pd}
    fare_of_ty = {}
    for ty in unique_type:
        if ty == 0:
            fare_of_ty[ty] = FixedFareTram
        elif ty == 1:
            fare_of_ty[ty] = FixedFareMetro
        elif ty == 2:
            fare_of_ty[ty] = FixedFareComm
        elif ty == 3:
            fare_of_ty[ty] = FixedFareBus
        elif ty == 4:
            fare_of_ty[ty] = FixedFareFerry
        elif ty == 5:
            fare_of_ty[ty] = FixedFareCable
        elif ty == 6:
            fare_of_ty[ty] = FixedFareLift
        elif ty == 7:
            fare_of_ty[ty] = FixedFareFunicular
        elif ty == 11:
            fare_of_ty[ty] = FixedFareTrolley
        elif ty == 12:
            fare_of_ty[ty] = FixedFareMono
        else:
            raise TypeError

    crt_rev_of_pd = {}

    # TODO we will update this by querying POLARIS Demand DB by agency and link type in the future
    for p, d in unique_pd:
        crt_rev_of_pd[p, d] = fare_of_ty[route_type_of_p[p]] * crt_ridership_of_pd[p, d]

    # calculate the total revenue from previous boardings
    # total_rev = sum([crt_rev_of_pd[p, d] for p, d in unique_pd])

    # calculate the total revenue from POLARIS Path_Multimodal_links where links are transit
    logging.error("THIS WILL NO LONGER WORK AFTER PATH_MULTIMODAL_LINKS WAS CONVERTED TO H5")
    total_rev = Conditional_Sqdb_reader(
        demand_path,
        "Path_Multimodal_links",
        "sum(value_act_monetary_cost)",
        "where value_link_type > 6",
        printer_off,
    )[1][0][0]

    total_rev /= trajectory_sampling_rate

    # correct the total revenue to account for fare reduction applied previously
    with closing(sqlite3.connect(supply_path)) as conn:
        fare_discount_rate_prev = read_about_model_value(conn, "transit_fare_discount_rate", cast=float, default=0.0)
    total_rev /= 1 - fare_discount_rate_prev

    # define a fare_discount percentage maximum
    fare_discount_cap = 0.99
    # budget coming from simulated output
    total_budget = sum(list(budget_of_a_type.values()))
    # increasing the budget using a percentage increase
    factored_budget = cost_adjustment_factor * total_budget
    # calculating the additional budget for fare
    additional_budget_for_fare = (1 - additional_budget_factor_for_freq) * additional_budget
    # cap the additional budget for fare at 99% of fare revenue
    additional_budget_for_fare = min(additional_budget_for_fare, fare_discount_cap * total_rev)
    # calculating the additional budget for frequency improvement
    additional_budget_for_freq = max(0.0, additional_budget - additional_budget_for_fare)
    # adding it to the factored budget
    final_budget = factored_budget + additional_budget_for_freq - fmlm_subsidy_takeaway
    # calculating the final adjustment used in the optimizer
    cost_rhs = max(1.0, final_budget / total_budget)
    # the budget_lb_agency_type is also adjusted by cost_rhs
    budget_lb_agency_type_adjusted = budget_lb_agency_type * cost_rhs

    fare_discount_rate = max(0.0, min(fare_discount_cap, additional_budget_for_fare / total_rev))

    fare_multiplier = (1 - fare_discount_rate) / (1 - fare_discount_rate_prev)
    fare_multiplier = max((1 - fare_discount_cap), fare_multiplier)

    logger.info(f"  - transit_fare_discount_rate: {fare_discount_rate_prev} -> {fare_discount_rate} (prev -> curr)")

    Cost1_of_a_type = {
        (a, ty): sum(crt_cost_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty)
        for a, ty in unique_a_type
    }
    Trips_of_a_type = {
        (a, ty): sum(crt_freq_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty)
        for a, ty in unique_a_type
    }
    Ridership_of_a_type = {
        (a, ty): sum(
            crt_ridership_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty
        )
        for a, ty in unique_a_type
    }
    Revenue_of_a_type = {
        (a, ty): sum(crt_rev_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty)
        for a, ty in unique_a_type
    }
    Obj1_of_a_type_sc1 = {
        (a, ty): sum(
            crt_ridership_of_rts[r, t, s]
            / cost_per_rider_of_r[r]
            * sum(
                rts_pd_ratio[r, t, s, p, d] * crt_freq_of_pd[p, d]
                for p, d in pd_of_rts[r, t, s]
                if agency_of_p[p] == a and route_type_of_p[p] == ty
            )
            for r, t, s in unique_rts_with_eliminated_r
        )
        for a, ty in unique_a_type
    }
    Obj1_of_a_type_sc2 = {
        (a, ty): sum(
            1
            / cost_per_rider_of_r[r]
            * sum(
                rts_pd_ratio[r, t, s, p, d] * crt_freq_of_pd[p, d]
                for p, d in pd_of_rts[r, t, s]
                if agency_of_p[p] == a and route_type_of_p[p] == ty
            )
            for r, t, s in unique_rts_with_eliminated_r
        )
        for a, ty in unique_a_type
    }
    Obj1_of_a_type_sc3 = {
        (a, ty): sum(
            crt_ridership_of_rts[r, t, s]
            * sum(
                rts_pd_ratio[r, t, s, p, d] * crt_freq_of_pd[p, d]
                for p, d in pd_of_rts[r, t, s]
                if agency_of_p[p] == a and route_type_of_p[p] == ty
            )
            for r, t, s in unique_rts_with_eliminated_r
        )
        for a, ty in unique_a_type
    }

    if printer_off != True:
        logger.info("Finished pre-processing the parameters.")
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))
    #############################################################################################
    ############################### END PRE-PROCESSING PARAMETERS ###############################
    #############################################################################################

    #############################################################################################
    ########################### BEGIN BUILDING THE OPTIMIZATION MODEL ###########################
    #############################################################################################
    logger.info("  The solver has been called.")
    if printer_off != True:
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    m = ConcreteModel("RTA-problem")
    timenow = time.time()

    if printer_off != True:
        logger.info("Began creating variables.")
    m.freq = Var(unique_pd, domain=NonNegativeReals, bounds=(0, max_freq_of_pd))
    m.dummy_var = Var(unique_pd, domain=Binary)
    if printer_off != True:
        logger.info("Time to create variables is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    timenow = time.time()
    if scenario == 1:
        m.OBJ = Objective(
            expr=sum(
                (crt_ridership_of_rts[r, t, s] / cost_per_rider_of_r[r])
                * sum(rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] for p, d in pd_of_rts[r, t, s])
                for r, t, s in unique_rts_with_eliminated_r
            ),
            sense=maximize,
        )
    elif scenario == 2:
        m.OBJ = Objective(
            expr=sum(
                (1 / cost_per_rider_of_r[r])
                * sum(rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] for p, d in pd_of_rts[r, t, s])
                for r, t, s in unique_rts_with_eliminated_r
            ),
            sense=maximize,
        )
    elif scenario == 3:
        m.OBJ = Objective(
            expr=sum(
                crt_ridership_of_rts[r, t, s]
                * sum(rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] for p, d in pd_of_rts[r, t, s])
                for r, t, s in unique_rts_with_eliminated_r
            ),
            sense=maximize,
        )
    else:
        if printer_off != True:
            logger.info("Objective function not defined. Set scenario to 1, 2, or 3.")
        else:
            pass

    if printer_off != True:
        logger.info("Objective function has been defined.")
        logger.info("Time to write the objective function is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Cost.")
    timenow = time.time()

    def Cost(m, a):
        if sum(unit_cost_of_p[p] * triptime_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a) == 0:
            return Constraint.Skip
        return (
            sum(
                unit_cost_of_p[p] * triptime_of_pd[p, d] * m.freq[p, d] / 60
                for p, d in unique_pd
                if agency_of_p[p] == a
            )
            <= sum(budget_of_a_type[a, ty] for ty in agency_types[a]) * cost_rhs
        )

    m.AxbConstraint = Constraint(unique_a, rule=Cost)
    if printer_off != True:
        logger.info("Cost constraints are done.")
        logger.info("Time to write Cost constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Cost2.")
    timenow = time.time()

    def Cost2(m, a, ty):
        if (
            sum(
                unit_cost_of_p[p] * triptime_of_pd[p, d]
                for p, d in unique_pd
                if agency_of_p[p] == a and route_type_of_p[p] == ty
            )
            == 0
        ):
            return Constraint.Skip
        return (
            sum(
                unit_cost_of_p[p] * triptime_of_pd[p, d] * m.freq[p, d] / 60
                for p, d in unique_pd
                if agency_of_p[p] == a and route_type_of_p[p] == ty
            )
            >= budget_of_a_type[a, ty] * budget_lb_agency_type_adjusted
        )

    m.AxbConstraint8 = Constraint(unique_a_type, rule=Cost2)
    if printer_off != True:
        logger.info("Cost2 constraints are done.")
        logger.info("Time to write Cost2 constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Load.")
    timenow = time.time()

    def Load(m, r, t, s):
        if sum(rts_pd_ratio[r, t, s, p, d] * cap_of_pd[p, d] for p, d in pd_of_rts[r, t, s]) == 0:
            return Constraint.Skip
        return crt_ridership_of_rts[r, t, s] * ridership_lhs * flag_of_rts[r, t, s] <= sum(
            rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] * cap_of_pd[p, d] for p, d in pd_of_rts[r, t, s]
        )

    m.AxbConstraint2 = Constraint(unique_rts_with_eliminated_r, rule=Load)
    if printer_off != True:
        logger.info("Load constraints are done.")
        logger.info("Time to write Load constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Bound_cons_pd_dummy1.")
    timenow = time.time()

    def Bound_cons_pd_dummy1(m, p, d):
        return m.freq[p, d] <= 99999 * m.dummy_var[p, d]

    m.AxbConstraint3 = Constraint(unique_pd, rule=Bound_cons_pd_dummy1)
    if printer_off != True:
        logger.info("Bound_cons_pd_dummy1 constraints are done.")
        logger.info("Time to write Bound_cons_pd_dummy1 constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

        logger.info("Starting to create constraints: Bound_cons_pd_dummy2.")

    timenow = time.time()

    def Bound_cons_pd_dummy2(m, p, d):
        return m.dummy_var[p, d] <= m.freq[p, d]

    m.AxbConstraint4 = Constraint(unique_pd, rule=Bound_cons_pd_dummy2)
    if printer_off != True:
        logger.info("Bound_cons_pd_dummy2 constraints are done.")
        logger.info("Time to write Bound_cons_pd_dummy2 constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Bound_cons_rts.")
    timenow = time.time()

    def Bound_cons_rts(m, r, t, s):
        if sum(rts_pd_ratio[r, t, s, p, d] for p, d in pd_of_rts[r, t, s]) == 0:
            return Constraint.Skip
        else:
            return sum(rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] for p, d in pd_of_rts[r, t, s]) <= max_freq_of_rts

    m.AxbConstraint5 = Constraint(unique_rts_with_eliminated_r, rule=Bound_cons_rts)
    if printer_off != True:
        logger.info("Bound_cons_rts constraints are done.")
        logger.info("Time to write Bound_cons_rts constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Bound_cons_ts.")
    timenow = time.time()

    def Bound_cons_ts(m, t, s):
        if sum(sum(rts_pd_ratio[r, t, s, p, d] for p, d in pd_of_rts[r, t, s]) for r in r_of_ts[t, s]) == 0:
            return Constraint.Skip
        else:
            return (
                sum(
                    sum(rts_pd_ratio[r, t, s, p, d] * m.freq[p, d] for p, d in pd_of_rts[r, t, s])
                    for r in r_of_ts[t, s]
                )
                <= max_freq_of_ts
            )

    m.AxbConstraint6 = Constraint(unique_ts, rule=Bound_cons_ts)
    if printer_off != True:
        logger.info("Bound_cons_ts constraints are done.")
        logger.info("Time to write Bound_cons_ts constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Starting to create constraints: Route_elimination.")
    timenow = time.time()

    def Route_elimination_cons(m, p, d):
        if route_of_p[p] in r_to_be_removed:
            return m.freq[p, d] == 0
        else:
            return Constraint.Skip

    m.AxbConstraint7 = Constraint(unique_pd, rule=Route_elimination_cons)
    if printer_off != True:
        logger.info("Route_elimination constraints are done.")
        logger.info("Time to write Route_elimination constraints is %s." % ((time.time() - timenow)))
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))

    if printer_off != True:
        logger.info("Beginning to solve the problem!")

    wsl_dir = "/home/polaris/cplex/bin"
    lcrc_dir = "/lcrc/project/POLARIS/crossover/cplex/bin"
    possible_dirs = [wsl_dir, lcrc_dir, solver_directory]
    possible_exes = [Path(e) / solver_name for e in possible_dirs if (Path(e) / solver_name).exists()]
    if len(possible_exes) == 0:
        raise FileNotFoundError(f"Can't find {solver_name} executable in any of {possible_dirs}")
    opt = SolverFactory(solver_name, executable=str(possible_exes[0]))

    if solver_name == "cplex":
        opt.options["timelimit"] = timelim
        opt.options["mipgap"] = mip_gap_threshold
    elif solver_name == "cplex_direct":
        opt.options["timelimit"] = timelim
        opt.options["mipgap"] = mip_gap_threshold
    elif solver_name == "glpk":
        opt.options["tmlim"] = timelim
        opt.options["mipgap"] = mip_gap_threshold
    elif solver_name == "gurobi":
        opt.options["TimeLimit"] = timelim
        opt.options["MIPgap"] = mip_gap_threshold
    if printer_off != True:
        results = opt.solve(m, tee=True)
    else:
        results = opt.solve(m)

    if printer_off != True:
        logger.info("Current elapsed time is %s seconds." % (time.time() - start))
    #############################################################################################
    ############################ END BUILDING THE OPTIMIZATION MODEL ############################
    #############################################################################################

    if (
        results.solver.status == SolverStatus.ok
        and results.solver.termination_condition != TerminationCondition.infeasible
    ):
        logger.info("  The problem has been solved.")
        logger.info("  Post-processing.")
        temp_freq = {(p, d): m.freq[p, d]() for p, d in unique_pd}

        freq = {(p, d): temp_freq[p, d] for p, d in unique_pd}
        del temp_freq

        #########################################################################################
        ####################### BEGIN POST-PROCESSING OPTIMIZATION RESULTS ######################
        #########################################################################################
        out_general = open("output_general.csv", "w", newline="")
        out_patterns = open("output_patterns.csv", "w", newline="")
        out_fleet = open("output_fleet.csv", "w", newline="")
        out_routes = open("output_routes.csv", "w", newline="")

        printfile(
            [
                "Stage",
                "Agency",
                "Type",
                "Cost",
                "Budget",
                "Trips",
                "Ridership",
                "Revenue",
                "Objective_sc1",
                "Objective_sc2",
                "Objective_sc3",
            ],
            out_general,
        )
        for a, ty in unique_a_type:
            printfile(
                [
                    1,
                    name_of_a[a],
                    ty,
                    Cost1_of_a_type[a, ty],
                    budget_of_a_type[a, ty],
                    Trips_of_a_type[a, ty],
                    Ridership_of_a_type[a, ty],
                    # Revenue_of_a_type[a, ty],
                    # TODO we will update this by querying POLARIS Demand DB by agency and link type in the future
                    total_rev,
                    Obj1_of_a_type_sc1[a, ty],
                    Obj1_of_a_type_sc2[a, ty],
                    Obj1_of_a_type_sc3[a, ty],
                ],
                out_general,
            )
        if printer_off != True:
            logger.info("Finished writing initial metrics.")
            logger.info("Current elapsed time is %s seconds." % (time.time() - start))

        cost_of_pd = {(p, d): unit_cost_of_p[p] * triptime_of_pd[p, d] * freq[p, d] / 60 for p, d in unique_pd}
        fleet_of_pd = {(p, d): triptimesurrogate_of_pd[p, d] * freq[p, d] / period_minutes for p, d in unique_pd}
        ridership_of_pd = {(p, d): 0 if freq[p, d] == 0 else crt_ridership_of_pd[p, d] for p, d in unique_pd}

        # TODO we will update this by querying POLARIS Demand DB by agency and link type in the future
        rev_of_pd = {
            (p, d): 0 if freq[p, d] == 0 else fare_of_ty[route_type_of_p[p]] * ridership_of_pd[p, d]
            for p, d in unique_pd
        }

        new_freq_of_r = {}
        new_cost_of_r = {}
        new_ridership_of_r = {}
        crt_revenue_of_r = {}
        new_revenue_of_r = {}
        for r in unique_r:
            new_freq_of_r[r] = sum([freq[p, d] for p, d in unique_pd if route_of_p[p] == r])
            new_cost_of_r[r] = sum([cost_of_pd[p, d] for p, d in unique_pd if route_of_p[p] == r])
            new_ridership_of_r[r] = sum([ridership_of_pd[p, d] for p, d in unique_pd if route_of_p[p] == r])
            crt_revenue_of_r[r] = sum([crt_rev_of_pd[p, d] for p, d in unique_pd if route_of_p[p] == r])
            new_revenue_of_r[r] = sum([rev_of_pd[p, d] for p, d in unique_pd if route_of_p[p] == r])

        Cost2_of_a_type = {
            (a, ty): sum(cost_of_pd[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty)
            for a, ty in unique_a_type
        }
        Trips2_of_a_type = {
            (a, ty): sum(freq[p, d] for p, d in unique_pd if agency_of_p[p] == a and route_type_of_p[p] == ty)
            for a, ty in unique_a_type
        }
        Obj2_of_a_type_sc1 = {
            (a, ty): sum(
                crt_ridership_of_rts[r, t, s]
                / cost_per_rider_of_r[r]
                * sum(
                    rts_pd_ratio[r, t, s, p, d] * freq[p, d]
                    for p, d in pd_of_rts[r, t, s]
                    if agency_of_p[p] == a and route_type_of_p[p] == ty
                )
                for r, t, s in unique_rts_with_eliminated_r
            )
            for a, ty in unique_a_type
        }
        Obj2_of_a_type_sc2 = {
            (a, ty): sum(
                1
                / cost_per_rider_of_r[r]
                * sum(
                    rts_pd_ratio[r, t, s, p, d] * freq[p, d]
                    for p, d in pd_of_rts[r, t, s]
                    if agency_of_p[p] == a and route_type_of_p[p] == ty
                )
                for r, t, s in unique_rts_with_eliminated_r
            )
            for a, ty in unique_a_type
        }
        Obj2_of_a_type_sc3 = {
            (a, ty): sum(
                crt_ridership_of_rts[r, t, s]
                * sum(
                    rts_pd_ratio[r, t, s, p, d] * freq[p, d]
                    for p, d in pd_of_rts[r, t, s]
                    if agency_of_p[p] == a and route_type_of_p[p] == ty
                )
                for r, t, s in unique_rts_with_eliminated_r
            )
            for a, ty in unique_a_type
        }

        FleetUsed_of_ad_type_cap = {}
        for a, d, ty, cap in unique_ad_type_cap:
            FleetUsed_of_ad_type_cap[(a, d, ty, cap)] = sum(
                triptimesurrogate_of_pd[p, d] * freq[p, d] / period_minutes for p in p_of_ad_type_cap[a, d, ty, cap]
            )
        printfile("", out_general)
        for a, ty in unique_a_type:
            printfile(
                [
                    2,
                    name_of_a[a],
                    ty,
                    Cost2_of_a_type[a, ty],
                    budget_of_a_type[a, ty],
                    Trips2_of_a_type[a, ty],
                    Ridership_of_a_type[a, ty],
                    # Revenue_of_a_type[a, ty],
                    # TODO we will update this by querying POLARIS Demand DB by agency and link type in the future
                    total_rev,
                    Obj2_of_a_type_sc1[a, ty],
                    Obj2_of_a_type_sc2[a, ty],
                    Obj2_of_a_type_sc3[a, ty],
                ],
                out_general,
            )

        printfile(["Agency", "Departure time", "Type", "Capacity", "Fleet Used", "Fleet Available"], out_fleet)
        for a, d, ty, cap in unique_ad_type_cap:
            printfile(
                [a, d, ty, cap, FleetUsed_of_ad_type_cap[a, d, ty, cap], FleetAvail_of_ad_type_cap[a, d, ty, cap]],
                out_fleet,
            )

        printfile(
            [
                "Pattern",
                "Agency",
                "Type",
                "Route",
                "Cost_per_Rider",
                "Time_Index",
                "Trip_Time",
                "Crt_Freq",
                "New_Freq",
                "Unit_Cost",
                "Crt_Pat_Cost",
                "New_Pat_Cost",
                "Crt_Pat_Fleet",
                "New_Pat_Fleet",
                "Pattern_Cap",
                "Crt_Ridership",
                "New_Ridership",
                "Crt_Revenue",
                "New_Revenue",
            ],
            out_patterns,
        )

        for p, d in unique_pd:
            printfile(
                [
                    p,
                    agency_of_p[p],
                    route_type_of_p[p],
                    route_of_p[p],
                    cost_per_rider_of_r[route_of_p[p]],
                    d,
                    triptime_of_pd[p, d] / 60,
                    crt_freq_of_pd[p, d],
                    freq[p, d],
                    unit_cost_of_p[p],
                    crt_cost_of_pd[p, d],
                    cost_of_pd[p, d],
                    crt_fleet_of_pd[p, d],
                    fleet_of_pd[p, d],
                    cap_of_pd[p, d],
                    crt_ridership_of_pd[p, d],
                    ridership_of_pd[p, d],
                    crt_rev_of_pd[p, d],
                    rev_of_pd[p, d],
                ],
                out_patterns,
            )

        printfile(
            [
                "Route",
                "Agency",
                "Type",
                "Cost_per_Rider",
                "Crt_Freq",
                "New_Freq",
                "Crt_Route_Cost",
                "New_Route_Cost",
                "Crt_Ridership",
                "New_Ridership",
                "Crt_Revenue",
                "New_Revenue",
            ],
            out_routes,
        )

        for r in unique_r:
            printfile(
                [
                    r,
                    agency_of_r[r],
                    route_type_of_r[r],
                    cost_per_rider_of_r[r],
                    crt_freq_of_r[r],
                    new_freq_of_r[r],
                    crt_cost_of_r[r],
                    new_cost_of_r[r],
                    crt_ridership_of_r[r],
                    new_ridership_of_r[r],
                    crt_revenue_of_r[r],
                    new_revenue_of_r[r],
                ],
                out_routes,
            )

        Data = [(p, d, freq[p, d]) for p, d in unique_pd]

        Headers = ("pattern", "time_index", "new_freq")
        Sqdb_writer(supply_path, "pattern_freq_existing", Headers, Data, printer_off)
        if printer_off != True:
            logger.info("Finished writing solution files.")
            logger.info("Total elapsed time is %s seconds." % (time.time() - start))
        out_general.close()
        out_patterns.close()
        out_fleet.close()
        out_routes.close()
        #########################################################################################
        ####################### BEGIN POST-PROCESSING OPTIMIZATION RESULTS ######################
        #########################################################################################

    #############################################################################################
    ################################ BEGIN UPDATING STOP_PAIR_TT ################################
    #############################################################################################
    pat_freq_ex = Conditional_Sqdb_reader(
        supply_path, "pattern_freq_existing", "*", "where new_freq > 0.0001", printer_off
    )[1]
    """i[0]: pattern_id, i[1]: pattern_time_index, i[2]: crt_freq"""

    Unique_pattern_ids = list(set([i[0] for i in pat_freq_ex]))

    freq_give_pat_time_ind = {(i[0], i[1]): i[2] for i in pat_freq_ex}

    Transit_Pattern_Links_Transposed = [list(sublist) for sublist in list(zip(*Transit_Pattern_Links.values()))]
    grouped_t_p_by_pat = [list(x[1]) for x in groupby(Transit_Pattern_Links_Transposed, key=lambda v: v[0])]
    link_counts = {}
    for i in grouped_t_p_by_pat:
        link_counts[i[0][0]] = len(i)

    node_pair_given_t_link = dict(
        zip(Transit_Links["TRANSIT_LINK"], tuple(zip(Transit_Links["FROM_NODE"], Transit_Links["TO_NODE"])))
    )

    avg_durations = dict(
        zip(
            tuple(
                zip(
                    Pattern_Departure_Index_Link_Durations["PATTERNID"],
                    Pattern_Departure_Index_Link_Durations["PATTERN_TIME_INDEX"],
                    Pattern_Departure_Index_Link_Durations["LINK_INDEX"],
                )
            ),
            Pattern_Departure_Index_Link_Durations["AVG_DURATION"],
        )
    )

    if printer_off != True:
        logger.info(
            """Began creating the lists 'trips_temp' and 'trips_sched_temp'
        which will be written into Polaris."""
        )
    indiff_size = period_seconds
    indiff_size2 = period_seconds2
    trip_name = {}
    trips_temp = []
    trips_sched_temp = []
    if printer_off != True:
        logger.info("There are %s patterns to be processed." % (len(Unique_pattern_ids)))
    counter = 0

    # pattern_id_multiplier = 1
    # pattern_found = True

    # while pattern_id_multiplier < 10000 and pattern_found is True:
    # pattern_found = False
    # for i in Unique_pattern_ids:
    # if i * pattern_id_multiplier % 10000 > 0:
    # pattern_id_multiplier *= 10
    # pattern_found = True
    # break

    all_trips_ctr = 0
    for i in Unique_pattern_ids:
        counter += 1
        j = 0
        current_time = 0
        time_reset = True
        # trip_per_pattern = 0
        while j <= time_frame - 1:
            if (i, j) in list(freq_give_pat_time_ind.keys()):
                our_freq = freq_give_pat_time_ind[i, j]
                our_headway = indiff_size / our_freq
                trip_found = False

                if time_reset == True:
                    current_time = j * indiff_size + our_headway * 0.5
                    j_curr = int((current_time) / indiff_size)
                    current_time = float(math.floor(current_time))
                    trip_found = True
                    time_reset = False

                elif int((current_time + our_headway) / indiff_size) == j:
                    current_time += our_headway
                    j_curr = int((current_time) / indiff_size)
                    current_time = float(math.floor(current_time))
                    trip_found = True

                elif (i, j + 1) in freq_give_pat_time_ind.keys():
                    next_freq = freq_give_pat_time_ind[i, j + 1]
                    next_headway = indiff_size / next_freq
                    current_time = current_time + 0.5 * our_headway + 0.5 * next_headway
                    j_curr = int((current_time) / indiff_size)
                    current_time = float(math.floor(current_time))
                    trip_found = True

                if trip_found == True:
                    j = j_curr
                    # trip_per_pattern += 1
                    # trip_name = i * pattern_id_multiplier + trip_per_pattern
                    all_trips_ctr += 1
                    trip_name = all_trips_ctr
                    trips_temp.append(
                        (
                            trip_name,
                            "%s" % (trip_name),
                            0,
                            i,
                            seated_cap[i],
                            design_cap[i],
                            total_cap[i],
                            "NULL",
                            "NULL",
                        )
                    )

                    my_duration = 0
                    my_time = current_time
                    for k in range(1, link_counts[i] + 1):
                        index = k - 1
                        arrival = departure = my_time
                        my_index = int((my_time) / indiff_size2)
                        if my_index > time_frame2 - 1:
                            my_index = my_index - time_frame2
                        trips_sched_temp.append((trip_name, index, arrival, departure))

                        my_time += float(round(avg_durations[i, j, index]))

                    index = link_counts[i]
                    arrival = departure = my_time
                    trips_sched_temp.append((trip_name, index, arrival, departure))
                else:
                    j += 1
                    time_reset = True

            else:
                j += 1
                time_reset = True
        if printer_off != True:
            logger.info("Completed pattern %s. Progress: %s/%s." % (i, counter, len(Unique_pattern_ids)))
    if printer_off != True:
        logger.info(
            """Finished creating the lists 'trips_temp' and 'trips_sched_temp'
        which will be written into Polaris."""
        )

    Headers = (
        "trip_id",
        "trip",
        "dir",
        "pattern_id",
        "seated_capacity",
        "design_capacity",
        "total_capacity",
        "is_artic",
        "number_of_cars",
    )
    Sqdb_updater(supply_path, "Transit_Trips", Headers, trips_temp, printer_off)

    Headers = ("trip_id", "index", "arrival", "departure")
    Sqdb_updater(supply_path, "Transit_Trips_Schedule", Headers, trips_sched_temp, printer_off)
    #############################################################################################
    ################################# END UPDATING STOP_PAIR_TT #################################
    #############################################################################################
    Sqdb_value_updater(supply_path, "Transit_Fare_Attributes", "price", "*%s" % (fare_multiplier), printer_off)

    with closing(sqlite3.connect(supply_path)) as conn:
        write_about_model_value(conn, "transit_fare_discount_rate", fare_discount_rate)
        conn.commit()

    logger.info("  Sanity-checking.")
    transit_sql_file = Path(__file__).parent.parent.parent.parent.parent / "runs" / "sql" / "transit_stats.sql"
    logging.info(f"Running transit summary sql file: {transit_sql_file}")
    run_sql_file(transit_sql_file, supply_path)
