from datetime import datetime, timedelta
import dateutil.parser # parse ISO
import json
import requests
import time as def_time
#import re

import kotibobot.command_queue

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

# If a command does not go through, we put it in queue. For this reason we need to convert the vacation command's
# hour to a time. This is marked with {h}. The variable is later converted to a time.
commands = {
'cool-1h':['olkkari vacation {1} 15', 'työkkäri vacation {1} 15', 'makkari vacation {1} 15'],
'cool-2h':['olkkari vacation {2} 15', 'työkkäri vacation {2} 15', 'makkari vacation {2} 15'],
'auto':['olkkari auto', 'työkkäri auto', 'makkari auto']
}
#'olkkari-cool'    : ['olkkari vacation {2} 10'],
#'tyokkari-cool'   :['työkkari vacation {2} 10'],
#'makkari-cool'    : ['makkari vacation {2} 10'],
#'makkari-normal'  : ['makkari vacation {2} 21.0'],
#'olkkari-normal'  : ['olkkari vacation {2} 21.5'],
#'tyokkari-normal' :['työkkäri vacation {2} 21.5']
#}

last_time = datetime.now() - timedelta(seconds=5)

def hours_from_now_rounded(h):
  time = datetime.now() + timedelta(hours = h)
  rounded = time + (datetime.min - time + timedelta(minutes = 15)) % timedelta(minutes=30) - timedelta(minutes = 15)
  string = rounded.strftime("%y-%m-%d %H:%M")
  return string

def replace_hours_with_time(string):
  s = string.split('{1}')
  if len(s) == 2:
    return "".join([s[0], hours_from_now_rounded(1), s[1]])
  
  s = string.split('{2}')
  if len(s) == 2:
    return "".join([s[0], hours_from_now_rounded(2), s[1]])
  
  return string

print('PHP-listener running...')

while True:
  def_time.sleep(5)
  for command in commands:
    try:
      fo = open('/var/www/html/kotibobot-komennot/visitors/' + command + '.txt', 'r')
      PHP_res = fo.read()
      fo.close()
    except:
      continue
    time_str = PHP_res.split('Time: ')[1].split('\n')[0]
    time = dateutil.parser.isoparse(time_str)
    
    if last_time >= time:
      continue
    
    print('time is ' + time_str)
    
    ip_address = PHP_res.split('IP: ')[1].split('\n')[0]
    print('ip_address: ' + ip_address)
    if not (ip_address == '192.168.1.1'):
      continue
      # IP -> country
      # https://www.abstractapi.com/guides/how-to-geolocate-an-ip-address-in-python
      # URL to send the request to
      #request_url = 'https://geolocation-db.com/jsonp/' + ip_address
      # Send request and decode the result
      #response = requests.get(request_url)
      #result = response.content.decode()
      # Clean the returned string so it just contains the dictionary data for the IP address
      #result = result.split("(")[1].strip(")")
      # Convert this data into a dictionary
      #country  = json.loads(result)['country_name']
      #print(country)
      #if country != 'Finland':
      #  continue
    
    print('Komennot menevät jonoon!')
    
    for c in commands[command]:
      co = replace_hours_with_time(c)
      print(co)
      res = kotibobot.eq3.command_human(co)
      if "Connection failed" in ''.join(res) or "ERROR" in ''.join(res):
        kotibobot.command_queue.append(co)
  last_time = datetime.now()
