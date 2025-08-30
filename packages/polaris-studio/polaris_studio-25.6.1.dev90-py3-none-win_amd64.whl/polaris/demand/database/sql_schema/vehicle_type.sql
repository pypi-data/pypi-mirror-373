-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ The Vehicle_Type table is a join table that pulls together many attributes of a vehicle 
--@ from associated lookup tables.
--@

CREATE TABLE "Vehicle_Type" (
  "type_id" INTEGER NOT NULL PRIMARY KEY,               --@ Unique identifier of this type
  "vehicle_class" INTEGER NULL,                         --@ The corresponding vehicle class (foreign key to the Vehicle_Class table)
  "connectivity_type" INTEGER NULL,                     --@ The corresponding connectivity type (foreign key to the Connectivity_Type table)
  "powertrain_type" INTEGER NULL,                       --@ The corresponding powertrain type (foreign key to the Powertrain_Type table) !Powertrain_Type_Keys!
  "automation_type" INTEGER NULL,                       --@ The corresponding automation type (foreign key to the Automation_Type table) !Automation_Type_Keys!
  "fuel_type" INTEGER NULL,                             --@ The corresponding fuel type (foreign key to the Fuel_Type table) !Fuel_Type_Keys!
  "vintage_type" INTEGER NULL,                          --@ The corresponding vintage (age) type  (foreign key to the Vintage_Type table) !Vintage_Type_Keys!
  "ev_features_id" INTEGER NULL,                        --@ The corresponding set of EV features (foreign key to the EV_Features table)
  "operating_cost_per_mile" REAL NOT NULL DEFAULT 0.18, --@ The cost to operate this vehicle for 1 mile (units: $USD/mi)

  CONSTRAINT "vehicle_class_fk"
    FOREIGN KEY ("vehicle_class")
    REFERENCES "Vehicle_Class" ("class_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "connectivity_type_fk"
    FOREIGN KEY ("connectivity_type")
    REFERENCES "Connectivity_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "powertrain_type_fk"
    FOREIGN KEY ("powertrain_type")
    REFERENCES "Powertrain_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "automation_type_fk"
    FOREIGN KEY ("automation_type")
    REFERENCES "Automation_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "fuel_type_fk"
    FOREIGN KEY ("fuel_type")
    REFERENCES "Fuel_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "vintage_type_fk"
    FOREIGN KEY ("vintage_type")
    REFERENCES "Vintage_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "ev_features_id_fk"
    FOREIGN KEY ("ev_features_id")
    REFERENCES "EV_Features" ("ev_features_id")
    DEFERRABLE INITIALLY DEFERRED)