import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


@app.callback(
    Output("temperature-value", "children"),
    Input('test-iterator', "n_intervals")
)
def live_feed(n_intervals):
    # temperature = bmp280.get_temperature()
    temperature = np.random.random() * np.random.randint(0, 31)
    return "{:.1f}°C".format(temperature)


def get_data_from_db():
    f = open('temperature.db', 'r')
    timestamps = []
    temps = []
    for l in f:
        datapoint = l.split(",")
        datapoint[1] = float(datapoint[1].strip())
        timestamps.append(datapoint[0][4:-5])
        temps.append(datapoint[1])
    f.close()
    return np.array(timestamps), np.array(temps)


def get_temp_plot():
    xData, yData = get_data_from_db()
    temp_plot = go.Figure(data=go.Scatter(x=xData, y=yData,
                    mode='lines',
                    name='lines'),
            layout_yaxis_range = [0, 40.0]
              )
    temp_plot.update_yaxes(ticks="outside", tickvals=np.arange(0, 45, 5), ticktext=np.arange(0, 45, 5))
    temp_plot.update_layout(title_text="Temperature Record",
                      title_font=dict(family="Courier New, monospace", size=28),
                      yaxis_title="Temperature °C"
                      )
    return temp_plot


app.layout = html.Div(children=[
    dbc.CardBody(
        [
            html.H4("Live Temperature", className="card-title align-self-center"),
            html.H2("NaN", className="card-text", id="temperature-value")
        ],
        style={"paddingLeft": "1.25rem"},
        id="temperature-card"
    ),
    html.Div(dcc.Graph(figure=get_temp_plot())),
    dcc.Interval(id='test-iterator', interval=1000 * 5)
])

if __name__ == '__main__':
    app.run_server(debug=True)
