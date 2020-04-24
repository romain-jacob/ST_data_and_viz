import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from src.preprocess import parse_all_data
from src.helpers import Modes

df = parse_all_data(force_computation=False)

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
        step=None
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
     Input('transmitter-pair', 'value'),])

def update_figure(PowerDelta,SamePayload,TransPair):

    # Filter the data to plot
    filter = (
        (df['TransPair'] == TransPair) &
        (df['SamePayload'] == SamePayload) &
        (df["PowerDelta"] == PowerDelta)
    )
    filtered_df = df.where(filter).dropna()

    # Initialize the list of traces to plot
    traces = []

    # Loop through the modes
    for mode in Modes:

        # Filter specific mode data
        mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
        mode_df = filtered_df.where(mode_filter).dropna()

        # Prepare data to plot
        if len(mode_df) > 0:
            # Extract all data points
            x_data = mode_df["TimeDelta"]
            y_data = mode_df["PRR"]

            # Compute the median line
            x_median = sorted(set(x_data))
            y_median = []
            for x in x_median:
                median_filter = (mode_df["TimeDelta"] == x)
                median_data = mode_df.where(median_filter).dropna().PRR
                y_median.append(np.median(median_data))

        else:
            # Force displaying the trace, even if empty
            x_data = [np.nan]
            y_data = [np.nan]
            x_median = [np.nan]
            y_median = [np.nan]


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

    return {
        'data': traces,
        'layout': dict(
            title={
                'text':'PRR = f(Time Delta) <br> with Power Delta = %d dB' % 0,
            },
            margin={'t':150},
            xaxis={
                'title':{'text':'Transmitters Time Delta [ticks]'},
            },
            yaxis={
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
