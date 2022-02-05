from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import time
import math

import kotibobot
from house import *
from common_functions import *

import kotibobot.electricity_price

def collect_and_save():
  new_data = json.loads("{}")
  
  new_data['time'] = pd.Timestamp.now().floor(freq='H') # rounded to hour
  file_name = '/home/lowpaw/Downloads/kotibobot/el-price_' + datetime.today().strftime("%Y") + '.pkl'
  
  price = kotibobot.electricity_price.get()
  
  if math.isnan(price) or (price == kotibobot.electricity_price.latest()):
    time.sleep(12.13)
    price = kotibobot.electricity_price.get()
  
  if math.isnan(price):
    return
  
  new_data["electricity price"] = price
  
  new_df = pd.json_normalize(new_data)
  
  new_file = False
  
  try:
    df = pd.read_pickle(file_name)
    df = df.append(new_df, sort=False, ignore_index=True)
  except:
    df = new_df
    new_file = True
  
  df = df[df['electricity price'].notna()]
  df['time'] = df['time'].dt.floor('H')
  df = df.drop_duplicates(subset=['time'])
  
  df.reset_index(drop=True, inplace=True)
  #print(df)
  
  df.to_pickle(file_name)

# run function
time.sleep(5.32)
collect_and_save()

# cron:
# 0 * * * * DISPLAY=:0 /usr/bin/python3 /home/lowpaw/Downloads/kotibobot/collect_el_data.py
