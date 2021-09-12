import fmi_weather_client as fmi
from datetime import timezone
from datetime import datetime
import pandas as pd

def temp():
  weather = fmi.weather_by_coordinates(60.19078966723265, 24.832829160598983)
  return weather.data.temperature.value
  
def humidity():
  weather = fmi.weather_by_coordinates(60.19078966723265, 24.832829160598983)
  return weather.data.humidity.value

def utc_to_local(utc_dt):
  return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def forecast():
  forecasts = fmi.forecast_by_coordinates(60.19078966723265, 24.832829160598983, timestep_hours=1).forecasts
  data = {}
  
  # first datapoint is current weather
  data['time'] = [datetime.now()]
  data['temp'] = [temp()]
  data['humidity'] = [humidity()]
  
  for forecast in forecasts:
    data['time'].append(utc_to_local(forecast.time).replace(tzinfo=None)) # remove timezone-information?
    data['temp'].append(forecast.temperature.value)
    data['humidity'].append(forecast.humidity.value)
  return pd.DataFrame(data)
