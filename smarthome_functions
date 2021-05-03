# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

rooms = json.loads("{}")

rooms["olkkari"] = json.loads("{}")
rooms["olkkari"]["eq-3"] = [koodit["eq-3-1"], koodit["eq-3-2"]]

rooms["makkari"] = json.loads("{}")
rooms["makkari"]["eq-3"] = [koodit["eq-3-3"]]

rooms["työkkäri"] = json.loads("{}")
rooms["työkkäri"]["eq-3"] = [koodit["eq-3-4"]]

# Create an array with all eq-3 devices
eq3s = []
for room in rooms:
  if "eq-3" in rooms[room]
    for eq3 in rooms[room]["eq-3"]:
      eq3s.append(eq3)

def mac_to_room(mac):
  for room in rooms:
    if "eq-3" in rooms[room] and mac in rooms[room]["eq-3"]
      return room
  return "!room-undefined!"

def eq3_command(str):
  res = subprocess.run(['./eq3.exp', str], stdout=subprocess.PIPE)
  return res.stdout.decode('utf-8')

def bad_battery_eq3():
  low_battery = []
  for eq3 in eq3s:
    if "battery" in eq3_command(eq3 + " sync"): # or "low battery" ?
      low_battery.append(mac_to_room(eq3))
  return low_battery

# voiko tämän yhdistää ylempään? olisi järkevää :)
def check_connections_eq3():
  bad_connection = []
  for eq3 in eq3s:
    # if eq3_command(eq3 + " status") == "ok":
    if false:
    bad_connection.append(mac_to_room(eq3))
  return bad_connection

def sys_check():
  x = check_connections_eq3()
  if x != []:
    return "Yhteyttä ei saatu muodostettua huoneen (tai huoneiden) " + ", ".join(x) + " eq-3 termostaatteihin."
  x = bad_batteries()
  if x != []:
    return "Huoneen (tai huoneiden) " + ", ".join(x) + " eq-3 termostaateissa on patterit lopussa."
  sync_time()
  # check that rooms have same settings
