from datetime import datetime
import json
import pandas as pd
import numpy as np

import kotibobot
#import kotibobot.eq3, kotibobot.mi, kotibobot.weather, kotibobot.hs110, kotibobot.plotting, kotibobot.regression, kotibobot.command_queue, kotibobot.thermostat_offset_controller
#from kotibobot import *
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
  
  new_data["outside temp"] = np.single(kotibobot.weather.temp())
  new_data["outside humidity"] = np.half(kotibobot.weather.humidity())
  
  #new_data["olkkari power socket"] = np.half(kotibobot.hs110.ufox_power())
  
  new_df = pd.json_normalize(new_data)
  
  new_file = False
  
  try:
    df = pd.read_pickle(file_name)
    df = df.append(new_df, sort=False, ignore_index=True)
  except:
    df = new_df
    new_file = True
  
  #print(df)
  
  df.to_pickle(file_name)
'''
def telegram_message(html_content): # import requests, urllib.parse
  chat_id = '131994588' # Lapa
  url = 'https://api.telegram.org/bot'
  url = url + koodit["L-bot"]
  url = url + '/sendMessage?chat_id='
  url = url + chat_id
  url = url + '&text='
  url = url + urllib.parse.quote(html_content)
  url = url + '&parse_mode=html'
  response = requests.get(url)
  return response

telegram_message('juu?')
'''
t = datetime.now()
collect_and_save()
#kotibobot.regression.do(['outside temp', 'olkkarin nuppi target', 'keittiön nuppi target'], 'olkkarin lämpömittari temp', [])
kotibobot.plotting.main_function()

#kotibobot.hs110.ufox_automation()
#kotibobot.hs110.makkari_humidifier_automation()
#kotibobot.hs110.tyokkari_humidifier_automation()

#kotibobot.thermostat_offset_controller.apply_control()
#kotibobot.command_queue.do()
restart_bluetooth()


print('jii')

#telegram_message('jii!')

