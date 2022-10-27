import kotibobot
from wakeonlan import send_magic_packet
import json
from kotibobot.requests_robust import telegram_message

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

data = kotibobot.plotting.latest_data_json()
temp = data['työkkärin lämpömittari temp']

print(kotibobot.electricity_price.precentile_interval(2, 3))

if kotibobot.electricity_price.precentile_interval(2, 2) > 0.5: # precentile
  print('Sähkö on kallista :(')
elif temp >= 20.8:
  print('Lämpö korkealla :(')
else:
  print('Käynnistyy...')
  send_magic_packet(koodit['pöytäkone-mac'])
  print('Käynnistetty!')
  telegram_message('Tietokone käynnistetty!')
