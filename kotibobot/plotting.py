# - *- coding: utf- 8 - *-
import time
from datetime import datetime, timedelta
# packages for time series
#import dateutil.parser
import matplotlib.pyplot as plt
#import numpy as np
import pandas as pd
#from matplotlib import pyplot
import matplotlib
import matplotlib.dates as mdates # helps to format dates in x-axis
import math
import multiprocessing as mp # asychronous plotting
from os.path import exists

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
    df = df.append(pd.read_pickle(file_name), sort=False, ignore_index=True)
  
  file_name = '/home/lowpaw/Downloads/kotibobot/{}.pkl'.format(this_month)
  if exists(file_name):
    df = df.append(pd.read_pickle(file_name), sort=False, ignore_index=True)
    
  return df

def figure_size():
  return (10,6.25)

def temp_hum_inside_outside_forecast(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_hum_in_out_forecast.svg'
  plotname = "Temp & hum, in & out, forecast"
  if not make_plot:
    return html_link(plotname, filename)
  
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 24*3)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
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
  
  fig, ax1 = plt.subplots(1,1,figsize=figure_size())
  
  data.plot(x="time",y='inside temp', alpha=0.7, color='r', ax=ax1)
  data.plot(x="time",y='outside temp', alpha=0.7,color='r',linestyle='dashed', ax=ax1)
  forecast.plot(x='time',y='temp',alpha=0.7, color='r', linestyle = ':', ax=ax1)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  data.plot(x="time",y='olkkarin lämpömittari humidity',color='b', ax=ax2, alpha=0.7) # ax=ax laittaa samaan kuvaan secondary_y=True,
  data.plot(x="time",y='outside humidity',color='b',linestyle='dashed', ax=ax2, alpha=0.7)
  humidity_65 = pd.DataFrame({'time':[t_start, t_end_forecast], '65 %':[65.0,65.0]})
  humidity_65.plot(x='time',y='65 %', color = 'b', ax=ax2, alpha = 0.4, linewidth=0.75)
  forecast.plot(x='time',y='humidity',alpha=0.7, color='b', linestyle = ':', ax=ax2)
  plt.ylim([-2, 102])
  #ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  plt.ylabel('%',rotation=0)
  
  ax1.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  #plt.xticks(rotation=0, ha='center', ax=ax1) ###########
  #ax1.set_xticklabels(rotation=0, ha='center', ax=ax1) ###########
  ax1.xaxis.set_major_formatter(myFmt)
  #plt.show()
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)
  

def temp_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'temp_allrooms.svg'
  plotname = "Temperature, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  # min and max temps are used to filter
  # too low and too high outside temp -values
  max_room_temp = -float('inf')
  min_room_temp =  float('inf')
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
      max_room_temp = max(max_room_temp, data[sensor + " temp"].max())
      min_room_temp = min(min_room_temp, data[sensor + " temp"].min())
      
  max_room_temp = max_room_temp + 5
  min_room_temp = min_room_temp - 5
  
  # we filter too low and
  # too high outside temp -values
  data['outside temp'] = data['outside temp'].where(data['outside temp'] < max_room_temp, float('nan'))
  data['outside temp'] = data['outside temp'].where(data['outside temp'] > min_room_temp, float('nan'))
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  #ax = data.plot(x="time",y=(temps), alpha=0.7)
  data.plot(x="time",y=(temps), alpha=0.7, ax=ax)
  data.plot(x="time",y="outside temp", alpha=0.7, ax=ax, linestyle='dashed')
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
  
  #plt.show()
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def humidity_48_all_rooms(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'humidity_allrooms.svg'
  plotname = "Humidity, 48h all rooms"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  humidities = []
  for sensor in mis:
    humidities.append(mac_to_name[sensor] + " humidity")
  
  fig, ax = plt.subplots(1,1,figsize=(11,9))
  data.plot(x="time",y=(humidities), ax=ax, alpha=0.7) # ax=ax laittaa samaan kuvaan
  data.plot(x="time",y="outside humidity", ax=ax, alpha=0.7, linestyle='dashed')
  
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
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_48(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_target_temp.svg'
  plotname = "Temperature, 48h"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  #data['real_target']
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
    data[eq3 + " target"] = data[eq3 + " target"] + hard_offset
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  fig, ax1 = plt.subplots(1,1,figsize=figure_size())
  
  data.plot(x="time",y=(temps), alpha=0.7, color='r', ax=ax1)
  if len(targets) > 0:
    data.plot(x="time",y=(targets), alpha=0.7,linestyle='dashed', ax=ax1)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  if len(valves) > 0:
    data.plot(x="time",y=(valves),linestyle=':', ax=ax2, alpha=0.7) # ax=ax laittaa samaan kuvaan secondary_y=True,
  #plt.ylim([-2, 102])
  #ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  plt.ylabel('%',rotation=0)
  ax1.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  #plt.xticks(rotation=0, ha='center', ax=ax1) ###########
  #ax1.set_xticklabels(rotation=0, ha='center', ax=ax1) ###########
  ax1.xaxis.set_major_formatter(myFmt)
  #plt.show()
  
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def temp_offset(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_offset.svg'
  plotname = "Error, 48h"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
      
  offsets = []
  for eq3 in eq3_in_rooms[room]:
    offsets.append(eq3 + " offset")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  data['temp'] =   data[temps].mean(axis = 1,skipna = True)
  data['target'] = data[targets].mean(axis = 1,skipna = True)
  data['error'] = data['temp'].subtract(data['target'])
  data['error'] = data['error'].subtract(data[offsets].mean(axis = 1,skipna = True))
  #offsets.append('error')
  
  fig, ax1 = plt.subplots(1,1,figsize=figure_size())
  data.plot(x="time",y='error', alpha=0.7, color = 'm', ax=ax1)
  data.plot(x="time",y=offsets, linestyle='dashed', alpha=0.7, ax=ax1)
  plt.ylabel('°C   ',rotation=0)
  
  lim = list(plt.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  plt.xticks(rotation=0, ha='center')
  
  ax2 = ax1.twinx()
  
  data.plot(x="time",y=valves,ax=ax2,linestyle=':', alpha=0.7) # ax=ax laittaa samaan kuvaan
  plt.ylabel('%',rotation=0)
  ax1.set_xlabel('')
  plt.ylim([-2, 102])
  ax1.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax1.set_yticks([0.0001], minor=True)
  
  ax1.yaxis.grid(True, which='major', alpha = 0.2)
  ax1.yaxis.grid(True, which='minor')
  ax1.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M\n%-d.%-m.')
  
  ax1.xaxis.set_major_formatter(myFmt)
  
  #plt.show()
  
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)


def temp_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_temp.svg'
  plotname = "Temperature, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  t3 = t2 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  data0 = data[data['time'] > t0]
  data0 = data0[data0['time'] < t1]
  data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] > t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] > t2]
  data2 = data2[data2['time'] < t3]
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  temp = temps[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  data2.plot(x="time",y=temp,color='r', alpha=0.8, ax=ax)
  data1.plot(x="time",y=temp,linestyle='dashed',ax=ax,color='r', alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=temp,linestyle=':',ax=ax,color='r', alpha=0.6) # ax=ax laittaa samaan kuvaan
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
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link(plotname, filename)
  
def humidity_days(room, data_orig, a, make_plot = True):
  plt.ioff()
  filename = room + '_humidity.svg'
  plotname = "Humidity, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  t3 = t2 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  data0 = data[data['time'] > t0]
  data0 = data0[data0['time'] < t1]
  data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] > t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] > t2]
  data2 = data2[data2['time'] < t3]
  
  humidities = []
  for sensor in mi_in_rooms[room]:
    humidities.append(sensor + " humidity")
  humidity = humidities[0] # mean could be calculated, if many sensors
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  data2.plot(x="time",y=humidity,color='b',alpha=0.8, ax=ax)
  plt.ylim([-2, 102])
  plt.ylabel(' %',rotation=0)
  
  data1.plot(x="time",y=humidity,linestyle='dashed',ax=ax,color='b',alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=humidity,linestyle=':',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)
  

def hs110_days(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'hs110.svg'
  plotname = "HS110 consumption"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  t3 = t2 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  data0 = data[data['time'] > t0]
  data0 = data0[data0['time'] < t1]
  data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] > t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] > t2]
  data2 = data2[data2['time'] < t3]
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  data2.plot(x="time",y='olkkari power socket',color='b',alpha=0.8, ax=ax)
  #plt.ylim([-2, 102])
  plt.ylabel(' W',rotation=0)
  
  data1.plot(x="time",y='olkkari power socket',linestyle='dashed',ax=ax,color='b',alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y='olkkari power socket',linestyle=':',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

#plot_ts(['työkkäri']) # , '2021-05-08T16:15', '2021-05-10T17:10'

def electricity_price_days(data_orig, a, make_plot = True):
  plt.ioff()
  filename = 'electricity_price.svg'
  plotname = "Electricity price, past three days"
  if not make_plot:
    return html_link(plotname, filename)
  data = data_orig
  
  t2 = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  
  t3 = t2 + timedelta(hours = 24)
  t4 = t3 + timedelta(hours = 24)
  t1 = t2 - timedelta(hours = 24)
  t0 = t2 - timedelta(hours = 48)
  
  #data0 = data[data['time'] >= t0]
  #data0 = data0[data0['time'] < t1]
  #data0['time'] = data0['time'] + timedelta(hours = 48)
  
  data1 = data[data['time'] >= t1]
  data1 = data1[data1['time'] < t2]
  data1['time'] = data1['time'] + timedelta(hours = 24)
  
  data2 = data[data['time'] >= t2] # from start of the day to current
  data2 = data2[data2['time'] < datetime.now()]
  
  data3 = data[data['time'] >= datetime.now() - timedelta(hours = 1)] # from current to end of the day
  data3 = data3[data3['time'] < t3]
  
  data4 = data[data['time'] >= t3]
  data4 = data4[data4['time'] < t4]
  data4['time'] = data4['time'] - timedelta(hours = 24)
  
  price = "electricity price"
  
  fig, ax = plt.subplots(1,1,figsize=figure_size())
  data2.plot(x="time",y=price,color='b',alpha=0.8, ax=ax)
  #plt.ylim([-2, 102])
  plt.ylabel('          c/kWh',rotation=0)
  
  data1.plot(x="time",y=price,linestyle='dashed',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  #data0.plot(x="time",y=price,linestyle=':',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  
  if not data3.empty:
    data3.plot(x="time",y=price,ax=ax,color='r',alpha=0.8) # ax=ax laittaa samaan kuvaan
  if not data4.empty:
    data4.plot(x="time",y=price,linestyle='dashed',ax=ax,color='r',alpha=0.8) # ax=ax laittaa samaan kuvaan
  
  duck = kotibobot.electricity_price.duck_curve(data_orig)
  df_duck = pd.DataFrame()
  df_duck['time'] = data1['time']
  df_duck['duck'] = duck
  df_duck.plot(x="time",y='duck',ax=ax,color='k',alpha=0.8) # ax=ax laittaa samaan kuvaan
  
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  plt.xticks(rotation=0, ha='center')
  
  #plt.show()
  #plt.savefig('/var/www/html/kotibobot/' + filename)
  a.save(fig,'/var/www/html/kotibobot/' + filename)
  return html_link(plotname, filename)

def html_link(text,url):
  return "<a href='https://cloud.laurijokinen.com/kotibobot/" + url + "'>" + text +"</a>"

def main_function(draw_plots = True):
  data_orig = load_ts_data()
  data_orig_el = kotibobot.electricity_price.load_ts_data()
  a = AsyncPlotter()
  res = ["Kaikki huoneet"] # in html
  res.append(temp_hum_inside_outside_forecast(data_orig,a,draw_plots))
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
  
  el_price  = data['electricity price']
  el_prec   = data['electricity price precentile']*100
  el_prec_h = data['electricity price precentile hourly']*100
  el_freq = data['electricity frequency']
  
  res = ['Latest measurement on ' + str(times['LATEST'].strftime(timeformat)) + '\n']
  res.append("el. price precentile : {:.2f} %".format(el_price))
  res.append("el. price precentile hourly : {:.2f} %".format(el_prec))
  res.append("electricity price : {:.2f} snt/kWh".format(el_prec_h))
  res.append("el. frequency : {:.2f} Hz".format(el_freq))
  
  for col in data:
    if not col in ['time','electricity price','electricity price precentile hourly','electricity price precentile','electricity frequency']:
      if not times['LATEST'] == times[col]:
        res.append("{} : {:.4G}".format(col, data[col]))
      else:
        res.append("{} : {:.4G} (on {})".format(col, data[col], str(times[col].strftime(timeformat))))
  res.sort()
  return '\n'.join(res)
