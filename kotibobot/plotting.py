# - *- coding: utf- 8 - *-
from datetime import datetime, timedelta
import pandas as pd
import math, time, matplotlib
import matplotlib.dates as mdates # helps to format dates in x-axis
import matplotlib.pyplot as plt
import multiprocessing as mp # asychronous plotting
from os.path import exists
from scipy import interpolate

from house import *
from common_functions import *
import kotibobot.weather
import kotibobot.electricity_price

matplotlib.use('svg') # no GUI when plotting

# asychronous plotting https://gist.github.com/astrofrog
class AsyncPlotter:
    def __init__(self, processes=mp.cpu_count()): #
        self.manager = mp.Manager()
        self.nc = self.manager.Value("i", 0)
        self.pids = []
        self.processes = processes
    def async_plotter(self, nc, fig, filename, processes):
        while nc.value >= processes:
            time.sleep(0.05)
        nc.value += 1
        #print("Plotting " + filename)
        fig.savefig(filename)
        plt.close(fig)
        nc.value -= 1
    def save(self, fig, filename):
        p = mp.Process(
            target=self.async_plotter, args=(self.nc, fig, filename, self.processes)
        )
        p.start()
        self.pids.append(p)
    def join(self):
        for p in self.pids:
            p.join()

def load_ts_data():
  df = pd.DataFrame({})
  timeformat = '%Y-%m'
  this_month = datetime.now().strftime(timeformat)
  last_month = (datetime.now().replace(day=1) - timedelta(days=2)).strftime(timeformat)
  
  file_name = '/home/lowpaw/Downloads/kotibobot/{}.pkl'.format(last_month)
  if exists(file_name):
    df = pd.concat([df, pd.read_pickle(file_name)], sort=False, ignore_index=True)
  
  file_name = '/home/lowpaw/Downloads/kotibobot/{}.pkl'.format(this_month)
  if exists(file_name):
    df = pd.concat([df, pd.read_pickle(file_name)], sort=False, ignore_index=True)
    
  return df

def figure_size():
  return (10,6.25)

def outside_hum_to_inside_hum(temp_in, temp_out, hum_out):
  temps =            [-50,   -20,  -10,     0,   5,  10,    11,    12,    13,    14,    15,   20, 25,   30, 37,   40,   50]
  satur_vapor_dens = [0.039, 0.89, 2.36, 4.85, 6.8, 9.4, 10.01, 10.66, 11.35, 12.07, 12.83, 17.3, 23, 30.4, 44, 51.1, 82.4]
  f = interpolate.interp1d(temps, satur_vapor_dens, kind='quadratic')
  SVD_in = f(temp_in)
  SVD_out = f(temp_out)
  return hum_out * SVD_out / SVD_in

def temp_hum_inside_outside_forecast(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_hum_in_out_forecast.svg'
  plotname = "Temp & hum, in & out, forecast"
  if not make_plot:
    return html_link(plotname, filename)
  
  data = data_orig.copy()
  
  x1 = datetime.now() - timedelta(hours=3*24)
  x2 = datetime.now() + timedelta(hours=2*24)
  x_range = [x1,x2]
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
      
  humidities = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      humidities.append(sensor + " humidity")
  
  data['inside temp'] = data[temps].mean(axis=1)
  data['inside humidity'] = data[humidities].mean(axis=1)
  
  forecast = kotibobot.weather.forecast()
  t_start_forecast = datetime.now() - timedelta(minutes = 1) # takes current time into account
  t_end_forecast = datetime.now() + timedelta(hours = 24*2)
  forecast = forecast[forecast['time'] > t_start_forecast]
  forecast = forecast[forecast['time'] < t_end_forecast]
  
  forecast['humidity converted'] = outside_hum_to_inside_hum(latest_data_json()['olkkarin lämpömittari temp'], forecast['temp'], forecast['humidity'])
  latest_data = latest_data_json()
  data['outside humidity converted'] = outside_hum_to_inside_hum(latest_data['olkkarin lämpömittari temp'], data['outside temp'], data['outside humidity'])
  
  fig, ax1 = plt.subplots(1,1,figsize=figure_size())
  
  (x,y) = get_plot_range(data, 'inside temp', x_range)
  ax1.plot(x,y, alpha=0.7, color='r', label='inside temp')
  (x,y) = get_plot_range(data, 'outside temp', x_range)
  ax1.plot(x,y, alpha=0.7,color='r',linestyle='dashed', label = 'outside temp')
  (x,y) = get_plot_range(forecast, 'temp', x_range)
  ax1.plot(x,y,alpha=0.7, color='r', linestyle = ':', label='forecast temp')
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  (x,y) = get_plot_range(data, 'olkkarin lämpömittari humidity', x_range)
  ax2.plot(x,y,color='b', alpha=0.7, label='olkkari humidity')
  (x,y) = get_plot_range(data, 'outside humidity converted', x_range)
  ax2.plot(x,y,color='b',linestyle='dashed', alpha=0.3, label='outside humidity')
  (x,y) = get_plot_range(forecast, 'humidity converted', x_range)
  ax2.plot(x,y,alpha=0.3, color='b', linestyle = ':', label='forecast humidity')
  plt.ylim([-2, 102])
  ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  plt.ylabel('%',rotation=0)
  
  ax1.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax1.set_xticklabels(rotation=0, ha='center', labels='')
  ax1.xaxis.set_major_formatter(myFmt)
  ax1.legend()
  ax2.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)
  

def temp_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_allrooms.svg'
  plotname = "Temperature, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  x2 = datetime.now() + timedelta(hours=5)
  x1 = datetime.now() - timedelta(hours=48)
  x_range = [x1,x2]
  
  # min and max temps are used to filter
  # too low and too high outside temp -values
  #max_room_temp = -float('inf')
  #min_room_temp =  float('inf')
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
      #max_room_temp = max(max_room_temp, data[sensor + " temp"].max())
      #min_room_temp = min(min_room_temp, data[sensor + " temp"].min())
  '''
  max_room_temp = max_room_temp + 5
  min_room_temp = min_room_temp - 5
  
  # we filter too low and
  # too high outside temp -values
  data['outside temp'] = data['outside temp'].where(data['outside temp'] < max_room_temp, float('nan'))
  data['outside temp'] = data['outside temp'].where(data['outside temp'] > min_room_temp, float('nan'))
  '''
  data['outside temp'] = data['outside temp'].where(data['outside temp'] < 27.0, float('nan'))
  data['outside temp'] = data['outside temp'].where(data['outside temp'] > 20.0, float('nan'))
  
  forecast = kotibobot.weather.forecast()
  t_start_forecast = datetime.now() - timedelta(minutes = 1) # takes current time into account
  t_end_forecast = datetime.now() + timedelta(hours = 6)
  forecast = forecast[forecast['time'] > t_start_forecast]
  forecast = forecast[forecast['time'] < t_end_forecast]
  forecast['temp'] = forecast['temp'].where(forecast['temp'] < 27.0, float('nan'))
  forecast['temp'] = forecast['temp'].where(forecast['temp'] > 20.0, float('nan'))
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  (x,y) = get_plot_range(data, temps, x_range)
  ax.plot(x, y, alpha=0.7, label = temps)
  (x,y) = get_plot_range(data, "outside temp", x_range)
  ax.plot(x, y, alpha=0.7, color='r', linestyle='dashed', label = "outside temp.")
  (x,y) = get_plot_range(forecast, 'temp', x_range)
  ax.plot(x, y, alpha=0.7, color='r', linestyle = ':', label='forecast temp')
  
  plt.ylabel('    °C',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  ax.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)
  
def temp_48_all_rooms_real_feel(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_allrooms_rf.svg'
  plotname = "Temperature real feel, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  x2 = datetime.now() + timedelta(hours=5)
  x1 = datetime.now() - timedelta(hours=48)
  x_range = [x1,x2]
  
  # min and max temps are used to filter
  # too low and too high outside temp -values
  #max_room_temp = -float('inf')
  #min_room_temp =  float('inf')
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
      data[sensor + " temp"] = data[sensor + " temp"] + 4.8/100*data[sensor + " humidity"] - 4.8/2
  
  data['outside temp'] = data['outside temp'] + 4.8/100*data['outside humidity'] - 4.8/2
  data['outside temp'] = data['outside temp'].where(data['outside temp'] < 27.0, float('nan'))
  data['outside temp'] = data['outside temp'].where(data['outside temp'] > 20.0, float('nan'))
  
  forecast = kotibobot.weather.forecast()
  t_start_forecast = datetime.now() - timedelta(minutes = 1) # takes current time into account
  t_end_forecast = datetime.now() + timedelta(hours = 6)
  forecast = forecast[forecast['time'] > t_start_forecast]
  forecast = forecast[forecast['time'] < t_end_forecast]
  forecast['temp'] = forecast['temp'] + 4.8/100*forecast['humidity'] - 4.8/2
  forecast['temp'] = forecast['temp'].where(forecast['temp'] < 27.0, float('nan'))
  forecast['temp'] = forecast['temp'].where(forecast['temp'] > 20.0, float('nan'))
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  (x,y) = get_plot_range(data, temps, x_range)
  ax.plot(x, y, alpha=0.7, label = temps)
  (x,y) = get_plot_range(data, "outside temp", x_range)
  ax.plot(x, y, alpha=0.7, color='r', linestyle='dashed', label = "outside temp.")
  (x,y) = get_plot_range(forecast, 'temp', x_range)
  ax.plot(x, y, alpha=0.7, color='r', linestyle = ':', label='forecast temp')
  
  plt.ylabel('    RF °C',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  ax.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def humidity_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'humidity_allrooms.svg'
  plotname = "Humidity, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  x2 = datetime.now()
  x1 = x2 - timedelta(hours=48)
  x_range = [x1,x2]
  
  humidities = []
  for sensor in mis:
    humidities.append(mac_to_name[sensor] + " humidity")
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  (x,y) = get_plot_range(data, humidities, x_range)
  ax.plot(x, y, alpha=0.7, label=humidities)
  (x,y) = get_plot_range(data, "outside humidity", x_range)
  ax.plot(x, y, alpha=0.7, linestyle='dashed', label="outside humidity")
  
  plt.ylim([-2, 102])
  
  plt.ylabel('%',rotation=0)
  ax.set_xlabel('')
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  ax.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_48(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_target_temp.svg'
  plotname = "Temperature, 48h"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
    data[eq3 + " target"] = data[eq3 + " target"] + hard_offset[room]
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  x2 = datetime.now()
  x1 = x2 - timedelta(hours=48)
  x_range = [x1,x2]
  
  fig, ax1 = plt.subplots(1,1,figsize=figure_size())
  
  # plot temperatures
  (x,y) = get_plot_range(data, temps, x_range)
  ax1.plot(x, y, alpha=0.7, color='r', label=temps)
  
  # plot targets
  if len(targets) > 0:
    (x,y) = get_plot_range(data, targets, x_range)
    ax1.plot(x,y, alpha=0.7,linestyle='dashed', label=targets)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  plt.xticks(rotation=0, ha='center')
    
  # plot valves
  ax2 = ax1.twinx()
  if len(valves) > 0:
    (x,y) = get_plot_range(data, valves, x_range)
    ax2.plot(x,y,linestyle=':', alpha=0.7, label=valves)
  plt.ylim([-2, 102])
  ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  plt.ylabel('%',rotation=0)
  ax1.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  plt.xticks(rotation=0, ha='center')
  ax1.set_xticklabels(rotation=0, ha='center', labels='')
  ax1.xaxis.set_major_formatter(myFmt)
  ax1.legend()
  ax2.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_temp.svg'
  plotname = "Temperature, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  temp = temps[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  
  x1 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  x2 = x1 + timedelta(hours=24)
  x_range = [x1,x2]
  
  (x,y) = get_plot_range(data, temp, x_range)
  ax.plot(x, y, color='r',alpha=0.8, label='Today')
  
  (x,y) = get_plot_range(data, temp, x_range, time_delta=timedelta(hours=24))
  ax.plot(x, y, linestyle='dashed',color='r',alpha=0.7, label='Previous day')
  
  (x,y) = get_plot_range(data, temp, x_range, time_delta=timedelta(hours=48))
  ax.plot(x, y, linestyle=':',color='r',alpha=0.6, label='2 days ago')
  
  plt.ylabel('    °C',rotation=0)
  ax.set_xlabel('')
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  ax.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)
  
def humidity_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_humidity.svg'
  plotname = "Humidity, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  
  humidities = []
  for sensor in mi_in_rooms[room]:
    humidities.append(sensor + " humidity")
  humidity = humidities[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  
  #get_plot_range(data, column, time_range, time_delta=timedelta(hours=0))
  x1 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  x2 = x1 + timedelta(hours=24)
  x_range = [x1,x2]
  
  (x,y) = get_plot_range(data, humidity, x_range)
  ax.plot(x, y, color='b',alpha=0.8, label='Today')
  
  (x,y) = get_plot_range(data, humidity, x_range, time_delta=timedelta(hours=24))
  ax.plot(x, y, linestyle='dashed',color='b',alpha=0.7, label='Previous day')
  
  (x,y) = get_plot_range(data, humidity, x_range, time_delta=timedelta(hours=48))
  ax.plot(x, y, linestyle=':',color='b',alpha=0.6,  label='2 days ago')
  
  plt.ylim([-2, 102])
  plt.ylabel(' %',rotation=0)
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  ax.legend()
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def electricity_price_days(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'electricity_price.svg'
  plotname = "Electricity price"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig.copy()
  time = data['time']
  x1 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  x2 = x1 + timedelta(hours=24)
  time_range = [x1,x2]
  
  # plot main graph
  fig, ax = plt.subplots(figsize=figure_size())
  (t0, d0) = get_plot_range(data, 'electricity price', time_range)
  ax.plot(t0, d0, label='El. price', color='b')
  
  # plot future graph
  (t1, d1) = get_plot_range(data, 'electricity price', time_range, time_delta = timedelta(hours=-24))
  ax.plot(t1, d1, label='Future el. price', color='b', linestyle='dashed')
  
  # plot duck curve
  duck = kotibobot.electricity_price.duck_curve(data_orig)
  df_duck = pd.DataFrame()
  time_vector = [datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)]
  for p in range(23):
    time_vector.append(time_vector[p] + timedelta(hours=1))
  df_duck['time'] = time_vector
  df_duck['duck curve'] = duck
  ax.plot(df_duck["time"],df_duck['duck curve'],color='k',alpha=0.8, label='Median price')
  
  current_price = kotibobot.electricity_price.current(data_orig)
  this_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
  ax.scatter([this_hour], [current_price], s=120, facecolors='none', edgecolors='r',label='Current price')
  
  ax.legend()
  ax.set_xlabel('')
  plt.ylabel('            c/kWh',rotation=0)
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def html_link(text,url):
  return "<a href='https://cloud.laurijokinen.com/kotibobot/" + url + "'>" + text +"</a>"

def get_plot_range(data, column, time_range, time_delta=timedelta(hours=0)):
  # this function returns vectors that are cropped to a correct time interval
  data2 = data.copy()
  data2['time'] = data2['time'] + time_delta
  data2 = data2[data2['time'] >= time_range[0]]
  data2 = data2[data2['time'] <  time_range[1]]
  time = data2['time']
  data2 = data2[column]
  return (time, data2)

def main_function(draw_plots = True):
  data_orig = load_ts_data()
  data_orig_el = kotibobot.electricity_price.load_ts_data()
  a = AsyncPlotter()
  res = ["Kaikki huoneet"] # in html
  res.append(temp_hum_inside_outside_forecast(data_orig,a,draw_plots))
  res.append(temp_48_all_rooms_real_feel(data_orig,a,draw_plots))
  res.append(temp_48_all_rooms(data_orig,a,draw_plots))
  res.append(humidity_48_all_rooms(data_orig,a,draw_plots))
  res.append(electricity_price_days(data_orig_el,a,draw_plots))
  #res.append(hs110_days(data_orig,a,draw_plots))
  for room in rooms:
    res.append("\n" + room.capitalize())
    res.append(temp_48(room, data_orig,a,draw_plots))
    res.append(temp_days(room, data_orig,a,draw_plots))
    res.append(humidity_days(room, data_orig,a,draw_plots))
  a.join()
  plt.close('all')
  
  return "\n".join(res)

#print('plotting...')
#main_function()

def latest_data_json(withTime = False):
  data = load_ts_data()
  cols = data.columns.values.tolist()
  res = json.loads("{}")
  times = json.loads("{}")
  times['LATEST'] = data.iloc[-1]['time']
  for col in cols:
    if not col == 'time':
      if not math.isnan(data.iloc[-1][col]):
        res[col] = data.iloc[-1][col]
        times[col] = data.iloc[-1]['time']
      else:
        subdf = data.iloc[:][[col, 'time']]
        subdf = subdf.dropna()
        res[col] = subdf.iloc[-1][col]
        times[col] = subdf.iloc[-1]['time']
        
  el_data = kotibobot.electricity_price.load_ts_data()
  res['electricity frequency'] = kotibobot.electricity_price.frequency()
  res['electricity price'] = kotibobot.electricity_price.current(el_data)
  res['electricity price precentile'] = kotibobot.electricity_price.precentile(el_data)
  res['electricity price precentile hourly'] = kotibobot.electricity_price.precentile_interval(datetime.now().hour, datetime.now().hour, el_data)
  if withTime:
    return (res, times)
  else:
    return res

def print_latest_data():
  (data,times) = latest_data_json(True)
  timeformat = '%-d.%-m. at %-H:%M'
  
  res = ['Latest measurement on ' + str(times['LATEST'].strftime(timeformat)) + '\n']
  res.append("el. price precentile : {:.2f} %".format(       data['electricity price precentile']*100))
  res.append("el. price precentile hourly : {:.2f} %".format(data['electricity price precentile hourly']*100))
  res.append("electricity price : {:.2f} snt/kWh".format(    data['electricity price']))
  res.append("el. frequency : {:.2f} Hz".format(             data['electricity frequency']))
  
  for col in data:
    if not col in ['time','electricity price','electricity price precentile hourly','electricity price precentile','electricity frequency']:
      if times['LATEST'] == times[col]:
        res.append("{} : {:.4G}".format(col, data[col]))
      else:
        res.append("{} : {:.4G} (on {})".format(col, data[col], str(times[col].strftime(timeformat))))
  res.sort()
  return '\n'.join(res)
