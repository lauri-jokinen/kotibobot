from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np
import requests
import time
import math
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

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

def load_ts_data():
  df = pd.DataFrame()
  year = datetime.now().year
  for i in range(1):
    file_name = '/home/lowpaw/Downloads/kotibobot/el-price_' + str(year) + '.pkl'
    try:
      df_year = pd.read_pickle(file_name)
      df = df_year.append(df, sort=False, ignore_index=True)
    except:
      "nothing here"
    year = year - 1
  return df[df['time'] > datetime.now() - timedelta(hours = 8765.81)]

def latest(df = load_ts_data()):
  res = float('nan')
  index = len(df.index)-1
  return df.iloc[-1]['electricity price']

def precentile(df = load_ts_data()):
  value = latest(df)
  df_below = df[df['electricity price']<=value]
  return len(df_below) / len(df)

def precentile_interval(h1, h2, df = load_ts_data()):
  df = df[df['time'].dt.hour>=h1]
  df = df[df['time'].dt.hour<=h2]
  value = latest(df)
  df_below = df[df['electricity price']<=value]
  return len(df_below) / len(df)

