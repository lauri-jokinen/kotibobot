import eq3_functions as eq3
from datetime import datetime, timedelta
import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
#from pandas import read_csv
#from pandas import DataFrame
import pandas as pd
from matplotlib import pyplot
import json
import matplotlib.dates as mdates # helps to format dates in x-axis

# THIS SCRIPT SHOULD NOT BE USED ANYMORE
# in: olkkari-keittiö
# 

def plot_ts(selected_rooms):
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  #series = pd.read_csv('./ts.txt', header=0, parse_dates=True, squeeze=True, delimiter = ";")
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  try:
    data = pd.read_pickle(file_name)
  except:
    print("Tiedostoa ei löydy!")
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  valves = []
  for room in selected_rooms:
    for valve in eq3.eq3_in_rooms[room]:
      valves.append(valve + " valve")
  
  targets = []
  for room in selected_rooms:
    for valve in eq3.eq3_in_rooms[room]:
      targets.append(valve + " target")
      
  temps = []
  for room in selected_rooms:
    for sensor in eq3.mi_in_rooms[room]:
      temps.append(sensor + " temp")
      
  humidities = []
  for room in selected_rooms:
    for sensor in eq3.mi_in_rooms[room]:
      humidities.append(sensor + " humidity")
  
  ax = data.plot(x="time",y=(valves+humidities))
  pyplot.ylim([-2, 102])
  pyplot.ylabel('%',rotation=0)
  
  data.plot(x="time",y=(targets+temps),secondary_y=True,linestyle='dashed',ax=ax) # ax=ax laittaa samaan kuvaan
  pyplot.ylabel('  °C',rotation=0)
  ax.set_xlabel('')
  
  
  myFmt = mdates.DateFormatter('%-d.%-m. - %-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  
  #pyplot.show()
  pyplot.savefig('time_series.png')

#plot_ts(['työkkäri']) # , '2021-05-08T16:15', '2021-05-10T17:10'
