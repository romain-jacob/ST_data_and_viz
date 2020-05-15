from pathlib import Path

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "none"
from plotly.subplots import make_subplots

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
        'range':[-3,103],
        'tickvals':[0,25,50,75,100]
    },
    # transition = {'duration': 500},
    legend = {
        'orientation':"h",
        'x': 0.5,
        'y':1.15,
        'xanchor':"center",
        'yanchor':"top",
    },
    uirevision = True
)

def prr_matrix_plot(
    df,
    DataPath,
    PowerDeltaList = [0,1,2,3,4],
    rowHeight = 100,
    layout = None,
    showMarkers=False,
    showCI=True,
    SamePayload=1
    ):

    # Initialization
    ModeList = [x for x in Modes]
    numRow = len(PowerDeltaList)
    numCol = len(ModeList)
    AnnotList = []
    figure = make_subplots(
        rows=numRow,
        cols=numCol,
        )

    # Initialize layout
    default_layout = dict(
        showlegend=False,
        margin = dict(l=250, r=20, t=60, b=60),
        height = (rowHeight*numRow),
        width = 2000,
    )
    figure.update_layout(default_layout)
    if layout is not None:
        figure.update_layout(layout)
    layout = figure.layout

    # Compute the plot area width
    plot_width = (layout['width']
        - layout['margin']['l']
        - layout['margin']['r'])
    plot_height = (layout['height']
        - layout['margin']['t']
        - layout['margin']['b'])

    # Setting column labels
    for j in range(numCol):
        col_label = go.layout.Annotation(
                x=((j+0.5)*1/numCol),
                y=(1+layout['margin']['t']/plot_height),
                xref="paper",
                yref="paper",
                text=Modes[ModeList[j]]['label'],
                showarrow=False,
                xanchor='center',
                yanchor='top',
            )
        AnnotList.append(col_label)
    col_label = go.layout.Annotation(
            x=-(layout['margin']['l']/plot_width),
            y=(1+layout['margin']['t']/plot_height),
            xref="paper",
            yref="paper",
            text=('Power<br>Delta'),
            align='left',
            showarrow=False,
            xanchor='left',
        )
    AnnotList.append(col_label)

    for i in range(numRow):

        # Set the row label
        row_label = go.layout.Annotation(
                x=-(layout['margin']['l']/plot_width),
                y=(1 - (i+0.5)*1/numRow),
                xref="paper",
                yref="paper",
                text=('%d dB' % PowerDeltaList[i]),
                showarrow=False,
                xanchor='left',
                yanchor='middle'
            )
        AnnotList.append(row_label)

        for j in range(numCol):

            # Get the figure data
            figure_data = __prep_TimeDelta_plot__(
                df,
                PowerDelta=PowerDeltaList[i],
                SamePayload=SamePayload,
                TransPair='all',
                ModesToShow=[ModeList[j]],
                DataPath=DataPath,
                showMarkers=showMarkers,
                showCI=showCI
                )

            # Add traces to the plot
            for trace in figure_data["data"]:
                figure.add_trace(
                    trace,
                    row=i+1,
                    col=j+1)

    # Customize the layout

    ## X axis
    figure.update_xaxes(
        range=[-50,50],
        )
    figure.update_xaxes(
        title_text='Transmitters Time Delta [ticks]',
        row=numRow, col=3
        )
    ## Y axis
    figure.update_yaxes(
        range=[-3,103],
        )
    figure.update_yaxes(
        title_text='PRR [%]',
        col=1
        )
    ## Add the annotations
    figure.update_layout(
        annotations=AnnotList,
        )

    return figure


def prr_f_TimeDelta(
    df,
    PowerDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath=Path('data_preprocessed'),
    showMarkers=False,
    showCI=True,
    showTimeThreshold=False
    ):

    # Get the figure data
    figure_data = __prep_TimeDelta_plot__(
        df,
        PowerDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=showMarkers,
        showCI=showCI,
        showTimeThreshold=showTimeThreshold
        )

    if figure_data is None:
        return

    # Customize the layout
    final_layout = figure_data["layout"].copy()
    final_layout["title"]["text"] = ('PRR = f(Time Delta) <br> with Power Delta = %i dB' % PowerDelta)
    final_layout["xaxis"]["title"]["text"] = ('Transmitters Time Delta [ticks]')
    # final_layout["xaxis"]["range"] = [-150,150]
    # final_layout["xaxis"]["range"] = [-50,50]
    final_layout["xaxis"]["range"] = [-20,20]
    final_layout["yaxis"]["range"] = [-3,103]
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
    DataPath=Path('data_preprocessed'),
    showMarkers=False,
    showCI=True
    ):

    # Get the figure data
    figure_data = __prep_PowerDelta_plot__(
        df,
        TimeDelta,
        SamePayload,
        TransPair,
        ModesToShow,
        DataPath,
        showMarkers=showMarkers,
        showCI=showCI
        )

    if figure_data is None:
        return

    # Customize the layout
    final_layout = figure_data["layout"].copy()
    final_layout["title"]["text"] = ('PRR = f(Power Delta) <br> with Time Delta = %i ticks' % TimeDelta)
    final_layout["xaxis"]["title"]["text"] = ('Estimated Power Delta at the receiver [dB]')
    final_layout["xaxis"]["range"] = [-17,17]
    final_layout["yaxis"]["range"] = [-3,103]
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
    final_layout = figure_data["layout"].copy()
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
            "range": [0,100],
            'tickvals':[0,25,50,75,100]
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
    DataPath,
    showMarkers=False,
    showCI=True,
    showTimeThreshold=False,
    ):

    # Filter the data to plot
    filter = (
        (df['SamePayload'] == SamePayload) &
        (df["PowerDelta"] == PowerDelta)
    )
    if TransPair != 'all':
        filter = filter & (df['TransPair'] == TransPair)
    filtered_df = df.where(filter).dropna()

    # Initialize the list of traces to plot
    traces = []
    layout = base_layout.copy()
    AnnotList = []

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

        if showMarkers:
            # Plot raw data
            scatter = dict(
                x=x_data,
                y=y_data,
                mode='markers',
                marker={
                    'color':Modes[mode]['color'],
                    'size':3
                },
                showlegend=False,
                legendgroup=Modes[mode]['id'],
                name=Modes[mode]['label'],
                hoverinfo='skip',
                opacity=0.3,
            )
            traces.append(scatter)

        # Plot median line
        median_line = dict(
            x=x_median,
            y=y_median,
            mode='lines',
            line={'color':Modes[mode]['color']},
            showlegend=True,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label']+' median',
        )
        traces.append(median_line)

        if showCI:
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

        # Add annotations
        if showTimeThreshold:
            left_bound = go.layout.Annotation(
                    # label position
                    axref="x",
                    ayref="y",
                    ax=-Modes[mode]['CIthreshold_ticks'],
                    ay=115,
                    # where we point
                    xref="x",
                    yref="y",
                    x=-Modes[mode]['CIthreshold_ticks'],
                    y=0,
                    text=' ',
                    font=dict(color=Modes[mode]['color']),
                    arrowcolor=Modes[mode]['color'],
                    showarrow=True,
                    arrowside='none',
                    borderpad=8,
                )
            AnnotList.append(left_bound)

            right_bound = go.layout.Annotation(
                    # label position
                    axref="x",
                    ayref="y",
                    ax=Modes[mode]['CIthreshold_ticks'],
                    ay=115,
                    # where we point
                    xref="x",
                    yref="y",
                    x=Modes[mode]['CIthreshold_ticks'],
                    y=0,
                    text=(Modes[mode]['CIthreshold_label']),
                    font=dict(color=Modes[mode]['color']),
                    arrowcolor=Modes[mode]['color'],
                    showarrow=True,
                    arrowside='none',
                    borderpad=8,
                )
            AnnotList.append(right_bound)

    # Add annotations to the layout
    layout['annotations'] = AnnotList

    return {
        'data': traces,
        'layout': layout
        }


# ===========================================
def __prep_PowerDelta_plot__(
    df,
    TimeDelta,
    SamePayload,
    TransPair,
    ModesToShow,
    DataPath,
    showMarkers=False,
    showCI=True
    ):

    # Filter the data to plot
    filter = (
        (df['SamePayload'] == SamePayload) &
        (df["TimeDelta"] == TimeDelta)
    )
    if TransPair != 'all':
        filter = filter & (df['TransPair'] == TransPair)
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
        if showMarkers:
            scatter = dict(
                x=x_data,
                y=y_data,
                mode='markers',
                marker={'color':Modes[mode]['color']},
                showlegend=False,
                legendgroup=Modes[mode]['id'],
                name=Modes[mode]['label'],
                hoverinfo='skip',
                opacity=0.3,
            )
            traces.append(scatter)

        # Plot median line
        median_line = dict(
            x=x_median,
            y=y_median,
            mode='lines',
            line={'color':Modes[mode]['color']},
            showlegend=True,
            legendgroup=Modes[mode]['id'],
            name=Modes[mode]['label'],
        )
        traces.append(median_line)

        if showCI:
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
        'layout': base_layout.copy()
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
        (df['SamePayload'] == SamePayload)
    )
    if TransPair != 'all':
        filter = filter & (df['TransPair'] == TransPair)
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
            opacity=0.3,
        )
        traces.append(scatter)

    return {
        'data': traces,
        'layout': base_layout.copy()
        }
