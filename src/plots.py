from pathlib import Path

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "none"

from src.helpers import Modes, Parameters
import src.colors as colors

base_layout =  dict(
    title={
        'text':'Title to update in function',
    },
    xaxis={
        'title':{'text':'x axis title to update'},
    },
    yaxis={
        'title':{'text':'PRR [%]'},
        'range':[-3,103]
    },
    transition = {'duration': 500},
    legend = {
        'orientation':"h",
        'x': 0.5,
        'y':1.15,
        'xanchor':"center",
        'yanchor':"top",
    },
)

def prr_f_TimeDelta(
    df,
    PowerDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath=Path('data_preprocessed')
    ):

    # Get the figure data
    figure_data = __prep_TimeDelta_plot__(
        df,
        PowerDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath
        )

    if figure_data is None:
        return

    # Customize the layout
    final_layout = figure_data["layout"]
    final_layout["title"]["text"] = ('PRR = f(Time Delta) <br> with Power Delta = %i dB' % PowerDelta)
    final_layout["xaxis"]["title"]["text"] = ('Transmitters Time Delta [ticks]')
    final_layout["xaxis"]["range"] = [-150,150]
    final_layout["height"] = 450
    final_layout["margin"] = {'t':150}

    # Generate the figure
    figure = go.Figure()
    for trace in figure_data["data"]:
        figure.add_traces(trace)
    figure.update_layout(final_layout)

    return figure

def prr_f_PowerDelta(
    df,
    TimeDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath=Path('data_preprocessed')
    ):

    # Get the figure data
    figure_data = __prep_PowerDelta_plot__(
        df,
        TimeDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath
        )

    if figure_data is None:
        return

    # Customize the layout
    final_layout = figure_data["layout"]
    final_layout["title"]["text"] = ('PRR = f(Power Delta) <br> with Time Delta = %i ticks' % TimeDelta)
    final_layout["xaxis"]["title"]["text"] = ('Estimated Power Delta at the receiver [dB]')
    final_layout["xaxis"]["range"] = [-17,17]
    final_layout["height"] = 450
    final_layout["margin"] = {'t':150}

    # Generate the figure
    figure = go.Figure()
    for trace in figure_data["data"]:
        figure.add_traces(trace)
    figure.update_layout(final_layout)

    return figure


def prr_3d(
    df,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath=Path('data_preprocessed')
    ):

    # Get the figure data
    figure_data = __prep_3d_plot__(
        df,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath
        )

    if figure_data is None:
        return

    # Customize the layout
    final_layout = figure_data["layout"]
    final_layout["title"]["text"] = ''
    final_layout["scene"] = dict(
        xaxis = {
            "title":{"text":'Estimated Power Delta at the receiver [dB]'},
            "range": [-17,17]
            },
        yaxis = {
            "title":{"text":'Transmitters Time Delta [ticks]'},
            "range": [-150,150]
            },
        zaxis = {
            "title":{"text":'PRR [%]'},
            "range": [0,100]
            },
        aspectmode= 'cube',
    )
    final_layout["height"] = 900
    final_layout["margin"] = {'t':0}

    # Generate the figure
    figure = go.Figure()
    for trace in figure_data["data"]:
        figure.add_traces(trace)
    figure.update_layout(final_layout)

    return figure


def __prep_TimeDelta_plot__(
    df,
    PowerDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath
    ):

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
    file_path = DataPath / Parameters['TransPair'][TransPair]['path'] / Parameters['SamePayload'][SamePayload]['path']
    file_name = 'TimeDeltaTraces_%s_%s_(%i).csv' % (TransPair,SamePayload,PowerDelta)
    try:
        df_median = pd.read_csv(file_path / file_name)
    except FileNotFoundError:
        print("[ERROR] Use the 'DataPath' argument to indicate the path to your time delta traces.")
        print("\tAssumed Path(\'data_preprocessed\') by default but nothing found there...")
        return

    # Loop through the modes
    for mode in ModesToShow:

        # Filter specific mode data
        mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
        mode_df = filtered_df.where(mode_filter).dropna()
        df_median_mode = df_median[["TimeDelta", 'median_'+mode, 'LB_'+mode, 'UB_'+mode]].dropna()

        # Prepare data to plot
        if len(mode_df) > 0:
            # Extract all data points
            x_data = mode_df["TimeDelta"].to_list()
            y_data = mode_df["PRR"].to_list()

            # Extract median data
            x_median = df_median_mode["TimeDelta"].to_list()
            y_median = df_median_mode['median_'+mode].to_list()

            # Extract CI data
            y_LB = df_median_mode['LB_'+mode].to_list()
            y_UB = df_median_mode['UB_'+mode].to_list()

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

        ## For debugging only
        # # Plot LB line
        # LB_line = dict(
        #     x=x_median,
        #     y=y_LB,
        #     mode='lines',
        #     line={'color':colors.blue},
        #     showlegend=False,
        #     legendgroup=Modes[mode]['id'],
        #     name=Modes[mode]['label']+' median',
        # )
        # traces.append(LB_line)
        #
        # # Plot LB line
        # UB_line = dict(
        #     x=x_median,
        #     y=y_UB,
        #     mode='lines',
        #     line={'color':colors.green},
        #     showlegend=False,
        #     legendgroup=Modes[mode]['id'],
        #     name=Modes[mode]['label']+' median',
        # )
        # traces.append(UB_line)

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
        'layout': base_layout
        }


# ===========================================
def __prep_PowerDelta_plot__(
    df,
    TimeDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath
    ):

    # Filter the data to plot
    filter = (
        (df['TransPair'] == TransPair) &
        (df['SamePayload'] == SamePayload) &
        (df["TimeDelta"] == TimeDelta)
    )
    filtered_df = df.where(filter).dropna()

    # Initialize the list of traces to plot
    traces = []

    # Load the median and CI data
    file_path = DataPath / Parameters['TransPair'][TransPair]['path'] / Parameters['SamePayload'][SamePayload]['path']
    file_name = 'PowerDeltaTraces_%s_%s_(%i).csv' % (TransPair,SamePayload,TimeDelta)
    try:
        df_median = pd.read_csv(file_path / file_name)
    except FileNotFoundError:
        print("[ERROR] Use the 'DataPath' argument to indicate the path to your power delta traces.")
        print("\tAssumed Path(\'data_preprocessed\') by default but nothing found there...")
        return

    # Loop through the modes
    for mode in ModesToShow:

        # Filter specific mode data
        mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
        mode_df = filtered_df.where(mode_filter).dropna()
        df_median_mode = df_median[["PowerDelta", 'median_'+mode, 'LB_'+mode, 'UB_'+mode]].dropna()

        # Prepare data to plot
        if len(mode_df) > 0:
            # Extract all data points
            x_data = mode_df["PowerDelta"].to_list()
            y_data = mode_df["PRR"].to_list()

            # Extract median data
            x_median = df_median_mode["PowerDelta"].to_list()
            y_median = df_median_mode['median_'+mode].to_list()

            # Extract CI data
            y_LB = df_median_mode['LB_'+mode].to_list()
            y_UB = df_median_mode['UB_'+mode].to_list()

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
        'layout': base_layout
        }

# ===========================================
def __prep_3d_plot__(
    df,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath
    ):

    # Filter the data to plot
    filter = (
        (df['TransPair'] == TransPair) &
        (df['SamePayload'] == SamePayload)
    )
    filtered_df = df.where(filter).dropna()

    # Initialize the list of traces to plot
    traces = []

    # Loop through the modes
    for mode in ModesToShow:

        # Filter specific mode data
        mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
        mode_df = filtered_df.where(mode_filter).dropna()

        # Prepare data to plot
        if len(mode_df) > 0:
            # Extract all data points
            x_data = mode_df["PowerDelta"].to_list()
            y_data = mode_df["TimeDelta"].to_list()
            z_data = mode_df["PRR"].to_list()

        else:
            # Force displaying the trace, even if empty
            x_data = [np.nan]
            y_data = [np.nan]
            z_data = [np.nan]

        # Plot raw data
        scatter = dict(
            type="scatter3d",
            x=x_data,
            y=y_data,
            z=z_data,
            mode='markers',
            marker={'color':Modes[mode]['color']},
            showlegend=True,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label'],
            hoverinfo='skip',
            opacity=0.7,
        )
        traces.append(scatter)

    return {
        'data': traces,
        'layout': base_layout
        }