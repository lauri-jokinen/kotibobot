import kotibobot.hs110, kotibobot.electricity_price
import pandas as pd
from os.path import exists
from datetime import date, datetime, timedelta

import requests, urllib.parse, json, math, time # telegram
import random
from kotibobot.requests_robust import telegram_message

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)
    
time.sleep(2)

file_name = '/home/lowpaw/Downloads/kotibobot/demand_response.pkl'

if exists(file_name):
  df = pd.read_pickle(file_name)
else:
  df = pd.DataFrame()
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)

#telegram_message(str(kotibobot.electricity_price.frequency(True)))

minutes_on = 9;

# If too much time has passed, turn it on!
# Also, the fridge is on with some probability
if random.random() < 0.6 or (df['last_time_on'].iloc[-1] + timedelta(minutes = minutes_on + 2.5) < datetime.now()):
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  freq = kotibobot.electricity_price.frequency()
  #telegram_message('liikaa aikaa pois {}'.format(freq))
  exit()

try:
  freq = kotibobot.electricity_price.frequency()
  if math.isnan(freq):
    raise ValueError('Frequency is NaN.')
except:
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  telegram_message('jotain meni vikaan demand responsessa')
  exit()

#print(freq)
#print(kotibobot.hs110.ufox_is_on())

if freq < 40.0 or freq > 60.0:
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  telegram_message('taajuus heittää häränpyllyä: {}'.format(freq))
  exit()

if freq < 50-0.013:
  # low freq? turn it off
  kotibobot.hs110.ufox_command('off')
  kotibobot.hs110.ufox_command('off')
  #telegram_message('decreasing demand!')
elif freq > 50:
  # high freq? turn it on!
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  #telegram_message('adding demand!')
elif kotibobot.hs110.ufox_is_on():
  # between 49 and 50? leave as is
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  #telegram_message('normi päälle')
else:
  kotibobot.hs110.ufox_command('off')
  kotibobot.hs110.ufox_command('off')
  #telegram_message('normi pois, taajuus {}'.format(freq))
