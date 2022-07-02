# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

def command_2(mac):
  try:
    s = ['python', '/home/lowpaw/Downloads/switchbot/switchbot.py', mac, 'Bot', 'Press']
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 32)
    res_str = res.stdout.decode('utf-8')
  except:
    res_str = "ERROR: Unknown error with a Switchbot."
  return res_str
  #return_dict['res'] = res_str

def press():
  mac = koodit['switchbot']
  res = command_2(mac)
  if "ERROR" in res or 'unsuccessful' in res:
    res = command_2(mac)
    if "ERROR" in res or 'unsuccessful' in res:
      return command_2(mac)
  return res
