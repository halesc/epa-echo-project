# https://github.com/plotly/dash-sample-apps/tree/main
import dash
import dash_core_components as dcc
import dash_html_components as html
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

# Sample data for major U.S. cities with latitude and longitude
cities = pd.DataFrame({
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia'],
    'Lat': [40.7128, 34.0522, 41.8781, 29.7604, 33.4484, 39.9526],
    'Lon': [-74.0060, -118.2437, -87.6298, -95.3698, -112.0740, -75.1652]
})

fig = px.choropleth(data, locations='State', color='Population', geojson=us_states, featureidkey="properties.NAME",
                    title="U.S. State Boundaries and Population", scope="usa", color_continuous_scale='Viridis')

# Add major U.S. cities as annotated dots
fig.add_trace(px.scatter_geo(cities, lat='Lat', lon='Lon', text='City').data[0])

# Create a text element for displaying the population value
population_text = html.Div(id='population-text', style={'padding': '10px'})

app.layout = html.Div([
    dcc.Graph(figure=fig, config={'scrollZoom': False}, style={'width': '100%', 'height': '100vh'}, id='map'),
    population_text
])

# Callback to update the population value when a state is clicked
@app.callback(
    dash.dependencies.Output('population-text', 'children'),
    [dash.dependencies.Input('map', 'selectedData')]
)
def display_population(selectedData):
    if selectedData is not None:
        selected_state = selectedData['points'][0]['location']
        population = data[data['State'] == selected_state]['Population'].values[0]
        return f"Population of {selected_state}: {population}"
    return ''

if __name__ == '__main__':
    app.run_server(debug=True)
