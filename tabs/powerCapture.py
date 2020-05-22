from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from app import app
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_f_PowerDelta
import src.colors as colors

# Load the main DataFrame
DataPath = Path('data_preprocessed')
df = parse_all_data()
TimeDeltaValues = sorted(df['TimeDelta'].dropna().unique())

# Initialize the figures
SamePacket_plot = go.Figure()
DiffPacket_plot = go.Figure()

# Helpers
Show3dPlot = 1
ShowMarkers = 2
ShowCI = 3

layout = html.Div([

    html.Div(
        html.P([
            html.H2('The Power Capture Effect'),
            html.Strong('Synchronous Transmissions are successful for all modes when the power delta at the receiver becomes sufficient.'),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
                When the same packet is sent by the transmitters (left plot), the median PRR is close to or larger than 50%
                even without any power delta. In these conditions, the “constructive interference” effect helps the reception of ST.
                '''
            ),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
                When different packets are sent (right plot), the PRR requires a larger power delta (between 2 and 10 dB depending on the mode) to reach 100%.
                The minimum power delta beyond which ST is successful independently of the time delta (i.e., capture effect threshold) is even larger.
                '''
            ),
            html.Br(),
            html.Span('''
                This can be observed by changing the time delta (slider below the plots).
                '''
            ),
        ],
        style={
            'width':'50%',
            'margin-left':20,
            'margin-bottom':20,}),
    ),

    # =================
    # Data Selectors
    # =================

    # Container row
    html.Div([

        # Box title
        html.H3('Data selectors'),

        # Basic instructions
        html.Div([
            html.Span('''
                The following settings filter the data being showed in the plots below.
                '''),
            html.Br(),
            html.Span('''
                > The default settings reproduce the figure shown in the paper.
                '''),
            html.Br(),
            html.Span('''
                > You can change the settings and update the plots by clicking the "Update plots" button.
                '''),
            ],
            style={
                # border
                'border-left':'solid',
                'border-width':5,
                'border-color':colors.orange,
                'background-color':colors.light_orange,
                # rest
                'padding':10,
                'width':'50%',
                'margin-bottom':20
            }),

        # Physical layers
        html.H5('Physical layers to display'),
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

        # Transmitter pairs
        html.H5('Pairs of transmitter to display'),
        dcc.RadioItems(
            id='transmitter-pair',
            options=[
                {'label': 'Pair A', 'value': 'A'},
                {'label': 'Pair B', 'value': 'B'},
                {'label': 'Both', 'value': 'all'},
             ],
            value='all',
            labelStyle={
                'display': 'inline-block',
                'padding-right':10}
        ),

        # Other options
        html.H5('Other options'),
        dcc.Checklist(
            id='enable-options',
            options=[
                # {'label' : 'Show 3D plot', 'value': Show3dPlot},
                {'label' : 'Show run data', 'value': ShowMarkers},
                {'label' : 'Show confidence intervals', 'value': ShowCI}
            ],
            value=[ShowCI],
            labelStyle={
                'display': 'inline-block',
                'padding-right':10}
        ),

        # Submit button
        html.Button(
            id='submit-button-state',
            n_clicks=0,
            children='Update plots',
            style={
                'margin-top':20,
                'background-color':'white'
                }
        ),

    ], style={
        'background-color':colors.light_grey,
        'padding':20
        }),

    # =================
    # Plots row
    # =================
    html.Div([

        # =================
        # Fist column
        html.Div([
            # -> Same packet content
            dcc.Graph(
                id='SamePacket_graph',
                figure=SamePacket_plot
            ),
        ], className="six columns"),
        # =================

        # =================
        # Second column
        html.Div([
            # -> Diff packet content
            dcc.Graph(
                id='DiffPacket_graph',
                figure=DiffPacket_plot
            ),
        ], className="six columns"),
        # =================

    ], className="row"),

    # Time delta
    html.H4(
        'Estimated time delta between transmittions (in ticks)',
        style={'textAlign': 'center',}
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
])

@app.callback(
    Output('SamePacket_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),
     Input('time-slider', 'value'),],
    [State('transmitter-pair', 'value'),
     State('modes', 'value'),
     State('enable-options', 'value'),])
def update_PowerDelta_graph(n_clicks,TimeDelta,TransPair,ModesToShow,Enable):
    return prr_f_PowerDelta(
        df,
        TimeDelta,
        1, #SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable)
        )

@app.callback(
    Output('DiffPacket_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),
     Input('time-slider', 'value'),],
    [State('transmitter-pair', 'value'),
     State('modes', 'value'),
     State('enable-options', 'value'),])
def update_PowerDelta_graph(n_clicks,TimeDelta,TransPair,ModesToShow,Enable):
    return prr_f_PowerDelta(
        df,
        TimeDelta,
        0, #SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable)
        )
