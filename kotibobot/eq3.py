# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
import time
from datetime import datetime

from house import *
from common_functions import *
from kotibobot.command_queue import append as command_queue_append

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
  
  ### THE APPEND-VACATION FUNCTIONALITY
  if "append-vacation" in str:
    sync_info = command_human("-".join(selected_rooms) + " sync")
    
    while len(sync_info)>=2: # this loop seeks a non-erronous sync report
      if "Connection failed" in sync_info[0] or "ERROR" in sync_info[0]:
        sync_info.pop(0)
      else:
        sync_info.pop(1)
    
    if "Connection failed" in sync_info[0] or "ERROR" in sync_info[0]:
      return ["ERROR: Devices did not return anything sensible with sync-command"]
    
    if "vacation" in sync_info[0]:
      current_vacation_datetime = read_vacation_datetime_from_sync(sync_info[0])
      new_vacation_datetime     = read_vacation_datetime_from_command(command)
      
      if current_vacation_datetime < new_vacation_datetime:
        # if existing vacation mode is longer than the new one, set a timer onto command_queue with new temp
        # this is in case of other existing commands in the queue and overwriting them
        res = command_human("-".join(selected_rooms) + " " + command[8:])
        command_queue_append("@" + current_vacation_datetime.isoformat() + " " + "-".join(selected_rooms) + " " + command[8:])
        return res
        
      elif current_vacation_datetime > new_vacation_datetime:
        # if existing vacation mode is longer than the new one, set a timer onto command_queue with old temp
        res = command_human("-".join(selected_rooms) + " " + command[8:])
        old_temp = (sync_info[0].split("Temperature:")[1]).split("°C")[0]
        old_temp = remove_extra_spaces(old_temp)
        command_array = command[8:].split(" ")
        command_array[-1] = old_temp
        command = " ".join(command_array)
        command_queue_append("@" + new_vacation_datetime.isoformat() + " " + "-".join(selected_rooms) + " " + current_vacation_datetime.strftime("%y-%m-%d %H:%M") + " " + old_temp)
        return res
        
      else: # if existing vacation mode has same end time as the new one, simply overwrite it
        command_human("-".join(selected_rooms) + " " + command[8:])
        
    else: # if no existing vacation mode, set it normally
      return command_human("-".join(selected_rooms) + " " + command[8:])
  ### END of the the append-vacation functionality
  
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
  
def read_vacation_datetime_from_sync(s):
  datetime_str = (s.split("Vacation until:")[1]).split("\n")[0]
  datetime_str = remove_extra_spaces(datetime_str)
  return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

def read_vacation_datetime_from_command(c):
  datetime_str = c.split("vacation ")[1]
  datetime_str = remove_extra_spaces(datetime_str)
  datetime_str = datetime_str[0:14]
  return datetime.strptime(datetime_str, '%y-%m-%d %H:%M')
