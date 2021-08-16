# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash

from house import *
from common_functions import *

def command_2(mac):
  try:
    s = ['/home/lowpaw/Downloads/mi_scripts/LYWSD03MMC.py', '--device', mac, '--count', '1', '--unreachable-count', '3']
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 32)
    res_str = res.stdout.decode('utf-8')
  except:
    res_str = "ERROR: Unknown error with a Mi device."
  return res_str
  #return_dict['res'] = res_str

def command(mac):
  res = command_2(mac)
  if "ERROR" in res or 'unsuccessful' in res:
    res = command_2(mac)
    if "ERROR" in res or 'unsuccessful' in res:
      return command_2(mac)
  return res

def to_json(mac):
  res = command(mac)
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
  
def read_human(s):
  s = remove_extra_spaces(s)
  selected_rooms = s.split(" ")[0].split("-")
  res = []
  if selected_rooms[0] == "kaikki":
    for mi in mis:
      res.append(command(mi))
  else:
    for room in selected_rooms:
      if room in rooms and "mi" in rooms[room]:
        for mi in rooms[room]["mi"]:
          res.append(replace_macs_to_names(command(mi)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res