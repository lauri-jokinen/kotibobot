import kotibobot_functions as kotibobot
from datetime import datetime
import json
import pandas as pd
import time

def collect_and_save():
  new_data = json.loads("{}")
  
  new_data['time'] = json.loads("{}")
  new_data['time'] = pd.Timestamp.now()
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  
  selected_rooms = []
  for room in kotibobot.rooms:
    selected_rooms.append(room)
  
  # gather data
  for room in selected_rooms:
    for eq3 in kotibobot.eq3_in_rooms[room]:
      eq3_reading = kotibobot.eq3_to_json(kotibobot.name_to_mac[eq3])
      new_data[eq3 + " target"] = eq3_reading['target']
      new_data[eq3 + " valve"]  = eq3_reading['valve']
      new_data[eq3 + " offset"] = eq3_reading['offset']
      
    for sensor in kotibobot.mi_in_rooms[room]:
      mi_reading = kotibobot.mi_to_json(kotibobot.name_to_mac[sensor])
      new_data[sensor + " temp"]     = mi_reading['temp']
      new_data[sensor + " humidity"] = mi_reading['humidity']
  
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
  time.sleep(60*10)
