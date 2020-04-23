import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
from src.preprocess import parse_all_data

df = parse_all_data(force_computation=False)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(
        id='graph-with-slider',
    ),
    dcc.Slider(
        id='power-slider',
        min=df['PowerDelta'].min(),
        max=df['PowerDelta'].max(),
        value=0,
        marks={str(Delta): str(Delta) for Delta in df['PowerDelta'].unique()},
        step=None
    )
])


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('power-slider', 'value')])

def update_figure(PowerDelta):
    traces = []
    filter = (
        (df['TransPair'] == "B") &
        (df['SamePayload'] == 1) &
        (df["PowerDelta"] == PowerDelta)
        # (df["PowerDelta"] < 9.5) &
        # (8.5 <= df["PowerDelta"])
    )
    filtered_df = df.where(filter).dropna()
    for mode_id in filtered_df["Mode"].unique():

        mode_filter = (filtered_df["Mode"] == mode_id)
        mode_df = filtered_df.where(mode_filter).dropna()
        mode_data = dict(
            x=mode_df["TimeDelta"],
            y=mode_df["PRR"],
            mode='markers',
            showlegend=True,
            name='%s' % mode_id,
            opacity=0.7,
        )
        traces.append(mode_data)

    return {
        'data': traces,
        'layout': dict(
            # xaxis={'type': 'log', 'title': 'GDP Per Capita',
            #        'range':[2.3, 4.8]},
            # yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
            yaxis={
                'range':[0,103]
            },
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            # legend={'x': 0, 'y': 1},
            # hovermode='closest',
            transition = {'duration': 500},
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
