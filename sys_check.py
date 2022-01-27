from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import time
from datetime import date, datetime
from wakeonlan import send_magic_packet

import kotibobot
import house

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

def send_email(message):
  # Step 2 - Create message object instance
  msg = MIMEMultipart()
   
  # Step 3 - Create message body
  #message = "Test from Python via AuthSMTP"
  
  # Step 4 - Declare SMTP credentials
  password = koodit["kotikone_salasana"]
  username = "lauri.jokinen@kotikone.fi"
  smtphost = "smtpa.kolumbus.fi:587"
  
  # Step 5 - Declare message elements
  msg['From'] = "lauri.jokinen@kotikone.fi"
  msg['To'] = "lateus96@gmail.com"
  msg['Subject'] = "Kotibobot"
  
  # Step 6 - Add the message body to the object instance
  msg.attach(MIMEText(message, 'plain'))
   
  # Step 7 - Create the server connection
  server = smtplib.SMTP(smtphost)
  
  # Step 8 - Switch the connection over to TLS encryption
  server.starttls()
   
  # Step 9 - Authenticate with the server
  server.login(username, password)
   
  # Step 10 - Send the message
  server.sendmail(msg['From'], msg['To'], msg.as_string())
  
  # Step 11 - Disconnect
  server.quit()

print('Ajetaan sys_check-skriptiä...')

time.sleep(55)
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
  send_email('Jotkin paristot ovat lopussa.') # low battery message
else:
  if date.today().weekday() == 0: # only on mondays
    send_email('Kaikki on hyvin.') # ok message

while datetime.now().hour != 2 or datetime.now().minute != 30:
  time.sleep(15)

if kotibobot.electricity_price.precentile_for_hours(kotibobot.electricity_price.get(), 3, 5) > 90.0:
  send_magic_packet(koodit['pöytäkone-mac'])
  send_email('Pöytäkone on käynnistetty')
else:
  send_email('Sähkö on kallista :(')
