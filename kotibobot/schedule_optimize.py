import kotibobot.house as .


def control():
  

schedules = {}
for room in rooms:
  schedule[room + ' schedule']
  schedule[room + ' integral']
  
try:
  with file('schedules.pkl', 'rb') as f:
    schedules = pickle.load(f)
except:
  schedules = {}
  for eq3 in eq3s:
    schedules[eq3 + ' schedule'] = kotibobot.class_schedule.Schedule()
    schedules[eq3 + ' integral'] = kotibobot.class_schedule.Schedule()




for room in rooms:
  eq3_in_rooms[room] = []
  if "eq3" in rooms[room]:
    for eq3 in rooms[room]["eq3"]:
      control(eq3, room)
  


