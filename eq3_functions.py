# - *- coding: utf- 8 - *-
import json
import subprocess # ubuntu bash

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

rooms = json.loads("{}")

rooms["olkkari"] = json.loads("{}")
rooms["olkkari"]["eq3"] = [koodit["keittiön nuppi"], koodit["olkkarin nuppi"]]

rooms["makkari"] = json.loads("{}")
rooms["makkari"]["eq3"] = [koodit["makkarin nuppi"]]

rooms["työkkäri"] = json.loads("{}")
rooms["työkkäri"]["eq3"] = [koodit["työkkärin nuppi"]]


mac_to_name = json.loads("{}")
mac_to_name[koodit["keittiön nuppi"]] = "keittiön nuppi"
mac_to_name[koodit["olkkarin nuppi"]] = "olkkarin nuppi"
mac_to_name[koodit["makkarin nuppi"]] = "makkarin nuppi"
mac_to_name[koodit["työkkärin nuppi"]] = "työkkärin nuppi"


name_to_mac = json.loads("{}")
for mac in mac_to_name:
  name_to_mac[mac_to_name[mac]] = mac

# Create an array with all eq-3 devices
eq3s = []
for room in rooms:
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3s.append(eq3)

print(eq3s)
#### FUNCTIONS

def replace_macs_to_names(str):
  for mac in thermostat_names:
    str = str.replace(mac, thermostat_names[mac])
  return str

def eq3_command(str):
  s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci1'] + str.split(' ')
  res = subprocess.run(s, stdout=subprocess.PIPE)
  res_str = res.stdout.decode('utf-8')
  if res_str == "Connection failed.":
    print('Yhteys pätki kerran')
    res = subprocess.run(s, stdout=subprocess.PIPE)
    res_str = res.stdout.decode('utf-8')
    if res_str == "Connection failed.":
      print('Yhteys pätki toisen kerran')
      res = subprocess.run(s, stdout=subprocess.PIPE)
      res_str = res.stdout.decode('utf-8')
  return res_str

#def bad_battery_eq3s():
#  low_battery = []
#  for eq3 in eq3s:
#    if "low battery" in eq3_command(eq3 + " sync"):
#      low_battery.append(mac_to_room(eq3))
#  return low_battery

def human_to_machine(str):
  selected_rooms = str.split(" ")[0].split("-")
  # No command -> return status
  if len(str.split(" ")) == 1:
    command = " status"
  else:
    command = " " + (" ").join(str.split(" ")[1:])
  res = []
  if selected_rooms == "kaikki":
    for eq3 in eq3s:
      eq3_command(eq3 + command)
  else:
    for room in selected_rooms:
      if room in rooms and "eq3" in rooms[room]:
        for eq3 in rooms[room]["eq3"]:
          res.append(replace_macs_to_names(eq3_command(eq3 + command)))
      else:
        res.append("Huonetta '" + room + "' ei ole. Valitse jokin näistä: " + ", ".join(rooms) + ". Käyn muut huoneet läpi.")
  return res
