import socket
from turtle import ht
from click import style
import dash
import yaml
import dash_daq as daq
import pickle
import argparse
import numpy as np
import ghcomponents as ghc

from yaml.loader import SafeLoader
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, ClientsideFunction
import plotly.graph_objects as go

from configurations import SSSConstants, SignedObject, SensorData

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_const', const=True,
                    help='Run web server with a mock sensor feed')
args = parser.parse_args()

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

previous_it = 0
previous_ih = 0
previous_ot = 0
previous_oh = 0
# style={'bordeStyle': 'outset', 'borderColor': '#c4c4c4'}

app.layout = html.Div(children=[
    ghc.navbar(),
    html.Div([
        ################################
        # Main left panel
        html.Div(children=[
            html.Div([
                ghc.git(20), ghc.got(20)
            ],
                style={'display': 'flex', 'borderStyle': 'outset', 'flex': '1'}
            ),
            html.Div([
                ghc.gih(20), ghc.goh(20)
            ],
                style={'display': 'flex', 'borderStyle': 'outset', 'flex': '1'}
            ),
            html.Div([
                ghc.toggle_switch("valve1", "Valve 1"), ghc.toggle_switch(
                    "valve2", "Valve 2"), ghc.toggle_switch("valve3", "Valve 3"), ghc.toggle_switch("t4", "Pump")
            ],
                style={'display': 'flex', 'borderStyle': 'outset',
                       'background': '#f7f7f7', 'flex': '1'}
            ),
            html.Div([
                ghc.tank("s1", "Sensor 2", value=25), ghc.tank(
                    "s2", "Sensor 2", value=75), ghc.tank("s3", "Sensor 3", value=50),
            ],
                style={'display': 'flex', 'borderStyle': 'outset',
                       'background': '#f7f7f7', 'flex': '1'}
            ),
            html.Div([
                html.Div([
                html.Table([
                    html.Tbody([
                        html.Th("Time", style={"border": "none", "padding": "1px", "color": "aliceblue"}),
                        html.Th("Description", style={"border": "none", "padding": "1px", "color": "aliceblue"}),
                        html.Tr([html.Td("y", style={"border": "", "paddingTop": "1px", "paddingBottom": "1px"}), html.Td("30000", style={"paddingTop": "1px", "paddingBottom": "1px"})]),
                    ])
                ],
                    style={"width": "100%"}
                )
                ], 
                style={'maxHeight': 'calc(100% - 20px)', 'background': '#737574', 'height': '100%'}),
            ],
                style={'flex': '2', 'borderTopStyle': 'outset','background': '#737574'}
            )
        ],
            style={'display': 'flex', 'flexFlow': 'column', 'flex': '1'},
            id='info-cluster'
        ),
        ################################
        # Main right panel
        html.Div([
            html.Div([
                html.Div(
                    html.Img(
                        src=ghc.get_video_stream_url(),
                        style={'height': '100%', 'width': '100%'},
                    ),
                    style={'flex': '75', 'background': 'chocolate',
                           'borderStyle': 'outset', 'minWidth': '300px', 'maxHeight': '600px'}
                ),
                html.Div(
                    html.ObjectEl(data="assets/plumbing.svg",
                                  type="image/svg+xml", id='embedded-diagram'),
                    style={'flex': '25', 'background': '#ffffff',
                           'borderStyle': 'outset', 'minWidth': '300px', 'paddingLeft': "5em"}
                )
            ], style={'display': 'flex', 'flex': '65', 'background': 'aqua', 'borderStyle': 'outset', 'maxHeight': '75%'}),
            
            html.Div(
                ghc.get_forecast(),
                style={'display': 'flex', 'flex': '35', 'background': 'darkred', 'borderStyle': 'outset'}
            )
        ],
            style={'display': 'flex', 'flexFlow': 'column',
                   'flex': '4', 'background': 'yellow'}
        )
    ],
        style={'display': 'flex', 'height': '100%', },
        id='Container'
    ),
    html.Div(
        "A Wacktec product",
        style={"position": "fixed", "textAlign": "center", "color": "white", "bottom": "0", "width": "100%", "height": "40px", "paddingTop": "10px", "background": "#363636"}
    ),
    dcc.Interval(id='live-feed', interval=1000 * 5)
],
    style={'height': '98vh', 'display': 'flex',
           'flexFlow': 'column', 'width': '100%'},
    id='main-container'
)


def get_address_book():
    f = open('address_book.yml', 'r')
    book = yaml.load(f, Loader=SafeLoader)
    f.close()
    return book


@app.callback(
    [
        Output("inside-temperature", "value"),
        Output("inside-humidity", "value"),
        Output("outside-temperature", "value"),
        Output("outside-humidity", "value"),
    ],
    Input('live-feed', "n_intervals")
)
def live_feed(n_intervals):
    if args.debug:
        return mock_feed()
    s = socket.socket()
    s.connect((rpi_addr, SSSConstants.port))
    byte_stream = s.recv(2048)
    s.close()
    signed_obj: SignedObject = pickle.loads(byte_stream)
    s_obj: SensorData = signed_obj.get_og_object()
    return s_obj.get_inside_temp(), s_obj.get_inside_humidity(), s_obj.get_outside_temp(), s_obj.get_outside_humidity()


app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='initializationFunc'
    ),
    Output('embedded-diagram', 'id'),
    Input('embedded-diagram', 'id')
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='toggleValve'
    ),
    Output('valve1', 'on'),
    Input('valve1', 'on'),
    Input('valve1', 'id'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='toggleValve'
    ),
    Output('valve2', 'on'),
    Input('valve2', 'on'),
    Input('valve2', 'id'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='toggleValve'
    ),
    Output('valve3', 'on'),
    Input('valve3', 'on'),
    Input('valve3', 'id'),
)

app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='switchPump'
    ),
    Output('t4', 'on'),
    Input('t4', 'on')
)


def mock_feed():
    inside_temp = np.random.randint(0, 40)
    inside_humidity = np.random.randint(0, 100)
    outside_temp = np.random.randint(0, 40)
    outside_humidity = np.random.randint(0, 100)
    return inside_temp, inside_humidity, outside_temp, outside_humidity


if __name__ == '__main__':
    if args.debug:
        app.run_server(debug=True, host="localhost")
    else:
        addr_book = get_address_book()
        rpi_addr = addr_book['rpi_server']
        app.run_server(debug=False, use_reloader=False, host="0.0.0.0")
