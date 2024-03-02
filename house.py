# - *- coding: utf- 8 - *-
import json

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

# more positive value implies a lower initial temp in the room
hard_offset = {'olkkari' : 2.0, 'makkari' : 0.5, 'työkkäri' : -3.0}

rooms = json.loads("{}")

# FILL IN THE ROOM INFORMATION IN JSON FORMAT
# {"room1" : {"eq3": ["mac1","mac2"], "mi" : ["mac3"]}, ...}
rooms["olkkari"] = json.loads("{}")
rooms["olkkari"]["eq3"] = [koodit["olkkarin nuppi"], koodit["keittiön nuppi"]]
rooms["olkkari"]["mi"] = [koodit["olkkarin lämpömittari"]]

rooms["makkari"] = json.loads("{}")
rooms["makkari"]["eq3"] = [koodit["makkarin nuppi"]]
rooms["makkari"]["mi"] = [koodit["työkkärin lämpömittari"]] # WRONG!

rooms["työkkäri"] = json.loads("{}")
rooms["työkkäri"]["eq3"] = [koodit["työkkärin nuppi"]]
rooms["työkkäri"]["mi"] = [koodit["makkarin lämpömittari"]] # WRONG!

# FILL IN THE MAC ADDRESSES AND NAMES OF ALL DEVICES
# {"mac1": "device name", ...}
mac_to_name = json.loads("{}")
mac_to_name[koodit["olkkarin nuppi"]] = "olkkarin nuppi"
mac_to_name[koodit["keittiön nuppi"]] = "keittiön nuppi"
mac_to_name[koodit["makkarin nuppi"]] = "makkarin nuppi"
mac_to_name[koodit["työkkärin nuppi"]] = "työkkärin nuppi"
mac_to_name[koodit["makkarin lämpömittari"]] = "työkkärin lämpömittari"
mac_to_name[koodit["työkkärin lämpömittari"]] = "makkarin lämpömittari"
mac_to_name[koodit["olkkarin lämpömittari"]] = "olkkarin lämpömittari"

# Next we construct all sorts of structs and arrays ...

# name to mac, inverse of the above
name_to_mac = json.loads("{}")
for mac in mac_to_name:
  name_to_mac[mac_to_name[mac]] = mac

# Create an array with all mac-addresses of all the eq-3 devices
eq3s = []
for room in rooms:
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3s.append(eq3)

# Create an array with all mac-addresses of all the mi devices
mis = []
for room in rooms:
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mis.append(mi)

# eq3s in rooms
# {"room1" : ["name1"], ...}
eq3_in_rooms = json.loads("{}")
for room in rooms:
  eq3_in_rooms[room] = []
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      eq3_in_rooms[room].append(mac_to_name[eq3])

# mi in rooms
# {"room1" : ["name1"], ...}
mi_in_rooms = json.loads("{}")
for room in rooms:
  mi_in_rooms[room] = []
  if "mi" in rooms[room]:
    for mi in rooms[room]["mi"]:
      mi_in_rooms[room].append(mac_to_name[mi])

# HUOM! NÄÄ ON VÄHÄN ULKOPUOLELTA!!!
def replace_macs_to_names(str):
  for mac in mac_to_name:
    str = str.replace(mac, mac_to_name[mac])
  return str
