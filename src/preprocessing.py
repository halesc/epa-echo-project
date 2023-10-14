"""
This script reads in the raw data from the lib/raw directory, processes it, and writes it to the lib/processed directory. The processed data is then used by the application to train the model. The processed data is also used by the application to make predictions.
"""

import os
import gc
import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Access the variables using os.environ
path_variable = os.environ.get("DEV_PATH")


# TODO: If adding state databases, clearly clean and join them.
# TODO: If above, normalize penalty by facility size.
# TODO: Explore and possibly add compliance_action_cost to penalty.

DT = datetime.datetime.now()
ECHO_LOC = f"{path_variable}/lib/raw/"
READ_PATH = os.path.join(os.path.dirname(os.path.abspath("")[:-3]), ECHO_LOC)
WRITE_PATH = READ_PATH[:-len(ECHO_LOC)] + f"{path_variable}/lib/processed/"

try:
    os.mkdir(WRITE_PATH)
except FileExistsError:
    pass

print("Starting Preprocessing...", flush=True)
# Read in data.
facilities = pd.read_csv(
    READ_PATH + "ICIS-AIR_FACILITIES.csv",
    usecols=["REGISTRY_ID", "PGM_SYS_ID", "AIR_POLLUTANT_CLASS_CODE", "AIR_POLLUTANT_CLASS_DESC"])
programs = pd.read_csv(
    READ_PATH + "ICIS-AIR_PROGRAMS.csv",
    usecols=["PGM_SYS_ID", "PROGRAM_CODE", "PROGRAM_DESC"])

facilities = facilities.merge(programs, on="PGM_SYS_ID", how="left")

# Remove smaller facilities.
facilities = facilities[facilities["PROGRAM_CODE"] != "CAANFRP"]

# Remove facilities with no registry_id.
facilities = facilities[facilities["REGISTRY_ID"].notna()]

# Rename columns to lower case.
facilities = facilities.rename(
    columns={"REGISTRY_ID": "registry_id", "PGM_SYS_ID": "pgm_sys_id", "PROGRAM_CODE": "program_code", "PROGRAM_DESC": "program_desc", "AIR_POLLUTANT_CLASS_CODE": "air_pollutant_class_code", "AIR_POLLUTANT_CLASS_DESC": "air_pollutant_class_desc"})

# Create a new dataframe with one row per facility .
# First one hot encode program_code, but there's an issue with high cardinality.

# Reduce the dimensionality of program_code by only keeping the top 5 based on value_counts and placing the rest in other. We'll then need to one hot encode them as a given facility can have multiple program_codes.
top_programs = facilities["program_code"].value_counts().head(5).index
facilities["program_code"] = facilities["program_code"].where(facilities["program_code"].isin(top_programs), "OTHER")

facilities = pd.concat([facilities, pd.get_dummies(facilities["program_code"])], axis=1)

# Create a new dataframe with one row per facility aggregating by registry_id and keeping registry_id, air_pollutant_class_code, and the one hot encoded program_code columns.
facilities = facilities.groupby("registry_id").agg(
    {"air_pollutant_class_code": "first", "CAASIP": "sum", "CAAMACT": "sum", "CAANSPS": "sum", "CAATVP": "sum", "CAAGACTM": "sum", "OTHER": "sum"}).reset_index()

# Rename columns
facilities = facilities.rename(
    columns={"CAASIP": "caasip", "CAAMACT": "caamact", "CAANSPS": "caansps", "CAATVP": "caatvp", "CAAGACTM": "caagactm", "OTHER": "other"})

# Write to csv.
facilities.to_csv(WRITE_PATH + "icis-air_facilities.csv", index=False)

# Delete dataframes to free up memory.
air = facilities

del facilities
del programs
gc.collect()

print("Completed: air facilities", flush=True)

# Read in data.
facilities = pd.read_csv(
    READ_PATH + "ICIS_FACILITIES.csv",
    usecols=["NPDES_ID", "FACILITY_UIN"]).rename(columns={"FACILITY_UIN": "REGISTRY_ID"})
programs = pd.read_csv(
    READ_PATH + "ICIS_PERMITS.csv",
    usecols=["EXTERNAL_PERMIT_NMBR", "MAJOR_MINOR_STATUS_FLAG", "RAD_WBD_HUC12S"]).rename(columns={"EXTERNAL_PERMIT_NMBR": "NPDES_ID"})

# Merge the two dataframes.
facilities = facilities.merge(programs, on="NPDES_ID", how="left")

# Remove smaller facilities.
facilities = facilities[facilities["MAJOR_MINOR_STATUS_FLAG"] == "M"]

# Remove facilities with no registry_id and drop major_minor_status_flag.
facilities = facilities[facilities["REGISTRY_ID"].notna()].drop(columns=["MAJOR_MINOR_STATUS_FLAG"])

# Rename columns
facilities = facilities.rename(
    columns={"REGISTRY_ID": "registry_id", "RAD_WBD_HUC12S": "rad_wbd_huc12s"})

# RAD_WBD_HUC12S gets to the subwatershed level, which is too granular for these purposes. Aggregate to the region watershed level by taking the first 2 digits of the string.
facilities["rad_wbd_huc12s"] = facilities["rad_wbd_huc12s"].str[:2]

# Drop duplicates and null values.
facilities = facilities.drop_duplicates().dropna()

# Group by registry_id and get the first instance of a region watershed. There are roughly 151 facilities with multiple region watersheds, but this is a small enough number to ignore for now. TODO: revisit this.
facilities = facilities.groupby("registry_id").agg(
    {"rad_wbd_huc12s": lambda x: x.value_counts().index[0]}).reset_index()

# Write to csv.
facilities.to_csv(WRITE_PATH + "icis-npdes_facilities.csv", index=False)

# Delete dataframes to free up memory.
npdes = facilities

del facilities
del programs
gc.collect()

print("Completed: npdes facilities", flush=True)

# Read in the data.
facilities = pd.read_csv(
    READ_PATH + "FRS_FACILITIES.csv",
    usecols=["REGISTRY_ID", "FAC_STATE", "FAC_COUNTY", "FAC_EPA_REGION", "LATITUDE_MEASURE", "LONGITUDE_MEASURE"])
demographics = pd.read_csv(
    READ_PATH + "ECHO_DEMOGRAPHICS.csv",
    usecols=["REGISTRY_ID", "RADIUS_OF_AREA", "LOWINCOME", "ACS_POPULATION", "WHITE_POPULATION", "AFRICAN_AMERICAN_POPULATION", "HISPANIC_ORIGIN_POPULATION", "ASIAN_PACIFIC_ISLANDER_POP", "AMERICAN_INDIAN_POPULATION"])

# Merge the two dataframes.
facilities = facilities.merge(demographics, on="REGISTRY_ID", how="left")

# Rename columns
facilities = facilities.rename(
    columns={"REGISTRY_ID": "registry_id", "FAC_NAME": "name", "FAC_STATE": "state", "FAC_COUNTY": "county", "FAC_CITY": "city", "FAC_EPA_REGION": "epa_region", "LOWINCOME": "low_income", "ACS_POPULATION": "acs_population", "WHITE_POPULATION": "white_population", "AFRICAN_AMERICAN_POPULATION": "african_american_population", "HISPANIC_ORIGIN_POPULATION": "hispanic_origin_population", "ASIAN_PACIFIC_ISLANDER_POP": "asian_pacific_islander_population", "AMERICAN_INDIAN_POPULATION": "american_indian_population", "RADIUS_OF_AREA": "radius", "LATITUDE_MEASURE": "lat", "LONGITUDE_MEASURE": "long"})

# Analysis done on radius of area 3.
facilities = facilities[facilities["radius"] == 3]

facilities["low_income_ratio"] = round(facilities["low_income"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["low_income_ratio"])

# Population ratio of White people
facilities["white_population_ratio"] = round(facilities["white_population"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["white_population_ratio"])
# Errors in the data, removed when ACS Population is somehow smaller than the number of white people
facilities = facilities[facilities['white_population_ratio'] <= 1]

# Population ratio of Black people
facilities["black_population_ratio"] = round(facilities["african_american_population"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["black_population_ratio"])
facilities = facilities[facilities['black_population_ratio'] <= 1]

# Population ratio of Hispanic people
facilities["hispanic_population_ratio"] = round(facilities["hispanic_origin_population"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["hispanic_population_ratio"])
facilities = facilities[facilities['hispanic_population_ratio'] <= 1]

# Population ratio of Asian people
facilities["asian_population_ratio"] = round(facilities["asian_pacific_islander_population"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["asian_population_ratio"])
facilities = facilities[facilities['asian_population_ratio'] <= 1]

# Population ratio of American Indian people
facilities["american_indian_population_ratio"] = round(facilities["american_indian_population"] / facilities["acs_population"], 2)
facilities = facilities.dropna(subset=["american_indian_population_ratio"])
facilities = facilities[facilities['american_indian_population_ratio'] <= 1]

# Drop columns that are no longer needed.
facilities = facilities.drop(columns=["low_income", "acs_population", "radius", "american_indian_population", "asian_pacific_islander_population", "hispanic_origin_population", "african_american_population", "white_population"])

# Write to csv.
facilities.to_csv(WRITE_PATH + "frs_facilities.csv", index=False)

# Delete dataframes to free up memory.
frs = facilities

del demographics
del facilities
gc.collect()

print("Completed: frs facilities", flush=True)

# Read in the data.
facilities = pd.read_csv(
    READ_PATH + "CASE_ENFORCEMENT_CONCLUSION_FACILITIES.csv",
    usecols=["FACILITY_UIN", "CASE_NUMBER"]).rename(columns={"FACILITY_UIN": "REGISTRY_ID"})

enforcements_1 = pd.read_csv(
    READ_PATH + "CASE_ENFORCEMENT_CONCLUSIONS.csv",
    usecols=["CASE_NUMBER", "ENF_CONCLUSION_ID", "ENF_CONCLUSION_ACTION_CODE", "SETTLEMENT_FY", "PRIMARY_LAW", "FED_PENALTY_ASSESSED_AMT", "STATE_LOCAL_PENALTY_AMT", "SEP_AMT", "COMPLIANCE_ACTION_COST", "COST_RECOVERY_AWARDED_AMT"])

enforcements_2 = pd.read_csv(
    READ_PATH + "CASE_ENFORCEMENTS.csv",
    usecols=["CASE_NUMBER", "FISCAL_YEAR", "ENF_OUTCOME_CODE", "VOLUNTARY_SELF_DISCLOSURE_FLAG"])

# Merge the two dataframes.
enforcements = enforcements_1.merge(enforcements_2, on=["CASE_NUMBER"], how="left").merge(facilities, on=["CASE_NUMBER"], how="left")

# Rename columns
enforcements = enforcements.rename(
    columns={"REGISTRY_ID": "registry_id", "CASE_NUMBER": "case_number", "ENF_CONCLUSION_ID": "enf_conclusion_id", "ENF_CONCLUSION_ACTION_CODE": "enf_conclusion_action_code", "SETTLEMENT_FY": "settlement_fy", "PRIMARY_LAW": "primary_law", "FED_PENALTY_ASSESSED_AMT": "fed_penalty_assessed_amt", "STATE_LOCAL_PENALTY_AMT": "state_local_penalty_amt", "SEP_AMT": "sep_amt", "COMPLIANCE_ACTION_COST": "compliance_action_cost", "COST_RECOVERY_AWARDED_AMT": "cost_recovery_awarded_amt", "FISCAL_YEAR": "fiscal_year", "ENF_OUTCOME_CODE": "enf_outcome_code", "VOLUNTARY_SELF_DISCLOSURE_FLAG": "voluntary_self_disclosure_flag"})

# Drop duplicates and null values.
enforcements = enforcements.drop_duplicates().dropna(subset=["registry_id"])

# Frequency of enforcement actions.
current_year = DT.now().year
enforcements = enforcements[enforcements['fiscal_year'] > (current_year - 10)]

enforcements["penalty_frequency"] = enforcements.groupby("registry_id")["registry_id"].transform('size')
enforcements["self_disclosure_frequency"] = enforcements[enforcements["voluntary_self_disclosure_flag"] == "Y"].groupby("registry_id")["registry_id"].transform('size')

# Fill nan for columns fed_penalty_assessed_amt, state_local_penalty_amt, sep_amt, compliance_action_cost, and cost_recovery_awarded_amt with 0.
enforcements["fed_penalty_assessed_amt"] = enforcements["fed_penalty_assessed_amt"].fillna(0)
enforcements["state_local_penalty_amt"] = enforcements["state_local_penalty_amt"].fillna(0)
enforcements["sep_amt"] = enforcements["sep_amt"].fillna(0)
enforcements["compliance_action_cost"] = enforcements["compliance_action_cost"].fillna(0)
enforcements["cost_recovery_awarded_amt"] = enforcements["cost_recovery_awarded_amt"].fillna(0)

# This should be unnecessary, as everything in this table should have one penalty to be present, but is here just in case.
enforcements["penalty_frequency"] = enforcements["penalty_frequency"].fillna(0)
enforcements["self_disclosure_frequency"] = enforcements["self_disclosure_frequency"].fillna(0)

# TODO: Probably need to sum to one penalty value. Might need to ask Nick.

# Sum up the penalties for each facility.
enforcements = enforcements.groupby("registry_id").agg(
    {"primary_law": "first", "enf_outcome_code": "first", "self_disclosure_frequency": "first", "penalty_frequency": "first", "fed_penalty_assessed_amt": "sum", "state_local_penalty_amt": "sum", "sep_amt": "sum", "compliance_action_cost": "sum", "cost_recovery_awarded_amt": "sum"}).reset_index()

# Write to csv.
enforcements.to_csv(WRITE_PATH + "enforcements.csv", index=False)

# Delete dataframes to free up memory.
del facilities
del enforcements_1
del enforcements_2
gc.collect()

print("Completed: enforcements", flush=True)

# Read in the data.
current = pd.read_json("https://theunitedstates.io/congress-legislators/legislators-current.json")
historical = pd.read_json("https://theunitedstates.io/congress-legislators/legislators-historical.json")

# Create a dataframe with all legislators.
legislators = pd.concat([current, historical], ignore_index=True)

# Create a dataframe with only legislators in the house or senate.
legislators = legislators[legislators["terms"].apply(lambda x: x[-1]["type"] in ["rep", "sen"])]

# Create a dataframe with only legislators in the house or senate in the last 10 years.
legislators = legislators[legislators["terms"].apply(lambda x: x[-1]["start"] > f"{current_year - 10}-01-01")]

# Create a dataframe that also includes the party and state of the legislator.
legislators = legislators[["id", "terms"]].explode("terms")
legislators["party"] = legislators["terms"].apply(lambda x: x["party"])
legislators["state"] = legislators["terms"].apply(lambda x: x["state"])
legislators = legislators.drop(columns=["terms"])

# Create a dataframe that counts the two parties for each state.
legislators = legislators.groupby(["state", "party"]).agg({"id": "count"}).reset_index()

# Create a dataframe that pivots the party counts to columns.
legislators = legislators.pivot(index="state", columns="party", values="id").reset_index()

# Rename columns
legislators = legislators.rename(
    columns={"Democrat": "democrat", "Republican": "republican", "Independent": "independent", "Libertarian": "libertarian"})

# Write to csv.
legislators.to_csv(WRITE_PATH + "legislators.csv", index=False)

# Delete dataframes to free up memory.
del current
del historical
gc.collect()

print("Completed: legislators", flush=True)

df = enforcements.merge(frs, how="left", on="registry_id").merge(air, how="left", on="registry_id").merge(npdes, how="left", on="registry_id").merge(legislators, how="left", on="state").dropna(subset=["state"])

# Fill nan for columns where the facility was not present in the other datasets where it makes sense to have the value 0.
df["democrat"] = df["democrat"].fillna(0)
df["republican"] = df["republican"].fillna(0)
df["libertarian"] = df["libertarian"].fillna(0)
df["independent"] = df["independent"].fillna(0)
df["caasip"] = df["caasip"].fillna(0)
df["caamact"] = df["caamact"].fillna(0)
df["caatvp"] = df["caatvp"].fillna(0)
df["caansps"] = df["caansps"].fillna(0)
df["caagactm"] = df["caagactm"].fillna(0)
df["other"] = df["other"].fillna(0)

# Write to csv.
df.to_csv(WRITE_PATH + "tidy_data.csv", index=False)
df.to_csv(WRITE_PATH + f"tidy_data_{DT.year}{DT.month}{DT.day}.csv", index=False)
print("Completed preprocessing: tidy_data.csv saved to lib/processed", flush=True)

del enforcements
del frs
del air
del npdes
del df
gc.collect()
