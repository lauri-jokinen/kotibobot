import kotibobot
from wakeonlan import send_magic_packet
import json

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

data = kotibobot.plotting.latest_data_json()
temp = data['työkkärin lämpömittari temp']

if kotibobot.electricity_price.precentile_interval(2, 3) > 75.0:
  print('Sähkö on kallista :(')
elif temp >= 21:
  print('Lämpö korkealla :(')
else:
  print('Käynnistyy...')
  send_magic_packet(koodit['pöytäkone-mac'])
  print('Käynnistetty!')
