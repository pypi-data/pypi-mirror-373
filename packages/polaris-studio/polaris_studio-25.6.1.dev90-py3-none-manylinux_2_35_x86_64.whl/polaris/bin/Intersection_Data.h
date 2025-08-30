// Copyright (c) 2025, UChicago Argonne, LLC
// All rights reserved. Full details of the terms by which this software is licensed can be found in LICENSE.md
#pragma once

#include "Link_Data.h"
#include "units.h"

// Simplified macros for external use
#ifndef t_data
    #define t_data(TYPE, NAME) TYPE NAME;
    #define t_object(...) t_data(__VA_ARGS__)

    #define t_static_data(TYPE, NAME) static TYPE NAME;
    #define t_static_object(...) t_static_data(__VA_ARGS__)
#endif

namespace Intersection_Components::Types
{
    enum Intersection_Type_Keys
    {
        NO_CONTROL = 0,
        YIELD_SIGN,
        ALL_WAY_STOP_SIGN,
        TWO_WAY_STOP_SIGN,
        PRE_TIMED_SIGNAL_CONTROL,
        ACTUATED_SIGNAL_CONTROL,
        ADAPTIVE_SIGNAL_CONTROL,
        API_CYLIC_CONTROL
    };
    enum Intersection_Configuration_Types
    {
        ALL_STOP,
        STOP_SIGN_PRIORITY,
        SIGNALIZED,
        MERGE_DIVERGE
    };
} // namespace Intersection_Components::Types

namespace Intersection_Components::Implementations
{
    struct Intersection_Data
    {
        Intersection_Data()
        {
            _uuid        = -1;
            _dbid        = -1;
            _internal_id = -1;

            _x_position = 0_m;
            _y_position = 0_m;
            _z_position = 0_m;

            _zone                       = 0;
            _has_transit_parking        = false;
            _intersection_type          = Types::NO_CONTROL;
            _intersection_configuration = Types::ALL_STOP;
            _general_node_model         = false;
            _signal_control_node_model  = false;
        };

        t_data(Intersection_Components::Types::Intersection_Type_Keys, intersection_type);

        t_data(int, uuid);
        t_data(int, dbid);
        t_data(int, internal_id);

        t_data(meter_t, x_position);
        t_data(meter_t, y_position);
        t_data(meter_t, z_position);

        t_data(int, zone);
        t_data(int, zone_index);

        t_data(bool, has_transit_parking);
        t_data(int, number_of_regular_docks);
        t_data(int, number_of_charging_docks);
        t_data(int, number_of_regular_docked_vehicles);
        t_data(int, number_of_charging_docked_vehicles);
        t_data(int, number_of_empty_regular_docks);
        t_data(int, number_of_empty_charging_docks);
        t_data(float, time_step);

        t_object(std::vector<int>, current_index_per_priority_level);
        t_data(Intersection_Components::Types::Intersection_Configuration_Types, intersection_configuration);
        t_data(bool, general_node_model);
        t_data(bool, signal_control_node_model);
        t_data(Link_Components::Types::Traffic_Flow_model_Keys, traffic_model);
    };

} // namespace Intersection_Components::Implementations
