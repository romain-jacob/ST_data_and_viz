from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from app import app
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_f_TimeDelta, prr_f_PowerDelta, prr_3d
import src.colors as colors

# Load the main DataFrame
DataPath = Path('data_preprocessed')
df = parse_all_data()
TimeDeltaValues = sorted(df['TimeDelta'].dropna().unique())

# Initialize the figures
TimeDelta_plot = go.Figure()
PowerDelta_plot = go.Figure()
threeD_plot = go.Figure()

# Helpers
Show3dPlot = 1
ShowMarkers = 2
ShowCI = 3

layout = html.Div([

    # Tab introduction
    html.Div(
        html.P([
            html.H2('General exploration'),
            html.Strong('''
            For all physical layers (Bluetooth 5 and 802.15.4),
            synchronous tranmittions eventually succeed with sufficiently strong power delta
            and/or sufficiently small time delta.
            '''),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
            The 3D plot shows that the PRR always rises to 100% then the power delta is large; that's the capture effect.
            '''),
            html.Br(style={'margin-bottom':0}),
            html.Span('''
            For smaller power delta, PRR drops to zero unless the time delta is small; that's the constructive interference effect.
            '''),
        ],
        style={
            'width':'50%',
            'margin-left':20,
            'margin-bottom':20,}),
    ),

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
            }
        ),

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

        html.H5('Transmitted packets'),
        dcc.RadioItems(
            id='packet-type',
            options=[
                {'label': 'Same Payload', 'value': 1},
                {'label': 'Different Payload', 'value': 0},
             ],
            value=1
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
                {'label' : 'Show 3D plot', 'value': Show3dPlot},
                {'label' : 'Show individual run data', 'value': ShowMarkers},
                {'label' : 'Show confidence intervals', 'value': ShowCI},
            ],
            value=[Show3dPlot,ShowCI],
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
        }
    ),

    # Containing row
    html.Div([

        # Fist column
        html.Div([

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
            html.Label('Select an estimated power delta at the receiver (in dB)'),
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
            html.Label('Select an estimated time delta between transmittions (in ticks)'),
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
     State('modes', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,PowerDelta,SamePayload,TransPair,ModesToShow,Enable):
    figure = prr_f_TimeDelta(
        df,
        PowerDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable)
        )
    figure.update_layout(dict(xaxis = {'range':[-120,120]}))
    return figure


@app.callback(
    Output('PowerDelta_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),
     Input('time-slider', 'value'),],
    [State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('modes', 'value'),
     State('enable-options', 'value'),])
def update_PowerDelta_graph(n_clicks,TimeDelta,SamePayload,TransPair,ModesToShow,Enable):
    return prr_f_PowerDelta(
        df,
        TimeDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable)
        )

@app.callback(
    Output('3d_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('modes', 'value'),
     State('enable-options', 'value'),])
def update_threeD_graph(n_clicks,SamePayload,TransPair,ModesToShow,Enable):
    if Show3dPlot in Enable:
        return prr_3d(
            df,
            SamePayload,
            TransPair,
            ModesToShow
            )
    else:
        return go.Figure()
