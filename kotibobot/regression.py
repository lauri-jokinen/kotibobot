import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import HuberRegressor, LinearRegression
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
#import seaborn as sns
#import sklearn.model_selection
import math

# comment for debugging!!!
pd.options.mode.chained_assignment = None  # default='warn'

from kotibobot.plotting import load_ts_data
'''
def load_ts_data():
  last_month = datetime.now() - timedelta(hours = 24*32)
  last_month_file_name = '/home/lowpaw/Downloads/kotibobot/' + last_month.strftime("%Y-%m") + '.pkl'
  last_month = pd.read_pickle(last_month_file_name)
  
  file_name = '/home/lowpaw/Downloads/kotibobot/' + datetime.today().strftime("%Y-%m") + '.pkl'
  
  try:
    df = pd.read_pickle(file_name)
  except:
    return last_month
  
  df = last_month.append(df, sort=False, ignore_index=True)
  return df
'''

def rounded_ten(t):
    ''' add 5 minutes to the date first and then apply mathematical floor to the minute part.
    It's easier to apply mathematical floor operation on date parts instead of rounding because for example you cannot round up 58 seconds to 60 seconds but you can always apply floor and stay within the range.
    '''
    #t=t+pd.Timedelta('5 minutes') 
    return t.replace(minute=t.minute//10*10).replace(second=0,microsecond=0)

def do(x_names, y_name, binary_attributes): # x_names is an array; y_name is str
  # x_names: ['outside temp', 'olkkarin nuppi valve']
  # y_names: 'olkkarin lämpömittari temp' (is also included in x)
  
  # Load data and discard useless information
  df = load_ts_data()
  df = df[x_names + [y_name, 'time']]
  df[x_names] = df[x_names].interpolate(axis=0)
  df[y_name] = df[y_name].interpolate(axis=0)
  
  
  # Moving average and difference
  #df[y_name] = df[y_name].rolling(window=3).mean()
  df['YDIFF'] = df[y_name].diff().shift(1)
  df['YOFFSET1'] = df['YDIFF'].shift(1)
  df['YOFFSET2'] = df['YDIFF'].shift(2)
  df['YOFFSET3'] = df['YDIFF'].shift(3)
  offset_names = ['YOFFSET1','YOFFSET2','YOFFSET3']
  
  for name in x_names:
    offset_names.append(name + ' OFFSET1')
    df[name + ' OFFSET1'] = df[name].shift(1)
    
  for name in x_names:
    offset_names.append(name + ' OFFSET2')
    df[name + ' OFFSET2'] = df[name].shift(2)
  
  # Remove infeasible values
  df = df.dropna()
  for b in binary_attributes:
    df = df[df[b] != -1]
  
  # Regression time period
  days = 7+1
  forecasted_days = 1
  t_start = datetime.now() - timedelta(hours = days*24) # 22*24
  t_end = datetime.now() - timedelta(hours = forecasted_days*24) # 24
  
  train = df
  train = train[train['time'] >= t_start]
  train = train[train['time'] < t_end]
  
  # seasonal effects
  means = np.zeros(6*24)
  
  # Loop tens of minutes
  for p in range(6*24):
    
    # Initialize for values
    values = np.zeros(days+2)*float('nan')
    
    # Loop days backwards
    for d in range(days+2):
      
      time = rounded_ten(pd.Timestamp.now() - timedelta(minutes = 10*p, hours=24*(d-1))) # round to minutes
      #print(time)
      diff_value = train[train['time'] == time]['YDIFF'].values
      #print(diff_value)
      # If time stamp exists, assing value to 'values'
      if len(diff_value) == 1:
        values[d] = diff_value[0]
      
    # Append the mean of the values to 'means'
    #print(values)
    means[p] = np.nanmean(values)
    
  #print(means)
  
  #print(train['YDIFF']*1000)
  
  # Store original data
  train_noseasonal = train.copy()
  
  # Remove seasonal effects from data
  for p in range(6*24):
    for d in range(days+2):
      time = rounded_ten(pd.Timestamp.now() - timedelta(hours=24*forecasted_days) + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = train[train['time'] == time]['YDIFF'].values
      if len(diff_value) == 1 and (not math.isnan(means[p])):
        index = train[train['time'] == time]['YDIFF'].index[0]
        train.at[index, 'YDIFF'] = diff_value[0] - means[p]
  
  #print(train['YDIFF']*1000)
  # The "training data" and regression
  x = train[x_names + [y_name] + offset_names]
  y = train['YDIFF']
  
  #mlr = HuberRegressor()
  mlr = LinearRegression()
  mlr.fit(x, y)
  #print(mlr.coef_)
  #print(mlr.intercept_)
  
  
  
  # No-seasonal fitting
  x = train_noseasonal[x_names + [y_name] + offset_names]
  y = train_noseasonal['YDIFF']
  mlr_noseasonal = LinearRegression()
  mlr_noseasonal.fit(x, y)
  print('Kontrollin vakio')
  print(mlr_noseasonal.coef_[1])
  
  train['YDIFF_RESIDUAL'] = y - mlr_noseasonal.predict(x)
  
  # Post-seasonal mean vector
  means_post = np.zeros(6*24)
  
  # Loop tens of minutes
  for p in range(6*24):
    
    # Initialize for values
    values = np.zeros(days+2)*float('nan')
    
    # Loop days backwards
    for d in range(days+2):
      
      time = rounded_ten(pd.Timestamp.now() - timedelta(minutes = 10*p, hours=24*(d-1))) # round to minutes
      #print(time)
      diff_value = train[train['time'] == time]['YDIFF_RESIDUAL'].values
      #print(diff_value)
      # If time stamp exists, assing value to 'values'
      if len(diff_value) == 1:
        values[d] = diff_value[0]
      
    # Append the mean of the values to 'means'
    #print(values)
    means_post[p] = np.nanmean(values)
  # Seasonal fixing, daily per hour
  #train['clock'] = train['time'].dt.hour + train['time'].dt.minute / 60
  #means = []
  #for i in range(24):
  #  train_sub = train[train['clock'] < i+1]
  #  train_sub = train_sub[i <= train_sub['clock']]
  #  means.append(train_sub['YDIFF_RESIDUAL'].mean())
  #  if math.isnan(means[-1]):
  #    means[-1] = 0.0
  
  
  
  
  #train['YDIFF_HOUR_FIXED'] = train['YDIFF'] - np.array(means)[train['time'].dt.hour]
  
  # Forecast compared with real data
  pred = df
  pred = pred[pred['time'] >= t_end]
  pred_t = pred['time']
  x_pred = pred[x_names + [y_name] + offset_names]
  
  pred['REAL'] = pred['YDIFF'].cumsum()
  
  pred['FORECAST'] = mlr.predict(x_pred)
  pred['FORECAST NO SEASONAL'] = mlr_noseasonal.predict(x_pred)
  #print(x_pred)
  pred['FORECAST POST SEASONAL'] = pred['FORECAST NO SEASONAL'] + 0.0 #.copy()
  #x_pred[x_names[1]] = x_pred[x_names[1]]*0.0 + 30.0
  #pred['FORECAST PS MAX'] = mlr_noseasonal.predict(x_pred)
  #x_pred[x_names[1]] = x_pred[x_names[1]]*0.0 + 5.0
  #print(x_pred)
  #pred['FORECAST PS MIN'] = mlr_noseasonal.predict(x_pred)
  
  
  # do real things pre-seasonal
  pred['TRUE FORECAST PRE SEASONAL'] = pred['FORECAST POST SEASONAL'].copy()
  index_last = -1
  for p in range(6*24):
    for d in range(3):
      time = rounded_ten(pd.Timestamp.now() + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = pred[pred['time'] == time]['FORECAST'].values
      if len(diff_value) == 1 and (not math.isnan(means[p])):
        index = pred[pred['time'] == time]['FORECAST'].index[0]
        if index_last != -1:
          x_pred.at[index, y_name] = pred.at[index_last, 'TRUE FORECAST PRE SEASONAL'] + x_pred[y_name].iloc[0]
          #x_pred.at[index, 'työkkärin nuppi target'] = 5.0 # simulate different scenarios
        #print(x_pred.loc[index])
        pred.at[index, 'TRUE FORECAST PRE SEASONAL'] = mlr.predict(x_pred.loc[index].array.reshape(1, -1))
        index_last = index
  
  
  # do real things
  pred['TRUE FORECAST'] = pred['FORECAST POST SEASONAL']
  index_last = -1
  for p in range(6*24):
    for d in range(3):
      time = rounded_ten(pd.Timestamp.now() + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = pred[pred['time'] == time]['FORECAST'].values
      if len(diff_value) == 1 and (not math.isnan(means[p])):
        index = pred[pred['time'] == time]['FORECAST'].index[0]
        if index_last != -1:
          x_pred.at[index, y_name] = pred.at[index_last, 'TRUE FORECAST'] + x_pred[y_name].iloc[0]
          #x_pred.at[index, 'työkkärin nuppi target'] = 5.0 # simulate different scenarios
        #print(x_pred.loc[index])
        pred.at[index, 'TRUE FORECAST'] = mlr_noseasonal.predict(x_pred.loc[index].array.reshape(1, -1))
        index_last = index
        
  # do real things min
  pred['TRUE FORECAST MIN'] = pred['FORECAST POST SEASONAL']
  pred['TRUE FORECAST MAX'] = pred['FORECAST POST SEASONAL']
  index_last = -1
  x_pred = pred[x_names + [y_name] + offset_names]
  x_predm = x_pred.copy()
  x_predM = x_pred.copy()
  for p in range(6*24):
    for d in range(3):
      time = rounded_ten(pd.Timestamp.now() + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = pred[pred['time'] == time]['FORECAST'].values
      if len(diff_value) == 1 and (not math.isnan(means[p])):
        index = pred[pred['time'] == time]['FORECAST'].index[0]
        if index_last != -1:
          x_predm.at[index, y_name] = pred.at[index_last, 'TRUE FORECAST MIN'] + x_predm[y_name].iloc[0]
          x_predM.at[index, y_name] = pred.at[index_last, 'TRUE FORECAST MAX'] + x_predM[y_name].iloc[0]
          x_predm.at[index, 'työkkärin nuppi target'] = 18.0 # simulate different scenarios
          x_predM.at[index, 'työkkärin nuppi target'] = 22.0 # simulate different scenarios
        #print(x_pred.loc[index])
        pred.at[index, 'TRUE FORECAST MIN'] = mlr_noseasonal.predict(x_predm.loc[index].array.reshape(1, -1))
        pred.at[index, 'TRUE FORECAST MAX'] = mlr_noseasonal.predict(x_predM.loc[index].array.reshape(1, -1))
        index_last = index
        
  
        
  # Add post-seasonal effects from data
  for p in range(6*24):
    for d in range(3):
      time = rounded_ten(pd.Timestamp.now() + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = pred[pred['time'] == time]['FORECAST POST SEASONAL'].values
      if len(diff_value) == 1 and (not math.isnan(means_post[p])):
        index = pred[pred['time'] == time]['FORECAST POST SEASONAL'].index[0]
        pred.at[index, 'FORECAST POST SEASONAL'] = diff_value[0] + means_post[p]
        #pred.at[index, 'FORECAST PS MAX'] = pred[pred['time'] == time]['FORECAST PS MAX'].values[0] + means_post[p]
        #pred.at[index, 'FORECAST PS MIN'] = pred[pred['time'] == time]['FORECAST PS MIN'].values[0] + means_post[p]
  
  
  # Add seasonal effects from data
  for p in range(6*24):
    for d in range(3):
      time = rounded_ten(pd.Timestamp.now() + timedelta(minutes = 10*p, hours=-24*(d-1))) # round to minutes
      diff_value = pred[pred['time'] == time]['FORECAST'].values
      if len(diff_value) == 1 and (not math.isnan(means[p])):
        index = pred[pred['time'] == time]['FORECAST'].index[0]
        pred.at[index, 'FORECAST'] = diff_value[0] + means[p]
        pred.at[index, 'TRUE FORECAST PRE SEASONAL'] = pred.at[index, 'TRUE FORECAST PRE SEASONAL'] + means[p]
        
  #pred['TRUE FORECAST'] = pred['TRUE FORECAST'] - x_pred[y_name].iloc[0]
  
  pred['FORECAST'] = pred['FORECAST'].cumsum()
  pred['FORECAST NO SEASONAL'] = pred['FORECAST NO SEASONAL'].cumsum()
  pred['TRUE FORECAST PRE SEASONAL'] = pred['TRUE FORECAST PRE SEASONAL'].cumsum()
  pred['TRUE FORECAST'] = pred['TRUE FORECAST'].cumsum()
  pred['TRUE FORECAST MIN'] = pred['TRUE FORECAST MIN'].cumsum()
  pred['TRUE FORECAST MAX'] = pred['TRUE FORECAST MAX'].cumsum()
  #print(pred['FORECAST NO SEASONAL'])
  pred['FORECAST POST SEASONAL'] = pred['FORECAST POST SEASONAL'].cumsum()
  #pred['FORECAST PS MAX'] = pred['FORECAST PS MAX'].cumsum()
  #pred['FORECAST PS MIN'] = pred['FORECAST PS MIN'].cumsum()
  pred['time'] = pred_t
  #print(pred['FORECAST POST SEASONAL']) # 'FORECAST','FORECAST POST SEASONAL',
  pred.plot(x="time",y=['TRUE FORECAST PRE SEASONAL','FORECAST POST SEASONAL','TRUE FORECAST','REAL']) # 'FORECAST NO SEASONAL',
  #pred.plot(x="time",y=['FORECAST','FORECAST POST SEASONAL','REAL'])
  plt.xlim(pred['time'].min(), pred['time'].max()) # fix to a axis problem that matplotlib screws up sometimes
  plt.savefig('/var/www/html/kotibobot/' + 'regression.svg')
  #print((mlr.coef_[0:-1], mlr.coef_[-1], mlr.intercept_))
  return (mlr.coef_[0:-1], mlr.coef_[-1], mlr.intercept_, means)

matplotlib.use('svg') # no GUI when plotting
#print(do(['outside temp', 'olkkari power socket'], 'olkkarin lämpömittari temp', []))

