
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

# TODO: A value is trying to be set on a copy of a slice from a DataFrame.
# In relation to rounding the values in the dataframe.
# TODO: App retrains at launch. Disable this and make this the only way to retrain. Add versioning.
# TODO: Make a county risk model. Add more features to this model.

STATES_DICT = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Canal Zone": "CZ", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Guam": "GU", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Puerto Rico": "PR", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virgin Islands": "VI", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
FILE_PATH = os.path.dirname(os.path.abspath("")[:-3])
RF_MODEL_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/models", "rf_model.pkl")
LN_MODEL_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/models", "ln_model.pkl")
DATA_PATH = os.path.join(FILE_PATH, f"{path_variable}/lib/processed", "tidy_data.csv")

# in order to received client inputs appended these inputs (created above) into dictionary as we mentioned before. And We returned into dataframe.


def model_rf(model, state, ratio_low_income, ratio_black_population, ratio_white_population, ratio_asian_population, ratio_american_indian_population, ratio_hispanic_population):
    my_dict = {
        "State": original_to_encoded.get(state),
        "low_income_ratio": ratio_low_income,
        "black_population_ratio": ratio_black_population,
        "white_population_ratio": ratio_white_population,
        "asian_population_ratio": ratio_asian_population,
        "american_indian_population_ratio": ratio_american_indian_population,
        "hispanic_population_ratio": ratio_hispanic_population,

    }
    df = pd.DataFrame.from_dict([my_dict])
    # And appended column names into column list. We need columns to use with reindex method as we mentioned before.
    df = pd.get_dummies(df).reindex(columns=columns, fill_value=0)
    # We append all columns in the user input dataframe and reindex method just received relevant user inputs , and return other columns from nan to zero with fill_value=0 parameter.
    # And now we can predict
    prediction = model.predict(df)
    # Success method demonstrate our prediction in a green square
    st.success("The estimated fine is ${}. ".format(int(prediction[0])))


def model_linear(case_data, test, demographic):
    dict_race = {"White": "white_population_ratio",
                 "Black": "black_population_ratio",
                 "Asian": "asian_population_ratio",
                 "American Indian": "american_indian_population_ratio",
                 "Hispanic": "hispanic_population_ratio"}

    demographic_column = dict_race.get(demographic)

    z_scores = np.abs((case_data["fed_penalty_assessed_amt"] - case_data["fed_penalty_assessed_amt"].mean()) / case_data["fed_penalty_assessed_amt"].std())
    threshold = 3
    case_data = case_data[z_scores < threshold]
    case_data_2 = case_data
    if demographic_column is None:
        st.error("Invalid demographic selection.")
        return

    if test == "Frequency of Fines":
        case_data[demographic_column] = case_data[demographic_column].round(2)
        case_data_2["low_income_ratio"] = case_data_2["low_income_ratio"].round(2)
        case_data = case_data.groupby(demographic_column)["fed_penalty_assessed_amt"].count().reset_index()
        case_data_2 = case_data_2.groupby("low_income_ratio")["fed_penalty_assessed_amt"].count().reset_index()
        case_data = case_data[case_data[demographic_column] != 0]

    X = case_data[[demographic_column]]
    y = case_data["fed_penalty_assessed_amt"]

    # Create and fit the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    predictions = model.predict(X)

    st.markdown("#### Coefficient Description")
    st.markdown("The coefficient represents the change in the Dollar Amount of Penalties for a unit change in the "
                "population ratio. A positive coefficient means that an increase in the "
                "population ratio will result in an increase in penalties.")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Coefficient", round(model.coef_.item(), 2))
    with col2:
        st.metric("Intercept:", round(model.intercept_, 2))

    case_data[demographic_column] = case_data[demographic_column].round(2)
    case_data_avg = case_data.groupby(demographic_column)["fed_penalty_assessed_amt"].mean().reset_index()

    # Extract the ratio and dollar amounts as variables
    ratio = case_data_avg[demographic_column]
    penalties = case_data_avg["fed_penalty_assessed_amt"]

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(ratio, penalties)

    # Plot the best-fit line
    ax.plot(X, predictions, color="red", linewidth=2)

    # Set labels and title
    ax.set_xlabel(f"Population Ratio - {demographic}")
    if test != "Frequency of Fines":
        ax.set_ylabel("Dollar Amount of Penalties")
    else:
        ax.set_ylabel("Frequency of Penalties")
    ax.set_title("Scatter Plot: Population Ratio vs. Penalties with Best-Fit Line")

    # Set a smaller figure background (padding)
    fig.set_facecolor("#f0f0f0")

    # Display the scatter plot in Streamlit
    st.pyplot(fig)

######################################################

    st.markdown("#### Income Level Relationship Graph")
    st.markdown("The low income ratio is based on the number of people in the selected area that have an income "
                "less than two times the poverty level, based on the 2016-2020 ACS 5-Year Summary ")
    X2 = case_data_2[["low_income_ratio"]]
    y2 = case_data_2["fed_penalty_assessed_amt"]

    # Create and fit the linear regression model
    model2 = LinearRegression()
    model2.fit(X2, y2)

    predictions2 = model2.predict(X2)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Coefficient", round(model2.coef_.item(), 2))
    with col2:
        st.metric("Intercept:", round(model2.intercept_, 2))

    case_data_2["low_income_ratio"] = case_data_2["low_income_ratio"].round(2)
    case_data_avg_2 = case_data_2.groupby("low_income_ratio")["fed_penalty_assessed_amt"].mean().reset_index()

    # Extract the ratio and dollar amounts as variables
    ratio2 = case_data_avg_2["low_income_ratio"]
    penalties2 = case_data_avg_2["fed_penalty_assessed_amt"]

    # Create the scatter plot
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.scatter(ratio2, penalties2)

    # Plot the best-fit line
    ax2.plot(X2, predictions2, color="red", linewidth=2)

    # Set labels and title
    ax2.set_xlabel("Low Income Population Ratio")
    if test != "Frequency of Fines":
        ax2.set_ylabel("Dollar Amount of Penalties")
    else:
        ax2.set_ylabel("Frequency of Penalties")
    ax2.set_title("Scatter Plot: Population Ratio vs. Penalties with Best-Fit Line")

    # Set a smaller figure background (padding)
    fig2.set_facecolor("#f0f0f0")

    # Display the scatter plot in Streamlit
    st.pyplot(fig2)


def display_facts(merged_data, state, county, primary_law, field_name, number_format="${:,}"):
    # print(merged_data)
    merged_data = merged_data[(merged_data["state"] == state) & (merged_data["county"] == county) & (merged_data["primary_law"] == primary_law)]
    print(merged_data)

    if not merged_data.empty:
        total = merged_data["fed_penalty_assessed_amt"].mean()

        if pd.notna(total):
            st.metric(field_name, number_format.format(round(total)))
        else:
            st.metric(field_name, "Data not available")
    else:
        st.metric(field_name, "Data not available")


def display_map(merged_data):
    dis_map = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False, tiles="CartoDB positron")
    oakland = st.selectbox("Remove Oakland?", ("Y", "N"))
    if oakland == "Y":
        merged_data = merged_data[merged_data["county"] != "OAKLAND"]
    state_data = merged_data.groupby(["full_state"])["fed_penalty_assessed_amt"].mean().reset_index()
    choropleth = folium.Choropleth(
        geo_data="./lib/us-state-boundaries.geojson",
        data=state_data,
        columns=("full_state", "fed_penalty_assessed_amt"),
        key_on="feature.properties.name",
        line_opacity=0.8,
        highlight=True)
    choropleth.geojson.add_to(dis_map)
    # choropleth.geojson.add_to(map)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(["name"], labels=False))
    st_map = st_folium(dis_map, width=700, height=450)
    state_name = ""
    if st_map["last_active_drawing"]:
        state_name = st_map["last_active_drawing"]["properties"]["name"]
    return abbrev_name(state_name)


def display_pie_chart(merged_data, grouped_data_low_income, state, county):
    merged_data = merged_data[(merged_data["state"] == state) & (merged_data["county"] == county)]
    demo_data = merged_data.loc[:, ["white_population_ratio", "black_population_ratio", "hispanic_population_ratio",
                                    "asian_population_ratio", "american_indian_population_ratio", "other"]]
    demo_data = demo_data.rename(
        columns={"white_population_ratio": "White", "black_population_ratio": "Black", "hispanic_population_ratio": "Hispanic",
                 "asian_population_ratio": "Asian", "american_indian_population_ratio": "American Indian", "other": "Other"})

    data_long = demo_data.melt()

    # Create the bar chart for demographic data
    fig, ax = plt.subplots(figsize=(8, 5))  # Set the size of the graph to 8x5 inches
    colors = ["#1f78b4", "#33a02c", "#fb9a99", "#e31a1c", "#ff7f00", "#6a3d9a"]  # Custom colors for the chart

    ax.bar(data_long["variable"], data_long["value"], color=colors)

    ax.set_title("Demographic Bar Chart")
    ax.set_xlabel("Demographic Group")
    ax.set_ylabel("Population Ratio")

    # Set a smaller figure background (padding)
    fig.set_facecolor("#f0f0f0")

    # Display the bar chart in Streamlit

    grouped_data_low_income = grouped_data_low_income[(grouped_data_low_income["state"] == state) & (grouped_data_low_income["county"] == county)]
    income_data = grouped_data_low_income.loc[:, ["low_income_ratio", "other_income_ratio"]]
    income_data = income_data.melt()

    # Create the pie chart for income ratio data
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    colors = ["#1f78b4", "#33a02c"]
    ax2.pie(income_data["value"], labels=income_data["variable"], autopct=lambda p: "{:.1f}%".format(p) if p >= 2 else "",
            startangle=140, colors=colors, textprops={"fontsize": 8, "fontweight": "bold"})

    ax2.axis("equal")
    ax2.set_title("Income Ratio Pie Chart")

    # Set a darker grey background for the plot area
    ax2.set_facecolor("#444444")

    # Set a smaller figure background (padding)
    fig2.set_facecolor("#f0f0f0")

    # Display the income ratio pie chart in Streamlit

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig)
    with col2:
        st.pyplot(fig2)


def full_name(state_abbrev: str, states_dict=STATES_DICT) -> str:
    reverse_states = {v: k for k, v in states_dict.items()}
    return reverse_states.get(state_abbrev)


def abbrev_name(state_name: str, states_dict=STATES_DICT) -> str:
    return states_dict.get(state_name)


def plot_count_of_violations_and_penalty_value(df):
    # Prompt the user to input the number of counties they want to analyze
    num_counties = st.number_input("Enter the number of counties you want to analyze:", min_value=1, step=1)

    selected_counties = []

    for i in range(num_counties):
        county = st.text_input(f"Enter the name of county {i + 1}:")
        if county.strip():
            # Convert to uppercase for consistency
            selected_counties.append(county.upper())

    if not selected_counties:
        st.warning("Please enter at least one county.")
        return
    # Filter the DataFrame based on the user-selected counties and store the result in "merged_data_filtered"
    merged_data_filtered = df[df["county"].isin(selected_counties)]

    # --- Plot the Count of Violations ---
    # Group data by FACILITY_STATE and STATUTE_CODE, and calculate the count of violations
    law_counts_by_county = merged_data_filtered.groupby(["county", "primary_law"]).size().reset_index(name="COUNT")

    # Pivot the data to have counties as rows and law status codes as columns
    law_counts_pivot = law_counts_by_county.pivot(index="county", columns="primary_law", values="COUNT").fillna(0)

    # Display the count of violations as a stacked bar chart using Streamlit"s bar_chart
    st.subheader("Count of Violations by Statute Code and County")
    st.bar_chart(law_counts_pivot, use_container_width=True)

    # --- Plot the Penalty Value ---
    # Group data by FACILITY_STATE and STATUTE_CODE, and calculate the sum of TOTAL_PENALTY_ASSESSED_AMT
    law_penalty_sum_by_county = merged_data_filtered.groupby(["county", "primary_law"])["fed_penalty_assessed_amt"].sum().reset_index(name="SUM_PENALTY")

    # Pivot the data to have counties as rows and law status codes as columns
    law_penalty_pivot = law_penalty_sum_by_county.pivot(index="county", columns="primary_law", values="SUM_PENALTY").fillna(0)

    # Display the penalty value as a stacked bar chart using Streamlit"s bar_chart
    st.subheader("Total Penalty Assessed Amount by Statute Code and County")
    st.bar_chart(law_penalty_pivot, use_container_width=True)


def run_and_display_stdout(*cmd_with_args):
    result = subprocess.Popen(cmd_with_args, stdout=subprocess.PIPE)
    for line in iter(lambda: result.stdout.readline(), b""):
        st.text(line.decode("utf-8"))


def main():
    case_data = pd.read_csv(DATA_PATH)

    laws_tuple = tuple(case_data["primary_law"].unique())
    # CLEAN DATA
    case_data["county"] = case_data["county"].str.replace("COUNTY", "").str.strip()
    case_data = case_data[case_data["county"] != "-- NOT DEFINED --"]

    def validate_lat_lon_us(data, lat_column, lon_column):
        min_lat, max_lat = 24.396308, 49.384358
        min_lon, max_lon = -125.000000, -66.934570

        invalid_rows = []

        for index, row in data.iterrows():
            lat = row[lat_column]
            lon = row[lon_column]

            if not (min_lat <= lat <= max_lat) or not (min_lon <= lon <= max_lon):
                invalid_rows.append(index)

        return data.drop(invalid_rows)

    # "LATITUDE_MEASURE" and "LONGITUDE_MEASURE" are the columns containing latitude and longitude values
    case_data = validate_lat_lon_us(case_data, "lat", "long")

    case_data = case_data[case_data["black_population_ratio"] <= 1]
    case_data = case_data[case_data["white_population_ratio"] <= 1]
    case_data = case_data[case_data["low_income_ratio"] <= 1]
    case_data = case_data.dropna(subset=["hispanic_population_ratio"])
    case_data = case_data.dropna(subset=["asian_population_ratio"])
    case_data = case_data.dropna(subset=["american_indian_population_ratio"])
    case_data = case_data.dropna(subset=["low_income_ratio"])
    case_data = case_data[case_data["hispanic_population_ratio"] <= 1]
    case_data = case_data[case_data["asian_population_ratio"] <= 1]
    case_data = case_data[case_data["american_indian_population_ratio"] <= 1]

    case_data["other"] = 1 - (case_data["hispanic_population_ratio"] + case_data["asian_population_ratio"] + case_data["american_indian_population_ratio"] + case_data["black_population_ratio"] + case_data["white_population_ratio"])
    case_data = case_data[case_data["other"] >= 0]

    choice = st.selectbox("Display Choice", ("Demographics and Fine Predictor", "Heat Map", "Utilities"))

    if choice == "Demographics and Fine Predictor":
        APP_TITLE = "DEMOGRAPHICS ANALYSIS"
        APP_SUB_TITLE = "Source: ECHO Data"

        st.title(APP_TITLE)
        st.caption(APP_SUB_TITLE)

        st.markdown("### Application Description")
        st.markdown("This application is designed to look at ratios of demographic populations and show the relationships "
                    "with EPA fines amounts and frequencies. In addition, using machine learning algorithms, this application "
                    "predicts what the EPA fine would be.")

        demographic = st.selectbox("Which Racial Population?", ("White", "Black", "Hispanic", "Asian", "American Indian"))

        test = st.radio("Which Analysis?", ("Dollar Amount Fines", "Frequency of Fines"))

        # We called back our models created before
        model = pickle.load(open(RF_MODEL_PATH, "rb"))

        # We use selectbox method and append our models to give a choice clients
        # We created selectbox for categorical columns and used slider numerical values ,specified range and step

        case_data = case_data.dropna()
        column_tuple = tuple(case_data["state"].unique())
        column_tuple = sorted(column_tuple)

        model_linear(case_data, test, demographic)

        st.markdown(" "
                    "### EPA Fine Predictor")
        st.markdown("Enter in the values below to predict the EPA dollar fine amount.")

        state = st.selectbox("Which State?", (column_tuple))

        ratio_low_income = st.slider("What is the ratio of low income households?", 0.0, 1.0, step=0.1)

        # For Black population
        max_slider_value_black = 1.0
        ratio_black_population = st.slider("What is the ratio of the Black population?", 0.0, max_slider_value_black, step=0.1)

        # For White population
        max_slider_value_white = 1.0 - ratio_black_population
        ratio_white_population = st.slider("What is the ratio of the White population?", 0.0, max_slider_value_white, step=0.1)

        # For Asian population
        max_slider_value_asian = 1.0 - ratio_black_population - ratio_white_population
        ratio_asian_population = st.slider("What is the ratio of the Asian population?", 0.0, max_slider_value_asian, step=0.1)

        # For American Indian population
        max_slider_value_american_indian = 1.0 - ratio_black_population - ratio_white_population - ratio_asian_population
        ratio_american_indian_population = st.slider("What is the ratio of the American Indian population?", 0.0, max_slider_value_american_indian, step=0.1)

        # For Hispanic population
        max_slider_value_hispanic = 1.0 - ratio_black_population - ratio_white_population - ratio_asian_population - ratio_american_indian_population

        ratio_hispanic_population = st.slider("What is the ratio of the Hispanic population?", 0.0, max_slider_value_hispanic, step=0.1)

        model_rf(model, state, ratio_low_income, ratio_black_population, ratio_white_population, ratio_asian_population, ratio_american_indian_population, ratio_hispanic_population)
    if choice == "Heat Map":
        APP_TITLE = "EPA at the County Level"
        APP_SUB_TITLE = "Source: ECHO Data"

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
    if choice == "Utilities":
        APP_TITLE = "Processing Utilities"
        APP_SUB_TITLE = "Here new data can be extracted and transformed, as well as models retrained."

        st.title(APP_TITLE)
        st.caption(APP_SUB_TITLE)

        ex_button = st.button("Extract Data", help="Extracts the data from the EPA ECHO website.")
        if ex_button:
            run_and_display_stdout("python", "src/extracting.py")

        pp_button = st.button("Transform Data", help="Transforms the data into a format used in modeling.")
        if pp_button:
            run_and_display_stdout("python", "src/preprocessing.py")

        md_button = st.button("Train Demographic Model", help="Retrains the demographic model using the most up to date data.")
        if md_button:
            run_and_display_stdout("python", "src/modeling.py")


if __name__ == "__main__":
    main()
