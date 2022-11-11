import numpy as np
from datetime import datetime, timedelta
from scipy import ndimage
#from pathlib import Path
import json
import kotibobot.command_queue
from house import eq3s
from house import rooms
from house import hard_offset
from os.path import exists

everyday = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
weekdays = ['mon', 'tue', 'wed', 'thu', 'fri']
weekend = ['sat', 'sun']

def only_time(a):
  ta = a.strftime('%H:%M')
  return datetime.strptime(ta, '%H:%M')

def eq3_schedule(sched):
  return simplify(bound(round1(sched)))

def eq3_command(room, day, sched):
  arr = eq3_format_array(simplify(round1(bound(sched-hard_offset[room]))))
  res = []
  for p in arr:
    res.append(str(p[2]))
    res.append(p[1])
  if len(res) == 2: # fixes a eq-3 bug with constant temp, e.g. '...everyday 21.5 24:00'
    res = [str(p[2]), '12:00', str(p[2]), '24:00']
  command = " ".join(res)
  kotibobot.command_queue.append(room + ' timer ' + day + ' ' + command)
  #print(room + ' timer ' + day + ' ' + command)
  return room + ' timer ' + day + ' ' + command

def bound(sched):
  res = np.zeros(24*3*2)
  for i in range(len(sched)):
    res[i] = min(30.0, max(5.0, sched[i]))
  return res


def print_whole_schedule(sched_days):
  res = []
  for day in everyday:
    arr2 = eq3_format_array(sched_days[day])
    res2 = []
    for p in arr2:
      res2.append(p[0] + '-' + p[1] + ' ' + str(p[2]))
    string = "\n".join(res2)
    res.append(day.capitalize() +'\n' + string)
  return '\n\n'.join(res)

def eq3_format_array(sched):
  dateformat = '%H:%M'
  i = 0
  j = 1
  ti = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
  tj = ti+timedelta(minutes=10)
  res = []
  while j < len(sched):
    if sched[i] == sched[j]:
      j = j+1
      tj = tj+timedelta(minutes=10)
    else:
      res.append([ti.strftime(dateformat), tj.strftime(dateformat), sched[i]])
      i = j
      j = j+1
      ti = tj
      tj = tj+timedelta(minutes=10)
  res.append([ti.strftime(dateformat), '24:00', sched[i]])
  return res
  
def simplify(sched):
    res = np.zeros(24*3*2)
    res = sched
    c = 1
    while not eq3_specs_ok(res):
      c = c+2
      res = np.ndarray.tolist(ndimage.median_filter(sched, size = c, mode='wrap'))
    res = np.array(res)
    return res

def round1(sched):
  res = np.zeros(24*3*2)
  res = np.round(sched*2)/2
  return res

def eq3_specs_ok(sched):
    return len(eq3_format_array(sched)) <= 5

def read(sched,time): # time is datetime
  t = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
  j = -1
  while only_time(t) <= only_time(time) and j+1 < len(sched):
    t = t+timedelta(minutes=10)
    j = j+1
  # t = t-timedelta(minutes=10) <- time of the given temperature
  return sched[j]

def to_day_list(string):
  if string == 'everyday':
    return everyday
  elif string == 'weekend':
    return weekend
  elif string == 'weekdays':
    return weekdays
  else:
    return [string]

def set1(room,d,T,t1,t2,do_eq3_command=False,export_schedule=False): # ti 1 and t2 are strings
  if t2=='24:00':
    t2 = '23:59'
    
  if t1=='24:00':
    t1 = '23:59'
  if datetime.strptime(t1, '%H:%M') > datetime.strptime(t2, '%H:%M'):
    return "ERROR: Invalid time interval"
  
  days = to_day_list(d)
  schedule = import1()
  
  for day in days:
    if "eq3" in rooms[room]:
      for eq3 in rooms[room]["eq3"]:
        t = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
        j = -1
        
        # find index for t1
        while only_time(t) <= datetime.strptime(t1, '%H:%M') and j+1 < len(schedule[eq3][day]):
          t = t+timedelta(minutes=10)
          j = j+1
        
        # set temperatures until t2
        while only_time(t) < datetime.strptime(t2, '%H:%M') and j+1 < len(schedule[eq3][day]):
          t = t+timedelta(minutes=10)
          schedule[eq3][day][j] = T
          j = j+1
        
        schedule[eq3][day][j] = T
        last_eq3 = eq3
  
  if do_eq3_command:
    for day in days:
      eq3_command(room, day, schedule[last_eq3][day])
  
  if export_schedule:
    export1(schedule)
  
  return print_whole_schedule(schedule[last_eq3])


def import1():
  file_name = "/home/lowpaw/Downloads/kotibobot/schedules.json"
  if exists(file_name):
    with open(file_name, 'r') as json_file:
      s = json.load(json_file)
  else:
    s = json.loads("{}")
  schedules = json.loads("{}")
  
  for eq3 in eq3s:
    schedules[eq3] = json.loads("{}")
    if eq3 in s:
      for day in everyday:
        if day in s[eq3]:
          schedules[eq3][day] = np.array(s[eq3][day])
        else:
          schedules[eq3][day] = np.zeros(24*3*2)
    else:
      for day in everyday:
        schedules[eq3][day] = np.zeros(24*3*2)
  return schedules

def export1(schedules):
  s = json.loads("{}")
  for eq3 in schedules:
    s[eq3] = json.loads("{}")
    for day in everyday:
      s[eq3][day] = np.ndarray.tolist(schedules[eq3][day])
  with open("/home/lowpaw/Downloads/kotibobot/schedules.json", 'w') as json_file:
    json.dump(s, json_file)
