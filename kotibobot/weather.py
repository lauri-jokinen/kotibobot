import fmi_weather_client as fmi

def temp():
  weather = fmi.weather_by_coordinates(60.19078966723265, 24.832829160598983)
  return weather.data.temperature.value
  
def humidity():
  weather = fmi.weather_by_coordinates(60.19078966723265, 24.832829160598983)
  return weather.data.humidity.value