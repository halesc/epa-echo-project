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
df = pd.read_csv('./lib/processed/tidy_data.csv')
df.head()

# Randomly select 10% of the data (for working locally)
# Calculate the number of rows to sample (10%)
sample_fraction = 0.10
sample_size = int(len(df) * sample_fraction)

# Randomly select 10% of the data
df = df.sample(n=sample_size, random_state=42)
df = df.dropna(subset=['lat', 'long'])

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
# boeing_data = pd.read_csv('../lib/raw/geocoded_data.csv')
# boeing_data = boeing_data.dropna(subset=['Latitude','Longitude'])

# # Create a feature group for host sites
# host_sites_layer = folium.FeatureGroup(name="Host Sites")

# for index, row in boeing_data.iterrows():
#     latlng = (float(row["Latitude"]), float(row["Longitude"]))
#     host_site = row["Host Site"]

#     annotation_columns = ['Description','Site','Property','Address','City']

#     # Create a popup message with annotations
#     popup_html = f"<b>{host_site}</b><br>"
#     for column in annotation_columns:
#         popup_html += f"{column}: {row[column]}<br>"

#     folium.CircleMarker(
#         location=latlng,
#         radius=4,
#         color="green",
#         fill=True,
#         fill_color="green",
#         fill_opacity=.6,
#         popup=popup_html,
#     ).add_to(host_sites_layer)

# # Add the host sites feature group to the map
# host_sites_layer.add_to(m)


########################## Citations

# Define a function to add markers and filters for a specific category
def add_markers_and_filter(df, category_column, map, annotation_columns=[]):
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
        
        # Create a popup message with annotations
        popup_html = f"<b>{category}</b><br>"
        for column in annotation_columns:
            popup_html += f"{column}: {row[column]}<br>"
        
        folium.Marker(
            location=latlng,
            icon=folium.DivIcon(html=icon_html),
            popup=folium.Popup(html=popup_html),  # Use the custom icon and annotation
            tags=[category]
        ).add_to(map)

    TagFilterButton(categories_sorted, name=category_column).add_to(map)

annotations = ['registry_id','primary_law', 'enf_outcome_code','fed_penalty_assessed_amt', 'compliance_action_cost', 'county', 'epa_region', 'air_pollutant_class_code']

# Create markers and filters for 'primary_law' with annotations for 'column1' and 'column2'
add_markers_and_filter(df, 'primary_law', m, annotation_columns=annotations)
# Create markers and filters for 'state' with annotations for 'column3' and 'column4'
add_markers_and_filter(df, 'state', m, annotation_columns=annotations)

# Create a HeatMap layer
heat_data = [[row['lat'], row['long']] for index, row in df.iterrows()]
heat_map = HeatMap(heat_data, name= "HeatMap")
heat_map.add_to(m)

folium.LayerControl().add_to(m)
folium.plugins.LocateControl(auto_start=False).add_to(m)
m.save('./lib/maps/map.html')






