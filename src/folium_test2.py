import folium
from folium.plugins import TagFilterButton
import pandas as pd
from folium.plugins import TagFilterButton
from folium.plugins import Search
from folium.plugins import LocateControl
import numpy as np
import random
import branca
import geopandas

def create_filtered_map(df, lat_col, lon_col, filter_cols):
    """
    Create a Folium map with filtered data points and interactive filters.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing data to be plotted.
        lat_col (str): The name of the column containing latitude coordinates.
        lon_col (str): The name of the column containing longitude coordinates.
        filter_cols (list of str): List of column names for which you want to create filters.

    Returns:
        folium.Map: The Folium map with data points and interactive filters.
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

        folium.Marker(
            location=latlng,
            popup=popup
        ).add_to(data_layer)

    # Create filters for specified columns
    for col in filter_cols:
        categories = df[col].unique()
        categories_sorted = sorted(str(categories))

        # Create a TagFilterButton for each filter
        TagFilterButton(categories_sorted, name=col).add_to(m)

    # Add a layer control to toggle the visibility of the data points and filters
    folium.LayerControl(collapsed=False).add_to(m)

    return m


######################## Citation Data ####################################
df = pd.read_csv('../lib/processed/tidy_data.csv')
df.head()

# Randomly select 10% of the data (for working locally)
# Calculate the number of rows to sample (10%)
sample_fraction = 0.5
sample_size = int(len(df) * sample_fraction)

# Randomly select 10% of the data
df = df.sample(n=sample_size, random_state=42)
df = df.dropna(subset=['lat', 'long'])

df.columns

# Specify the columns for which you want to create filters
filter_columns = ['primary_law', 'state', 'county', 'air_pollutant_class_code', 'democrat', 'independent', 'libertarian',
       'republican']

# Create the Folium map with filters
filtered_map = create_filtered_map(df, 'lat', 'long', filter_columns)






# Save or display the map
filtered_map.save('filtered_map.html')


