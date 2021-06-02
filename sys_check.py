from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import kotibobot_functions as kotibobot
import json
import time



with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

def send_email(message):
  # Step 2 - Create message object instance
  msg = MIMEMultipart()
   
  # Step 3 - Create message body
  #message = "Test from Python via AuthSMTP"
  
  # Step 4 - Declare SMTP credentials
  password = "lapamato"
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
time.sleep(55) # 50 normisti
flag = False

for mi in kotibobot.mis:
  res = kotibobot.mi_to_json(mi)
  if 'battery' in res and res['battery'] < 10:
    flag = True
    break

if not flag:
  for eq3 in kotibobot.eq3s:
    res = kotibobot.eq3_command(eq3 + ' sync')
    if 'batt' in res:
      flag = True
      break

if flag:
  send_email('Jotkin paristot ovat lopussa.')
else:
  send_email('Kaikki on hyvin.')
