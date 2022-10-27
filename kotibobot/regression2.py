from kotibobot.plotting import load_ts_data

import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
#import matplotlib.pyplot as plt
#import matplotlib
import statsmodels.api as sm


def do(): # x_names is an array; y_name is str
  df = load_ts_data()
  #day_lag = 6*24
  #ma = (1, (0,)*day_lag, 1)
  
  df['työkkärin lämpömittari temp'] = np.double(df['työkkärin lämpömittari temp'].interpolate(axis=0))
  df['työkkärin nuppi valve'] = np.double(df['työkkärin nuppi valve'].interpolate(axis=0))
  df['työkkärin nuppi valve sq'] = df['työkkärin nuppi valve']**2
  df['outside temp lag'] = df['outside temp'].shift(1) # etsi lag kovarianssilla
  df['työkkärin nuppi valve lag'] = df['työkkärin nuppi valve'].shift(2) # etsi lag kovarianssilla
  
  days = 7+1
  forecasted_days = 1
  t_start = datetime.now() - timedelta(hours = days*24) # 22*24
  t_end = datetime.now() - timedelta(hours = forecasted_days*24) # 24
  
  train = df
  train = train[train['time'] >= t_start]
  train = train[train['time'] < t_end]
  
  
  mod = sm.tsa.statespace.SARIMAX(train['työkkärin lämpömittari temp'], train[['työkkärin nuppi valve lag', 'outside temp lag']], order=(3,1,3))
  res = mod.fit(disp=False)
  print(res.summary())
  
# forecast
# https://www.statsmodels.org/stable/examples/notebooks/generated/statespace_sarimax_stata.html

# interpret
# https://analyzingalpha.com/interpret-arima-results
# we want: high p-value; low AIC; high Log-l.
