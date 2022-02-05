import numpy as np
#import scipy.stats
import random
import math

import kotibobot.eq3
import kotibobot.mi
import kotibobot.command_queue
import kotibobot.schedule
from house import *
from kotibobot.plotting import load_ts_data
from datetime import date, datetime

'''
def target_has_changed(eq3_name, really):
  data = load_ts_data()
  index = len(data.index)-1
  col1 = eq3_name + ' target'
  col2 = eq3_name + ' offset'
  res = []
  if not math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  else:
    while index > 0 and math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
      index = index - 1
    if really == "really":
      res.append(data.iloc[index][col1] + hard_offset)
    else:
      res.append(data.iloc[index][col1] + data.iloc[index][col2])
  
  index = index-1
  if not math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  else:
    while index > 0 and math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
      index = index - 1
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  
  return not (res[0] == res[1])
'''
def read_schedule(eq3):
  weekday = date.today().weekday()
  schedule = kotibobot.schedule.import1()
  print(kotibobot.schedule.everyday[weekday])
  return kotibobot.schedule.read(schedule[eq3][kotibobot.schedule.everyday[weekday]],datetime.now())

def latest_temp(room):
  data = load_ts_data()
  res = []
  
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
    
      col = mac_to_name[mi] + ' temp'
      index = len(data.index)-1
  
      while index >= 0 and math.isnan(data.iloc[index][col]):
        index = index - 1
      res.append(data.iloc[index][col])
  
  if len(res) == 0:
    return float('nan')
  else:
    return sum(res)/len(res) # evaluate mean value


def apply_control():
  for room in rooms:
    if "eq3" in rooms[room]:
      for eq3 in rooms[room]["eq3"]:
      
        print(mac_to_name[eq3] + ' käsittelyyn...')
        
        status = kotibobot.eq3.to_json(eq3)
        print(status)
        
        # if status is nan, we won't do anything, but integral decay
        if math.isnan(status['target']):
          kotibobot.eq3.store_attribute_database(eq3, status['integral']*0.95, 'integral')
          continue
        
        # if mode is not auto, we won't touch the temperatures
        if status['automode']==1 and status['vacationmode']==0 and status['boostmode']==0:
          target_temp = read_schedule(eq3)
        else:
          continue
        
        # recent mi data
        temp = latest_temp(room)
        print('Lämpötila: ' +str(temp) + ' C')
        
        # tuning parameters
        par_intercept = 0.22275 * 1.1 * 1.1
        par_integral = 5.625e-7 * 100 * 1.1 * 1.1 * 1.1 * 1.1
        
        # evaluate integral and store it
        integral = status['integral']*0.95 + kotibobot.command_queue.median_timedelta().total_seconds() * (- temp + target_temp)
        kotibobot.eq3.store_attribute_database(eq3, integral, 'integral')
        
        # if cold, wipe integral
        if target_temp < 16.5:
          kotibobot.eq3.store_attribute_database(eq3, 0.0, 'integral')
          print("It's cold")
        
        print('ind_interc:   ' + str((-temp + target_temp) * par_intercept))
        print('ind_integral: ' + str(integral* par_integral))
        indicator = (-temp + target_temp) * par_intercept
        indicator = indicator + integral*par_integral
        
        # we give the control bigger effect, if the data collecting cycle is longer
        indicator = indicator * kotibobot.command_queue.median_timedelta().total_seconds() / 500
        
        if abs(indicator) < 1e-13:
          continue
        else:
          delta = 0.5 * (random.random() < abs(indicator)) * indicator / abs(indicator)
        
        if (delta < 0 and status['valve']==0.0) or (delta > 0 and status['valve']>=95.0):
          delta = 0
        
        if (delta < 0 and status['valve']>=95.0) or (delta > 0 and status['valve']==0.0):
          delta = 2*delta
        
        print('delta: ' + str(delta))
        
        if abs(delta) < 0.01:
          continue
        
        new_target = status['target'] + delta
        
        print('new_target: ' + str(new_target))
        
        status = kotibobot.eq3.command(eq3 + ' temp ' + str(new_target))
