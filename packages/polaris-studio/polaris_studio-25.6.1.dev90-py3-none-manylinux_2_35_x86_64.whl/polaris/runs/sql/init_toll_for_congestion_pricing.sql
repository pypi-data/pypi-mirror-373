-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
DELETE FROM Toll_Pricing;
INSERT INTO Toll_Pricing SELECT link, 0, 0, 86400, 0.0, 0.0, 0.0 FROM Link WHERE lanes_ab > 0 AND type in ('EXTERNAL','FREEWAY', 'RAMP','MINOR','MAJOR','COLLECTOR','LOCAL','EXPRESSWAY','OTHER');
INSERT INTO Toll_Pricing SELECT link, 1, 0, 86400, 0.0, 0.0, 0.0 FROM Link WHERE lanes_ba > 0 AND type in ('EXTERNAL','FREEWAY', 'RAMP','MINOR','MAJOR','COLLECTOR','LOCAL','EXPRESSWAY','OTHER');