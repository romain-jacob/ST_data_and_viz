from pathlib import Path

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from src.preprocess import parse_all_data
from src.helpers import Modes, Parameters

df = parse_all_data()
data_path = Path('data_preprocessed')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(
        id='graph-with-slider',
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
    html.Label('Select the physical layers of interest'),
    dcc.Checklist(
        id='modes',
        options=[
            {'label' : Modes[i]['label'], 'value': i} for i in Modes
        ],
        value=[i for i in Modes],
        labelStyle={'display': 'inline-block'}
    ),
    html.Label('Select the type of packets sent'),
    dcc.RadioItems(
        id='packet-type',
        options=[
            {'label': 'Same Payload', 'value': 1},
            {'label': 'Different Payload', 'value': 0},
         ],
        value=1,
    ),
    html.Label('Select the pair of transmitters'),
    dcc.RadioItems(
        id='transmitter-pair',
        options=[
            {'label': 'Pair A', 'value': 'A'},
            {'label': 'Pair B', 'value': 'B'},
         ],
        value='A',
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('power-slider', 'value'),
     Input('packet-type', 'value'),
     Input('transmitter-pair', 'value'),
     Input('modes', 'value'),])

def update_figure(PowerDelta,SamePayload,TransPair,ModesToShow):

    # Filter the data to plot
    filter = (
        (df['TransPair'] == TransPair) &
        (df['SamePayload'] == SamePayload) &
        (df["PowerDelta"] == PowerDelta)
    )
    filtered_df = df.where(filter).dropna()

    # Initialize the list of traces to plot
    traces = []

    # Load the median and CI data
    file_path = data_path / Parameters['TransPair'][TransPair]['path'] / Parameters['SamePayload'][SamePayload]['path']
    file_name = 'TimeDeltaTraces_%s_%s_(%i).csv' % (TransPair,SamePayload,PowerDelta)
    df_median = pd.read_csv(file_path / file_name)

    # Loop through the modes
    for mode in ModesToShow:

        # Filter specific mode data
        mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
        mode_df = filtered_df.where(mode_filter).dropna()

        # Prepare data to plot
        if len(mode_df) > 0:
            # Extract all data points
            x_data = mode_df["TimeDelta"].to_list()
            y_data = mode_df["PRR"].to_list()

            # Extract median data
            x_median = df_median["TimeDelta"].to_list()
            y_median = df_median['median_'+mode].to_list()

            # Extract CI data
            y_LB = df_median['LB_'+mode].to_list()
            y_UB = df_median['UB_'+mode].to_list()

            # Prepare the trace for the CI area
            x_CI = x_median + x_median[::-1]
            y_CI = y_LB + y_UB[::-1]


        else:
            # Force displaying the trace, even if empty
            x_data = [np.nan]
            y_data = [np.nan]
            x_median = [np.nan]
            y_median = [np.nan]
            y_LB = [np.nan]
            y_UB = [np.nan]
            x_CI = [np.nan]
            y_CI = [np.nan]

        # Plot raw data
        scatter = dict(
            x=x_data,
            y=y_data,
            mode='markers',
            marker={'color':Modes[mode]['color']},
            showlegend=True,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label'],
            hoverinfo='skip',
            opacity=0.7,
        )
        traces.append(scatter)

        # Plot median line
        median_line = dict(
            x=x_median,
            y=y_median,
            mode='lines',
            line={'color':Modes[mode]['color']},
            showlegend=False,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label']+' median',
        )
        traces.append(median_line)

        CI = dict(
            x=x_CI,
            y=y_CI,
            mode='lines',
            line={
                'color':Modes[mode]['color'],
                'width':0
            },
            showlegend=False,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label']+' CI',
            fill='toself',
            hoverinfo='skip',
            opacity=0.3,
        )
        traces.append(CI)

    return {
        'data': traces,
        'layout': dict(
            title={
                'text':'PRR = f(Time Delta) <br> with Power Delta = %i dB' % PowerDelta,
            },
            margin={'t':150},
            xaxis={
                'title':{'text':'Transmitters Time Delta [ticks]'},
                'range':[-150,150]
            },
            yaxis={
                'title':{'text':'PRR [%]'},
                'range':[0,103]
            },
            transition = {'duration': 500},
            legend = {
                # 'font':{'size':font_size},
                'orientation':"h",
                'x': 0.5,
                'y':1.15,
                'xanchor':"center",
                'yanchor':"top",
            }
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
