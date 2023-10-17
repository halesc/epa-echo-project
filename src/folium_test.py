import folium
import pandas as pd
import geopandas as gpd

# Create a Map object
m = folium.Map(location=[51.5074, -0.1278], zoom_start=12, tiles="CartoDB dark_matter")  # London coordinates

# Sample DataFrame with your data
data = pd.DataFrame({
    'site_name': ['London', 'Paris', 'New York'],
    'lat': [51.5074, 48.8566, 40.7128],
    'long': [-0.1278, 2.3522, -74.0060],
    'note': ['Capital of the UK', 'Capital of France', 'Big Apple']
})

# Add markers for each row in the DataFrame
for index, row in data.iterrows():
    folium.Marker(
        location=[row['lat'], row['long']],
        popup=f"{row['site_name']} - {row['note']}",
        icon=folium.Icon(icon="cloud"),
    ).add_to(m)



# Load the air pollution shapefile using GeoPandas
air_pollution_shapefile = gpd.read_file("../lib/fire/Perimeters.shp")

# Convert the GeoDataFrame to GeoJSON
air_pollution_geojson = air_pollution_shapefile.to_json()

# Overlay the air pollution data on the map using folium.GeoJson
air_pollution_layer = folium.GeoJson(air_pollution_geojson)
air_pollution_layer.add_to(m)



m.save("../maps/interactive_map_with_show_hide_button.html")


