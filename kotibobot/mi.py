# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash
#from lywsd03mmc import Lywsd03mmcClient

from house import *
from common_functions import *

def command_2(mac):
  try:
    s = ['/home/lowpaw/Downloads/mi_scripts/LYWSD03MMC.py', '--device', mac, '--count', '1', '--unreachable-count', '5', '--interface', '1']
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 60)
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
'''
def to_json_new_bad(mac):
  mi_json = json.loads("{}")
  mi_json['temp']     = float('nan')
  mi_json['humidity'] = float('nan')
  mi_json['battery']  = float('nan')
  for i in range(10):
    try:
      data = Lywsd03mmcClient(mac).data
      mi_json['temp'] = data.temperature
      mi_json['humidity'] = data.humidity
      mi_json['battery'] = data.battery
      break
    except:
      'nothing here'
    time.sleep(0.68)
  return mi_json
'''
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
