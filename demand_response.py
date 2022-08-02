import kotibobot
import pandas as pd
from os.path import exists
from datetime import date, datetime, timedelta

import requests, urllib.parse, json, math, time # telegram

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

def frequency():
    TOKEN = koodit["fingrid"] # lateus96
    # TOKEN = koodit["fingrid2"] lauri.a.jokinen
    five_minutes = timedelta(minutes=80)
    now = datetime.now() + five_minutes
    before = datetime.now() - five_minutes
    start = before.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') + '%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    end = now.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') +'%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    url2 = 'https://api.fingrid.fi/v1/variable/177/events/json?start_time=' + start + '&end_time=' + end
    return requests.get(url2, headers={'x-api-key': TOKEN, 'Accept': 'application/json'}).json()[-1]

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

#telegram_message(str(frequency()))

minutes_on = 9;

# If too much time has passed, turn it on!
if df['last_time_on'].iloc[-1] + timedelta(minutes = minutes_on + 2.5) < datetime.now():
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  freq = kotibobot.electricity_price.frequency()
  telegram_message('liikaa aikaa pois {}'.format(freq))
  exit()

try:
  freq = kotibobot.electricity_price.frequency()
  freq >= 50.0
except:
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  telegram_message('jotain meni vikaan')

#print(freq)
#print(kotibobot.hs110.ufox_is_on())

if freq < 40.0 or freq > 60.0:
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  telegram_message('taajuus heittää häränpyllyä: {}'.format(freq))
  exit()

if freq < 50-1.25*3.28e-2: # 2.5 sigma = 2% of time, 49.9344
  # low freq? turn it off
  kotibobot.hs110.ufox_command('off')
  kotibobot.hs110.ufox_command('off')
  #telegram_message('decreasing demand!')
elif freq > 50+1.25*3.28e-2:
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

