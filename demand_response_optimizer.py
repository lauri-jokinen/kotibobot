import json, requests, math, time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
import matplotlib.pyplot as plt

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

def frequency():
    TOKEN = koodit["fingrid"] # lateus96
    # TOKEN = koodit["fingrid2"] lauri.a.jokinen
    five_minutes = timedelta(hours=30*24)
    now = datetime.now() + five_minutes
    before = datetime.now() - five_minutes
    start = before.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') + '%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    end = now.strftime("%Y-%m-%dT%HXXX%MXXX%S").replace('XXX','%3A') +'%2B' + "%02d" % math.floor(-time.timezone / 3600) + '%3A00'
    url2 = 'https://api.fingrid.fi/v1/variable/177/events/json?start_time=' + start + '&end_time=' + end
    return requests.get(url2, headers={'x-api-key': TOKEN, 'Accept': 'application/json'}).json() # dataframeksi

df = pd.DataFrame(frequency())
print(df)
df = df[df['value'] > 45.0]
df = df[df['value'] < 55.0]
df.replace([np.inf, -np.inf], np.nan, inplace=True) # replace +-inf with nan
df = df[df['value'].notna()] # remove nans
freqs = np.array(df['value'])

#df = pd.DataFrame()
#freqs = [50.2, 51.4, 49.7, 49.43, 50.4,49.89,49,49,49,49,49,48,50.234]

#freqs = np.random.normal(0, 1.42e-2, 50)
#freqs = np.concatenate((freqs, -freqs))
#freqs = np.cumsum(freqs) + 50

ds = np.linspace(0,0.04,100)
ints = np.linspace(0,0.04,100)
prob_pivot = 0.2

# pivot gives the fraction of time we'd like to shut down the appliance

# now, we integrate frequency, but only at times when the appliance is down.
# we want to maximize the frequency integral, s.t. we use electricity at high frequencies

for p in range(len(ds)):
  d=ds[p]
  #print(d)
  prob = sum(df['value'] < 50 - d)/len(freqs)
  #print(prob * 24*60) # ~ minutes off per day
  if prob < prob_pivot:
    ints[p] = 50
    continue
  f_low = 50-d
  f_up = 50+d*0.5 # change this and find optimum
  off_count = 0
  integral = 0
  is_on = 1
  minutes_on = 9; # 9

  for i in range(len(freqs)-1):
    #print(is_on)
    if off_count >= minutes_on/3:
      integral = integral + (freqs[i] + freqs[i+1])/2 * (off_count+1)
      off_count = 0
      is_on = 1
      continue
    
    if freqs[i] < f_low:
      # low freq? turn it off
      off_count = off_count + 1
      is_on = 0
    elif freqs[i] > f_up:
      # high freq? turn it on!
      integral = integral + (freqs[i] + freqs[i+1])/2 * (off_count+1)
      off_count = 0
      is_on = 1
    elif is_on:
      integral = integral + (freqs[i] + freqs[i+1])/2 * 1
      # between 49 and 50? leave as is
      off_count = 0
      is_on = 1
    else:
      off_count = off_count + 1
      is_on = 0
      
  ints[p] = integral / (len(freqs)-1)
  ints[p] = (ints[p] - 50)*prob_pivot / prob + 50

plt.plot(ds,ints - freqs.mean())
plt.show()
