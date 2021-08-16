# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
import time

from house import *
from common_functions import *

def command(str):
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
def command_with_extras(str):
  if in_allday_timer_format(str):
    return command(str + ' 24:00')
  else:
    return command(str)

# input: makkari offset -1
#        työkkäri-makkari timer 12:00-13:00 17
def command_human(str):
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
      res.append(replace_macs_to_names(command_with_extras(eq3 + command)))
  else:
    for room in selected_rooms:
      if room in rooms and "eq3" in rooms[room]:
        for eq3 in rooms[room]["eq3"]:
          res.append(replace_macs_to_names(command_with_extras(eq3 + command)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res

def to_json(mac):
  res = command(mac + ' sync')
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

# command could be e.g. 'mac timer mon 22.5'
def in_allday_timer_format(command):
  arr = command.split(" ")
  return (len(arr) == 4 and arr[1] == 'timer')