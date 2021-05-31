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
    for valve in kotibobot.eq3_in_rooms[room]:
      status = kotibobot.eq3_command(eq3.name_to_mac[valve] + ' sync')
      #status = 'not this time'
      if "Valve:" in status and "Temperature:" in status:
        valve_reading = (status.split("Valve:")[1]).split("%")[0]
        valve_reading = float(valve_reading.split(" ")[-1])
        target_reading = (status.split("Temperature:")[1]).split("°C")[0]
        target_reading = float(target_reading.split(" ")[-1])
      else:
        valve_reading = float("nan")
        target_reading = float("nan")
      
      new_data[valve + " target"] = json.loads("{}")
      new_data[valve + " target"] = target_reading
      new_data[valve + " valve"] = json.loads("{}")
      new_data[valve + " valve"] = valve_reading
      
    for sensor in kotibobot.mi_in_rooms[room]:
      mi_reading = kotibobot.mi_to_json(kotibobot.name_to_mac[sensor])
      if 'temp' in mi_reading and 'humidity' in mi_reading:
        temp_reading = mi_reading['temp']
        humidity_reading = mi_reading['humidity']
      else:
        temp_reading = float("nan")
        humidity_reading = float("nan")
      new_data[sensor + " temp"] = json.loads("{}")
      new_data[sensor + " temp"] = temp_reading
      new_data[sensor + " humidity"] = json.loads("{}")
      new_data[sensor + " humidity"] = humidity_reading
  
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
