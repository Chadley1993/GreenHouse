from cProfile import label
import json
from turtle import color
from click import style
import datetime
import dash_daq as daq
from dash import html
import dash_bootstrap_components as dbc

gauge_th_style = {'flex': '1', 'background': '#f7f7f7'}
switch_style = {'flex': '1', 'background': '#f7f7f7', 'marginBottom': '1rem'}

def git(init_value):
    return html.Div(
        daq.Thermometer(
            id='inside-temperature',
            label={'label': 'Inside Temperature', 'style': {'textAlign': 'center'}},
            showCurrentValue=True,
            value=init_value,
            min=0,
            max=40,
            height=80,
            width=15,
            scale={'interval': 10},
            color='#0b0b9e'
        ),
        style=gauge_th_style,
        id="inside-temp-card"
    )

def gih(init_value):
    return html.Div([
        html.Div([
            daq.Gauge(
            id="inside-humidity",
            units="%",
            value=init_value,
            label='Inside Humidity',
            max=100,
            min=0,
            color='#0b0b9e',
            size=130
            ),
            html.Div("20%", style={'textAlign': "center", 'fontSize': '25px'})
        ])
    ],
        style=gauge_th_style,
        id="inside-humidity-card"
    )

def got(init_value):
    return html.Div([
        daq.Thermometer(
            id='outside-temperature',
            label={'label': 'Outside Temperature', 'style': {'textAlign': 'center'}},
            value=init_value,
            showCurrentValue=True,
            min=0,
            max=50,
            width=15,
            height=80,
            scale={'interval': 10},
            color='#0b0b9e'
        )],
        style=gauge_th_style,
        id="outside-temp-card"
    )

def goh(init_value):
    return html.Div([
        html.Div([
            daq.Gauge(
                id="outside-humidity",
                units="%",
                value=init_value,
                label='Outside Humidity',
                max=100,
                min=0,
                color='#0b0b9e',
                size=130
            ),
            html.Div("20%", style={'textAlign': "center", 'fontSize': '25px'})
        ])
    ],
        style=gauge_th_style,
        id="outside-humidity-card"
    )

def navbar():
    return html.Div(
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                dbc.NavItem(dbc.NavLink("Page 2", href="#")),
                dbc.NavItem(dbc.NavLink("Page 3", href="#")),
            ],
            id="navbar",
            brand="Wactec Green House",
            brand_href="#",
            color="primary",
            style={}
        ),
        style={"width": "100%"},
        id='navbar-ghost'
    )

def toggle_switch(id, label):
    return html.Div([
        daq.BooleanSwitch(
            on=True,
            color="#9B51E0",
            id=id,
            label=label
        )],
        style=switch_style
    )

def tank(id, label, value=0):
    return html.Div(
        daq.Tank(
            id=id,
            value=value,
            min=0,
            showCurrentValue=True,
            units='%',
            max=100,
            label=label,
            color='#0b0b9e',
            labelPosition='top',
            width=50,
            scale={'custom': {'0': ''}},
            height=150
        ),
        style=gauge_th_style,
    )


def get_video_stream_url():
    if find_stream_url():
        return "http://192.168.0.4:5000/video_feed"
    else:
        return "assets/WacktecGreenHouse.png"

def find_stream_url():
    # TODO: find the stream address.
    return False

    f = open('openweather_forecast.json', 'r')
    data = json.load()
    f.close()

def get_weather_data():
    try:
        f = open('openweather_forecast.json', 'r')
        data = json.load(f)
        f.close()
        return data
    except FileNotFoundError:
        return {}

def classify_wind_dir(wind_dir):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return directions[int(wind_dir / 360) % 16]


def get_weather_details(data, index):
    min_temp = data["daily"][index]["temp"]["min"]
    max_temp = data["daily"][index]["temp"]["max"]
    wind_speed = data["daily"][index]["wind_speed"]
    wind_direction = classify_wind_dir(data["daily"][index]["wind_deg"])
    temperature_template = "{}\u00B0C/{}\u00B0C".format(int(min_temp), int(max_temp))
    wind_template = "Wind {}km/h {}".format(wind_speed, wind_direction)
    return temperature_template, wind_template


def get_forecast():
    cards = []
    day_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_index = datetime.datetime.today().weekday()
    day_of_week_ordered = day_of_week[start_index:] + day_of_week[:start_index]
    data = get_weather_data()
    if len(data) == 0:
        return html.Div("Weather service not available.", style={"fontSize": "24px", "backgroundColor": "#0d6efd", "flex": "1", "textAlign": "center", "padding": "auto", "height": "100%"})

    for index in range(7):
        day_div = html.Div(day_of_week_ordered[index], style={'flex':'1', 'textAlign': 'center', 'width': '100%'})
        
        icon = html.Img(src="assets/weather-icons/" + data["daily"][index]["weather"][0]["icon"] + ".png", style={'height': '75%', 'width': '50%', 'margin': 'auto'})

        tempeture, wind = get_weather_details(data, index)
        temperature_div = html.Div([html.Div(tempeture), html.Div(wind)], style={'flex':'1', 'textAlign': 'center', 'width': '100%'})
        icon_div = html.Div(icon, style={'flex':'2', 'textAlign': 'center', 'width': '100%', 'height': '40%'})
        
        day = html.Div([day_div, icon_div, temperature_div], style={'display': 'flex', 'flexFlow': 'column', 'flex': '1', 'background': 'deepskyblue', 'borderStyle': 'outset', 'minWidth': '200px'})
        cards.append(day)
    return cards
