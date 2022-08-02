import subprocess # ubuntu bash
from datetime import datetime

#from kotibobot.plotting import load_ts_data, latest_data_json
#from house import *
#import kotibobot.electricity_price
#import kotibobot.schedule

def read_schedule(eq3):
  weekday = date.today().weekday()
  schedule = kotibobot.schedule.import1()
  return kotibobot.schedule.read(schedule[eq3][kotibobot.schedule.everyday[weekday]],datetime.now())

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

def tyokkari_humidifier_command(string):
  return plug_command(string, 'työkkärin_kostutin')
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

'''
# HUMIDIFIER CODE
def ufox_automation():
  data = latest_data_json()
  humidity = data['olkkarin lämpömittari humidity']
  
  if humidity >= 48.0:
    #print('Humidity is high')
    return ufox_command('off')
  
  if kotibobot.electricity_price.precentile_interval(9,21) >= 0.85 and humidity >= 42.0:
    #print('Electricity is costly')
    return ufox_command('off')
  
  if datetime.now().hour >= 22 or datetime.now().hour < 9:
    #print("It's night time")
    return ufox_command('off')
    
  if (data['olkkarin nuppi vacationmode'] == 1 or data['keittiön nuppi vacationmode'] == 1) and (data['olkkarin nuppi target'] <= 16.0 or data['keittiön nuppi target'] <= 16.0):
    print("It's cold time")
    return ufox_command('off')
  
  print("Ufox on")
  return ufox_command('on')


def makkari_humidifier_automation():
  data = latest_data_json()
  humidity = data['makkarin lämpömittari humidity']
  temp = data['makkarin lämpömittari temp']
  
  if (datetime.now().hour >= 23 or datetime.now().hour < 1) and humidity >= 43.0:
    #print("It's the middle of the night")
    return makkari_humidifier_command('off')
  
  if humidity >= 50.0:
    #print('Humidity is high in makkari')
    return makkari_humidifier_command('off')
  
  #if not (datetime.now().hour >= 20 or datetime.now().hour < 10):
  #  #print("It's day time")
  #  return makkari_humidifier_command('off')
  
  if (data['makkarin nuppi vacationmode'] == 1) and (data['makkarin nuppi target'] <= 16.0):
    print("It's cold time")
    return makkari_humidifier_command('off')
  
  #print("Makkari humidifier on")
  return makkari_humidifier_command('on')
  
def tyokkari_humidifier_automation():
  data = latest_data_json()
  humidity = data['työkkärin lämpömittari humidity']
  #print('Humidity: ' + str(humidity))
  
  if datetime.now().hour >= 22 or datetime.now().hour < 9:
    #print("It's night time")
    return tyokkari_humidifier_command('off')
  
  if humidity >= 50.0:
    #print('Humidity is high')
    return tyokkari_humidifier_command('off')
    
  if (data['työkkärin nuppi vacationmode'] == 1) and (data['työkkärin nuppi target'] <= 16.0):
    print("It's cold time")
    return tyokkari_humidifier_command('off')
  
  #print("Makkari humidifier on")
  return tyokkari_humidifier_command('on')
'''
