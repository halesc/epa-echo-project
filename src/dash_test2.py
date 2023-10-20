# https://github.com/plotly/dash-sample-apps/tree/main
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json
import requests

app = dash.Dash(__name__)

# Load GeoJSON data for U.S. states and counties
with open("./lib/us-state-boundaries.geojson") as f:
    us_states = json.load(f)

url_counties = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
us_counties = json.loads(requests.get(url_counties).text)

# Sample data (you can replace this with your actual data)
data = pd.DataFrame({
    'State': ['California', 'California', 'New York', 'Texas', 'New York', 'Texas'],
    'County': ['Los Angeles', 'San Francisco', 'New York County', 'Harris', 'Kings', 'Dallas'],
    'Population': [10000000, 800000, 8500000, 4500000, 2700000, 2800000],
    'Area': [4687, 121, 468.9, 1772, 113, 881],
})

app.layout = html.Div([
    dcc.Graph(
        id='map',
        config={'scrollZoom': False},
        style={'width': '100%', 'height': '100vh'}
    ),
    dcc.Dropdown(
        id='state-selector',
        options=[{'label': state, 'value': state} for state in data['State'].unique()],
        value='All'
    )
])

@app.callback(
    Output('map', 'figure'),
    Input('state-selector', 'value')
)
def update_map(selected_state):
    if selected_state == 'All':
        filtered_data = data
    else:
        filtered_data = data[data['State'] == selected_state]

    fig = px.choropleth(filtered_data, locations='State', color='Population', geojson=us_states, featureidkey="properties.NAME",
                        title="U.S. State Boundaries and Population", scope="usa")

    if selected_state != 'All':
        # Add county boundaries for the selected state
        selected_state_counties = [county for county in us_counties['features'] if county['properties']['STATE'] == selected_state]
        county_fig = px.choropleth(locations=[selected_state] * len(selected_state_counties),
                                   geojson={'type': 'FeatureCollection', 'features': selected_state_counties},
                                   featureidkey="properties.NAME", hover_name="County")
        fig.add_traces(county_fig.data)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
