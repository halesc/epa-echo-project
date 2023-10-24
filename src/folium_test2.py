import folium
from folium.plugins import TagFilterButton
from folium.plugins import Search
from folium.plugins import LocateControl
import pandas as pd
import numpy as np
import geopandas

def create_base_map(df, lat_col, lon_col):
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=5)
    return m

def add_citation_count_layer(m, df, states, state_abbreviations):
    citation_count_layer = folium.FeatureGroup(name="Citation Count by State")

    def style_function_count(x):
        state_name = x["properties"]["name"]
        state_abbreviation = state_abbreviations.get(state_name, state_name)
        citation_count = df[df['state'] == state_abbreviation]['state'].count()
        
        return {
            "fillColor": f"#ff0000{citation_count:02}",
            "color": "black",
            "weight": 2,
            "fillOpacity": 0.6
        }

    stategeo_count = folium.GeoJson(
        states,
        style_function=style_function_count,
        tooltip=folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["State"],
            localize=True
        ),
    ).add_to(citation_count_layer)

    citation_count_layer.add_to(m)
    return m

def add_avg_compliance_cost_layer(m, df, states, state_abbreviations):
    avg_cost_layer = folium.FeatureGroup(name="Avg Compliance Cost by State")

    def style_function_avg_cost(x):
        state_name = x["properties"]["name"]
        state_abbreviation = state_abbreviations.get(state_name, state_name)
        avg_compliance_action = df[df['state'] == state_abbreviation]['compliance_action_cost'].mean()
        
        if pd.notna(avg_compliance_action):
            min_cost = df['compliance_action_cost'].min()
            max_cost = df['compliance_action_cost'].max()
            normalized_cost = (avg_compliance_action - min_cost) / (max_cost - min_cost)

            return {
                "fillColor": f"#ff0000{int(normalized_cost * 100):02}",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6
            }
        else:
            return {
                "fillColor": "#cccccc",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.6
            }

    stategeo_avg_cost = folium.GeoJson(
        states,
        style_function=style_function_avg_cost,
        tooltip=folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["State"],
            localize=True
        ),
    ).add_to(avg_cost_layer)

    avg_cost_layer.add_to(m)
    return m

def add_data_points_layer(m, df, lat_col, lon_col):
    data_points_layer = folium.FeatureGroup(name="Unique Citation")

    for index, row in df.iterrows():
        latlng = (row[lat_col], row[lon_col])
        popup = ", ".join([f"{col}: {row[col]}" for col in df.columns])

        icon_html = """
        <div style="font-size: 8px; color: red;">
          <i class="fas fa-exclamation-circle"></i>
        </div>
        """

        folium.Marker(
            location=latlng,
            popup=popup,
            icon=folium.DivIcon(html=icon_html)
        ).add_to(data_points_layer)

    data_points_layer.add_to(m)
    return m

def create_filtered_map(df, lat_col, lon_col, filter_cols, geospatial_layers=None, layer_names=None, boeing_data=None, states_geo=None):
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
    
    m = create_base_map(df, lat_col, lon_col)

    if "Citation Count by State" in geospatial_layers:
        m = add_citation_count_layer(m, df, geospatial_layers["Citation Count by State"], state_abbreviations)

    if "Avg Compliance Cost by State" in geospatial_layers:
        m = add_avg_compliance_cost_layer(m, df, geospatial_layers["Avg Compliance Cost by State"], state_abbreviations)

    m = add_data_points_layer(m, df, lat_col, lon_col)

    for col in filter_cols:
        categories = df[col].unique()
        categories_sorted = sorted(str(categories))
        TagFilterButton(categories_sorted, name=col).add_to(m)

    if boeing_data is not None:
        boeing_layer = folium.FeatureGroup(name="Boeing Locations")
        boeing_layer.add_to(m)

        for index, row in boeing_data.iterrows():
            latlng = (row['Latitude'], row['Longitude'])
            
            icon = folium.CustomIcon(
                icon_image='https://palmettogoodwill.org/wp-content/uploads/2022/04/png-transparent-boeing-logo-boeing-business-jet-logo-boeing-commercial-airplanes-integrated-blue-company-text.png',
                icon_size=(20, 20)
            )
            
            folium.Marker(
                location=latlng,
                icon=icon,
            ).add_to(boeing_layer)

    folium.LayerControl(collapsed=False).add_to(m)

    return m

######################## DATA PREP ####################################
df = pd.read_csv('../lib/processed/tidy_data.csv')

sample_fraction = 0.05
sample_size = int(len(df) * sample_fraction)

df = df.sample(n=sample_size, random_state=42)
df = df.dropna(subset=['lat', 'long'])

filter_columns = ['primary_law', 'state', 'democrat', 'independent', 'libertarian', 'republican']

states = geopandas.read_file(
    "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json",
    driver="GeoJSON",
)

states_geo = states.to_json()

cities = geopandas.read_file(
    "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_populated_places_simple.geojson",
    driver="GeoJSON",
)

us_cities = geopandas.sjoin(cities, states, how="inner", predicate="within")

pop_ranked_cities = us_cities.sort_values(by="pop_max", ascending=False)[["nameascii", "pop_max", "geometry"]].iloc[:40]

boeing_data = pd.read_csv('../lib/raw/geocoded_data.csv')
boeing_data = boeing_data.dropna(subset=['Latitude', 'Longitude'])

geospatial_layers = {
    "Citation Count by State": states,
    "Avg Compliance Cost by State": states
}

filtered_map = create_filtered_map(df, 'lat', 'long', filter_columns, geospatial_layers=geospatial_layers, boeing_data=boeing_data, states_geo=states_geo)

filtered_map.save('filtered_map.html')
