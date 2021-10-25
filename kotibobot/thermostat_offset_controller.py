import numpy as np
import scipy.stats
import random
import math

import kotibobot.eq3
import kotibobot.mi
import kotibobot.command_queue
from house import *
from kotibobot.plotting import load_ts_data

def target_has_changed(eq3_name):
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
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  
  index = index-1
  if not math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  else:
    while index > 0 and math.isnan(data.iloc[index][col1] + data.iloc[index][col2]):
      index = index - 1
    res.append(data.iloc[index][col1] + data.iloc[index][col2])
  
  return not (res[0] == res[1])


def latest_temps(room):
  # three latest datapoints for each mi in the room
  data = load_ts_data()
  res = json.loads("{}")
  pts = 3
  
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

def apply_control():
  for room in rooms:
    if "eq3" in rooms[room]:
      for eq3 in rooms[room]["eq3"]:
      
        print(mac_to_name[eq3] + ' käsittelyyn...')
        print('target changed: ' + str(target_has_changed(mac_to_name[eq3])))
        
        status = kotibobot.eq3.to_json(eq3)
        print(status)
        
        # if status is nan, we won't do anything
        if math.isnan(status['target']):
          continue
        
        # if mode is not auto, we won't touch the temperatures
        if status['automode']==1:
          target_temp = status['target'] + status['offset']
        else:
          continue
        
        # if target has changed in recent data history, eq3 has reached the next scheduled temp
        # here we set the mode to auto, and store offset 0.0
        if target_has_changed(mac_to_name[eq3]):
          kotibobot.command_queue.append(room + ' auto')
          kotibobot.eq3.store_offset(eq3, 0.0)
          continue
        
        # evaluate regression of recent mi data
        regression = error_slope(room)
        print(regression)
        
        # tuning parameters
        par_slope = 1e4 * 0.16 * 0.8
        par_intercept = 0.5 * 0.6 * 0.8
        
        print('ind_interc: ' + str((-regression['intercept'] + target_temp) * par_intercept) + ' ind_slope: ' + str(-regression['slope'] * par_slope))
        indicator = -regression['slope'] * par_slope + (-regression['intercept'] + target_temp) * par_intercept
        
        # we give the control bigger effect, if the data collecting cycle is longer
        indicator = indicator * kotibobot.command_queue.median_timedelta().total_seconds() / 500
        
        if abs(indicator) < 1e-13:
          continue
        else:
          delta = 0.5 * (random.random() < abs(indicator)) * indicator / abs(indicator)
        
        print('delta: ' + str(delta))
        
        if delta == 0.0:
          continue
        
        new_offset = status['offset'] - delta
        new_offset = min(3, max(-4, new_offset))
        
        new_target = target_temp - new_offset
        
        print('new_offset: ' + str(new_offset) + ' new_target: ' + str(new_target))
        
        status = kotibobot.eq3.command(eq3 + ' temp ' + str(new_target))
        if "Connection failed" in status or "ERROR" in status:
          'do nothing!'
        else:
          kotibobot.eq3.store_offset(eq3, new_offset)
