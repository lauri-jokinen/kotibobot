from datetime import date, datetime, timedelta
import pandas as pd
#from wakeonlan import send_magic_packet
import requests
from bs4 import BeautifulSoup
import numpy as np
from multiprocessing import Pool

def get_nonrobust():
  # fetch the current electricity price in Finland
  url = "https://fortum.heydaypro.com/tarkka/graph.php"
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'lxml')
  html_data = str(soup.find('div',attrs = {'class':'price-container col-xs-12 col-sm-4'}))
  # parse float from the following string:
  # ...chart_price_now">18<span class="comma">,</span>89</span>...
  # above the price is 18.89 c/kWh
  price_str = html_data.split('chart_price_now">')[1].split('<span')[0]
  price_str = price_str + '.' + html_data.split('comma">,</span>')[1].split('</span')[0]
  price = float(price_str)
  return price

def get():
  try:
    res = get_nonrobust()
  except:
    res = float('nan')
  return res

def load_ts_data_year():
  df = pd.DataFrame()
  month_duration = timedelta(hours = 24*30.43685) # average month duration
  now = datetime.now()
  for i in range(13):
    month = now - i*month_duration
    month_file_name = '/home/lowpaw/Downloads/kotibobot/' + month.strftime("%Y-%m") + '.pkl'
    try:
      df_month = pd.read_pickle(month_file_name)
      df = df_month.append(df, sort=False, ignore_index=True)
    except:
      "nothing here"
  return df[df['time'] > datetime.now() - timedelta(hours = 8765.81)]

def precentile(value):
  # returns the fraction: (time when el.price < value over the past year) / (past year)
  df = load_ts_data_year()
  df = df[['time','electricity price']]
  df = df[df['electricity price'].notna()]
  df.reset_index(drop=True, inplace=True) # index from zero
  # sum of the time when price > value
  now = datetime.now()
  d = now-now
  for ind in range(len(df)-1):
    p1 = df['electricity price'][ind]
    p2 = df['electricity price'][ind+1]
    if p1 < value and p2 < value:
      d = d + (df['time'][ind+1] - df['time'][ind])
    elif (p1 - value) * (p2 - value) < 0:
      # the case where the price at the other point is above and at the other point under the given value
      # here we make a linear interpolation, and approximate the time
      d = d + (df['time'][ind+1] - df['time'][ind]) * abs((min(p1,p2)-value)/(p1-p2))
  fraction = d/(df['time'][len(df)-1] - df['time'][0])
  return fraction
'''
def precentile_interval(value, start, end):
  # start end are str; for example, '00:00' and '24:00'
  tA = datetime.strptime(start, '%H:%M')
  tB = datetime.strptime(end, '%H:%M')
  df = load_ts_data_year()
  df = df[['time','electricity price']]
  df = df[df['electricity price'].notna()]
  df.reset_index(drop=True, inplace=True) # index from zero
  # sum of the time when price > value
  T = np.array([timedelta(hours=0), timedelta(hours=0)])
  for ind in range(len(df)-1):
    T = T + precentile_interval_datapts(value, df['time'][ind], df['time'][ind+1], df['electricity price'][ind], df['electricity price'][ind+1], tA, tB)
  return T[0]/T[1]
'''
def precentile_interval(value, start, end): # parallel
  # start end are str; for example, '00:00' and '24:00'
  tA = datetime.strptime(start, '%H:%M')
  tB = datetime.strptime(end, '%H:%M')
  df = load_ts_data_year()
  df = df[['time','electricity price']]
  df = df[df['electricity price'].notna()]
  df.reset_index(drop=True, inplace=True) # index from zero
  # sum of the time when price > value
  
  t = datetime.now()
  jobs = []
  for ind in range(len(df)-1):
    jobs.append((value, df['time'][ind], df['time'][ind+1], df['electricity price'][ind], df['electricity price'][ind+1], tA, tB))
  #print('create jobs: ' + str(datetime.now()-t))
  
  t = datetime.now()
  pool = Pool(4).map(precentile_interval_datapts_parallel, jobs)
  #print('execute pool: ' + str(datetime.now()-t))
  
  T = np.array([timedelta(hours=0), timedelta(hours=0)])
  for ind in range(len(df)-1):
    T = T+pool[ind]
  
  return T[0]/T[1]

def is_before(a,b):
  return only_time(a) < only_time(b)

def only_time(a):
  ta = a.strftime('%H:%M')
  return datetime.strptime(ta, '%H:%M')

def time_above(value, t1, t2, v1, v2):
    if v1 < value and v2 < value:
      return t2-t1
    if (v1 - value) * (v2 - value) < 0:
      # the case where the price at the other point is above and at the other point under the given value
      # here we make a linear interpolation, and approximate the time
      return (t2-t1) * abs((min(v1,v2)-value)/(v1-v2))
    
    return timedelta(hours=0)

def precentile_interval_datapts(value, t1, t2, v1, v2, tA, tB):
  if t2-t1 > timedelta(hours=24):
    return np.array([timedelta(hours=0), timedelta(hours=0)])
  
  T1 = only_time(t1)
  T2 = only_time(t2)
  
  if is_before(only_time(t2),only_time(t1)):
    MN1 = datetime.strptime('00:00', '%H:%M')
    MN2 = datetime.strptime('23:59', '%H:%M')
    vMN = interpolate(MN2, only_time(t1), only_time(t2)+timedelta(hours=24), v1, v2)
    return precentile_interval_datapts(value, T1, MN2, v1, vMN, tA, tB) + precentile_interval_datapts(value, MN1, T2, vMN, v2, tA, tB)
  
  if tA < T1 and T2 < tB:
    return np.array([time_above(value, T1, T2, v1, v2), T2 - T1])
    
  if tA >= T1 and T2 >= tB:
    vB = interpolate(tB, T1, T2, v1, v2)
    vA = interpolate(tA, T1, T2, v1, v2)
    return np.array([time_above(value, tA, tB, vA, vB), tB - tA])
    
  if tA >= T1 and T2 < tB:
    vA = interpolate(tA, T1, T2, v1, v2)
    return np.array([time_above(value, tA, T2, vA, v2), T2 - tA])
    
  # the case where (tA < T1 and T2 >= tB)
  vB = interpolate(tB, T1, T2, v1, v2)
  return np.array([time_above(value, T1, tB, v1, vB), tB - T1])
    

def precentile_interval_datapts_parallel(args):
  return precentile_interval_datapts(args[0], args[1], args[2], args[3], args[4], args[5], args[6])

def interpolate(T, t1, t2, v1, v2):
  if t1 == t2:
    return 0.0
  alpha = (T-t1)/(t2-t1)
  V = v1 * (1 - alpha) + v2 * alpha
  return V
'''
print('here we go')
t = datetime.now()
print(precentile_interval(9.2, '09:00', '21:00'))
print(precentile_interval(5.2, '03:00', '23:00'))
print(datetime.now()-t)
#t = datetime.now()
#print(datetime.now()-t)
'''
