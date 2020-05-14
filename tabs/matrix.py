from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from app import app
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_matrix_plot

# Load the main DataFrame
DataPath = Path('data_preprocessed')
df = parse_all_data()
# TimeDeltaValues = sorted(df['TimeDelta'].dropna().unique())

matrix_plot = go.Figure()

layout = html.Div([
    html.H3('Plot matrix'),
    html.Button(
        id='submit-button-state',
        n_clicks=0,
        children='Update plot',
        style={'margin-top':20}),
    dcc.Graph(
        id='matrix_graph',
        figure=matrix_plot
    ),
])


@app.callback(
    Output('matrix_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    # [State('packet-type', 'value'),
    #  State('transmitter-pair', 'value'),
    #  State('modes', 'value'),]
     )
def update_matrix_graph(n_clicks):
    return prr_matrix_plot(
        df,
        DataPath
        )
