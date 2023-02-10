from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import time
import requests
import math
import json
from os.path import exists

# https://github.com/kipe/nordpool
#from nordpool import elspot
import kotibobot.requests_robust

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import time
import math

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
  return price-0.3 # Fortum price premium


def get_nonrobust_2():
  caps = DesiredCapabilities().CHROME
  caps["pageLoadStrategy"] = "normal"  #  complete
  #caps["pageLoadStrategy"] = "eager"  #  interactive
  #caps["pageLoadStrategy"] = "none"
  
  s = Service("/usr/lib/chromium-browser/chromedriver")
  browser = webdriver.Chrome(desired_capabilities=caps,service=s)
  
  url = ("https://sahko.tk/")
  browser.get(url)
  #class_element = browser.find_elements(By.ID, "price_now") # ei toimi aina... miksi?
  time.sleep(0.87)
  html_source = browser.page_source
  browser.quit()
  
  #res = ""
  #for e in class_element:
  #  res = res + e.text
  #return float(res.split(" snt/kWh")[0])
  return float(html_source.split("price_now")[1].split(" snt/kWh")[0].split(">")[-1])

def get():
  try:
    res = get_nonrobust()
  except:
    res = float('nan')
  if math.isnan(res):
    time.sleep(4.23)
    try:
      res = get_nonrobust_2()
    except:
      res = float('nan')
  if math.isnan(res):
    time.sleep(8.16)
    try:
      res = get_nonrobust_2()
    except:
      res = float('nan')
  return res
'''

def get_forwards(time_delta = 0):
  for i in range(120): # 120 * 120 sek = 4 h
    try:
      res = get_forwards3(time_delta)
      break
    except Exception as e:
      print(e)
    time.sleep(120.752345)
  return res

def get_forwards3(time_delta):
  url = "https://www.nordpoolgroup.com/api/marketdata/page/10?currency=,,,EUR"
  r = kotibobot.requests_robust.get_url(url).json()['data']
  # check if today's data
  today = (datetime.now() - timedelta(hours=time_delta)).replace(hour=0, minute=0, second=0, microsecond=0)
  if not (datetime.strptime(r['DateUpdated'][0:10], '%Y-%m-%d') == today):
    raise Exception("Forward data is not yet published; data date is yesterday")
    
  # read data
  r = r['Rows']
  prices = []
  for row in r:
      for col in row['Columns']:
          if col['Name'] == 'FI' and len(prices) < 24:
              if col['Value']!='-': # accounts for daylight savings time; actually NP api does not work at days around DST for some reason
                if True: # datetime.now().month == 12: (only 10% tax for now)
                  prices.append(float(col['Value'].replace(',','.'))*1.10*0.1) # tax 10 % and conversion EUR/MW to cent/kW
                else:
                  prices.append(float(col['Value'].replace(',','.'))*1.24*0.1) # tax 24 % and conversion EUR/MW to cent/kW
  df = pd.DataFrame()
  
  df['electricity price'] = np.single(prices[0:24])
  
  # Create time column
  dates = []
  for p in range(24):
      dates.append(today + timedelta(hours = p+24))
  df['time'] = dates
  df['time'] = df['time'].dt.tz_localize('CET').dt.tz_convert('Europe/Helsinki').dt.tz_localize(None)
  print(df)
  return df
'''
def get_forwards2():
  # Initialize class for fetching Elspot prices
  prices_spot = elspot.Prices()
  # Fetch hourly Elspot prices for Finland and print the resulting dictionary
  p = prices_spot.hourly(areas=['FI'])
  df = pd.DataFrame(p['areas']['FI']['values'])
  df['time'] = df['start'].dt.tz_convert('Europe/Helsinki').dt.tz_localize(None)
  df['electricity price'] = np.single(df['value'] * 1.24 * 0.1) # tax 24 % and conversion EUR/MW to cent/kW
  df = df[['time','electricity price']]
  return df
'''
def load_ts_data():
  df = pd.DataFrame()
  year = datetime.now().year
  for i in range(2):
    file_name = '/home/lowpaw/Downloads/kotibobot/el-price_' + str(year - i) + '.pkl'
    if exists(file_name):
      df_year = pd.read_pickle(file_name)
      df = pd.concat([df_year,df], sort=False, ignore_index=True)
  
  if 'time' in df.columns:
    df = df.drop_duplicates(subset=['time'])
    df['electricity price'] = df['electricity price'] + 2.96 + 2.793 # NOTE! Caruna's price is added here
    return df[df['time'] > datetime.now() - timedelta(hours = 8765.81)]
  else:
    df['time'] = [datetime.now()]
    df['electricity price'] = [float('nan')]
    return df

def current(df = pd.DataFrame()):
  if not ('time' in df.columns):
    df = load_ts_data()
  time = datetime.now().replace(minute=0, second=0, microsecond=0)
  df_with_value = df[df['time'] == time]
  if len(df_with_value.index) >= 1:
    return df_with_value.iloc[0]['electricity price']
  else:
    return float('nan')

def precentile(df = pd.DataFrame()):
  if not ('time' in df.columns):
    df = load_ts_data()
  value = current(df)
  df_below = df[df['electricity price']<=value]
  return len(df_below) / len(df)

def precentile_interval(h1, h2, df = pd.DataFrame()):
  if not ('time' in df.columns):
    df = load_ts_data()
  value = current(df)
  df = df[df['time'].dt.hour>=h1]
  df = df[df['time'].dt.hour<=h2]
  df_below = df[df['electricity price']<=value]
  return len(df_below) / len(df)

def duck_curve(df = pd.DataFrame()):
  if not ('time' in df.columns):
    df = load_ts_data()
  # note that we use MEDIAN instead of MEAN!
  # it's more robust to outliers; price peaks may be high, but lows are not as striking
  means = []
  for h in range(24):
    df_hour = df[df['time'].dt.hour==h].dropna()
    #df_hour = df_hour[~df_hour.isin([np.nan, np.inf, -np.inf]).any(1)]
    means.append(df_hour.median(numeric_only=True).iloc[0])
  #print(means)
  return means

def frequency(full_response = False):
  try:
    TOKEN = koodit["fingrid"] # lateus96
    # TOKEN = koodit["fingrid2"] lauri.a.jokinen
    five_minutes = timedelta(minutes=130)
    now = datetime.now() + five_minutes
    before = datetime.now() - five_minutes
    start = before.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') + '%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    end = now.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') +'%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    url2 = 'https://api.fingrid.fi/v1/variable/177/events/json?start_time=' + start + '&end_time=' + end
    resp = kotibobot.requests_robust.get_url(url2, {'x-api-key': TOKEN, 'Accept': 'application/json'})
    if full_response:
      return resp.json()[-1]
    else:
      return resp.json()[-1]['value']
  except:
    return float('nan')
    
'''
### TOINEN HIDDEN API (jos nordpool ei toimi)
# Tää on se oikee sivu https://www.pks.fi/sahkotarjoukset/kotiin/mita-on-porssisahko/
# Ajat on unix, ilman aikaeroa (?)
# onko alv mukana? Toimiiko DST oikein?
# Onko edes järkevää pitää omaa databasea, koska tuolta saa vuoden datat.
r = requests.get("https://www.pks.fi/wp-content/themes/pks/sahkoporssi/domparser/sahkoporssiDataHourly.json").json()
r_end = r['Series']['Prices']['Data']
df = pd.DataFrame(r_end)
df.columns = ['time','electricity price']
df['time'] = pd.to_datetime(df['time'],origin='unix',unit='ms')
df['electricity price'] = np.single(df['electricity price'])
print(df)
'''
