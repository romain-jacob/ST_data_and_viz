import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from tabs import general, matrix, powerCapture, constructiveInterference

# Suppress errors from callback IDs not found
app.config['suppress_callback_exceptions']=True
# mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
# app.scripts.append_script({ 'external_url' : mathjax })

# Main layout
app.layout = html.Div([

    dcc.Tabs(
        id='tabs-example',
        children=[
            dcc.Tab(label='Data Exploration', value='tab-general'),
            dcc.Tab(label='Power Capture Effect', value='tab-capture'),
            dcc.Tab(label='Constructive Interference', value='tab-CI'),
            dcc.Tab(label='Mixed Effects', value='tab-matrix'),
        ],
        value='tab-matrix' ),
    html.Div(id='tabs-example-content'),

])

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-general':
        return general.layout
    elif tab == 'tab-capture':
        return powerCapture.layout
    elif tab == 'tab-CI':
        return constructiveInterference.layout
    elif tab == 'tab-matrix':
        return matrix.layout

if __name__ == '__main__':
    app.run_server(
        debug=True,
        )
