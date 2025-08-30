-- Copyright (c) 2025, UChicago Argonne, LLC
-- BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
create TABLE IF NOT EXISTS "Land_Use" (
    "land_use"              TEXT    NOT NULL PRIMARY KEY,
    "is_home"               INTEGER NOT NULL DEFAULT 0,
    "is_work"               INTEGER NOT NULL DEFAULT 0,
    "is_school"               INTEGER NOT NULL DEFAULT 0,
    "is_discretionary"      INTEGER NOT NULL DEFAULT 0,
    "notes"                 TEXT
);

create INDEX IF NOT EXISTS "idx_land_use" ON "Land_Use" ("land_use");

INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RESIDENTIAL-SINGLE',1,0,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RESIDENTIAL-MULTI',1,0,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('MAJ_SHOP',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('MIX',1,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('BUSINESS',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('CULTURE',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('HOTEL',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('MEDICAL',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('EDUCATION',0,1,1,0,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('HIGHER_EDUCATION',0,1,1,0,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('CIVIC',1,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('SPECIAL_GEN',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('INDUSTRY',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('MANUFACTURING',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('DISTRIBUTION',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('INTERMODAL',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RECREATION',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RES',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('ALL',1,1,1,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('AGRICULTURE',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RESTAURANT',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('RETAIL',0,1,0,1,'Inserted by the network upgrader');
INSERT OR IGNORE INTO land_use(land_use, is_home, is_work,is_school,is_discretionary,notes) VALUES('SERVICES',0,1,0,1,'Inserted by the network upgrader');

insert into Land_Use select distinct(land_use), 1 is_home, 1 is_work, 1 is_school, 1 is_discretionary, 'Inserted by the network upgrader' notes from Location where land_use not in (select land_use from Land_use);

delete from Land_use where land_use not in (select DISTINCT(land_use) from location);