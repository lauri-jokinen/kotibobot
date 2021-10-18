from datetime import datetime
import json
import pandas as pd
import time

import kotibobot
from house import *
from common_functions import *

import kotibobot.thermostat_offset_controller

def collect_and_save():
  new_data = json.loads("{}")
  
  new_data['time'] = json.loads("{}")
  new_data['time'] = pd.Timestamp.now()
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  
  selected_rooms = []
  for room in rooms:
    selected_rooms.append(room)
  
  # gather data
  for room in selected_rooms:
    for eq3 in eq3_in_rooms[room]:
      eq3_reading = kotibobot.eq3.to_json(name_to_mac[eq3])
      new_data[eq3 + " target"] = eq3_reading['target']
      new_data[eq3 + " valve"]  = eq3_reading['valve']
      new_data[eq3 + " offset"] = eq3_reading['offset']
      
    for sensor in mi_in_rooms[room]:
      mi_reading = kotibobot.mi.to_json(name_to_mac[sensor])
      new_data[sensor + " temp"]     = mi_reading['temp']
      new_data[sensor + " humidity"] = mi_reading['humidity']
  
  new_data["outside temp"] = kotibobot.weather.temp()
  new_data["outside humidity"] = kotibobot.weather.humidity()
  
  new_df = pd.json_normalize(new_data)
  
  new_file = False
  
  try:
    df = pd.read_pickle(file_name)
    df = df.append(new_df, sort=False, ignore_index=True)
  except:
    df = new_df
    new_file = True
  
  print(df)
  
  df.to_pickle(file_name)

while True:
  collect_and_save()
  kotibobot.plotting.main_function()
  time.sleep(60*3)
  restart_bluetooth()
  time.sleep(60*2)
  try:
    kotibobot.command_queue.do()
  except:
    print('Queue run failed')
  time.sleep(60*2)
  try:
    kotibobot.thermostat_offset_controller.apply_control()
  except:
    print('Jotain meni pieleen kontrollissa, kun erroria pukkaa')
