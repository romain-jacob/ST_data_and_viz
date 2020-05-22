import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output, State
#
# import pandas as pd
# import numpy as np
# import plotly.graph_objects as go
#
# from src.helpers import Modes, Parameters
# from src.plots import prr_f_TimeDelta, prr_f_PowerDelta, prr_3d
#
# import tabs.general
# import tabs.matrix

# Application stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    external_scripts=[
      'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML',])

# For deployment
server = app.server
# app.config.suppress_callback_exceptions = True
