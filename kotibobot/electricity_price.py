from datetime import date, datetime, timedelta
import pandas as pd
#from wakeonlan import send_magic_packet
import requests
from bs4 import BeautifulSoup

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

def precentile_for_hours(value, start, end):
  if start > end:
    return precentile_for_hours(end, start)
  
  df = load_ts_data_year()
  df = df[['time','electricity price']]
  df = df[df['electricity price'].notna()]
  df.reset_index(drop=True, inplace=True) # index from zero
  # sum of the time when price > value
  now = datetime.now()
  d = now-now
  for ind in range(len(df)-1):
    if df['time'][ind].hour <= start or df['time'][ind].hour > end:
      continue
    p1 = df['electricity price'][ind]
    p2 = df['electricity price'][ind+1]
    if p1 < value and p2 < value:
      d = d + (df['time'][ind+1] - df['time'][ind])
    elif (p1 - value) * (p2 - value) < 0:
      # the case where the price at the other point is above and at the other point under the given value
      # here we make a linear interpolation, and approximate the time
      d = d + (df['time'][ind+1] - df['time'][ind]) * abs((min(p1,p2)-value)/(p1-p2))
  fraction = d/((df['time'][len(df)-1] - df['time'][0])*(end-start)/24)
  return fraction
