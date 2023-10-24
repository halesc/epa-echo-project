# https://gispub.epa.gov/air/trendsreport/2021/#pm2_5_composition
# Medium: https://medium.com/p/e3aff3b0ed43

# Word Press: https://waterprogramming.wordpress.com/2023/04/05/creating-interactive-geospatial-maps-in-python-with-folium/
# Examples: https://github.com/TrevorJA/Folium_Interactive_Map_Demo

# Folium examples: https://github.com/python-visualization/folium/tree/main/examples

# ****Filters: https://python-visualization.github.io/folium/latest/user_guide/plugins/tag_filter_button.html

# Crime Example: https://domino.ai/blog/creating-interactive-crime-maps-with-folium

## Wants:
# https://python-visualization.github.io/folium/latest/user_guide/plugins/search.html
# https://python-visualization.github.io/folium/latest/user_guide/plugins/heatmap.html
# https://python-visualization.github.io/folium/latest/user_guide/plugins/locate_control.html
# https://python-visualization.github.io/folium/latest/user_guide/plugins/measure_control.html
# https://python-visualization.github.io/folium/latest/user_guide/plugins/mouse_position.html
# https://python-visualization.github.io/folium/latest/user_guide/plugins/timeslider_choropleth.html

# Advanced Options 
# https://python-visualization.github.io/folium/latest/advanced_guide.html


# https://medium.com/planet-os/analyzing-air-quality-data-from-planet-os-datahub-using-python-pandas-and-plotly-f2766c003c6c


# Options:
# https://openaq.org/

# DataSources
# Full list: https://github.com/openaq/awesome-air-quality
# AWS Example: https://github.com/openaq/openaq-api-v2
# BigQuery: https://medium.com/@Faraz_EA/analyzing-epa-air-quality-data-using-bigquery-and-choropleth-map-f1c59b0406f4

import pandas as pd
import folium
from folium.plugins import TagFilterButton, Search, LocateControl, HeatMap
import numpy as np
import random
import branca
import geopandas

state_abbreviations = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


states = geopandas.read_file(
    "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    driver="GeoJSON",
)

cities = geopandas.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_populated_places_simple.geojson",
    driver="GeoJSON",
)

######################## DATA PREP ####################################
df = pd.read_csv('../lib/processed/tidy_data.csv')
df.head()

# Randomly select 10% of the data (for working locally)
# Calculate the number of rows to sample (10%)
sample_fraction = 0.10
sample_size = int(len(df) * sample_fraction)

# Randomly select 10% of the data
df = df.sample(n=sample_size, random_state=42)
df = df.dropna(subset=['lat', 'long'])

# penalty_frequency color
def rd2(x):
    return round(x, 2)

us_cities = geopandas.sjoin(cities, states, how="inner", predicate="within")
us_cities.head()

pop_ranked_cities = us_cities.sort_values(by="pop_max", ascending=False)[
    ["nameascii", "pop_max", "geometry"]
].iloc[:20]

# Function to create a folium map with a specific location and zoom level
def create_base_map():
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('cartodbpositron').add_to(m)
    return m


# Create map and set the initial view to cover the USA
m = create_base_map()

# Modify the style_function to use state abbreviations for lookup and set state color based on citation count
def style_function(x):
    state_name = x["properties"]["name"]
    # Use the mapping to get the abbreviation
    state_abbreviation = state_abbreviations.get(state_name, state_name)
    
    # Use the abbreviation for lookup
    citation_count = df[df['state'] == state_abbreviation]['state'].count()
    
    return {
        "fillColor": f"#ff0000{citation_count:02x}",  # Set state color based on citation count
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.7
    }

# Create the stategeo GeoJson feature and add the annotation
stategeo = folium.GeoJson(
    states,
    name="Citation Count",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["name"],
        aliases=["State"],
        localize=True
    ),
).add_to(m)


citygeo = folium.GeoJson(
    pop_ranked_cities,
    name="US Cities",
    tooltip=folium.GeoJsonTooltip(
        fields=["nameascii", "pop_max"], aliases=["", "Population Max"], localize=True
    ),
).add_to(m)

statesearch = Search(
    layer=stategeo,
    geom_type="Polygon",
    placeholder="Search for a US State",
    collapsed=False,
    search_label="name",
    weight=3,
).add_to(m)

citysearch = Search(
    layer=citygeo,
    geom_type="Point",
    placeholder="Search for a US City",
    collapsed=False,
    search_label="nameascii",
).add_to(m)

########################## Boeing Layer
boeing_data = pd.read_csv('../lib/raw/geocoded_data.csv')
boeing_data = boeing_data.dropna(subset=['Latitude','Longitude'])

# Create a feature group for host sites
host_sites_layer = folium.FeatureGroup(name="Host Sites")

for index, row in boeing_data.iterrows():
    latlng = (float(row["Latitude"]), float(row["Longitude"]))
    host_site = row["Host Site"]

    folium.CircleMarker(
        location=latlng,
        radius=4,
        color="green",
        fill=True,
        fill_color="green",
        fill_opacity=.6,
        popup=host_site,
    ).add_to(host_sites_layer)

# Add the host sites feature group to the map
host_sites_layer.add_to(m)


########################## Citations

# Define a function to add markers and filters for a specific category
def add_markers_and_filter(df, category_column, map):
    categories = df[category_column].unique().tolist()
    categories_sorted = sorted(categories)
    
    for index, row in df.iterrows():
        latlng = (row['lat'], row['long'])
        category = row[category_column]

        # Create a custom HTML icon with a red exclamation mark
        icon_html = """
        <div style="font-size: 8px; color: red;">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        """

        folium.Marker(
            location=latlng,
            icon=folium.DivIcon(html=icon_html),  # Use the custom icon
            popup=category,
            tags=[category]  # Set the category as a popup message
        ).add_to(map)

    TagFilterButton(categories_sorted, name=category_column).add_to(map)


# Create markers and filters for 'primary_law'
add_markers_and_filter(df, 'primary_law', m)
add_markers_and_filter(df, 'state', m)

# Create a HeatMap layer
heat_data = [[row['lat'], row['long']] for index, row in df.iterrows()]
heat_map = HeatMap(heat_data, name= "HeatMap")
heat_map.add_to(m)

folium.LayerControl().add_to(m)
folium.plugins.LocateControl(auto_start=False).add_to(m)
m.save('map.html')






