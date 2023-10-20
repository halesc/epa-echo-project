import os
import streamlit as st
import pickle
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
from modeling import columns
from modeling import original_to_encoded
from sklearn.linear_model import LinearRegression
import numpy as np
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv

load_dotenv()

# Access the variables using os.environ
path_variable = os.environ.get("DEV_PATH")
APP_TITLE = "EPA at the County Level"
APP_SUB_TITLE = "Source: ECHO Data"

STATES_DICT = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Canal Zone": "CZ", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Guam": "GU", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Puerto Rico": "PR", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virgin Islands": "VI", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
FILE_PATH = os.path.dirname(os.path.abspath("")[:-3])
RF_MODEL_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/models", "rf_model.pkl")
LN_MODEL_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/models", "ln_model.pkl")
DATA_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/processed", "tidy_data.csv")





st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

selected_cols = ["white_population_ratio", "black_population_ratio", "hispanic_population_ratio", "asian_population_ratio", "american_indian_population_ratio", "other", "lat", "long", "fed_penalty_assessed_amt"]
grouped_data = case_data.groupby(["state", "county"])[selected_cols].mean().reset_index()
grouped_data_low_income = case_data.groupby(["state", "county"])["low_income_ratio"].mean().reset_index()
grouped_data_low_income["other_income_ratio"] = 1 - grouped_data_low_income["low_income_ratio"]

grouped_data_metrics = case_data.groupby(["state", "county", "primary_law"])["fed_penalty_assessed_amt"].mean().reset_index()

# Merge the penalty_counts_df and grouped_data on "state", "county", and "primary_law"
merged_data = grouped_data
merged_data["full_state"] = merged_data["state"].apply(full_name)
state = display_map(merged_data)
cleaned_data = merged_data[["state", "county"]]
cleaned_data = cleaned_data.drop_duplicates(subset=["state", "county"])
counties_in_state = tuple(cleaned_data[cleaned_data["state"] == state]["county"].unique())
county = st.selectbox("Which County?", (counties_in_state))
display_pie_chart(merged_data, grouped_data_low_income, state, county)
st.subheader(f"EPA Data for {county} County in the State of {state}")
primary_law = st.selectbox("Which Primary Law?", (laws_tuple))
display_facts(grouped_data_metrics, state, county, primary_law, "Average Penalty")
plot_count_of_violations_and_penalty_value(case_data)