from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_f_TimeDelta, prr_f_PowerDelta, prr_3d

# Application stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Load the main
DataPath = Path('data_preprocessed')
df = parse_all_data()
TimeDeltaValues = sorted(df['TimeDelta'].dropna().unique())

# Initialize the figures
TimeDelta_plot = go.Figure()
PowerDelta_plot = go.Figure()
threeD_plot = go.Figure()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# For deployment
server = app.server

app.layout = html.Div([

    # Containing row
    html.Div([

        # Fist column
        html.Div([
            # =================
            # Data Selectors
            # =================
            html.H2('Data Selection'),
            html.Label('Select the physical layers of interest'),
            dcc.Checklist(
                id='modes',
                options=[
                    {'label' : Modes[i]['label'], 'value': i} for i in Modes
                ],
                value=[i for i in Modes],
                labelStyle={
                    'display': 'inline-block',
                    'padding-right':10}
            ),

            html.Div([
                html.Div([
                    html.Label('Select the type of packets sent'),
                    dcc.RadioItems(
                        id='packet-type',
                        options=[
                            {'label': 'Same Payload', 'value': 1},
                            {'label': 'Different Payload', 'value': 0},
                         ],
                        value=1
                    ),
                ], className="six columns"),
                html.Div([
                    html.Label('Select the pair of transmitters'),
                    dcc.RadioItems(
                        id='transmitter-pair',
                        options=[
                            {'label': 'Pair A', 'value': 'A'},
                            {'label': 'Pair B', 'value': 'B'},
                         ],
                        value='A',
                    ),
                ], className="six columns"),
            ], className="row", style={'padding-top':10}),
            html.Button(
                id='submit-button-state',
                n_clicks=0,
                children='Update plots',
                style={'margin-top':20}),

            # Horizontal separator
            html.Hr(),

            # =================
            # 3D Graph
            # =================
            dcc.Graph(
                id='3d_graph',
                figure=threeD_plot
            ),
        ], className="six columns"),

        # Second column
        html.Div([
            # ================
            # Time Delta Graph
            # ================
            dcc.Graph(
                id='TimeDelta_graph',
                figure=TimeDelta_plot
            ),
            html.Label('Select the estimated power delta at the receiver (in dB)'),
            dcc.Slider(
                id='power-slider',
                min=-16,
                max=16,
                value=0,
                marks={str(Delta): str(Delta) for Delta in range(-16,17)},
                step=None,
                included=False
            ),

            # Horizontal separator
            html.Hr(),

            # =================
            # Power Delta Graph
            # =================
            dcc.Graph(
                id='PowerDelta_graph',
                figure=PowerDelta_plot
            ),
            dcc.Slider(
                    id='time-slider',
                    min=-140,
                    max=140,
                    value=0,
                    marks={str(Delta): str(Delta) for Delta in TimeDeltaValues},
                    step=None,
                    included=False
                ),
        ], className="six columns"),
    ], className="row")
])


@app.callback(
    Output('TimeDelta_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),
     Input('power-slider', 'value'),],
    [State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('modes', 'value'),])
def update_TimeDelta_graph(n_clicks,PowerDelta,SamePayload,TransPair,ModesToShow):
    return prr_f_TimeDelta(
        df,
        PowerDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath
        )


@app.callback(
    Output('PowerDelta_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),
     Input('time-slider', 'value'),],
    [State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('modes', 'value'),])
def update_PowerDelta_graph(n_clicks,TimeDelta,SamePayload,TransPair,ModesToShow):
    return prr_f_PowerDelta(
        df,
        TimeDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath
        )

@app.callback(
    Output('3d_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('modes', 'value'),])
def update_threeD_graph(n_clicks,SamePayload,TransPair,ModesToShow):
    return prr_3d(
        df,
        SamePayload,
        TransPair,
        ModesToShow
        )


if __name__ == '__main__':
    app.run_server(debug=True)
