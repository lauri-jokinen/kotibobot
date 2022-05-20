import numpy as np
import scipy.stats
import random
import math

import kotibobot.eq3
import kotibobot.mi
import kotibobot.command_queue
import kotibobot.schedule
from house import *
from kotibobot.plotting import load_ts_data, latest_data_json
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

def latest_temps(room):
  # three latest datapoints for each mi in the room
  data = load_ts_data()
  res = json.loads("{}")
  pts = 4
  
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
    
      col = mac_to_name[mi] + ' temp'
      res[mi + ' temp'] = []
      res[mi + ' time'] = []
      
      index = len(data.index)-1
  
      for i in range(pts):
        if not math.isnan(data.iloc[index][col]):
          res[mi + ' temp'].append(data.iloc[index][col])
          res[mi + ' time'].append(data.iloc[index]['time'])
        else:
          while index >= 0 and math.isnan(data.iloc[index][col]):
            index = index - 1
          res[mi + ' temp'].append(data.iloc[index][col])
          res[mi + ' time'].append(data.iloc[index]['time'])
        index = index-1
  
  return res

def error_slope(room):
  data = latest_temps(room)
  
  # result arrays are needed for multiple mis in a room
  slopes = []
  intercepts = []
  
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      
      if len(data[mi + ' time']) == 1:
        # if only one datapoint, slope is set to zero
        slopes.append(0.0)
        intercepts.append(data[mi + ' temp'][0])
      
      elif len(data[mi + ' time']) >= 2:
        # convert timestamps to timedeltas in seconds
        latest_timestamp = data[mi + ' time'][0]
        for i in range(len(data[mi + ' time'])):
          data[mi + ' time'][i] = (data[mi + ' time'][i] - latest_timestamp).total_seconds() # minutes
        
        # perform the regression and store the results
        regression = scipy.stats.siegelslopes(data[mi + ' temp'], data[mi + ' time'])
        slopes.append(regression[0])
        intercepts.append(regression[1])
  
  # if results are ok, take their median, mi-wise
  if len(slopes) == 0:
    return {'intercept': 0.0, 'slope' : 0.0}
  else:
    return {'intercept': np.nanmedian(np.array(intercepts)), 'slope' : np.nanmedian(np.array(slopes))}

def read_schedule(eq3):
  weekday = date.today().weekday()
  schedule = kotibobot.schedule.import1()
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
        
        target_temp = read_schedule(eq3)
        
        # if cold, wipe integral
        if target_temp < 16.5:
          kotibobot.eq3.store_attribute_database(eq3, 0.0, 'integral')
          #print("It's cold")
        
        #status = kotibobot.eq3.to_json(eq3)
        status = latest_data_json()
        status['target'] = status[mac_to_name[eq3] + ' target']
        status['valve'] = status[mac_to_name[eq3] + ' valve']
        status['vacationmode'] = status[mac_to_name[eq3] + ' vacationmode']
        status['boostmode'] = status[mac_to_name[eq3] + ' boostmode']
        status['automode'] = status[mac_to_name[eq3] + ' automode']
        status['integral'] = kotibobot.eq3.read_attribute_database(eq3, 'integral')
        #print(status)
        
        # if status is nan, we won't do anything, but integral decay
        if math.isnan(status['target']):
          #if math.isnan(data[mac_to_name[eq3] + ' target']):
          kotibobot.eq3.store_attribute_database(eq3, status['integral']*0.95, 'integral')
          continue
        
        # if mode is not auto, we won't touch the temperatures
        if not (status['automode']==1 and status['vacationmode']==0 and status['boostmode']==0):
          continue
        
        # recent mi data
        temp = latest_temp(room)
        #print('Lämpötila: ' +str(temp) + ' C')
        
        # evaluate regression of recent mi data
        regression = error_slope(room)
        #print(regression)
        
        # tuning parameters
        par_intercept = 0.245 * 0.9
        par_integral = 7.49e-05 * 0.9
        par_slope = 990 * 0.9
        
        # evaluate integral and store it
        integral = status['integral']*0.9 + kotibobot.command_queue.median_timedelta().total_seconds() * (- temp + target_temp)
        kotibobot.eq3.store_attribute_database(eq3, integral, 'integral')
        
        print('ind_interc:   ' + str((-temp + target_temp) * par_intercept))
        print('ind_integral: ' + str(integral* par_integral))
        print('ind_der:      ' + str(-regression['slope'] * par_slope))
        indicator = (-temp + target_temp) * par_intercept
        indicator = indicator + integral*par_integral
        indicator = indicator - max(min(regression['slope'] * par_slope, 0.3), -0.3)
        
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
        
        #print('delta: ' + str(delta))
        
        if abs(delta) < 0.01:
          continue
        
        new_target = status['target'] + delta
        
        #print('new_target: ' + str(new_target))
        
        status = kotibobot.eq3.command(eq3 + ' temp ' + str(new_target))
