import smtplib, ssl
import kotibobot_functions as kotibobot
import json
import time

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

def send_email(str):
  port = 587  # For SSL
  smtp_server = "smtpa.kolumbus.fi"
  sender_email = "lauri.jokinen@kotikone.fi"  # Enter your address
  receiver_email = "lauri.jokinen@iki.fi"  # Enter receiver address
  password = koodit["kotikone_salasana"]
  message = """\
Subject: Kotibobot

"""
  message = message + str
  
  context = ssl.create_default_context()
  with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)

time.sleep(55) # 50 normisti
flag = False

for mi in kotibobot.mis:
  res = kotibobot.mi_to_json(mi)
  if res['battery'] < 10:
    print('Mi vailla virtaa :DD')
    flag = True
    break

if not flag:
  for eq3 in kotibobot.eq3s:
    res = kotibobot.eq3_command(eq3 + ' sync')
    if "batt" in res:
      flag = True
      break


if flag:
  print('Yritän lähettää postia...')
  send_email('Jotkin paristot ovat lopussa.')
