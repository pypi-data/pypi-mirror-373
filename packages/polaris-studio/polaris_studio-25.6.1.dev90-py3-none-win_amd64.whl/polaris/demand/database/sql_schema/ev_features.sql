-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ EV Features table brings together information related
--@ to the EV powertrain. EV-related features are especially
--@ required in the ML-based consumption model in POLARIS
--@ to update battery level during simulation.
--@
--@ It is a static table and is not updated by POLARIS.

CREATE TABLE "EV_Features" (
  "ev_features_id" INTEGER NOT NULL PRIMARY KEY, --@ unique identifier for this set of EV feature
  "veh_class" INTEGER NULL,                      --@ References vehicle class
  "veh_pwt" INTEGER NULL,                        --@ References vehicle powertrain
  "veh_fuel" INTEGER NULL,                       --@ References vehicle fuel type
  "veh_autolvl" INTEGER NULL,                    --@ References vehicle automation level
  "veh_vintagelvl" INTEGER NULL,                 --@ References vehicle vintage level
  "veh_mass" REAL NULL DEFAULT 0,                --@ The mass of the vehicle  (units: kg)
  "veh_whl_roll1" REAL NULL DEFAULT 0,
  "veh_chas_fa" REAL NULL DEFAULT 0,
  "veh_chas_cd" REAL NULL DEFAULT 0,
  "veh_accelec_pwr" REAL NULL DEFAULT 0,
  "veh_fd_ratio" REAL NULL DEFAULT 0,
  "veh_eng_pwrmax" REAL NULL DEFAULT 0,
  "veh_eng_effmax" REAL NULL DEFAULT 0,
  "veh_mot_pwrmax" REAL NULL DEFAULT 0,
  "veh_mot_effmax" REAL NULL DEFAULT 0,
  "veh_mot2_pwrmax" REAL NULL DEFAULT 0,
  "veh_mot2_effmax" REAL NULL DEFAULT 0,
  "veh_ess_pwrmax" REAL NULL DEFAULT 0,
  "veh_ess_energy" REAL NULL DEFAULT 0,          --@ Maximum battery level (units: Wh)
  "veh_gb_nb" REAL NULL DEFAULT 0,
  "veh_gb_effmax" REAL NULL DEFAULT 0,
  CONSTRAINT "veh_class_fk"
    FOREIGN KEY ("veh_class")
    REFERENCES "Vehicle_Class" ("class_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "veh_pwt_fk"
    FOREIGN KEY ("veh_pwt")
    REFERENCES "Powertrain_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "veh_fuel_fk"
    FOREIGN KEY ("veh_fuel")
    REFERENCES "Fuel_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "veh_autolvl_fk"
    FOREIGN KEY ("veh_autolvl")
    REFERENCES "Automation_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED,
  CONSTRAINT "veh_vintagelvl_fk"
    FOREIGN KEY ("veh_vintagelvl")
    REFERENCES "Vintage_Type" ("type_id")
    DEFERRABLE INITIALLY DEFERRED)