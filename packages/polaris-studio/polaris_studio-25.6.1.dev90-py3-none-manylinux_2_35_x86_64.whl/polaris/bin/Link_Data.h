// Copyright (c) 2025, UChicago Argonne, LLC
// All rights reserved. Full details of the terms by which this software is licensed can be found in LICENSE.md
#pragma once

#include "by_time.h"
#include "units.h"

// Simplified macros for external use
#ifndef t_data
    #define t_data(TYPE, NAME) TYPE NAME;
    #define t_object(...) t_data(__VA_ARGS__)

    #define t_static_data(TYPE, NAME) static TYPE NAME;
    #define t_static_object(...) t_data(__VA_ARGS__)
#endif

namespace Link_Components::Types
{
    enum Link_Type_Keys
    {
        FREEWAY = 0,
        ON_RAMP,
        OFF_RAMP,
        EXPRESSWAY,
        ARTERIAL,
        LOCAL,
        EXTERNAL,
        BIKEWAY,
        WALK,
        LIGHT_RAIL,    // GTFS type = 0
        RAIL,          // GTFS type = 1
        COMMUTER_RAIL, // GTFS type = 2
        BUS,           // GTFS type = 3
        FERRY,         // GTFS type = 4
        CABLE_TRAM,    // GTFS type = 5
        AERIAL_LIFT,   // GTFS type = 6
        FUNICULAR,     // GTFS type = 7
        TROLLEY_BUS,   // GTFS type = 11
        MONO_RAIL      // GTFS type = 12
    };

    Link_Type_Keys linkTypeFromString(string s)
    {
        if (s == "FREEWAY")
            return FREEWAY;
        if (s == "EXPRESSWAY")
            return EXPRESSWAY;
        if (s == "RAMP")
            return ON_RAMP;
        if (s == "LOCAL" || s == "COLLECTOR" /* || s=="MINOR"*/)
            return LOCAL;
        if (s == "BIKEWAY")
            return BIKEWAY;
        if (s == "FERRY")
            return FERRY;
        if (s == "EXTERNAL")
            return EXTERNAL;
        if (s == "ARTERIAL" || s == "MAJOR" || s == "MINOR" || s == "OTHER" || s == "BUSWAY" || s == "PRINCIPAL")
            return ARTERIAL;
        if (s == "WALK")
            return WALK;
        THROW_EXCEPTION("Unknown link type: " << s);
    }

    Link_Type_Keys linkTypeFromGtfsId(int gtfs_id)
    {
        if (gtfs_id == 0)
            return LIGHT_RAIL;
        if (gtfs_id == 1)
            return RAIL;
        if (gtfs_id == 2)
            return COMMUTER_RAIL;
        if (gtfs_id == 3)
            return BUS;
        if (gtfs_id == 4)
            return FERRY;
        if (gtfs_id == 5)
            return CABLE_TRAM;
        if (gtfs_id == 6)
            return AERIAL_LIFT;
        if (gtfs_id == 7)
            return FUNICULAR;
        if (gtfs_id == 11)
            return TROLLEY_BUS;
        if (gtfs_id == 12)
            return MONO_RAIL;
        THROW_EXCEPTION("Unknown GTFS type ID: " << gtfs_id);
    }

    bool is_highway(Link_Type_Keys e)
    {
        // EXTERNAL link types act as highway/expressway links (to avoid over loading them with external trips)
        return e == FREEWAY || e == EXPRESSWAY || e == EXTERNAL;
    }

    bool is_ramp(Link_Type_Keys e) { return e == ON_RAMP || e == OFF_RAMP; }

    // bool is_arterial(Link_Type_Keys e)
    // {
    //     return e == ARTERIAL || e == LOCAL;
    // }

    enum Traffic_Flow_model_Keys
    {
        MESOSCOPIC,
        LAGRANGIAN
    };

    Traffic_Flow_model_Keys trafficFlowModelFromString(string s)
    {
        return s == "LAGRANGIAN" ? Traffic_Flow_model_Keys::LAGRANGIAN : Traffic_Flow_model_Keys::MESOSCOPIC;
    }

    struct TrafficIncident
    {
        TrafficIncident()
        {
            start_time     = 0;
            end_time       = 0;
            link_id        = 0;
            dir            = 0;
            capacity_scale = 0.0f;
        }

        int   start_time;
        int   end_time;
        int   link_id;
        int   dir;
        float capacity_scale;
    };

    struct ClassSpecificImpact
    {
        ClassSpecificImpact()
        {
            speed_multiplier         = 1.0f;
            reaction_time_multiplier = 1.0f;
        }
        ClassSpecificImpact(float speed_multiplier_, float reaction_time_multiplier_)
        {
            speed_multiplier         = speed_multiplier_;
            reaction_time_multiplier = reaction_time_multiplier_;
        }
        float speed_multiplier;
        float reaction_time_multiplier;
    };

    enum ImpactsDefinition
    {
        ALL_HOMOGENEOUS = 0,
        LINK_TYPE_BY_REGULAR_AV_TRUCK,
    };

    enum MultiClassIndex
    {
        REGULAR_SOV          = 0,
        AV_EXPRESSWAY        = 1,
        AV_SIGNALIZED        = 2,
        AV_LOCAL             = 3,
        FREIGHT_EXPRESSWAY   = 4,
        FREIGHT_SIGNALIZED   = 5,
        FREIGHT_LOCAL        = 6,
        AVFREIGHT_EXPRESSWAY = 7,
        AVFREIGHT_SIGNALIZED = 8,
        AVFREIGHT_LOCAL      = 9
    };

    struct LinkDemandInfo
    {
        LinkDemandInfo() : left_demand(0), right_demand(0), thru_demand(0) {}
        int left_demand;
        int right_demand;
        int thru_demand;
    };

} // namespace Link_Components::Types

namespace Link_Components::Implementations
{

    struct Link_MOE_Data
    {
        int                 start_time                           = 0;
        int                 end_time                             = 0;
        second_t            link_travel_time                     = 0_s;
        second_t            link_travel_time_standard_deviation  = 0_s;
        float               link_queue_length                    = 0.0f;
        second_t            link_travel_delay                    = 0_s;
        second_t            link_travel_delay_standard_deviation = 0_s;
        meters_per_second_t link_speed                           = 0_mps;
        float               link_density                         = 0.0f;
        float               link_in_flow_rate                    = 0.0f;
        float               link_out_flow_rate                   = 0.0f;

        float link_in_volume  = 0.0f;
        float link_out_volume = 0.0f;

        float link_speed_ratio       = 0.0f;
        float link_in_flow_ratio     = 0.0f;
        float link_out_flow_ratio    = 0.0f;
        float link_density_ratio     = 0.0f;
        float link_travel_time_ratio = 0.0f;

        float num_vehicles_in_link = 0.0f;
        float entry_queue_length   = 0.0f;

        float volume_cum_MDT = 0.0f;
        float volume_cum_HDT = 0.0f;
    };

    struct Pocket_Data
    {
        Pocket_Data() : num_pockets(0), num_pockets_left(0), num_pockets_right(0), pocket_length(0.0f) {}
        int   num_pockets;
        int   num_pockets_left;
        int   num_pockets_right;
        float pocket_length;
    };

    struct Last_Departure_Data
    {
        Last_Departure_Data()
            : last_departure_left(0), last_departure_right(0), last_departure_thru(0), last_departure_link(0)
        {
        }
        int last_departure_left;
        int last_departure_right;
        int last_departure_thru;
        int last_departure_link;
    };

    //=============================================================================================================
    /// Polaris_Link_Base
    //-------------------------------------------------------------------------------------------------------------
    struct Link_Data
    {
        Link_Data()
        {

            _current_sub_step = 0;

            _uuid                                         = 0;
            _internal_id                                  = 0;
            _dbid                                         = 0;
            _direction                                    = 0;
            _num_lanes                                    = 0;
            _bearing                                      = 0;
            _length                                       = 0_m;
            _speed_limit                                  = 0_mph;
            _grade                                        = 0.0f;
            _zone                                         = 0;
            _zone_index                                   = 0;
            _link_type                                    = Link_Components::Types::FREEWAY;
            _num_inbound_turn_lanes                       = 0;
            _link_fftt                                    = 0;
            _link_bwtt                                    = 0;
            _link_fftt_cached_simulation_interval_size    = 0;
            _link_bwtt_cached_simulation_interval_size    = 0;
            _link_capacity                                = 0;
            _link_supply                                  = 0;
            _reserved_entry_queue                         = 0;
            _link_upstream_arrived_vehicles               = 0;
            _link_downstream_departed_vehicles            = 0;
            _link_origin_arrived_vehicles                 = 0;
            _link_origin_departed_vehicles                = 0;
            _link_origin_loaded_vehicles                  = 0;
            _link_origin_loaded_capacity_leftover         = 0;
            _link_destination_arrived_vehicles            = 0;
            _link_upstream_cumulative_arrived_vehicles    = 0;
            _link_upstream_cumulative_vehicles            = 0;
            _link_downstream_cumulative_vehicles          = 0;
            _link_downstream_cumulative_arrived_vehicles  = 0;
            _link_origin_cumulative_arrived_vehicles      = 0;
            _link_origin_cumulative_departed_vehicles     = 0;
            _link_destination_cumulative_arrived_vehicles = 0;
            _cacc_count                                   = 0;
            _volume_cum_MDT                               = 0;
            _volume_cum_HDT                               = 0;
            _maximum_flow_rate                            = per_hour_t(0);
            _free_flow_speed                              = 0_mph;
            _backward_wave_speed                          = 0_mph;
            _prevailing_backward_wave_speed               = 0_mph;
            _jam_density                                  = per_mile_t(0);
            _critical_density                             = 0;
            _num_vehicles_under_jam_density               = 0;
            _original_free_flow_speed                     = 0_mph;
            _original_maximum_flow_rate                   = per_hour_t(0);
            _original_speed_limit                         = 0_mph;
            _original_num_lanes                           = 0;
            _shoulder_opened                              = false;
            _speed_adjustment_factor_due_to_weather       = 0;
            _speed_adjustment_factor_due_to_accident      = 0;
            _capacity_adjustment_factor_due_to_weather    = 0;
            _capacity_adjustment_factor_due_to_accident   = 0;
            _lane_adjustment_due_to_accident              = 0;
            _link_origin_vehicle_current_position         = 0;
            _link_num_vehicles_in_queue                   = 0;
            _num_vehicles_on_link                         = 0;
            _link_vmt                                     = 0;
            _link_vht                                     = 0;
            _C                                            = 0;
            _Q                                            = 0;
            _travel_time                                  = 0;
            _realtime_travel_time                         = 0;
            _weather_event_to_process                     = 0;
            _accident_event_to_process                    = 0;
            _has_stop_sign                                = false;
            _moes_by_entry_computed                       = false;
            _ld_monetary_cost                             = dollar_t(0);
            _md_monetary_cost                             = dollar_t(0);
            _hd_monetary_cost                             = dollar_t(0);
            _step_flow                                    = 0;
            _remaining_supply                             = 0.0f;
            _capacity_discrete                            = 0;
            _capacity_discrete_thru                       = 0;
            _has_rsu                                      = false;

            _min_multi_modal_cost     = 0.0f;
            _walk_length              = 0_m;
            _walk_distance_to_transit = 0_m;

            _drive_time                                     = 0.0f;
            _drive_fft_to_transit                           = 0.0f;
            _touch_transit                                  = false;
            _has_transit_parking                            = false;
            _total_delay_experienced_on_assignment_interval = 0.0f;
            _outflow_on_the_interval                        = 0.0f;
            _link_delay                                     = 0.0f;

            _link_num_vehicles_in_queue = 0;
            _num_vehicles_on_link       = 0;

            _link_vmt = 0.0f;
            _link_vht = 0.0f;
            _C        = 0.0f;
            _Q        = 0.0f;

            _touch_transit                        = false;
            _has_transit_parking                  = false;
            _number_of_regular_docks              = 0;
            _number_of_charging_docks             = 0;
            _number_of_regular_docked_vehicles    = 0;
            _number_of_charging_docked_vehicles   = 0;
            _number_of_empty_regular_docks        = 0;
            _number_of_empty_charging_docks       = 0;
            _index_along_pattern_at_upstream_node = 0;

            _grand_total_flow_in_prev_tolling_interval = 0;
            _last_acceptance                           = -1;
        }

        //========================================================================================================
        /// Simple Link Members
        //--------------------------------------------------------------------------------------------------------
        t_static_object(std::vector<Link_Components::Types::ClassSpecificImpact>, multi_class_impacts);
        t_static_data(Link_Components::Types::ImpactsDefinition, impact_definition_type,
                      Link_Components::Types::ImpactsDefinition::ALL_HOMOGENEOUS);
        t_static_data(float, max_acc, -1.0f);
        t_static_data(float, max_dec, -1.0f);
        t_static_data(bool, bounded_acc);

        t_data(int, uuid);
        t_data(int, internal_id);
        t_data(int, dbid);
        t_data(int, direction);
        t_data(int, num_lanes);
        t_data(meter_t, length);
        t_data(miles_per_hour_t, speed_limit);
        t_data(miles_per_hour_t, original_speed_limit);
        t_data(float, grade);
        t_data(int, bearing);
        t_data(Link_Components::Types::Traffic_Flow_model_Keys, traffic_model);

        t_data(int, zone);       // Zone UUID (from db)
        t_data(int, zone_index); // Zone internal index

        t_data(Link_Components::Types::Link_Type_Keys, link_type);
        t_data(int, num_inbound_turn_lanes);

        // link state
        t_data(float, link_fftt);
        t_data(float, link_bwtt);
        t_data(int, link_fftt_cached_simulation_interval_size);
        t_data(int, link_bwtt_cached_simulation_interval_size);

        // current interval
        t_data(float, link_capacity);
        t_data(float, link_supply);

        t_data(float, reserved_entry_queue);

        t_data(int, link_origin_arrived_vehicles);
        t_data(int, link_origin_departed_vehicles);
        t_data(int, link_origin_loaded_vehicles);
        t_data(float, link_origin_loaded_capacity_leftover);

        t_data(int, link_destination_arrived_vehicles);

        // The following member variables are declared t_object so that they can be
        // easily incremented by other classes
        t_object(int, link_upstream_arrived_vehicles);
        t_object(int, link_downstream_departed_vehicles);

        // cumulative - Mid-Trip
        t_object(int, link_upstream_cumulative_arrived_vehicles);
        t_object(int, link_upstream_cumulative_vehicles);
        t_object(int, link_downstream_cumulative_vehicles);
        t_object(int, link_downstream_cumulative_arrived_vehicles);

        // cumulative - Begin/End-Trip
        t_object(int, link_origin_cumulative_arrived_vehicles);
        t_object(int, link_origin_cumulative_departed_vehicles);
        t_object(int, link_destination_cumulative_arrived_vehicles);

        // AV information....
        t_object(int, cacc_count);

        t_data(bool, has_street_parking);

        // Estimated CV (Commercial Vehicle) Volumes
        t_data(int, volume_cum_MDT);
        t_data(int, volume_cum_HDT);

        // other attributes
        t_data(per_hour_t, maximum_flow_rate);
        t_data(per_hour_t, original_maximum_flow_rate);

        t_data(miles_per_hour_t, backward_wave_speed);
        t_data(miles_per_hour_t, prevailing_backward_wave_speed);

        t_data(float, piecewise_v2_vehs_per_meter);
        t_data(float, piecewise_k2_meters_per_second);
        t_data(per_mile_t, jam_density);
        t_data(float, critical_density);
        t_data(float, num_vehicles_under_jam_density);
        t_data(miles_per_hour_t, free_flow_speed);
        t_data(miles_per_hour_t, original_free_flow_speed);
        t_data(int, original_num_lanes);
        t_data(bool, shoulder_opened);
        t_data(bool, has_stop_sign);
        t_data(bool, is_signalized);
        t_data(float, capacity_discrete);
        t_data(float, capacity_discrete_thru);
        t_data(float, remaining_supply);
        t_data(float, step_flow);
        t_data(bool, moes_by_entry_computed);
        t_data(bool, has_rsu);
        t_data(Last_Departure_Data, departure_data);

        t_data(float, total_delay_experienced_on_assignment_interval);
        t_data(float, outflow_on_the_interval);
        t_data(int, current_sub_step);

        t_data(float, speed_adjustment_factor_due_to_weather);
        t_data(float, speed_adjustment_factor_due_to_accident);
        t_data(float, capacity_adjustment_factor_due_to_weather);
        t_data(float, capacity_adjustment_factor_due_to_accident);
        t_data(float, lane_adjustment_due_to_accident);

        // Overrides queue - called by Set_Link_Override()
        t_object(std::queue<int>, override_times);

        //============================================================================================================
        /// Transit-Related Members
        //------------------------------------------------------------------------------------------------------------

        t_object(std::vector<float>, dijkstra_cost);

        t_data(int, index_along_pattern_at_upstream_node);
        t_object(vector<float>, heur_cost_to_dest);

        t_data(float, min_multi_modal_cost);

        t_data(meter_t, walk_length);
        t_data(meter_t, walk_distance_to_transit);

        t_data(float, drive_time);
        t_data(float, drive_fft_to_transit);
        t_data(bool, touch_transit);
        t_data(bool, has_transit_parking);
        t_data(int, number_of_regular_docks);
        t_data(int, number_of_charging_docks);
        t_data(int, number_of_regular_docked_vehicles);
        t_data(int, number_of_charging_docked_vehicles);
        t_data(int, number_of_empty_regular_docks);
        t_data(int, number_of_empty_charging_docks);

        //=============================================================================================================
        /// Inbound and Outbound Turn Movement Members
        //------------------------------------------------------------------------------------------------------------

        //========================================================================================================
        /// Upstream and Downstream Intersections Reference
        //--------------------------------------------------------------------------------------------------------

        //========================================================================================================
        /// Containers of Cached Cumulative Vehicle Statistics
        //--------------------------------------------------------------------------------------------------------

        t_object(std::vector<int>, cached_link_upstream_cumulative_vehicles_array);
        t_object(std::vector<int>, cached_link_downstream_cumulative_vehicles_array);

        //========================================================================================================
        /// Vehicle Origin Containers
        //--------------------------------------------------------------------------------------------------------
        t_data(int, link_origin_vehicle_current_position);

        //========================================================================================================
        /// Current Vehicles Containers
        //--------------------------------------------------------------------------------------------------------

        t_object(std::vector<int>, vehicles_processed_by_entry_time);
        t_object(std::vector<float>, raw_delay_by_entry_time);

        t_data(float, total_delay_experienced_on_assignment_interval_cv);
        t_data(float, outflow_on_the_interval_cv);
        t_data(float, link_delay);
        t_data(float, link_delay_cv);

        t_object(std::vector<Link_Components::Types::TrafficIncident>, traffic_incidents);

        //=========================================================================================================
        /// Replicas Container
        //---------------------------------------------------------------------------------------------------------

        t_data(int, link_num_vehicles_in_queue);
        t_data(int, num_vehicles_on_link);

        t_data(float, link_vmt);

        t_object(Pocket_Data, pocket_data);

        t_data(float, link_vht);
        t_data(float, C);
        t_data(float, Q);
        t_data(float, time_step);

        Link_MOE_Data link_moe_data;
        Link_MOE_Data non_volatile_link_moe_data;
        Link_MOE_Data normal_day_link_moe_data;
        Link_MOE_Data realtime_link_moe_data;

        t_data(int, last_acceptance);
        t_object(std::vector<float>, turn_delay_by_entry_time);

        //========================================================================================================
        /// travel_time
        //--------------------------------------------------------------------------------------------------------

        t_data(float, travel_time);
        t_data(float, realtime_travel_time);
        t_data(dollar_t, ld_monetary_cost);
        t_data(dollar_t, md_monetary_cost);
        t_data(dollar_t, hd_monetary_cost);
        t_object(by_time<dollar_t>, dynamic_toll);
        t_object(by_time<dollar_t>, dynamic_md_toll);
        t_object(by_time<dollar_t>, dynamic_hd_toll);

        // Congestion Pricing
        t_data(float, grand_total_flow_in_prev_tolling_interval);

        //========================================================================================================
        /// Events
        //--------------------------------------------------------------------------------------------------------

        t_data(bool, weather_event_to_process);
        t_data(bool, accident_event_to_process);

        //========================================================================================================
        /// ITS
        //-------------------------------------------------------------------------------------------------------

        static float link_capacity_adjustment_factors_for_weather[19];
        static float link_free_flow_speed_adjustment_factors_for_weather[19][5];
        static float link_capacity_adjustment_factors_for_accident[8][5];
    };
} // namespace Link_Components::Implementations
