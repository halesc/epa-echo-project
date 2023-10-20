import folium
import pandas as pd
import geopandas as gpd
import json 

# Create a Map object
dis_map = folium.Map(location=[40.7128, -74.0060], zoom_start=6, tiles="CartoDB dark_matter")  # London coordinates

# Load the fire pollution shapefile using GeoPandas
fire_shapefile = gpd.read_file("./lib/fire/Perimeters.shp")
fire_geojson = fire_shapefile.to_json()

air_shapefile = gpd.read_file("./lib/fire/Sevenaoks_Open_Data_-_Air_Pollution_Control_Sites.shp")
air_geojson = air_shapefile.to_json()

site_data = pd.read_csv('./lib/raw/geocoded_data.csv')

# Add markers for each row in the DataFrame
for index, row in site_data.iterrows():
    try:
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['City']} - {row['Site']}",
            icon=folium.Icon(icon="cloud"),
        ).add_to(dis_map)
    except (ValueError):
        print(f"Skipping row {index} due to missing or invalid latitude/longitude values.")

# Load GeoJSON data for U.S. states and counties
with open("./lib/us-state-boundaries.geojson") as f:
    us_border_gdf = json.load(f)

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

# Add the fire and air layers to the map
fire_layer.add_to(dis_map)
air_layer.add_to(dis_map)

# Create a custom filter control using an HTML div
filter_control_html = """
<div style="position: fixed; top: 10px; left: 10px; background-color: white; padding: 10px; border-radius: 5px; z-index: 1000;">
    <h4>Filter by State</h4>
    <select id="state-filter">
        <option value="all">All States</option>
        <option value="Washington">Washington</option>
        <!-- Add more state options as needed -->
    </select>
</div>
"""

# Add the HTML filter control to the map
dis_map.get_root().html.add_child(folium.Element(filter_control_html))

# Define a JavaScript function to filter data by state
filter_js = """
function filterByState(state) {
    var markers = document.getElementsByClassName('leaflet-marker-icon');
    for (var i = 0; i < markers.length; i++) {
        var marker = markers[i];
        var markerState = marker.getAttribute('data-state');
        if (state === 'all' || markerState === state) {
            marker.style.display = 'block';
        } else {
            marker.style.display = 'none';
        }
    }
}
document.getElementById('state-filter').addEventListener('change', function() {
    var selectedState = this.value;
    filterByState(selectedState);
});
"""
# Add the JavaScript code to the map
dis_map.get_root().script.add_child(folium.Element(filter_js))

# Function to add markers with state information
def add_marker_with_state(row, state):
    try:
        marker = folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['City']} - {row['Site']}",
            icon=folium.Icon(icon="cloud"),
            data_state=state
        )
        marker.add_to(dis_map)
    except (ValueError):
        print(f"Skipping row {index} due to missing or invalid latitude/longitude values.")

# Add markers with state information
for state in site_data['State'].unique():
    state_data = site_data[site_data['State'] == state]
    for index, row in state_data.iterrows():
        add_marker_with_state(row, state)

# Add Layer Control
folium.LayerControl().add_to(dis_map)

# Save the map
dis_map.save("./maps/interactive_map_with_state_filter.html")
