from datetime import datetime
import json
import pandas as pd
import numpy as np

import kotibobot
from house import *
from common_functions import *

def collect_and_save():
  new_data = json.loads("{}")
  
  new_data['time'] = json.loads("{}")
  new_data['time'] = pd.Timestamp.now().round(freq='T') # round to minutes
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  
  selected_rooms = []
  for room in rooms:
    selected_rooms.append(room)
  
  # gather data
  for room in selected_rooms:
    for eq3 in eq3_in_rooms[room]:
      eq3_reading = kotibobot.eq3.to_json(name_to_mac[eq3])
      new_data[eq3 + " target"] = np.half(eq3_reading['target']) # conversion to half-precision float
      new_data[eq3 + " valve"]  = np.half(eq3_reading['valve'])
      new_data[eq3 + " vacationmode"]  = np.half(eq3_reading['vacationmode'])
      new_data[eq3 + " boostmode"]  = np.half(eq3_reading['boostmode'])
      new_data[eq3 + " automode"]  = np.half(eq3_reading['automode'])
      
    for sensor in mi_in_rooms[room]:
      mi_reading = kotibobot.mi.to_json(name_to_mac[sensor])
      new_data[sensor + " temp"]     = np.single(mi_reading['temp'])
      new_data[sensor + " humidity"] = np.half(mi_reading['humidity'])
  
  try:
    new_data["outside temp"] = np.single(kotibobot.weather.temp())
    new_data["outside humidity"] = np.half(kotibobot.weather.humidity())
  except:
    'nothing here'
  
  #new_data["olkkari power socket"] = np.half(kotibobot.hs110.ufox_power())
  
  new_df = pd.json_normalize(new_data)
  
  new_file = False
  
  try:
    df = pd.read_pickle(file_name)
    df = pd.concat([df, new_df], sort=False, ignore_index=True)
  except:
    df = new_df
    new_file = True
  
  #print(df)
  
  df.to_pickle(file_name)



def two_latest_datas(col, data):
  return [data.iloc[-2][col], data.iloc[-1][col]]

def inform_window_actions():
  df = kotibobot.plotting.load_ts_data()
  df['olkkarin lämpömittari temp'] = df['olkkarin lämpömittari temp'] + 4.8/100 * df['olkkarin lämpömittari humidity']
  df['työkkärin lämpömittari temp'] = df['työkkärin lämpömittari temp'] + 4.8/100 * df['työkkärin lämpömittari humidity']
  df['makkarin lämpömittari temp'] = df['makkarin lämpömittari temp'] + 4.8/100 * df['makkarin lämpömittari humidity']
  df['outside temp'] = df['outside temp'] + 4.8/100 * df['outside humidity']
  
  subdf = df[['outside temp', 'olkkarin lämpömittari temp']].dropna()
  outside_temps = two_latest_datas('outside temp',subdf)
  pivot_temps = two_latest_datas('olkkarin lämpömittari temp',subdf)
  if outside_temps[0] > pivot_temps[0] and  pivot_temps[1] >= outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Olkkarin ikkuna auki ja liesituuletin päälle')
  if outside_temps[0] <= pivot_temps[0] and  pivot_temps[1] < outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Olkkarin ikkuna kiinni ja liesituuletin pois')
    kotibobot.hs110.ufox_command('off')
    kotibobot.hs110.ufox_command('off')
  
  subdf = df[['outside temp', 'työkkärin lämpömittari temp']].dropna()
  outside_temps = two_latest_datas('outside temp',subdf)
  pivot_temps = two_latest_datas('työkkärin lämpömittari temp',subdf)
  if outside_temps[0] > pivot_temps[0] and  pivot_temps[1] >= outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Työkkärin ikkuna auki')
  if outside_temps[0] <= pivot_temps[0] and  pivot_temps[1] < outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Työkkärin ikkuna kiinni')
    kotibobot.hs110.tyokkari_humidifier_command('off')
    kotibobot.hs110.tyokkari_humidifier_command('off')
  
  subdf = df[['outside temp', 'makkarin lämpömittari temp']].dropna()
  outside_temps = two_latest_datas('outside temp',subdf)
  pivot_temps = two_latest_datas('makkarin lämpömittari temp',subdf)
  if outside_temps[0] > pivot_temps[0] and  pivot_temps[1] >= outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Makkarin ikkuna auki')
  if outside_temps[0] <= pivot_temps[0] and  pivot_temps[1] < outside_temps[1]:
    kotibobot.requests_robust.telegram_message('Makkarin ikkuna kiinni')
    kotibobot.hs110.makkari_humidifier_command('off')
    kotibobot.hs110.makkari_humidifier_command('off')
  


collect_and_save()
inform_window_actions()
kotibobot.plotting.main_function()

#kotibobot.hs110.makkari_humidifier_automation() # moved to demand_response.py
#kotibobot.hs110.tyokkari_humidifier_automation()

kotibobot.thermostat_offset_controller.apply_control()
kotibobot.command_queue.do()

#print('jii')

#kotibobot.requests_robust.telegram_message('jii!')

