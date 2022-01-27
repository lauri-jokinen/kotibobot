import subprocess # ubuntu bash
from datetime import datetime

from kotibobot.plotting import load_ts_data, latest_data_json
from house import *
import kotibobot.electricity_price

def plug_command(string, name):
  s = ['/home/lowpaw/Downloads/HS110/'+ name +'.py', '-c'] + string.split(' ')
  try:
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 15)
  except:
    return "Task failed."
  return res.stdout.decode('utf-8')


def ufox_command(string):
  return plug_command(string, 'ufox')

def makkari_humidifier_command(string):
  return plug_command(string, 'makkarin_kostutin')


def ufox_automation():
  data = latest_data_json()
  humidity = max([data['työkkärin lämpömittari humidity'], data['olkkarin lämpömittari humidity']])
  
  if humidity >= 44.0:
    print('Humidity is high')
    return ufox_command('off')
  
  if kotibobot.electricity_price.precentile_for_hours(kotibobot.electricity_price.get(), 9, 21) >= 0.90:
    print('Electricity is costly')
    return ufox_command('off')
  
  if datetime.now().hour >= 21 or datetime.now().hour < 9:
    print("It's night time")
    return ufox_command('off')
  
  print("Ufox on")
  return ufox_command('on')


def makkari_humidifier_automation():
  data = latest_data_json()
  humidity = data['makkarin lämpömittari humidity']
  
  if humidity >= 43.0:
    print('Humidity is high in makkari')
    return makkari_humidifier_command('off')
  
  if datetime.now().hour >= 9 or datetime.now().hour < 21:
    print("It's day time")
    return makkari_humidifier_command('off')
  
  print("Makkari humidifier on")
  return makkari_humidifier_command('on')
