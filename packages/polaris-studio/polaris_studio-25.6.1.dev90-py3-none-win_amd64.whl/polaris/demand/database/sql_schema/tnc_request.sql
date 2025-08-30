-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The TNC_Request table stores records for all requests recevied by any shared mobility operator in POLARIS.
--@ A variety of information is recorded to understand demand for the different shared mobility services, and
--@ the outcome details when trying to serve the request is also logged. 
--@
--@ The data in this table is purely an output of POLARIS and is not read back in by subsequent iterations.

CREATE TABLE "TNC_Request" (
  "TNC_request_id" INTEGER NOT NULL PRIMARY KEY,              --@ Unique identifier for requests that are made in the simulation.
  "request_time" REAL NULL DEFAULT 0,                         --@ Time at which the request was made (units: seconds)
  "reserve_time" REAL NULL DEFAULT 0,                         --@ Time for which the request was made, either same as request_time or ahead (units: seconds)
  "assignment_time" REAL NULL DEFAULT 0,                      --@ Time at which the request is assigned to a vehicle or 0 if not assigned. (units: seconds)
  "pickup_time" REAL NULL DEFAULT 0,                          --@ Time at which the request was picked up by the vehicle or 0 if not assigned. (units: seconds)
  "dropoff_time" REAL NULL DEFAULT 0,                         --@ Time at which the request was dropped off by the vehicle or 0 if not assigned or was not dropped off before simulation ended. (units: seconds)
  "access_walk_duration" REAL NULL DEFAULT 0.0,               --@ Time needed for request to walk to vehicle from origin before pickup, if needed. (units: seconds)
  "egress_walk_duration" REAL NULL DEFAULT 0.0,               --@ Time needed for request to walk to destination from vehicle after dropoff, if needed. (units: seconds)
  "origin_location" INTEGER NOT NULL DEFAULT 0,               --@ Location of the request origin. Can be 0 if origin is not near any location and is only tagged by a link. (foreign key to the Location table)
  "destination_location" INTEGER NOT NULL DEFAULT 0,          --@ Location of request destination. Can be 0 if destination is not near any location and is only tagged by a link. (foreign key to the Location table)
  "origin_link" INTEGER NOT NULL DEFAULT 0,                   --@ Link of the request origin. Cannot be NULL/0. (foreign key to the Link table)
  "destination_link" INTEGER NOT NULL DEFAULT 0,              --@ Link of the request destination. Cannot be NULL/0. (foreign key to the Link table)
  "adjusted_origin_location" INTEGER NOT NULL DEFAULT 0,      --@ Certain assignment strategies may alert requests to walk/move to a nearby location from the origin and the new origin Location ID is stored in this column.
  "adjusted_destination_location" INTEGER NOT NULL DEFAULT 0, --@ Certain assignment strategies may alert requests to walk/move from a nearby location to the destination and the new destination Location ID is stored in this column.
  "adjusted_origin_link" INTEGER NOT NULL DEFAULT 0,          --@ Certain assignment strategies may alert requests to walk/move to a nearby link from the origin and the new origin Link ID is stored in this column.
  "adjusted_destination_link" INTEGER NOT NULL DEFAULT 0,     --@ Certain assignment strategies may alert requests to walk/move from a nearby link to the destination and the new destination Link ID is stored in this column.
  "service_mode" INTEGER NOT NULL DEFAULT 0,                  --@ The shared mobility mode requested that is consistent with the entries in the Mode table. Options now include TNC, On-Demand Delivery, or Relocation for E-Scooters. 
  "origin_zone" INTEGER NOT NULL DEFAULT 0,                   --@ The origin Zone of the request (foreign key to the Zone table)
  "destination_zone" INTEGER NOT NULL DEFAULT 0,              --@ The destination Zone of the request (foreign key to the Zone table)
  "pooled_service" INTEGER NOT NULL DEFAULT 0,                --@ boolean flag - did the request allow pooling? (Not a guarantee that the ride was actually pooled)
  "party_size" INTEGER NOT NULL DEFAULT 0,                    --@ Number of travelers/objects bundled within this request
  "estimated_od_travel_time" REAL NULL DEFAULT 0,             --@ Estimated travel time obtained from the skim (units: seconds)
  "person" INTEGER NULL,                                      --@ Person ID that requested the trip, if it is a TNC mode request. NULL if it is an on-demand delivery or e-scooter request. (foreign key to the Person table)
  "assigned_vehicle" INTEGER NULL,                            --@ Shared mobility vehicle assigned to serve the request. Unassigned request if NULL. (foreign key to the Vehicle table)
  "number_of_attempts" INTEGER NOT NULL DEFAULT 0,            --@ Number of attempts made in finding a candidate vehicle for assigning to the request. Each attempt is made every 30 seconds until the TNC_MAX_ASSIGNMENT_TIME threshold is hit.
  "fare" REAL NULL DEFAULT 0.0,                               --@ Fare collected in serving the request (units: $USD)
  "distance" REAL NULL DEFAULT 0.0,                           --@ Distance traveled in serving the request (units: miles)
  "discount" REAL NULL DEFAULT 0.0,                           --@ Discount provided when trip is assigned to a vehicle by operator (units: $USD)
  "service_type" INTEGER NULL DEFAULT 0,                      --@ Service type requested based on the available options defined in @@ TNC_Service_Types @@
  "seating_type" INTEGER NULL DEFAULT 0,                      --@ Number of minimum seats requested for the vehicle, regardless of how many seats will be occupied by request.

  CONSTRAINT "person_fk"
    FOREIGN KEY ("person")
    REFERENCES "Person" ("person")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "assigned_vehicle_fk"
    FOREIGN KEY ("assigned_vehicle")
    REFERENCES "Vehicle" ("vehicle_id")
    DEFERRABLE INITIALLY DEFERRED);
