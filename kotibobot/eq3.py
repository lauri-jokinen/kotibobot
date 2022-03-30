# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
import time
# import re # resplit

from house import *
from common_functions import *
import kotibobot.append_vacation
from kotibobot.command_queue import remove_append_vacation as remove_append_vacation

'''
def substitute_hard_offset(string):
  s = re.split('\n|°C| |\t', string)
  for i in range(len(s)):
    try:
      f = float(s[i])
    except:
      continue
    s[i] = str(f - hard_offset)
  return 
'''

def command(string):
  s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci1'] + string.split(' ')
  res = subprocess.run(s, stdout=subprocess.PIPE)
  res_str = res.stdout.decode('utf-8')
  if "Connection failed" in res_str or "ERROR" in res_str:
    #print('Yhteys pätki kerran')
    time.sleep(5)
    res = subprocess.run(s, stdout=subprocess.PIPE)
    res_str = res.stdout.decode('utf-8')
    if "Connection failed" in res_str or "ERROR" in res_str:
      #print('Yhteys pätki toisen kerran')
      time.sleep(5)
      res = subprocess.run(s, stdout=subprocess.PIPE)
      res_str = res.stdout.decode('utf-8')
  return res_str

# Extra definitions to the basic commands
def command_with_extras(string):
  if in_allday_timer_format(string):
    return command(string + ' 24:00')
  else:
    return command(string)

# input: makkari offset -1
#        työkkäri-makkari timer 12:00-13:00 17
def command_human(s):
  s = remove_extra_spaces(s)
  selected_rooms = s.split(" ")[0].split("-")
  
  # No command -> return status
  if len(s.split(" ")) == 1:
    command = " status"
  else:
    command = " " + (" ").join(s.split(" ")[1:])
  
  if "auto" in command or "man" in command:
    remove_append_vacation(selected_rooms)
  
  # the append-vacation functionality
  if "append-vacation" in command:
    return kotibobot.append_vacation.main(selected_rooms, command)
  
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

def store_attribute_database(mac, value, attribute):
  with open("/home/lowpaw/Downloads/kotibobot/eq3_offset.json") as json_file:
    json_data = json.load(json_file)
  json_data[mac + attribute] = value
  with open("/home/lowpaw/Downloads/kotibobot/eq3_offset.json", 'w') as json_file:
    json.dump(json_data, json_file)

def read_attribute_database(mac, attribute):
  with open("/home/lowpaw/Downloads/kotibobot/eq3_offset.json") as json_file:
    json_data = json.load(json_file)
  if (mac + attribute) in json_data:
    return json_data[mac + attribute]
  else:
    return 0.0

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
    #offset_reading = (res.split("Offset temperature:")[1]).split("°C")[0]
    #offset_reading = float(offset_reading.split(" ")[-1])
    #res_json['offset'] = offset_reading
    res_json['offset'] = read_attribute_database(mac, 'offset')
    res_json['integral'] = read_attribute_database(mac, 'integral')
    res_json['automode'] = int('auto' in res)
    res_json['vacationmode'] = int('vacation' in res) # note lowercase 'vacation'
    res_json['boostmode'] = int('boost' in res) # note lowercase 'vacation'
  except:
    res_json['target'] = float('nan')
    res_json['valve'] = float('nan')
    res_json['offset'] = read_attribute_database(mac, 'offset')
    res_json['integral'] = read_attribute_database(mac, 'integral')
    res_json['automode'] = -1
  return res_json

# command could be e.g. 'mac timer mon 22.5'
def in_allday_timer_format(command):
  arr = command.split(" ")
  return (len(arr) == 4 and arr[1] == 'timer')
