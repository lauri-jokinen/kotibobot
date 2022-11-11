from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import time
from datetime import date

import kotibobot
import house

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

print('Ajetaan sys_check-skriptiä...')

time.sleep(5)
flag = False

for mi in house.mis:
  res = kotibobot.mi.to_json(mi)
  if 'battery' in res and res['battery'] < 10:
    flag = True
    break

if not flag:
  for eq3 in house.eq3s:
    res = kotibobot.eq3.command(eq3 + ' sync')
    if 'batt' in res:
      flag = True
      break

if flag:
  # low battery message
  kotibobot.requests_robust.telegram_message('Jotkin paristot ovat lopussa.')
else:
  if date.today().weekday() == 0:
    # ok message, only on mondays
    kotibobot.requests_robust.telegram_message('Kaikki on hyvin.')
