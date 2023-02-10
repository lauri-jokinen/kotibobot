# - *- coding: utf- 8 - *-
import dateutil.parser
from datetime import datetime
from house import *
from common_functions import *
import kotibobot.eq3

from kotibobot.plotting import load_ts_data as load_ts_data

# Command queue for eq3 devices, in case connection is lost for an extensive amount of time.

def read():
  fo = open('/home/lowpaw/Downloads/kotibobot/command_queue.txt', 'r')
  commands = fo.read()
  fo.close()
  return commands.split('\n')

def append(new_command):
  fo = open('/home/lowpaw/Downloads/kotibobot/command_queue.txt', 'a')
  fo.write("\n"+new_command)
  fo.close()

def rewrite(commands):
  fo = open('/home/lowpaw/Downloads/kotibobot/command_queue.txt', "w")
  fo.write("\n".join(commands))
  fo.close()


'''
# with @-functionality:
def do():
  queue = read()
  i = 0
  while i < len(queue):
    if "@" in queue[i]: # sceduled commands
      due_time_str = queue[i].split("@")[1].split(" ")[0]
      due_time = dateutil.parser.isoparse(due_time_str)
      # we take into account the cycle time of the loop in collect_data.py
      if datetime.now() + median_timedelta() > due_time:
        queue[i] = " ".join(queue[i].split(" ")[1:]) # conversion to non-sceduled command
        rewrite(queue)
      else:
        i = i+1
    else: # non-sceduled commands
      res = " ".join(kotibobot.eq3.command_human(queue[i]))
      if not ("ERROR" in res or "failed" in res):
        # read, modify and rewrite because of time consumed by the eq3 command
        # new commands may have been appended during this time
        queue = read()
        queue.pop(i)
        rewrite(queue)
      else:
        i = i+1
  rewrite(queue)
'''

def do():
  queue = read()
  i = 0
  while i < len(queue):
    res = " ".join(kotibobot.eq3.command_human(queue[i]))
    if not ("ERROR" in res or "failed" in res):
      # read, modify and rewrite because of time consumed by the eq3 command
      # new commands may have been appended during this time
      queue = read()
      queue.pop(i)
      rewrite(queue)
    else:
      i = i+1
  rewrite(queue)

def print_queue():
  queue = '\n'.join(read())
  if queue == '':
    return 'Jono on tyhjä'
  else:
    return queue
  
def wipe():
  commands = '\n'.join(read())
  rewrite('')
  return 'Komennot pyyhitty! Ne olivat:\n\n' + commands
  
def remove_append_vacation(selected_rooms):
  queue = read()
  for room in selected_rooms:
    i = 0
    while i < len(queue):
      if room in queue[i] and "vacation" in queue[i]:
        queue.pop(i)
      else:
        i = i+1
  rewrite(queue)

def median_timedelta():
  # median cycle time for the last five measurements
  df = load_ts_data()
  return ((df.iloc[-5:])['time']).diff().median()
