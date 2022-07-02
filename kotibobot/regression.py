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
def do(x_names, y_name, binary_attributes): # x_names is an array; y_name is str
  # x_names: ['outside temp', 'olkkarin nuppi valve']
  # y_names: 'olkkarin lämpömittari temp' (is also included in x)
  
  # Load data and discard useless information
  df = load_ts_data()
  df = df[x_names + [y_name, 'time']]
  
  # Moving average and difference
  df[y_name] = df[y_name].rolling(window=5).mean()
  df['YDIFF'] = df[y_name].diff()
  
  
  # Remove infeasible values
  df = df.dropna()
  for b in binary_attributes:
    df = df[df[b] != -1]
  
  # Regression time period
  t_start = datetime.now() - timedelta(hours = 22*24) # 22*24
  t_end = datetime.now() - timedelta(hours = 24) # 24
  
  train = df
  train = train[train['time'] >= t_start]
  train = train[train['time'] < t_end]
  
  # The "training data" and regression
  x = train[x_names + [y_name]]
  y = train['YDIFF']
  
  #mlr = HuberRegressor()
  mlr = LinearRegression()
  mlr.fit(x, y)
  
  train['YDIFF_RESIDUAL'] = y - mlr.predict(x)
  
  # Seasonal fixing, daily per hour
  train['clock'] = train['time'].dt.hour + train['time'].dt.minute / 60
  means = []
  for i in range(24):
    train_sub = train[train['clock'] < i+1]
    train_sub = train_sub[i <= train_sub['clock']]
    means.append(train_sub['YDIFF_RESIDUAL'].mean())
    if math.isnan(means[-1]):
      means[-1] = 0.0
  
  #plt.scatter(range(24),means)
  
  #train['YDIFF_HOUR_FIXED'] = train['YDIFF'] - np.array(means)[train['time'].dt.hour]
  
  # Forecast compared with real data
  pred = df
  pred = pred[pred['time'] >= t_end]
  pred_t = pred['time']
  x_pred = pred[x_names + [y_name]]
  
  pred['REAL'] = pred['YDIFF'].cumsum()
  pred['FORECAST'] = (mlr.predict(x_pred) + np.array(means)[pred['time'].dt.hour]).cumsum()
  pred['time'] = pred_t
  
  pred.plot(x="time",y=['FORECAST','REAL'])
  plt.xlim(pred['time'].min(), pred['time'].max()) # fix to a axis problem that matplotlib screws up sometimes
  plt.savefig('/var/www/html/kotibobot/' + 'regression.svg')
  return mlr.coef_

matplotlib.use('svg') # no GUI when plotting
#print(do(['outside temp', 'olkkari power socket'], 'olkkarin lämpömittari temp', []))

