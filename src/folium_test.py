# Could we use a free version of looker???

import folium
import pandas as pd
import geopandas as gpd
import json 

# Create a Map object
dis_map = folium.Map(location=[51.5074, -0.1278], zoom_start=12, tiles="CartoDB dark_matter")  # London coordinates

# Load the fire pollution shapefile using GeoPandas
fire_shapefile = gpd.read_file("./lib/fire/Perimeters.shp")
fire_geojson = fire_shapefile.to_json()

air_shapefile = gpd.read_file("./lib/fire/Sevenaoks_Open_Data_-_Air_Pollution_Control_Sites.shp")
air_geojson = air_shapefile.to_json()

# Load GeoJSON data for U.S. states and counties
with open("./lib/us-state-boundaries.geojson") as f:
    us_border_gdf = json.load(f)



# Sample DataFrame with your data
data = pd.DataFrame({
    'site_name': ['London', 'Paris', 'New York'],
    'lat': [51.5074, 48.8566, 40.7128],
    'long': [-0.1278, 2.3522, -74.0060],
    'note': ['Capital of the UK', 'Capital of France', 'Big Apple']
})

# # Create a CustomPane for the filter control
# filter_pane = folium.features.CustomPane(z_index=1000, name='filter_pane')
# dis_map.add_child(filter_pane)

# # Create a filter control in the filter pane
# filter_control_html = """
# <div style="background-color: white; padding: 10px; border-radius: 5px;">
#     <h4>Filter Data</h4>
#     <label><input type="checkbox" id="filter_us" checked> Inside US</label><br>
#     <label><input type="checkbox" id="filter_outside_us" checked> Outside US</label><br>
# </div>
# """
# filter_control = folium.IFrame(html=filter_control_html, width=150, height=120)
# filter = folium.MacroElement()
# filter._template = folium.ElementTemplate(template=filter_control)
# dis_map.get_root().add_child(filter)

# # Perform a spatial join to filter data points within the US
# data_gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data['long'], data['lat'], crs="EPSG:4326"))
# data_within_us = gpd.sjoin(data_gdf, us_border_gdf, op="within")

# Add markers for each row in the DataFrame
markers = []
for index, row in data.iterrows():
    marker = folium.Marker(
        location=[row['lat'], row['long']],
        popup=f"{row['site_name']} - {row['note']}",
        icon=folium.Icon(icon="cloud"),
    ).add_to(dis_map)
    markers.append(marker)

# Define a custom style function for the Fire layer
def fire_style(feature):
    return {
        'fillColor': 'red',  # Set the fill color to red
        'color': 'red',  # Set the border color to red
    }

# Define a custom style function for the Air layer
def air_style(feature):
    return {
        'fillColor': 'blue',  # Set the fill color to blue
        'color': 'blue',  # Set the border color to blue
    }

# Overlay the Layers with custom styles
fire_layer = folium.GeoJson(fire_geojson, name='Fire', style_function=fire_style)
air_layer = folium.GeoJson(air_geojson, name='Air', style_function=air_style)


# Add to maps
fire_layer.add_to(dis_map)
air_layer.add_to(dis_map)

# # Function to update marker visibility based on filter
# def update_marker_visibility():
#     filter_us = dis_map.get_root().filter_us.checked
#     filter_outside_us = dis_map.get_root().filter_outside_us.checked

#     for marker in markers:
#         lat, lon = marker.location
#         # Perform your own logic to check if the marker is inside or outside the US
#         # Here, we are using a simple example where we check the longitude
#         if filter_us and -125 <= lon <= -65:
#             marker.add_to(dis_map)
#         elif filter_outside_us and (lon < -125 or lon > -65):
#             marker.add_to(dis_map)
#         else:
#             marker.get_root().render()

# # Add a callback to update marker visibility when the filter is changed
# dis_map.get_root().filter_us.add_callback(update_marker_visibility)
# dis_map.get_root().filter_outside_us.add_callback(update_marker_visibility)

# Add Layer Control
folium.LayerControl().add_to(dis_map)


dis_map.save("./maps/interactive_map_with_show_hide_button.html")
