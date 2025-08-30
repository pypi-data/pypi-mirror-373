-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ Table that records all persons synthesized in simulation and all associated attributes.
--@ Records are either a result of population synthesis or are being moved from one Demand to the next 
--@ when reading population from database.

CREATE TABLE "Person" (
  "person" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,            --@ The unique identifier of this individual
  "id" INTEGER NOT NULL DEFAULT 0,                                --@ 0-based index (0 through n-1 persons) for individual within their specific household 
  "school_location_id" INTEGER NOT NULL DEFAULT 0,                --@ Location identifier of the educational institutions (foreign key to the Location table)
  "work_location_id" INTEGER NOT NULL DEFAULT 0,                  --@ Location identifier of the work locations (foreign key to the Location table)
  "age" INTEGER NOT NULL DEFAULT 0,                               --@ Age of the individual (units: years)
  "worker_class" INTEGER NOT NULL DEFAULT 0,                      --@ Worker class of the individual. !CLASS_OF_WORKER!
  "education" INTEGER NOT NULL DEFAULT 0,                         --@ Educational attainment of the individual. !EDUCATION_LEVEL!
  "industry" INTEGER NOT NULL DEFAULT 0,                          --@ Employment industry where individual works. !EMPLOYMENT_INDUSTRY!
  "employment" INTEGER NOT NULL DEFAULT 0,                        --@ Employment status of person as defined in the ACS field ESR (based on the survey week). !EMPLOYMENT_STATUS!
  "gender" INTEGER NOT NULL DEFAULT 0,                            --@ Gender of the individual. !GENDER!
  "income" INTEGER NOT NULL DEFAULT 0,                            --@ Annual personal income of the individual (units: $USD)
  "journey_to_work_arrival_time" INTEGER NOT NULL DEFAULT 0,      --@ Usual arrival time of an individual's work trip (units: seconds)
  "journey_to_work_mode" INTEGER NOT NULL DEFAULT 0,              --@ Usual travel mode of an individual's work trip
  "journey_to_work_travel_time" INTEGER NOT NULL DEFAULT 0,       --@ Usual commute time of an individual's work trip (units: seconds)
  "journey_to_work_vehicle_occupancy" INTEGER NOT NULL DEFAULT 0, --@ Usual number of people present in the car an individual's work trip
  "marital_status" INTEGER NOT NULL DEFAULT 0,                    --@ Marital status of the individual. !MARITAL_STATUS!
  "race" INTEGER NOT NULL DEFAULT 0,                              --@ Race of the individual. !RACE!
  "school_enrollment" INTEGER NOT NULL DEFAULT 0,                 --@ If a student, type of school the individual is enrolled in. !SCHOOL_ENROLLMENT!
  "school_grade_level" INTEGER NOT NULL DEFAULT 0,                --@ If a student, individuals' school grade level. !SCHOOL_GRADE_LEVEL!
  "work_hours" INTEGER NOT NULL DEFAULT 0,                        --@ Number of hours individual works
  "telecommute_level" INTEGER NOT NULL DEFAULT 0,                 --@ Individual's level of telecommuting. !TELECOMMUTE_FREQUENCY!
  "transit_pass" INTEGER NOT NULL,                                --@ boolean flag - does the individual hold a transit pass?
  "household" INTEGER NOT NULL,                                   --@ The household to which this individual belongs (foreign key to Household table)
  "time_in_job" REAL NOT NULL DEFAULT 0,                          --@ Time in the job (units: years)
  "disability" INTEGER NOT NULL DEFAULT 2,                        --@ Type of disability as referenced by ACS. !DISABILITY_STATUS!
  "escooter_use_level" INTEGER NOT NULL DEFAULT 0,                --@ Individual's level of escooter usage. !ESCOOTER_FREQUENCY!
  "is_long_term_chooser" INTEGER NOT NULL DEFAULT 1,              --@ Boolean flag denoting whether the individual should be making LT decisions (work/school location choice)

  CONSTRAINT "household_fk"
    FOREIGN KEY ("household")
    REFERENCES "Household" ("household")
    DEFERRABLE INITIALLY DEFERRED)