import requests
import json
import os

openweather_params = {
    "lat": -33.92923930375892,
    "lon": 18.672138731835695,
    "exclude": "hourly",
    "appid": os.environ["OPENWEATHER_APIKEY"],
    "units": "metric"
}


def get_openweather_forecast():
    response = requests.get("https://api.openweathermap.org/data/2.5/onecall", params=openweather_params)
    f = open('openweather_forecast.json', 'w')
    json.dump(response.json(), f)
    f.close()


if __name__ == '__main__':
    get_openweather_forecast()
