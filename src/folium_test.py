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



import pandas as pd
import folium
from folium.plugins import TagFilterButton
from folium.plugins import Search
import numpy as np
import random
import branca

import geopandas

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
df.columns

# Assuming 'lat' and 'lng' are the column names in your DataFrame
missing_lat = df['lat'].isnull().sum()
missing_lng = df['long'].isnull().sum()

total_rows = len(df)
percentage_missing_lat = (missing_lat / total_rows) * 100
percentage_missing_lng = (missing_lng / total_rows) * 100

## Good to drop those missing (small %)
print(f"Percentage of missing latitude data: {percentage_missing_lat:.2f}%")
print(f"Percentage of missing longitude data: {percentage_missing_lng:.2f}%")
df = df.dropna(subset=['lat', 'long'])

# penalty_frequency color
def rd2(x):
    return round(x, 2)

minimum, maximum = df["penalty_frequency"].quantile([0.05, 0.95]).apply(rd2)

mean = round(df["penalty_frequency"].mean(), 2)

print(f"minimum: {minimum}", f"maximum: {maximum}", f"Mean: {mean}", sep="\n\n")


colormap = branca.colormap.LinearColormap(
    colors=["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f"],
    index=df["penalty_frequency"].quantile([0.2, 0.4, 0.6, 0.8]),
    vmin=minimum,
    vmax=maximum,
)

us_cities = geopandas.sjoin(cities, states, how="inner", predicate="within")

pop_ranked_cities = us_cities.sort_values(by="pop_max", ascending=False)[
    ["nameascii", "pop_max", "geometry"]
].iloc[:20]


# Create map and set the initial view to cover the USA
m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
folium.TileLayer('openstreetmap').add_to(m)

########################## SEARCH ###############################################
def style_function(x):
    return {
        "fillColor": colormap(x["properties"]["density"]),
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.5,
    }


stategeo = folium.GeoJson(
    states,
    name="US States",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["name", "density"], aliases=["State", "Density"], localize=True
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
    collapsed=True,
    search_label="nameascii",
).add_to(m)

folium.LayerControl().add_to(m)
colormap.add_to(m)

########################## MAPPING ##############################################

# Define a function to add markers and filters for a specific category
def add_markers_and_filter(df, category_column, map):
    categories = df[category_column].unique().tolist()
    
    for index, row in df.iterrows():
        latlng = (row['lat'], row['long'])
        category = row[category_column]

        folium.Marker(
            location=latlng,
            popup=category,
            tags=[category]  # Set the category as a popup message
        ).add_to(map)

    TagFilterButton(categories, name=category_column).add_to(map)


# Create markers and filters for 'primary_law'
add_markers_and_filter(df, 'primary_law', m)
add_markers_and_filter(df, 'state', m)

# Add layer control
folium.LayerControl().add_to(m) 
m.save('map.html')


