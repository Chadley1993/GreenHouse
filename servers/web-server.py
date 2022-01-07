import socket
import dash
import yaml
import dash_daq as daq
import pickle

from yaml.loader import SafeLoader
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

from configurations import SSSConstants, SignedObject, SensorData

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

previous_ot = 0
previous_oh = 0
previous_it = 0
previous_ih = 0

app.layout = html.Div(children=[
    html.Div(
        [
            daq.Thermometer(
                id='inside-temperature',
                label='Inside Temperature',
                showCurrentValue=True,
                value=previous_it,
                min=0,
                max=50,
                style={
                    'margin-bottom': '5%'
                }
            )
        ],
        style={"paddingLeft": "1.25rem"},
        id="inside-temp-card"
    ),
    html.Div(
        [
            daq.Gauge(
                id="inside-humidity",
                showCurrentValue=True,
                units="%",
                value=previous_ih,
                label='Inside Humidity',
                max=100,
                min=0
            )
        ],
        style={"paddingLeft": "1.25rem"},
        id="inside-humidity-card"
    ),
    html.Div(
        [
            daq.Thermometer(
                id='outside-temperature',
                label='Outside Temperature',
                value=previous_ot,
                showCurrentValue=True,
                min=0,
                max=50,
                style={
                    'margin-bottom': '5%'
                }
            )
        ],
        style={"paddingLeft": "1.25rem"},
        id="outside-temp-card"
    ),
    html.Div(
        [
            daq.Gauge(
                id="outside-humidity",
                showCurrentValue=True,
                units="%",
                value=previous_oh,
                label='Outside Humidity',
                max=100,
                min=0
            )
        ],
        style={"paddingLeft": "1.25rem"},
        id="outside-humidity-card"
    ),
    dcc.Interval(id='test-iterator', interval=1000 * 5)
])


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
    Input('test-iterator', "n_intervals")
)
def live_feed(n_intervals):
    s = socket.socket()
    s.connect((rpi_addr, SSSConstants.port))
    byte_stream = s.recv(2048)
    s.close()
    signed_obj: SignedObject = pickle.loads(byte_stream)
    s_obj: SensorData = signed_obj.get_og_object()
    return s_obj.get_inside_temp(), s_obj.get_inside_humidity(), s_obj.get_outside_temp(), s_obj.get_outside_humidity()


addr_book = get_address_book()
rpi_addr = addr_book['rpi_server']

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, host="0.0.0.0")
