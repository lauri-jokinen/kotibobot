import kotibobot.hs110, kotibobot.electricity_price, kotibobot.plotting, kotibobot.thermostat_offset_controller, kotibobot.command_queue
import pandas as pd
from os.path import exists
from datetime import date, datetime, timedelta

import requests, urllib.parse, json, math, time # telegram
import random
from kotibobot.requests_robust import telegram_message


with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

time.sleep(2)

try:
  freq = kotibobot.electricity_price.frequency()
  if math.isnan(freq):
    raise ValueError('Frequency is NaN.')
except:
  #kotibobot.hs110.ufox_command('on') # for fridge
  #kotibobot.hs110.ufox_command('on')
  #df['last_time_on'] = [datetime.now()]
  #df.to_pickle(file_name)
  freq = 50.0
  #telegram_message('jotain meni vikaan demand responsessa')
  #exit()

freq_limit = 49.999
(data, data_times) = kotibobot.plotting.latest_data_json(True)


def olkkari_humidifier_automation(data, data_times, target_humidity, freq, freq_limit):
  Q = kotibobot.command_queue.read()
  for q in Q:
    if "olkkari vacation" in q and float(q[-3:]) <= 20:
      print('olkkari Q vacation')
      return kotibobot.hs110.ufox_command('off')
  humidity = data['olkkarin lämpömittari humidity']
  temp = data['olkkarin lämpömittari temp']
  target_temp = kotibobot.thermostat_offset_controller.read_schedule(koodit["olkkarin nuppi"])
  # relative humidity at target temperature
  #if temp > target_temp:
  humidity = kotibobot.plotting.outside_hum_to_inside_hum(target_temp, temp, humidity)
  humidity_timestamp = data_times['olkkarin lämpömittari humidity']

  if humidity > target_humidity or humidity_timestamp < datetime.now() - timedelta(minutes=20):
    #print('Humidity is high')
    return kotibobot.hs110.ufox_command('off')

  if datetime.now().hour >= 23 or datetime.now().hour < 7:
    #print("It's night time")
    return kotibobot.hs110.ufox_command('off')

  if target_temp <= 20.0:
    #print("It's scheduled cold time")
    return kotibobot.hs110.ufox_command('off')
    
  if (data['olkkarin nuppi vacationmode'] == 1 or data['keittiön nuppi vacationmode'] == 1) and (data['olkkarin nuppi target'] < 20.0 or data['keittiön nuppi target'] < 20.0):
    #print("It's cold vacation")
    return kotibobot.hs110.ufox_command('off')

  if freq <= freq_limit and humidity > target_humidity-2:
    return kotibobot.hs110.ufox_command('off')

  #print("Olkkari humidifier on")
  return kotibobot.hs110.ufox_command('on')



def makkari_humidifier_automation(data, data_times, target_humidity, freq, freq_limit):
  humidity = data['makkarin lämpömittari humidity']
  temp = data['makkarin lämpömittari temp']
  target_temp = kotibobot.thermostat_offset_controller.read_schedule(koodit["makkarin nuppi"])
  # relative humidity at target temperature
  #if temp > target_temp:
  humidity = kotibobot.plotting.outside_hum_to_inside_hum(target_temp, temp, humidity)
  humidity_timestamp = data_times['makkarin lämpömittari humidity']
  
  if humidity > target_humidity or humidity_timestamp < datetime.now() - timedelta(minutes=20):
    #print('Humidity is high in makkari')
    return kotibobot.hs110.makkari_humidifier_command('off')
    
  if target_temp > 21.0 and humidity > target_humidity - 2: # morning heat
    return kotibobot.hs110.makkari_humidifier_command('off')
  
  if not (datetime.now().hour >= 22 or datetime.now().hour < 8):
    #print("It's day time")
    return kotibobot.hs110.makkari_humidifier_command('off')
  
  if (data['makkarin nuppi vacationmode'] == 1) and (data['makkarin nuppi target'] <= 20.0):
    print("It's cold time")
    return kotibobot.hs110.makkari_humidifier_command('off')
  
  if target_temp <= 19.0:
    #print("It's scheduled cold time")
    return kotibobot.hs110.makkari_humidifier_command('off')
    
  if freq <= freq_limit and humidity > target_humidity-2:
    return kotibobot.hs110.makkari_humidifier_command('off')
  
  #print("Makkari humidifier on")
  return kotibobot.hs110.makkari_humidifier_command('on')



def tyokkari_humidifier_automation(data, data_times, target_humidity, freq, freq_limit):
  Q = kotibobot.command_queue.read()
  for q in Q:
    if "työkkäri vacation" in q and float(q[-3:]) <= 20:
      return kotibobot.hs110.tyokkari_humidifier_command('off')
  humidity = data['työkkärin lämpömittari humidity']
  temp = data['työkkärin lämpömittari temp']
  target_temp = kotibobot.thermostat_offset_controller.read_schedule(koodit["työkkärin nuppi"])
  # relative humidity at target temperature
  #if temp > target_temp:
  humidity = kotibobot.plotting.outside_hum_to_inside_hum(target_temp, temp, humidity)
  humidity_timestamp = data_times['työkkärin lämpömittari humidity']
  
  if datetime.now().hour >= 22 or datetime.now().hour < 7:
    #print("It's night time")
    return kotibobot.hs110.tyokkari_humidifier_command('off')
  
  if humidity > target_humidity or humidity_timestamp < datetime.now() - timedelta(minutes=20):
    #print('Humidity is high')
    return kotibobot.hs110.tyokkari_humidifier_command('off')
    
  if (data['työkkärin nuppi vacationmode'] == 1) and (data['työkkärin nuppi target'] <= 20.0):
    #print("It's cold vacation")
    return kotibobot.hs110.tyokkari_humidifier_command('off')
  
  if target_temp <= 20.0:
    #print("It's scheduled cold time")
    return kotibobot.hs110.tyokkari_humidifier_command('off')
    
  if freq <= freq_limit and humidity > target_humidity-2:
    return kotibobot.hs110.tyokkari_humidifier_command('off')
  
  #print("On!")
  return kotibobot.hs110.tyokkari_humidifier_command('on')



makkari_humidifier_automation (data, data_times, 48, freq, freq_limit)
olkkari_humidifier_automation (data, data_times, 42, freq, freq_limit)
#tyokkari_humidifier_automation(data, data_times, 45, freq, freq_limit)

print('jii')

'''

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

kotibobot.hs110.ufox_automation(freq)

minutes_on = 9;

# If too much time has passed, turn it on!
# Also, the fridge is on with some probability
if random.random() > 0.3 or (df['last_time_on'].iloc[-1] + timedelta(minutes = minutes_on + 2.5) < datetime.now()):
  kotibobot.hs110.ufox_command('on')
  kotibobot.hs110.ufox_command('on')
  df['last_time_on'] = [datetime.now()]
  df.to_pickle(file_name)
  freq = kotibobot.electricity_price.frequency()
  #telegram_message('liikaa aikaa pois {}'.format(freq))
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

if freq < 50-0.0184:
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
  

#telegram_message('jii')
'''


'''
### DEMAND RESPONSE OPTIMOINTI
### EHKEI KÄYTTISTÄ
import requests, math, time
from datetime import datetime, timedelta
import pandas as pd
#import matplotlib.pyplot as plt
import numpy as np
token = "5UZ5AmOLC27BpjSVmKgnc2ROwKfLmWwy4k2f69su"

def frequency(full_response = False):
    #try:
    TOKEN = "5UZ5AmOLC27BpjSVmKgnc2ROwKfLmWwy4k2f69su" # lateus96
    # TOKEN = koodit["fingrid2"] lauri.a.jokinen
    five_minutes = timedelta(hours=24*14)
    now = datetime.now() + five_minutes
    before = datetime.now() - five_minutes
    start = before.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') + '%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    end = now.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') +'%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    url2 = 'https://api.fingrid.fi/v1/variable/177/events/json?start_time=' + start + '&end_time=' + end
    #resp = kotibobot.requests_robust.get_url(url2, {'x-api-key': TOKEN, 'Accept': 'application/json'})
    head = {'x-api-key': TOKEN, 'Accept': 'application/json'}
    resp = requests.get(url2, headers = head)
    if full_response:
      return resp.json()
    else:
      return resp.json()[-1]['value']
    #except:
    #return float('nan')

data = pd.DataFrame(frequency(True))

# Halutaan, että kunkin tunnin intervallin aikana,
#    Ufox on päällä vähintään 20 % ajasta. 
# Etsitään historiasta intervalli, jolla on pienin prosentti,
#    ja tuunataan rajaa, s.e., pienin prosentti olisi lähellä 20:tä.

# values sisältää kunkin intervallin %:n, s.e. taajuus on suurempi kuin esim. 49.9
values = np.zeros(np.sum(data['value'] > 0.0) - 21)

for ind in range(np.sum(data['value'] > 0.0) - 21):
    values[ind] = np.sum((data['value'])[ind:(ind+20)] > 49.955) / 20

#plt.plot(values)
print(min(values))
'''
