import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from tabs import general, matrix, powerCapture, constructiveInterference
import src.colors as colors

# Suppress errors from callback IDs not found
app.config['suppress_callback_exceptions']=True

# For deployment
server = app.server

# Main layout
app.layout = html.Div([

    # Introduction block
    html.H1('Synchronous transmissions on Bluetooth 5 and IEEE 802.15.4 – A replication study'),

    html.Div([
        html.P(
            html.Strong('Welcome to the synchronous transmission data visualization app!'),
        ),
        html.P(
            '''
            The app is separated in several tabs, where each tab fetches a given part of the dataset and produces plots highlighting
            specific aspects/findings.
            '''),
        html.P([
            html.Span('''
                All the plots are dynamic: you can zoom in, get point values on hover,
                or toggle for traces on and off (click on the legend).
                The plots are generated and rendered when you open a tab; the more data there is to display
                the longer the loading time. The performance obviously depends on your Internet connection;
                '''),
            html.Br(),
            html.Strong('a loading time of a few seconds is to be expected.'),
            ]),
        html.P('''
            Each tab is structured similarly:
            '''),
        html.Ul([
            html.Li('At the top, a text block shortly describes the data displayed in the tab and the corresponding findings.'),
            html.Li('A "Data selectors" block let you customize/modify certain data filters.'),
            html.Li('Finally, the corresponding plots are shown.'),
        ]),
        html.Span('''
                The first tab "Data Exploration" contains the most general data visualizations
                to let you explore the dataset freely.
            '''),
        html.Br(),
        html.Span('''
                The other tabs highlight more specific effects.
                By default, the plots produced are the same as the one showed in the article.
                As mentioned before, you can modify them via the filters in the "Data selectors" block.
            '''),
    ],
    style={
        'width':'50%',
        'margin-bottom':20,
        'margin-left':20,
    }),

    # Container row
    html.Div([
        html.Span([
            'The source code of this application is available on ',
            html.A(
                'Github',
                href='https://github.com/romain-jacob/ST_data_and_viz',
                target='_blank',
                ),
            ' and archived on ',
            html.A(
                'Zenodo',
                href='https://doi.org/10.5281/zenodo.3964355',
                target='_blank',
                ),
            '.'
            ]),
        html.Br(),
        html.Span(
            html.A(
                html.Img(src='https://zenodo.org/badge/DOI/10.5281/zenodo.3964355.svg', alt='DOI'),
                href='https://doi.org/10.5281/zenodo.3964355',
                target='_blank',
                ),
            ),
    ], style={
        'background-color':colors.light_grey,
        'padding':20,
        'line-height': '250%',
        }
    ),

    # Content tabs
    dcc.Tabs(
        id='tabs-example',
        children=[
            dcc.Tab(label='Data Exploration', value='tab-general'),
            dcc.Tab(label='Power Capture Effect', value='tab-capture'),
            dcc.Tab(label='Constructive Interference', value='tab-CI'),
            dcc.Tab(label='Mixed Effects', value='tab-matrix'),
        ],
        value='tab-general' ),
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
