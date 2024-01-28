import subprocess # ubuntu bash
from datetime import datetime, timedelta

from kotibobot.plotting import load_ts_data, latest_data_json, outside_hum_to_inside_hum
#from house import *
import kotibobot.electricity_price, kotibobot.thermostat_offset_controller, json

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)
'''
#import kotibobot.schedule

def read_schedule(eq3):
  weekday = date.today().weekday()
  schedule = kotibobot.schedule.import1()
  return kotibobot.schedule.read(schedule[eq3][kotibobot.schedule.everyday[weekday]],datetime.now())
'''
def plug_command(string, name):
  s = ['/home/lowpaw/Downloads/HS110/'+ name +'.py', '-c'] + string.split(' ')
  try:
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 15)
  except:
    return "Task failed."
  return res.stdout.decode('utf-8')


def ufox_command(string):
  return plug_command(string, 'ufox') # jääkaappi

def makkari_humidifier_command(string):
  return plug_command(string, 'makkarin_kostutin') # makkarin kostutuin

def tyokkari_humidifier_command(string):
  return plug_command(string, 'työkkärin_kostutin') # olkkarin kostutin, ufox
'''
def ufox_is_on():
  try:
    res = float(plug_command('energy', 'ufox').split('power_mw":')[1].split(',')[0])
    return (res > 1*1000) # milli Watts
  except:
    return True # weird precaution. do something about this
'''

def ufox_is_on():
  try:
    res = int(plug_command('energy', 'ufox').split('relay_state":')[1].split(',')[0]) == 1
  except:
    res = True
  return res


def ufox_power():
  try:
    res = float(plug_command('energy', 'ufox').split('power_mw":')[1].split(',')[0])
    return res/1000 # conversion from mW to W
  except:
    return float('nan')

def FTP_is_on():
  try:
    res = int(plug_command('info', 'työkkärin_kostutin').split('relay_state":')[1].split(',')[0]) == 1
  except:
    res = False
  return res

'''
# HUMIDIFIER CODE

def makkari_humidifier_automation():
  (data, data_times) = latest_data_json(True)
  humidity = data['makkarin lämpömittari humidity']
  temp = data['makkarin lämpömittari temp']
  target_temp = kotibobot.thermostat_offset_controller.read_schedule(koodit["makkarin nuppi"])
  # relative humidity at target temperature
  if temp > target_temp:
    humidity = outside_hum_to_inside_hum(target_temp, temp, humidity)
  humidity_timestamp = data_times['makkarin lämpömittari humidity']
  
  if humidity > 52.0 or humidity_timestamp < datetime.now() - timedelta(minutes=20):
    #print('Humidity is high in makkari')
    return makkari_humidifier_command('off')
    
  if target_temp > 21.0 and humidity > 47.0: # morning heat
    return makkari_humidifier_command('off')
  
  if not (datetime.now().hour >= 22 or datetime.now().hour < 8):
    #print("It's day time")
    return makkari_humidifier_command('off')
  
  if (data['makkarin nuppi vacationmode'] == 1) and (data['makkarin nuppi target'] <= 19.0):
    print("It's cold time")
    return makkari_humidifier_command('off')
  
  if target_temp <= 19.0:
    #print("It's scheduled cold time")
    return makkari_humidifier_command('off')
  
  #print("Makkari humidifier on")
  return makkari_humidifier_command('on')

def tyokkari_humidifier_automation():
  (data, data_times) = latest_data_json(True)
  humidity = data['työkkärin lämpömittari humidity']
  temp = data['työkkärin lämpömittari temp']
  target_temp = kotibobot.thermostat_offset_controller.read_schedule(koodit["työkkärin nuppi"])
  # relative humidity at target temperature
  if temp > target_temp:
    humidity = outside_hum_to_inside_hum(target_temp, temp, humidity)
  humidity_timestamp = data_times['työkkärin lämpömittari humidity']
  
  if datetime.now().hour >= 22 or datetime.now().hour < 7:
    #print("It's night time")
    return tyokkari_humidifier_command('off')
  
  if humidity > 48.0 or humidity_timestamp < datetime.now() - timedelta(minutes=20):
    #print('Humidity is high')
    return tyokkari_humidifier_command('off')
    
  if (data['työkkärin nuppi vacationmode'] == 1) and (data['työkkärin nuppi target'] <= 19.0):
    #print("It's cold vacation")
    return tyokkari_humidifier_command('off')
  
  if target_temp <= 20.0:
    #print("It's scheduled cold time")
    return tyokkari_humidifier_command('off')
  
  #print("On!")
  return tyokkari_humidifier_command('on')
'''
