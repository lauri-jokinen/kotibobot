from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import time
import math
from os.path import exists

import kotibobot
from house import *
from common_functions import *

import kotibobot.electricity_price

def collect_and_save(time_delta = 0):
  
  new_df = kotibobot.electricity_price.get_forwards(time_delta)
  print(new_df)
  file_name = '/home/lowpaw/Downloads/kotibobot/el-price_' + datetime.today().strftime("%Y") + '.pkl'
  
  if exists(file_name):
    df = pd.read_pickle(file_name)
    df = pd.concat([df, new_df], sort=False, ignore_index=True)
  else:
    df = new_df
  
  df.replace([np.inf, -np.inf], np.nan, inplace=True) # replace +-inf with nan
  df = df[df['electricity price'].notna()] # remove nans
  df['time'] = df['time'].dt.floor('H')
  
  df = df.iloc[::-1]
  df = df.drop_duplicates(subset=['time'])
  df = df.iloc[::-1]
  
  df = df.sort_values(by=['time'])
  
  df.reset_index(drop=True, inplace=True)
  #print(df)
  df.to_pickle(file_name)

if datetime.now().hour <= 6:
  collect_and_save(24) # today
else:
  collect_and_save() # tomorrow

# cron:
# 0 * * * * DISPLAY=:0 /usr/bin/python3 /home/lowpaw/Downloads/kotibobot/collect_el_data.py
