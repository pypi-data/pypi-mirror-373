-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
--@ List of rail operators by railports in the model
--@

CREATE TABLE Rail_Operator_Railports (
    "rail_operator" INTEGER NOT NULL DEFAULT 0,  --@ The unique identifier of the rail operator as in the Rail_Operator table
    "railport"      INTEGER NOT NULL DEFAULT 0,  --@ The unique identifier of the railport as in the Railport table

    CONSTRAINT railport_fk FOREIGN KEY (railport)
    REFERENCES Railport (railport) DEFERRABLE INITIALLY DEFERRED

    CONSTRAINT rail_operator_rp_fk FOREIGN KEY (rail_operator)
    REFERENCES Rail_Operator (rail_operator) DEFERRABLE INITIALLY DEFERRED
);
