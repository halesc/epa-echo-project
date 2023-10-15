import folium

# Create a Map object
m = folium.Map(location=[51.5074, -0.1278], zoom_start=12, tiles="CartoDB dark_matter" ) # London coordinates

# Add a Marker to the map
folium.Marker(
    location=[51.5074, -0.1278],  # Location for the marker
    popup="London",  # Popup text
    icon=folium.Icon(icon="cloud"),  # Icon for the marker
).add_to(m)

# Save the map to an HTML file
m.save("./dark_map.html")

# Display the map in a Jupyter Notebook
# If you're using Jupyter Notebook, you can simply display the map like this:
# m


