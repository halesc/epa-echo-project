# https://github.com/plotly/dash-sample-apps/tree/main
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

# Sample data
data = pd.DataFrame({
    'State': ['California', 'California', 'New York', 'Texas', 'New York', 'Texas'],
    'County': ['Los Angeles', 'San Francisco', 'New York County', 'Harris', 'Kings', 'Dallas'],
    'Population': [10000000, 800000, 8500000, 4500000, 2700000, 2800000],
    'Area': [4687, 121, 468.9, 1772, 113, 881],
})

app.layout = html.Div([
    dcc.Graph(id='map'),
    dcc.Dropdown(id='state-selector', options=[{'label': state, 'value': state} for state in data['State'].unique()], value='All')
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

    fig = px.scatter_geo(filtered_data, locationmode='USA-states', scope='usa', locations='State', text='County', size='Population')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

# python src/dash_test1.py 