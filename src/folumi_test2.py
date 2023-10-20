import folium
import pandas as pd
import json
import requests
from ipywidgets import interact
import ipywidgets as widgets
from IPython.display import display

# Load GeoJSON data for U.S. states and counties
url_counties = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"

with open("./lib/us-state-boundaries.geojson") as f:
    us_states = json.load(f)

us_counties = json.loads(requests.get(url_counties).text)

# Create a map
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

# Add U.S. states to the map
folium.GeoJson(
    us_states,
    name="U.S. States",
).add_to(m)

# Add U.S. counties to the map with popups
for feature in us_counties['features']:
    geojson = folium.GeoJson(
        feature,
        name="U.S. Counties",
        style_function=lambda x: {
            "weight": 0.5,
            "color": "black",
        },
    )
    popup = folium.GeoJsonPopup(fields=['NAME'], aliases=['County Name'])
    popup.add_to(geojson)
    geojson.add_to(m)

# Sample data for illustration (you can replace this with your data)
data = pd.DataFrame({
    'State': ['California', 'California', 'New York', 'Texas', 'New York', 'Texas'],
    'County': ['Los Angeles', 'San Francisco', 'New York County', 'Harris', 'Kings', 'Dallas'],
    'Population': [10000000, 800000, 8500000, 4500000, 2700000, 2800000],
    'Area': [4687, 121, 468.9, 1772, 113, 881],
})

# Function to filter and display data
def display_data(state, county):
    if state == "All":
        filtered_data = data
    else:
        filtered_data = data[(data["State"] == state) & (data["County"] == county)]
    display(filtered_data)

# Dropdown widgets for selecting a state and a county
states_list = data["State"].unique()
counties_list = data["County"].unique()
state_selector = widgets.Dropdown(
    options=["All"] + list(states_list),
    description="Select a State:",
)
county_selector = widgets.Dropdown(
    options=["All"] + list(counties_list),
    description="Select a County:",
)

# Define an interaction function
@interact(state=state_selector, county=county_selector)
def on_selection_change(state, county):
    display_data(state, county)

# Display the map
m.save("./maps/interactive_map_with_interactivity2.html")
