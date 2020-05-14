import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from tabs import general, matrix

# Suppress errors from callback IDs not found
app.config['suppress_callback_exceptions']=True
# mathjax = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML'
# app.scripts.append_script({ 'external_url' : mathjax })

# Main layout
app.layout = html.Div([

    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content'),

])

@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return general.layout
    elif tab == 'tab-2':
        return matrix.layout

if __name__ == '__main__':
    app.run_server(
        debug=True,
        )
