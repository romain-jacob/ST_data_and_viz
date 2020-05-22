from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from app import app
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_f_TimeDelta
import src.colors as colors

# Load the main DataFrame
DataPath = Path('data_preprocessed')
df = parse_all_data()

# Initialize the figures
BLE2M_plot = go.Figure()
BLE1M_plot = go.Figure()
BLE500k_plot = go.Figure()
BLE125k_plot = go.Figure()
ZigBeeSamePacket_plot = go.Figure()
ZigBeeDiffPacket_plot = go.Figure()

# Initialize custom figure layout
custom_layout = dict(
    title = 'Prout',
    showlegend = False,
    margin = dict(t=150),
    xaxis = {'tickvals':[-16,-8,0,8,16]},
)

# Helpers
ShowThreshold = 1
ShowMarkers = 2
ShowCI = 3

layout = html.Div([

    html.Div(
        html.P([
            html.H2('The "Constructive Interference" Effect'),
            html.Strong('Without power delta, synchronous transmissions can still be successful when'),
            html.Br(style={'margin-bottom':0}),
            html.Strong('(i) the same packets are sent'),
            html.Br(style={'margin-bottom':0}),
            html.Strong('(ii) the time delta between the transmitters are sufficiently small'),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
                For the 4 Bluetooth modes (left and middle columns) the median PRR drops to 0 when the time delta between transmitters becomes too big. The bounds found in our experiments are marked and labeled with the tolerable time delta (in ratio of the symbol period and the corresponding time in μs).
                '''),
            html.Br(style={'margin-bottom':0}),
            html.Span('''
                In previous studies, authors have concluded that Bluetooth modes cannot tolerate more than τ /4 of delay; our results show that some modes can.
                '''),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
                For IEEE 802.15.4 (right column), the PRR never drops to 0 thanks to the DSSS error correction (top row); thus we redefine the “constructive interference” region as the time deltas for which the PRR is 0 when transmitters send different packets (bottom row). We observe a limit around τ /2 (or 0.25 μs), which matches previous studies.
                '''),
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
                {'label' : 'Show run data', 'value': ShowMarkers},
                {'label' : 'Show confidence intervals', 'value': ShowCI},
                {'label' : 'Show threshold', 'value': ShowThreshold},
            ],
            value=[ShowMarkers, ShowCI, ShowThreshold],
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
    # Plots - First Row
    # =================

    html.H6(
        "All plots show data with an estimated power delta of 0 dB.",
        style={'margin-left':20}
    ),

    html.Div([

        # =================
        # Fist column
        html.Div([
            # -> Same packet content
            dcc.Graph(
                id='BLE2M_graph',
                figure=BLE2M_plot
            ),
        ], className="four columns"),
        # =================

        # =================
        # Second column
        html.Div([
            # -> Diff packet content
            dcc.Graph(
                id='BLE1M_graph',
                figure=BLE1M_plot
            ),
        ], className="four columns"),
        # =================

        # =================
        # Third column
        html.Div([
            # -> Diff packet content
            dcc.Graph(
                id='ZigBeeSamePacket_graph',
                figure=ZigBeeSamePacket_plot
            ),
        ], className="four columns"),
        # =================

    ], className="row"),


    # =================
    # Plots - Second Row
    # =================
    html.Div([

        # =================
        # Fist column
        html.Div([
            # -> Same packet content
            dcc.Graph(
                id='BLE500k_graph',
                figure=BLE500k_plot
            ),
        ], className="four columns"),
        # =================

        # =================
        # Second column
        html.Div([
            # -> Diff packet content
            dcc.Graph(
                id='BLE125k_graph',
                figure=BLE125k_plot
            ),
        ], className="four columns"),
        # =================

        # =================
        # Third column
        html.Div([
            # -> Diff packet content
            dcc.Graph(
                id='ZigBeeDiffPacket_graph',
                figure=ZigBeeDiffPacket_plot
            ),
        ], className="four columns"),
        # =================

    ], className="row"),

])

@app.callback(
    Output('BLE2M_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'BLE_2M'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        1, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label']
    figure.update_layout(custom_layout)
    return figure

@app.callback(
    Output('BLE1M_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'BLE_1M'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        1, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label']
    figure.update_layout(custom_layout)
    return figure

@app.callback(
    Output('BLE500k_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'BLE_500K'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        1, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label']
    figure.update_layout(custom_layout)
    return figure

@app.callback(
    Output('BLE125k_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'BLE_125K'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        1, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label']
    figure.update_layout(custom_layout)
    return figure

@app.callback(
    Output('ZigBeeSamePacket_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'ZigBee'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        1, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label'] + '<br>Same packet content'
    figure.update_layout(custom_layout)
    return figure

@app.callback(
    Output('ZigBeeDiffPacket_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks'),],
    [State('transmitter-pair', 'value'),
     State('enable-options', 'value'),])
def update_TimeDelta_graph(n_clicks,TransPair,Enable):
    mode = 'ZigBee'
    figure = prr_f_TimeDelta(
        df,
        0, #TimeDelta,
        0, #SamePayload,
        TransPair,
        [mode], #ModesToShow,
        DataPath,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        showTimeThreshold=(ShowThreshold in Enable)
        )
    custom_layout['title'] = Modes[mode]['label'] + '<br>Different packet content'
    figure.update_layout(custom_layout)
    return figure
