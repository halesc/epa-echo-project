import folium
from folium.plugins import TagFilterButton
from folium.plugins import Search
from folium.plugins import LocateControl
import pandas as pd
import numpy as np
import geopandas

def create_filtered_map(df, lat_col, lon_col, filter_cols, geospatial_layers=None, layer_names=None, boeing_data=None):
    """
    Create a Folium map with filtered data points, interactive filters, and geospatial layers.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing data to be plotted.
        lat_col (str): The name of the column containing latitude coordinates.
        lon_col (str): The name of the column containing longitude coordinates.
        filter_cols (list of str): List of column names for which you want to create filters.
        geospatial_layers (list of geopandas.GeoDataFrame, optional): List of geospatial layers to add.

    Returns:
        folium.Map: The Folium map with data points, interactive filters, and geospatial layers.
    """
    # Create a base map
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=5)

    # Create a common layer for all data points
    data_layer = folium.FeatureGroup(name="Data Points")
    data_layer.add_to(m)

    # Create markers for each row in the DataFrame
    for index, row in df.iterrows():
        latlng = (row[lat_col], row[lon_col])
        popup = ", ".join([f"{col}: {row[col]}" for col in df.columns])

        # Create a custom HTML icon with a red exclamation mark
        icon_html = """
        <div style="font-size: 8px; color: red;">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        """

        folium.Marker(
            location=latlng,
            popup=popup,
            icon=folium.DivIcon(html=icon_html)
        ).add_to(data_layer)

    # Create filters for specified columns
    for col in filter_cols:
        categories = df[col].unique()
        categories_sorted = sorted(str(categories))

        # Create a TagFilterButton for each filter
        TagFilterButton(categories_sorted, name=col).add_to(m)

    # Add geospatial layers if provided
    if geospatial_layers and layer_names:
        for i, layer in enumerate(geospatial_layers):
            folium.GeoJson(layer, name= layer_names[i]).add_to(m)

    # Add a layer for Boeing data if provided
    if boeing_data is not None:
        boeing_layer = folium.FeatureGroup(name="Boeing Data")
        boeing_layer.add_to(m)

        for index, row in boeing_data.iterrows():
            latlng = (row['Latitude'], row['Longitude'])
            
            # Create a custom airplane-shaped icon
            icon = folium.CustomIcon(
                icon_image='https://palmettogoodwill.org/wp-content/uploads/2022/04/png-transparent-boeing-logo-boeing-business-jet-logo-boeing-commercial-airplanes-integrated-blue-company-text.png',
                icon_size=(20, 20)
            )
            
            folium.Marker(
                location=latlng,
                icon=icon,
            ).add_to(boeing_layer)

    # Add a layer control to toggle the visibility of the data points, filters, and geospatial layers
    folium.LayerControl(collapsed=False).add_to(m)

    return m



######################## DATA PREP ####################################
df = pd.read_csv('../lib/processed/tidy_data.csv')
df.head()

# Randomly select 10% of the data (for working locally)
# Calculate the number of rows to sample (10%)
sample_fraction = 0.05
sample_size = int(len(df) * sample_fraction)

# Randomly select 10% of the data
df = df.sample(n=sample_size, random_state=42)
df = df.dropna(subset=['lat', 'long'])

df.columns

# Specify the columns for which you want to create filters
filter_columns = ['primary_law', 'state', 'democrat', 'independent', 'libertarian',
       'republican']

# Load the geospatial layers
states = geopandas.read_file(
    "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    driver="GeoJSON",
)

cities = geopandas.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_populated_places_simple.geojson",
    driver="GeoJSON",
)

us_cities = geopandas.sjoin(cities, states, how="inner", predicate="within")
us_cities.head()

pop_ranked_cities = us_cities.sort_values(by="pop_max", ascending=False)[
    ["nameascii", "pop_max", "geometry"]
].iloc[:40]

# Load Boeing data
boeing_data = pd.read_csv('../lib/raw/geocoded_data.csv')
boeing_data = boeing_data.dropna(subset=['Latitude', 'Longitude'])

# Create the Folium map with filters and geospatial layers
filtered_map = create_filtered_map(df, 'lat', 'long', filter_columns, geospatial_layers=[states, pop_ranked_cities], layer_names = ["states", "cities"], boeing_data= boeing_data)

# Save or display the map
filtered_map.save('filtered_map.html')
