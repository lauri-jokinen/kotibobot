# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
import time
from datetime import datetime, timedelta
# packages for time series
import dateutil.parser
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import pyplot
import matplotlib.dates as mdates # helps to format dates in x-axis
import math
import multiprocessing as mp # timeout function for Mi-command

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

rooms = json.loads("{}")

# FILL IN THE ROOM INFORMATION IN JSON FORMAT
# {"room1" : {"eq3": ["mac1","mac2"], "mi" : ["mac3"]}, ...}
rooms["olkkari"] = json.loads("{}")
rooms["olkkari"]["eq3"] = [koodit["keittiön nuppi"], koodit["olkkarin nuppi"]]
rooms["olkkari"]["mi"] = [koodit["olkkarin lämpömittari"]]

rooms["makkari"] = json.loads("{}")
rooms["makkari"]["eq3"] = [koodit["makkarin nuppi"]]
rooms["makkari"]["mi"] = [koodit["makkarin lämpömittari"]]

rooms["työkkäri"] = json.loads("{}")
rooms["työkkäri"]["eq3"] = [koodit["työkkärin nuppi"]]
rooms["työkkäri"]["mi"] = [koodit["työkkärin lämpömittari"]]

# FILL IN THE MAC ADDRESSES AND NAMES OF ALL DEVICES
# {"mac1": "device name", ...}
mac_to_name = json.loads("{}")
mac_to_name[koodit["keittiön nuppi"]] = "keittiön nuppi"
mac_to_name[koodit["olkkarin nuppi"]] = "olkkarin nuppi"
mac_to_name[koodit["makkarin nuppi"]] = "makkarin nuppi"
mac_to_name[koodit["työkkärin nuppi"]] = "työkkärin nuppi"
mac_to_name[koodit["työkkärin lämpömittari"]] = "työkkärin lämpömittari"
mac_to_name[koodit["makkarin lämpömittari"]] = "makkarin lämpömittari"
mac_to_name[koodit["olkkarin lämpömittari"]] = "olkkarin lämpömittari"

# Next we construct all sorts of structs and arrays ...

# name to mac, inverse of the above
name_to_mac = json.loads("{}")
for mac in mac_to_name:
  name_to_mac[mac_to_name[mac]] = mac

# Create an array with all mac-addresses of all the eq-3 devices
eq3s = []
for room in rooms:
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3s.append(eq3)

# Create an array with all mac-addresses of all the mi devices
mis = []
for room in rooms:
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mis.append(mi)

# eq3s in rooms
# {"room1" : ["name1"], ...}
eq3_in_rooms = json.loads("{}")
for room in rooms:
  eq3_in_rooms[room] = []
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3_in_rooms[room].append(mac_to_name[eq3])

# mi in rooms
# {"room1" : ["name1"], ...}
mi_in_rooms = json.loads("{}")
for room in rooms:
  mi_in_rooms[room] = []
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mi_in_rooms[room].append(mac_to_name[mi])

#### FUNCTIONS

def replace_macs_to_names(str):
  for mac in mac_to_name:
    str = str.replace(mac, mac_to_name[mac])
  return str

def eq3_command(str):
  s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci1'] + str.split(' ')
  res = subprocess.run(s, stdout=subprocess.PIPE)
  res_str = res.stdout.decode('utf-8')
  if "Connection failed" in res_str or "ERROR" in res_str:
    print('Yhteys pätki kerran')
    time.sleep(5)
    res = subprocess.run(s, stdout=subprocess.PIPE)
    res_str = res.stdout.decode('utf-8')
    if "Connection failed" in res_str or "ERROR" in res_str:
      print('Yhteys pätki toisen kerran')
      time.sleep(5)
      res = subprocess.run(s, stdout=subprocess.PIPE)
      res_str = res.stdout.decode('utf-8')
  return res_str

# Extra definitions to the basic commands
def eq3_command_with_extras(str):
  if in_allday_timer_format(str):
    return eq3_command(str + ' 24:00')
  else:
    return eq3_command(str)

# input: makkari offset -1
#        työkkäri-makkari timer 12:00-13:00 17
def eq3_command_human(str):
  str = remove_extra_spaces(str)
  selected_rooms = str.split(" ")[0].split("-")
  
  # No command -> return status
  if len(str.split(" ")) == 1:
    command = " status"
  else:
    command = " " + (" ").join(str.split(" ")[1:])
  
  res = [] # resulting strings are collected to this array
  if selected_rooms[0] == "kaikki":
    for eq3 in eq3s:
      res.append(replace_macs_to_names(eq3_command_with_extras(eq3 + command)))
  else:
    for room in selected_rooms:
      if room in rooms and "eq3" in rooms[room]:
        for eq3 in rooms[room]["eq3"]:
          res.append(replace_macs_to_names(eq3_command_with_extras(eq3 + command)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res

def eq3_to_json(mac):
  res = eq3_command(mac + ' sync')
  res_json = json.loads("{}")
  try:
    target_reading = (res.split("Temperature:")[1]).split("°C")[0]
    target_reading = float(target_reading.split(" ")[-1])
    res_json['target'] = target_reading
    valve_reading = (res.split("Valve:")[1]).split("%")[0]
    valve_reading = float(valve_reading.split(" ")[-1])
    res_json['valve'] = valve_reading
    offset_reading = (res.split("Offset temperature:")[1]).split("°C")[0]
    offset_reading = float(offset_reading.split(" ")[-1])
    res_json['offset'] = offset_reading
  except:
    res_json['target'] = float('nan')
    res_json['valve'] = float('nan')
    res_json['offset'] = float('nan')
  return res_json

#def mi_command_2(mac,return_dict):
def mi_command_2(mac):
  try:
    s = ['/home/lowpaw/Downloads/mi_scripts/LYWSD03MMC.py', '--device', mac, '--count', '1', '--unreachable-count', '3']
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 32)
    res_str = res.stdout.decode('utf-8')
  except:
    res_str = "ERROR: Unknown error with a Mi device."
  return res_str
  #return_dict['res'] = res_str
'''
def mi_command_3(mac):
  q = multiprocessing.Queue()
  # Create a shared dictionary for results
  manager = multiprocessing.Manager()
  return_dict = manager.dict()
  
  # Start process
  p = multiprocessing.Process(target=mi_command_2, args=(mac,return_dict))
  p.start()
  
  # Check every 0.1 seconds if the process is done
  for i in range(250): #290
    if not p.is_alive():
      print('Odotus palkittiin ' +str(i/10) +' sekunnin jälkeen.')
      break
    time.sleep(0.1)
  
  # Kill if the process is still running after the wait
  if p.is_alive():
    print("Mi command is still running, let's kill it!")
    return_dict['res'] = "ERROR: Mi device timeout."
    p.terminate()
    time.sleep(0.1)
    p.join(timeout=2.0)
    q.close()
    
  # Return results
  return return_dict['res']
'''
def mi_command(mac):
  res = mi_command_2(mac)
  if "ERROR" in res or 'unsuccessful' in res:
    res = mi_command_2(mac)
    if "ERROR" in res or 'unsuccessful' in res:
      return mi_command_2(mac)
  return res

def mi_to_json(mac):
  res = mi_command(mac)
  mi_json = json.loads("{}")
  try:
    mi_json['temp'] = float(remove_extra_spaces(res.split('Temperature:')[1].split('\nHumidity')[0]))
    mi_json['humidity'] = float(remove_extra_spaces(res.split('Humidity:')[1].split('\nBattery')[0]))
    mi_json['battery'] = float(remove_extra_spaces(res.split('Battery level:')[1].split('\n1 measurem')[0]))
  except:
    mi_json['temp'] = float('nan')
    mi_json['humidity'] = float('nan')
    mi_json['battery'] = float('nan')
  return mi_json
  
def mi_read_human(s):
  s = remove_extra_spaces(s)
  selected_rooms = s.split(" ")[0].split("-")
  res = []
  if selected_rooms[0] == "kaikki":
    for mi in mis:
      res.append(mi_command(mi))
  else:
    for room in selected_rooms:
      if room in rooms and "mi" in rooms[room]:
        for mi in rooms[room]["mi"]:
          res.append(replace_macs_to_names(mi_command(mi)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res

def remove_extra_spaces(str):
  arr = str.split(" ")
  i = 0
  while i < len(arr):
    if arr[i] == '':
      arr.pop(i)
    else:
      i = i+1
  return " ".join(arr)
  
# command : 'mac timer mon 22.5'
def in_allday_timer_format(command):
  arr = command.split(" ")
  return (len(arr) == 4 and arr[1] == 'timer')

"""
FUNCTIONS THAT ARE NO LONGER USED
# command : 'mac timer mon 19:00-20:00 22.5'
# command is identified by 'timer', number of spaces, and '-' between the times
def in_new_timer_format(command):
  arr = command.split(" ")  
  if len(arr) == 5 and arr[1] == 'timer':
    times = arr[3].split("-")
    return len(times) == 2
  return False

def str_to_time(str):
    if str == '24:00':
        return datetime.strptime('1900-01-02 00:00', '%Y-%m-%d %H:%M')
    else:
        return datetime.strptime(str, '%H:%M')

def new_timer_command(old_command, new_command):
    # Convert str to time
    try:
        t1 = str_to_time(new_command.split('-')[0])
        t2 = str_to_time(new_command.split('-')[1].split(" ")[0])
        temp = new_command.split(" ")[1]
        temp_float = float(temp)
    except:
        return "ERROR: Invalid syntax. Example of a valid input: '9:30-10:00 18.5'"
    if t1 >= t2:
        return "ERROR: Invalid time period."

    if t1.strftime("%M")[-1] != '0' or t2.strftime("%M")[-1] != '0':
        return "ERROR: The times must be rounded to ten minutes. For example, 19:11 is invalid and 19:10 is valid."

    if 2*temp_float % 1 != 0.0:
        return "ERROR: Temperature must be rouded to a half of a celsius."

    if temp_float < 5 or temp_float > 29.5:
        return "ERROR: Temperature must lie in between 5 and 29.5."
    
    old = old_command.split(' ')
    
    # Look for the indices where to remove the old array
    # we keep [0:start_ind] and [end_ind:]
    i = 0
    start_ind = -1
    while start_ind == -1 and i < len(old)/2:
        if str_to_time(old[1+2*i]) >= t1:
            start_ind = 2*i+1
        i = i+1
    
    i = 0
    end_ind = -1
    while end_ind == -1 and i < len(old)/2:
        if str_to_time(old[1+2*i]) > t2:
            end_ind = 2*i
        i = i+1
    
    # Create new array, from the start
    if start_ind != -1:
        new_arr = old[0:start_ind]
    else:
        new_arr = []
    
    # Add new timer settings
    new_arr.append(t1.strftime("%H:%M"))
    new_arr.append(temp)
    if new_command.split('-')[1].split(" ")[0] == '24:00':
        new_arr.append('24:00')
    else:
        new_arr.append(t2.strftime("%H:%M"))
    
    # Add the rest of the old timer setting
    if end_ind != -1:
        new_arr = new_arr + old[end_ind:]
    
    # Remove possible '00:00'
    if new_arr[1] == '00:00':
        new_arr = new_arr[2:]
    
    # Cleanup: remove the same consecutive temperatures
    i = 0
    while i+2 < len(new_arr):
        if float(new_arr[i]) == float(new_arr[i+2]):
            new_arr = new_arr[0:i] + new_arr[(i+2):]
        else:
            i = i+2

    # See if the schedule is too long
    if len(new_arr)/2 > 7:
        return "ERROR: Too complicated schedule. Up to seven events are possible per day."
    return " ".join(new_arr)


#Luo funktio : timer1 == timer2;

def set_different_days_with_new_timer_command(old, new_command, days):
  #old = [mon: '', ...]
  #new_command = 
  print(old)
  print(new_command)
  print(days)
  
  if days == 'everyday':
    day_set = ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri']
  elif days == 'weekend':
    day_set = ['sat', 'sun']
  else:
    day_set = [days] # eli esim. ['mon']
  
  all_equal = True
  timer_first = new_timer_command(old[day_set[0]], new_command)
  print('Eka päivä:')
  print(timer_first)
  
  for day in day_set:
    if not timers_equal(timer_first, new_timer_command(old[day], new_command)):
      all_equal = False
  
  if all_equal:
    print('kaikki päivät samanlaisia; lopullinen komento:')
    print(days + ' ' + timer_first)
    return [days + ' ' + timer_first]
    
  else:
    res_set = []
    print('kaikki päivät ei samanlaisia; lopulliset komennot:')
    for day in day_set:
      print(day + ' ' + new_timer_command(old[day], new_command))
      res_set.append(day + ' ' + new_timer_command(old[day], new_command))
    return res_set

# e.g., '25 10:00 13 24:00'
def timers_equal(one, other):
  a = one.split(' ')
  b = other.split(' ')
  if len(a) != len(b):
    return False
  
  for i in range(len(a)):
    if i%2 == 0:
      if float(a[i]) != float(b[i]):
        return False
    else:
      if str_to_time(a[i]) != str_to_time(b[i]):
        return False
  return True
"""
# TIME SERIES PLOTTING

def load_ts_data():
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  return pd.read_pickle(file_name)

def plot_temp_48_all_rooms(data_orig):
  #data = load_ts_data()
  data = data_orig
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  temps = []
  for room in rooms:
    for sensor in mi_in_rooms[room]:
      temps.append(sensor + " temp")
  
  ax = data.plot(x="time",y=(temps), alpha=0.7)
  pyplot.ylabel('    °C',rotation=0)
  
  lim = list(pyplot.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  #pyplot.ylim([-2, 102])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  #pyplot.ylabel('%',rotation=0)
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-d.%-m. - %-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  
  #pyplot.show()
  filename = 'temp_allrooms.svg'
  pyplot.savefig('/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link("Temperature, 48h all rooms", filename)

def plot_temp_48(room, data_orig):
  #data = load_ts_data()
  data = data_orig
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  
  t_start = datetime.now() - timedelta(hours = 48)
  t_end = datetime.now()
  
  data = data[data['time'] > t_start]
  data = data[data['time'] < t_end]
  
  valves = []
  for eq3 in eq3_in_rooms[room]:
    valves.append(eq3 + " valve")
  
  targets = []
  for eq3 in eq3_in_rooms[room]:
    targets.append(eq3 + " target")
      
  temps = []
  for sensor in mi_in_rooms[room]:
    temps.append(sensor + " temp")
  
  ax = data.plot(x="time",y=(temps), alpha=0.7, color='r')
  ax = data.plot(x="time",y=(targets), alpha=0.7,linestyle='dashed', ax=ax)
  pyplot.ylabel('°C   ',rotation=0)
  
  lim = list(pyplot.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  data.plot(x="time",y=(valves),secondary_y=True,linestyle=':', ax=ax, alpha=0.7) # ax=ax laittaa samaan kuvaan
  pyplot.ylim([-2, 102])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  pyplot.ylabel('%',rotation=0)
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-d.%-m. - %-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  
  #pyplot.show()
  filename = room + '_target_temp.svg'
  pyplot.savefig('/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link("Temperature, 48h", filename)

def plot_temp_offset(room, data_orig):
  #data = load_ts_data()
  data = data_orig
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  
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
  #offsets.append('error')
  
  ax = data.plot(x="time",y='error', alpha=0.7, color = 'm')
  data.plot(x="time",y=offsets, linestyle='dashed', alpha=0.7, ax=ax)
  pyplot.ylabel('°C   ',rotation=0)
  
  lim = list(pyplot.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  
  data.plot(x="time",y=valves, secondary_y=True,ax=ax,linestyle=':', alpha=0.7) # ax=ax laittaa samaan kuvaan
  pyplot.ylabel('%',rotation=0)
  ax.set_xlabel('')
  pyplot.ylim([-2, 102])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax.set_yticks([0.0001], minor=True)
  
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.yaxis.grid(True, which='minor')
  ax.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-d.%-m. - %-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  
  #pyplot.show()
  filename = room + '_offset.svg'
  pyplot.savefig('/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link("Error, 48h", filename)


def plot_temp_days(room, data_orig):
  #data = load_ts_data()
  data = data_orig
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  
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
  
  ax = data2.plot(x="time",y=temp,color='r', alpha=0.8)
  data1.plot(x="time",y=temp,linestyle='dashed',ax=ax,color='r', alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=temp,linestyle=':',ax=ax,color='r', alpha=0.6) # ax=ax laittaa samaan kuvaan
  pyplot.ylabel('    °C',rotation=0)
  ax.set_xlabel('')
  
  lim = list(pyplot.ylim())
  lim[0] = math.floor(lim[0])
  lim[1] = math.ceil(lim[1])
  ax.set_yticks(list(range(lim[0],lim[1]+1)), minor=False)
  ax.yaxis.grid(True, which='major', alpha = 0.2)
  ax.xaxis.grid(True, alpha=0.2)
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  
  #pyplot.show()
  filename = room + '_temp.svg'
  pyplot.savefig('/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link("Temperature, past three days", filename)
  
def plot_humidity_days(room, data_orig):
  #data = load_ts_data()
  data = data_orig
  #data = pd.DataFrame(series)
  #data['time'] = pd.to_datetime(data['time'], format="%Y-%m-%dT%H:%M")
  
  #t_start = "2021-05-08T16:15"
  #t_end   = "2021-05-10T17:10"
  #data = data[data['time'] > pd.to_datetime(t_start, format="%Y-%m-%dT%H:%M")]
  #data = data[data['time'] < pd.to_datetime(t_end, format="%Y-%m-%dT%H:%M")]
  
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
  
  ax = data2.plot(x="time",y=humidity,color='b',alpha=0.8)
  pyplot.ylim([-2, 102])
  pyplot.ylabel(' %',rotation=0)
  
  data1.plot(x="time",y=humidity,linestyle='dashed',ax=ax,color='b',alpha=0.7) # ax=ax laittaa samaan kuvaan
  data0.plot(x="time",y=humidity,linestyle=':',ax=ax,color='b',alpha=0.6) # ax=ax laittaa samaan kuvaan
  ax.set_xlabel('')
  
  myFmt = mdates.DateFormatter('%-H:%M')
  ax.xaxis.set_major_formatter(myFmt)
  ax.xaxis.grid(True, alpha=0.2)
  ax.yaxis.grid(True, alpha=0.2)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")
  
  #pyplot.show()
  filename = room + '_humidity.svg'
  #pyplot.savefig('/home/lowpaw/Downloads/kotibobot/' + filename)
  pyplot.savefig('/var/www/html/kotibobot/' + filename)
  #subprocess.run(['cp', '/home/lowpaw/Downloads/kotibobot/' + filename, '/var/www/html/kotibobot/'])
  return html_link("Humidity, past three days", filename)

#plot_ts(['työkkäri']) # , '2021-05-08T16:15', '2021-05-10T17:10'

def html_link(text,url):
  return "<a href='https://cloud.laurijokinen.com/kotibobot/" + url + "'>" + text +"</a>"

def plot_parallel():
  pool = mp.Pool(mp.cpu_count())
  pool.map(plot_parallel_indivudal_tasks, [index for index in range(plot_parallel_task_length())])
  pool.close()

def plot_parallel_indivudal_tasks(index):
  data_orig = load_ts_data()
  if index == 0:
    plot_temp_48_all_rooms(data_orig)
  k = 1
  for room in rooms:
    if k == index:
      plot_temp_48(room, data_orig)
    if k+1 == index:
      plot_temp_offset(room, data_orig)
    if k+2 == index:
      plot_temp_days(room, data_orig)
    if k+3 == index:
      plot_humidity_days(room, data_orig)
    k=k+4
    
def plot_parallel_task_length():
  k = 1
  for room in rooms:
    k=k+4
  return k-1
    
def plot_main_function():
  data_orig = load_ts_data()
  res = ["Kaikki huoneet"] # in html
  res.append(plot_temp_48_all_rooms(data_orig))
  for room in rooms:
    res.append("\n" + room.capitalize())
    res.append(plot_temp_48(room, data_orig))
    res.append(plot_temp_offset(room, data_orig))
    res.append(plot_temp_days(room, data_orig))
    res.append(plot_humidity_days(room, data_orig))
  return "\n".join(res)

def read_latest_data():
  data = load_ts_data()
  index = len(data.index)-1
  cols = data.columns.values.tolist()
  res = ['Latest measurement at ' + str(data.iloc[index]['time'])]
  for col in cols:
    if not col == 'time':
      if not math.isnan(data.iloc[-1][col]):
        res.append(col + ' : ' + str(data.iloc[-1][col]))
      else:
        index = len(data.index)-1
        while index > 0 and math.isnan(data.iloc[index][col]):
          index = index - 1
        res.append(col + ' : ' + str(data.iloc[index][col]) + ' (timestamp: ' + str(data.iloc[index]['time']) + ')')
  res.sort()
  return '\n'.join(res)

#print(read_latest_data())
'''
  q = multiprocessing.Queue()
  # Create a shared dictionary for results
  manager = multiprocessing.Manager()
  return_dict = manager.dict()
  
  # Start process
  p = multiprocessing.Process(target=mi_command_2, args=(mac,return_dict))
  p.start()
  
  # Check every 0.1 seconds if the process is done
  for i in range(250): #290
    if not p.is_alive():
      print('Odotus palkittiin ' +str(i/10) +' sekunnin jälkeen.')
      break
    time.sleep(0.1)
  
  # Kill if the process is still running after the wait
  if p.is_alive():
    print("Mi command is still running, let's kill it!")
    return_dict['res'] = "ERROR: Mi device timeout."
    p.terminate()
    time.sleep(0.1)
    p.join(timeout=2.0)
    q.close()
'''
