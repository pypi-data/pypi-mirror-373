# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
import logging
import pandas as pd

from .target_categories import ActivityType, PersonType, ModeType, DeparturePeriod
from .utils import military_time_to_minutes
from .nhts import NHTSDataset


class NHTS17Dataset(NHTSDataset):

    @classmethod
    def download(cls, csv_zip_url="https://nhts.ornl.gov/media/2016/download/csv.zip", unzip_dir=None):
        return super().download(csv_zip_url, unzip_dir)

    def get_activity_table(self, activity_mapping):
        p_df = _add_person_type(self.per_df)
        p_df = p_df[p_df.PERTYPE != PersonType.IGNORE]

        t_df = self.trip_df.copy()
        t_df["ACTTYPE"] = t_df["WHYTO"].map(activity_mapping)
        t_df = t_df[t_df.ACTTYPE != ActivityType.IGNORE]

        act_df = t_df.merge(p_df[["HOUSEID", "PERSONID", "PERTYPE"]])

        # Assert all work activities are work for full-time workers
        act_df.loc[
            (act_df.PERTYPE == PersonType.FULLTIME_WORKER) & (act_df.ACTTYPE == ActivityType.PART_WORK), "ACTTYPE"
        ] = ActivityType.WORK

        # Assert all work activities are part-time work for part-time workers
        act_df.loc[
            (act_df.PERTYPE == PersonType.PARTTIME_WORKER) & (act_df.ACTTYPE == ActivityType.WORK), "ACTTYPE"
        ] = ActivityType.PART_WORK

        return act_df

    def generate_activity_generation_targets(self, activity_mapping):

        act_df = self.get_activity_table(activity_mapping)
        act_df = _filter_to_weekday(act_df)

        p_df = _add_person_type(self.per_df)
        p_df = _filter_to_weekday(p_df)
        p_df = p_df[p_df.PERTYPE != PersonType.IGNORE]

        # Select only trips less than 75 miles
        act_df = act_df[act_df["TRPMILES"] < 75]

        actgen_df = act_df.groupby(["PERTYPE", "ACTTYPE"], sort=False)[["WTTRDFIN"]].sum().reset_index()
        person_wts = p_df.groupby("PERTYPE", sort=False)[["WTPERFIN"]].sum().reset_index()
        actgen_df = actgen_df.merge(person_wts, on="PERTYPE", how="left").fillna(0)
        actgen_df["target"] = actgen_df["WTTRDFIN"] / actgen_df["WTPERFIN"] / 365
        actgen_df["target"] = actgen_df["target"].fillna(0)

        target_act_names = {
            ActivityType.EAT_OUT: "EAT_OUT",
            ActivityType.ERRANDS: "ERRANDS",
            ActivityType.HEALTHCARE: "HEALTHCARE",
            ActivityType.LEISURE: "LEISURE",
            ActivityType.PERSONAL: "PERSONAL_BUSINESS",
            ActivityType.RELIGIOUS_CIVIC: "RELIGIOUS_OR_CIVIC",
            ActivityType.SERVICE: "SERVICE_VEHICLE",
            ActivityType.SHOP_MAJOR: "MAJOR_SHOPPING",
            ActivityType.SHOP_OTHER: "OTHER_SHOPPING",
            ActivityType.SOCIAL: "SOCIAL",
            ActivityType.WORK: "WORK",
            ActivityType.PART_WORK: "PART_TIME_WORK",
            ActivityType.WORK_AT_HOME: "WORK_HOME",
            ActivityType.SCHOOL: "SCHOOL",
            ActivityType.PICKUP_DROPOFF: "PICKUP",
            ActivityType.HOME: "HOME",
        }
        # TODO Consider adding OTHER

        index = pd.MultiIndex.from_product(
            [[p for p in PersonType if p != PersonType.IGNORE], target_act_names.keys()], names=["PERTYPE", "ACTTYPE"]
        )
        actgen_df = actgen_df.set_index(["PERTYPE", "ACTTYPE"]).reindex(index, fill_value=0)

        actgen_df = actgen_df.reset_index()
        actgen_df["PERTYPE"] = actgen_df["PERTYPE"].map(lambda x: x.value)
        actgen_df["ACTTYPE"] = actgen_df["ACTTYPE"].map(lambda x: target_act_names[x])

        actgen_df = actgen_df.rename(
            columns={"PERTYPE": "pertype", "ACTTYPE": "acttype", "WTTRDFIN": "trip_weight", "WTPERFIN": "person_weight"}
        )

        return actgen_df[["pertype", "acttype", "target", "trip_weight"]].copy()

    def generate_destination_choice_targets(self, activity_mapping):
        act_df = self.get_activity_table(activity_mapping)
        act_df = _filter_to_weekday(act_df)
        act_df = _add_trip_time_min(act_df)

        # Selecting only non-long-distance trips with valid trip distances
        act_df = act_df[(act_df["TRPMILES"] < 75) & (act_df["TRPMILES"] >= 0)]

        # Select only trips less than 4 hours (ignore outliers)
        act_df = act_df[act_df["TRIPTIME"] < 4 * 60]

        act_df["WTTRIPTIME"] = act_df["TRIPTIME"] * act_df["WTTRDFIN"]
        act_df["WTTRAVDIST_KM"] = act_df["TRPMILES"] * 1.609344 * act_df["WTTRDFIN"]

        dest_df = act_df.groupby(["ACTTYPE"], sort=False)[["WTTRIPTIME", "WTTRAVDIST_KM", "WTTRDFIN"]].sum()
        dest_df["travel_time"] = dest_df["WTTRIPTIME"] / dest_df["WTTRDFIN"]
        dest_df["distance"] = dest_df["WTTRAVDIST_KM"] / dest_df["WTTRDFIN"]
        dest_df = dest_df.drop(columns=["WTTRIPTIME", "WTTRAVDIST_KM"])

        target_act_names = {
            ActivityType.EAT_OUT: "EAT OUT",
            ActivityType.ERRANDS: "ERRANDS",
            ActivityType.HEALTHCARE: "HEALTHCARE",
            ActivityType.HOME: "HOME",
            ActivityType.LEISURE: "LEISURE",
            ActivityType.PART_WORK: "PART_WORK",
            ActivityType.PERSONAL: "PERSONAL",
            ActivityType.PICKUP_DROPOFF: "PICKUP-DROPOFF",
            ActivityType.RELIGIOUS_CIVIC: "RELIGIOUS-CIVIC",
            ActivityType.SCHOOL: "SCHOOL",
            ActivityType.SERVICE: "SERVICE",
            ActivityType.SHOP_MAJOR: "SHOP-MAJOR",
            ActivityType.SHOP_OTHER: "SHOP-OTHER",
            ActivityType.SOCIAL: "SOCIAL",
            ActivityType.WORK: "WORK",
            ActivityType.WORK_AT_HOME: "WORK AT HOME",
            ActivityType.OTHER: "OTHER",
        }
        index = pd.Index(target_act_names.keys(), name="ACTIVITY_TYPE")
        dest_df = dest_df.reindex(index, fill_value=0)

        # Work trip distances are not calibrated the same as other activity trips
        # For work trips, we need the straight-line distance from home to work weighted by person

        p_df = self.per_df.copy()
        p_df = _filter_to_weekday(p_df)

        # Using network distances to filter out long distance trips
        p_df = p_df[(p_df.DISTTOWK17 > 0) & (p_df.DISTTOWK17 < 75)]

        work_distance_target = (p_df.GCDWORK * p_df.WTPERFIN).sum() / p_df.WTPERFIN.sum()
        work_distance_target = work_distance_target * 1.609344  # Convert miles to km

        # Since POLARIS currently uses the same measure for part-time and
        # full-time work distance calibration, we set them the same here
        dest_df.loc[ActivityType.WORK, "distance"] = work_distance_target
        dest_df.loc[ActivityType.PART_WORK, "distance"] = work_distance_target
        dest_df = dest_df.rename(columns={"WTTRDFIN": "trip_weight"})

        dest_df.index = dest_df.index.map(lambda x: target_act_names[x])

        return dest_df.reset_index()[["ACTIVITY_TYPE", "travel_time", "distance"]].copy()

    def generate_departure_time_targets(self, activity_mapping):
        act_df = self.get_activity_table(activity_mapping)
        act_df = _filter_to_weekday(act_df)
        act_df = _add_departure_period(act_df)

        # Selecting only non-long-distance trips
        act_df = act_df[(act_df["TRPMILES"] < 75)]

        depart_df = act_df.groupby(["DEPART_PERIOD", "ACTTYPE"], sort=False)[["WTTRDFIN"]].sum().reset_index()
        depart_df = depart_df.pivot(index="DEPART_PERIOD", columns="ACTTYPE", values="WTTRDFIN").fillna(0)

        index = pd.Index([e for e in DeparturePeriod if e != DeparturePeriod.IGNORE], name="PERIOD")
        target_act_names = {
            ActivityType.EAT_OUT: "EAT_OUT",
            ActivityType.ERRANDS: "ERRANDS",
            ActivityType.HEALTHCARE: "HEALTHCARE",
            ActivityType.LEISURE: "LEISURE",
            ActivityType.PERSONAL: "PERSONAL",
            ActivityType.RELIGIOUS_CIVIC: "RELIGIOUS",
            ActivityType.SERVICE: "SERVICE",
            ActivityType.SHOP_MAJOR: "SHOP_MAJOR",
            ActivityType.SHOP_OTHER: "SHOP_OTHER",
            ActivityType.SOCIAL: "SOCIAL",
            ActivityType.WORK: "WORK",
            ActivityType.PART_WORK: "WORK_PART",
            ActivityType.WORK_AT_HOME: "WORK_HOME",
            ActivityType.SCHOOL: "SCHOOL",
            ActivityType.PICKUP_DROPOFF: "PICKUP",
            ActivityType.HOME: "HOME",
        }
        col_index = pd.Index(target_act_names.keys())
        depart_df = depart_df.reindex(index=index, columns=col_index, fill_value=0)

        depart_df.columns = depart_df.columns.map(lambda x: target_act_names[x] + "_trip_weight")
        depart_df.index = depart_df.index.map(lambda x: x.value)
        depart_df["TOTAL_trip_weight"] = depart_df.sum(axis=1)

        depart_df[[c.replace("_trip_weight", "") for c in depart_df.columns]] = (
            depart_df.div(depart_df.sum(axis=0), axis=1).fillna(0).values
        )

        return depart_df.reset_index()[["PERIOD"] + [target_act_names[c] for c in col_index] + ["TOTAL"]].copy()

    def generate_mode_choice_targets(self):

        p_df = _add_person_type(self.per_df)
        p_df = _filter_to_weekday(p_df)
        p_df = p_df.loc[p_df.AGE >= 18, ["HOUSEID", "PERSONID"]]

        t_df = self.trip_df.copy()
        t_df = _filter_to_weekday(t_df)

        # Selecting only adult trips
        t_df = t_df.merge(p_df, on=["HOUSEID", "PERSONID"], how="inner")

        # Renaming trip purpose types
        t_df["TYPE"] = t_df.TRIPPURP
        t_df.loc[t_df.TYPE.isin(["HBSHOP", "HBSOCREC"]), "TYPE"] = "HBO"

        # Selecting only non-long-distance trips
        t_df = t_df[t_df["TRPMILES"] < 75].copy()

        # Assigning mode types
        t_df["MODE"] = ModeType.IGNORE
        t_df.loc[t_df.TRPTRANS == 1, "MODE"] = ModeType.WALK
        t_df.loc[t_df.TRPTRANS == 2, "MODE"] = ModeType.BIKE
        t_df.loc[
            t_df.TRPTRANS.isin([3, 4, 5, 6, 8, 18]), "MODE"  # Car  # SUV  # Van  # Pickup  # Motorcycle  # Rental car
        ] = ModeType.AUTO
        t_df.loc[t_df.TRPTRANS == 17, "MODE"] = ModeType.TAXI

        t_df.loc[(t_df.MODE == ModeType.AUTO) & (t_df.WHODROVE != t_df.PERSONID), "MODE"] = ModeType.AUTO_PASS

        # Creating targets
        mode_df = t_df.groupby(["TYPE", "MODE"], sort=False)[["WTTRDFIN"]].sum()
        index = pd.MultiIndex.from_product(
            [["HBW", "HBO", "NHB"], [m for m in ModeType if m != ModeType.IGNORE]], names=["TYPE", "MODE"]
        )
        mode_df = mode_df.reindex(index, fill_value=0).reset_index()
        mode_df.MODE = mode_df.MODE.map(lambda x: x.value)
        mode_df = mode_df.pivot(index="TYPE", columns="MODE", values="WTTRDFIN").fillna(0)
        mode_df.loc["total"] = mode_df.sum()

        cols = mode_df.columns
        mode_df.columns = [c + "_trip_weight" for c in cols]
        mode_df[cols] = mode_df.div(mode_df.sum(axis=1), axis=0).fillna(0).values

        return mode_df[list(cols)].reset_index()


def _add_person_type(per_df):
    per_df = per_df.copy()

    per_df["AGE"] = per_df.R_AGE
    # Fill missing values of age with imputed age
    per_df.loc[per_df.AGE < 0, "AGE"] = per_df.R_AGE_IMP

    per_df["PERTYPE"] = PersonType.IGNORE

    per_df.loc[
        (
            (per_df.WKFTPT == 1) | ((per_df.WORKER == 1) & ~per_df.WKFTPT.isin([1, 2]))  # Full-time worker
        )  # Unknown work duration (refused to answer or WFH) but is worker
        & (per_df.PERTYPE == PersonType.IGNORE),
        "PERTYPE",
    ] = PersonType.FULLTIME_WORKER
    per_df.loc[(per_df.WKFTPT == 2) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = PersonType.PARTTIME_WORKER

    per_df.loc[(per_df.AGE >= 18) & (per_df.PRMACT == 5) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = (
        PersonType.ADULT_STUDENT
    )
    per_df.loc[(per_df.AGE >= 65) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = PersonType.SENIOR

    per_df.loc[(per_df.AGE < 5) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = PersonType.PRESCHOOL
    # The public NHTS 2017 dataset does not include any children under 5 years old
    # So there will be no rows with PERTYPE == PersonType.PRESCHOOL
    per_df.loc[(per_df.AGE < 16) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = PersonType.SCHOOL_CHILD
    per_df.loc[(per_df.AGE >= 16) & (per_df.AGE <= 18) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = (
        PersonType.STUDENT_DRIVER
    )
    per_df.loc[(per_df.WORKER == 2) & (per_df.PERTYPE == PersonType.IGNORE), "PERTYPE"] = PersonType.NONWORKER

    if len(per_df[per_df.PERTYPE == PersonType.IGNORE]) > 0:
        # Log the number of persons with unknown PERTYPE
        logging.warning(f"Unknown PERTYPE for {len(per_df[per_df.PERTYPE == PersonType.IGNORE])} persons.")

    return per_df


def _add_departure_period(trip_df):
    trip_df = trip_df.copy()

    # Create a new column for departure period
    trip_df["DEPART_PERIOD"] = DeparturePeriod.IGNORE

    # Define the departure periods based on the departure time
    trip_df.loc[(trip_df["STRTTIME"] >= 0) & (trip_df["STRTTIME"] < 600), "DEPART_PERIOD"] = DeparturePeriod.NIGHT
    trip_df.loc[(trip_df["STRTTIME"] >= 600) & (trip_df["STRTTIME"] < 900), "DEPART_PERIOD"] = DeparturePeriod.AMPEAK
    trip_df.loc[(trip_df["STRTTIME"] >= 900) & (trip_df["STRTTIME"] < 1200), "DEPART_PERIOD"] = (
        DeparturePeriod.AMOFFPEAK
    )
    trip_df.loc[(trip_df["STRTTIME"] >= 1200) & (trip_df["STRTTIME"] < 1600), "DEPART_PERIOD"] = (
        DeparturePeriod.PMOFFPEAK
    )
    trip_df.loc[(trip_df["STRTTIME"] >= 1600) & (trip_df["STRTTIME"] < 1900), "DEPART_PERIOD"] = DeparturePeriod.PMPEAK
    trip_df.loc[(trip_df["STRTTIME"] >= 1900) & (trip_df["STRTTIME"] <= 2359), "DEPART_PERIOD"] = (
        DeparturePeriod.EVENING
    )

    if len(trip_df[trip_df["DEPART_PERIOD"] == DeparturePeriod.IGNORE]) > 0:
        logging.warning(
            f"DEPART_PERIOD could not be identified for {len(trip_df[trip_df['DEPART_PERIOD'] == DeparturePeriod.IGNORE])} trips."
        )
    return trip_df


def _add_trip_time_min(trip_df):
    trip_df = trip_df.copy()
    strtime = trip_df["STRTTIME"].apply(military_time_to_minutes)
    endtime = trip_df["ENDTIME"].apply(military_time_to_minutes)
    endtime = endtime.where(endtime >= strtime, endtime + 24 * 60)  # Adjust for next day
    trip_df["TRIPTIME"] = endtime - strtime
    return trip_df


def _filter_to_weekday(df):
    return df[df.TRAVDAY.isin(range(2, 7))].copy()  # Monday to Friday
