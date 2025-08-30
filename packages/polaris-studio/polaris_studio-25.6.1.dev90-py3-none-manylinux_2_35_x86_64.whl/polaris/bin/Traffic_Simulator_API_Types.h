// Copyright (c) 2025, UChicago Argonne, LLC
// All rights reserved. Full details of the terms by which this software is licensed can be found in LICENSE.md
#pragma once
#include <vector>
#include <string>

namespace polaris
{
    struct API_Vehicle_State
    {
        int    state_time;
        int    vehicle_id;
        int    current_link_uid;
        int    next_link_uid;
        int    current_pocket_identifier;
        double position;
        double speed;
    };

    struct API_Vehicle_Static_Data
    {
        int               vehicle_id;
        int               in_network;
        API_Vehicle_State state;
    };

    struct API_Vehicle_Trip_Data
    {
        int              vehicle_id;
        float            departure_time_seconds;
        int              origin_location;
        int              destination_location;
        int              current_link;
        std::vector<int> route_sequence;
    };

    struct PolarisSignalState
    {
        int current_time;
        int current_interval;
        int cycle_time;
        int current_phase;
        int current_color;
        int remaining_time_in_color;
        int remaining_time_in_cycle;
    };

    enum API_ROW_TYPE
    {
        API_PROTECTED,
        API_PERMITTED,
        API_STOP_PERMITTED,
        API_STOP
    };

    enum API_TURN_TYPE
    {
        API_THROUGH,
        API_LEFT,
        API_RIGHT,
        API_UTURN
    };

    enum API_NEMA_DIRECTION_TYPE
    {
        API_EASTBOUND,
        API_NORTHBOUND,
        API_WESTBOUND,
        API_SOUTHBOUND
    };

    struct API_Connection
    {
        API_Connection()
        {
            inbound_link_uuid  = -1;
            outbound_link_uuid = -1;
            turn_type          = API_UTURN;
            direction_type     = API_EASTBOUND;
            num_lanes          = -1;
            movement_id        = -1;
            conn_index         = -1;
        }

        API_Connection(int inbound_link_uuid_, int outbound_link_uuid_, API_TURN_TYPE turn_type_,
                       API_NEMA_DIRECTION_TYPE direction_, int num_lanes_, int movement_id_, int conn_index_)
        {
            inbound_link_uuid  = inbound_link_uuid_;
            outbound_link_uuid = outbound_link_uuid_;
            turn_type          = turn_type_;
            direction_type     = direction_;
            num_lanes          = num_lanes_;
            movement_id        = movement_id_;
            conn_index         = conn_index_;
        };
        int                       inbound_link_uuid;
        int                       outbound_link_uuid;
        int                       movement_id;
        std::vector<API_ROW_TYPE> conn_rows;
        API_TURN_TYPE             turn_type;
        API_NEMA_DIRECTION_TYPE   direction_type;
        int                       num_lanes;
        int                       conn_index;
    };

    struct API_Phase
    {
        API_Phase(){

        };
        API_Phase(int phase_index_, int phase_id_, int minimum_green_, int intergreen_,
                  std::vector<API_Connection> protected_conn, std::vector<API_Connection> permitted_conn,
                  std::vector<API_Connection> stop_permit_conn)
        {
            phase_index             = phase_index_;
            phase_id                = phase_id_;
            minimum_green           = minimum_green_;
            intergreen              = intergreen_;
            protected_connections   = protected_conn;
            permitted_connections   = permitted_conn;
            stop_permit_connections = stop_permit_conn;
            yellow                  = 0;
        };

        int                         phase_index;
        int                         phase_id;
        int                         minimum_green;
        int                         intergreen;
        int                         yellow;
        std::vector<API_Connection> protected_connections;
        std::vector<API_Connection> permitted_connections;
        std::vector<API_Connection> stop_permit_connections;
    };

    struct API_Intersection_Configuration
    {
        API_Intersection_Configuration() { intersection_id = -1; };

        API_Intersection_Configuration(int intersection_id_, std::vector<API_Phase> phases_,
                                       std::vector<API_Connection> connections_, int area_type_)
        {
            intersection_id = intersection_id_;
            phases          = phases_;
            connections     = connections_;
            area_type       = area_type_;
        }

        int                         intersection_id;
        std::vector<API_Phase>      phases;
        std::vector<API_Connection> connections;
        int                         area_type;
    };

    struct API_Link_Static_Data
    {
        double length;
        double free_flow_speed;
        double shock_wave_speed;
        double jam_density;
        int    num_lanes;
        int    num_left_pockets;
        int    num_right_pockets;
        int    signalized;
        int    upstream_intersection_id;
        int    downstream_intersection_id;
    };

    // These are the functions that we expose to an external DLL. Each time we call out to the
    // dll, we provide these functions to enable the dll to callback into us to discover some
    // of our internal state
    struct TrafficAPIFunctions
    {
        std::string (*get_simulation_dir)();
        void (*enable_api_control)(int);
        void (*disable_api_control)(int);
        void (*get_current_plan)(int, int&, int&, std::vector<int>&);
        void (*set_next_plan)(int, int, std::vector<int>);
        void (*switch_to_phase)(int, int);
        int (*get_number_of_vehicles_in_link)(int);
        int (*get_number_of_vehicles_in_pocket)(int, int);
        int (*get_number_of_vehicles_heading_left_pocket)(int);
        int (*get_number_of_vehicles_heading_right_pocket)(int);
        int (*get_number_of_vehicles_heading_thru_pocket)(int);
        float (*get_loop_detector_occupancy)(int);
        float (*get_loop_detector_count)(int);
        void (*get_traffic_signal_state)(int, PolarisSignalState&);
        void (*get_vehicle_states_at_link)(int, std::vector<API_Vehicle_State>&);
        void (*get_vehicle_state)(int, API_Vehicle_State&);
        void (*get_junction_configuration)(int, API_Intersection_Configuration&);
        void (*get_link_static_data)(int, API_Link_Static_Data&);
        void (*enable_vehicle_control)(int, float (*)(float, float, float, int, int));
        void (*register_load_callback)(void (*)(int));
        void (*register_unload_callback)(void (*)(int));
        void (*disable_vehicle_control)(int);
        bool (*is_vehicle_controlled)(int);
        void (*get_vehicles_static_data)(std::vector<API_Vehicle_Static_Data>&);
        void (*get_vehicle_trip_data)(int, API_Vehicle_Trip_Data&);
    };

} // namespace polaris