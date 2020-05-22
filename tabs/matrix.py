from pathlib import Path

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from app import app
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters
from src.plots import prr_matrix_plot
import src.colors as colors

# Load the main DataFrame
DataPath = Path('data_preprocessed')
df = parse_all_data()

# Initialize the figures
matrix_plot = go.Figure()

# Initialize custom figure layout
custom_layout = dict(
    margin = dict(t=100),
    xaxis = {'tickvals':[-16,-8,0,8,16]},
)

# Helpers
ShowMarkers = 2
ShowCI = 3

layout = html.Div([

    html.Div(
        html.P([
            html.H2('Mixed Effects'),
            html.Strong('''
            For the Bluetooth modes, it is not all “constructive interference” or “capture effect”:
            '''),
            html.Br(style={'margin-bottom':0}),
            html.Strong('''
            a power delta smaller than the capture threshold still improves the reception of ST for moderate time delta.
            '''),
            html.Br(style={'margin-bottom':0}),
            html.Strong('''
            In other words, even a small power delta increases the tolerable time delay and improves the PRR.
            '''),
            html.Br(style={'margin-bottom':10}),
            html.Span('''
            Consider for example the 1 Mbit mode: we observe a capture threshold (i.e., when ST becomes successful regardless of the time delta) at about 10 dB.
            '''),
            html.Br(style={'margin-bottom':0}),
            html.Span('''
            However, with only 6 dB power delta, the median PRR is close to 100% for time delta below 16 ticks (1 μs).
            '''),
            html.Br(style={'margin-bottom':0}),
            html.Span('''
            A similar observation can be made for the 125 kbit mode: a 2 dB power delta is sufficient to provide good reliability up to 8 ticks time delta (0.5 μs).
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

        # Power delta (rows)
        html.H5('Power delta to display (in dB)'),
        # Warning
        html.P(
            '''
            Beware: the loading time scales linearly with the number of values selected...
            ''',
            style={
            # border
            'border-left':'solid',
            'border-width':5,
            'border-color':colors.orange,
            'background-color':'white',
            # rest
            'padding':10,
            'width':'50%',
            'margin-bottom':10,
            'margin-top':10
            }
        ),
        dcc.Checklist(
            id='power-delta-list',
            options=[
                {'label' : ('%d'%i), 'value': i} for i in range(-10,11)
             ],
            value=[0,2,4,6,8,10],
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
        }
    ),

    # =================
    # Plots - First Row
    # =================

    # html.H6(
    #     "All plots show data with an estimated power delta of 0 dB.",
    #     style={'margin-left':20}
    # ),

    dcc.Graph(
        id='matrix_graph',
        figure=matrix_plot,
    ),

])


@app.callback(
    Output('matrix_graph', 'figure'),
    [Input('submit-button-state', 'n_clicks')],
    [State('modes', 'value'),
     State('packet-type', 'value'),
     State('transmitter-pair', 'value'),
     State('power-delta-list', 'value'),
     State('enable-options', 'value'),]
     )
def update_matrix_graph(n_clicks,ModesToShow,SamePayload,TransPair,PowerList,Enable):
    figure = prr_matrix_plot(
        df,
        DataPath,
        PowerDeltaList = sorted(PowerList),
        # custom_layout = custom_layout,
        ModesToShow = ModesToShow,
        SamePayload=SamePayload,
        showMarkers=(ShowMarkers in Enable),
        showCI=(ShowCI in Enable),
        rowHeight = 250,
        )
    figure.update_layout(custom_layout)
    return figure
