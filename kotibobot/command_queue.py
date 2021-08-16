# - *- coding: utf- 8 - *-
import dateutil.parser
from datetime import datetime
from house import *
from common_functions import *
import kotibobot.eq3

import pytz
utc=pytz.UTC

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

def do():
  queue = read()
  i = 0
  while i < len(queue):
    if "@" in queue[i]: # sceduled commands
      due_time_str = queue[i].split("@")[1].split(" ")[0]
      due_time = dateutil.parser.isoparse(due_time_str)
      if datetime.now() > due_time:
        queue[i] = " ".join(queue[i].split(" ")[1:]) # conversion to non-sceduled command
        rewrite(queue)
      else:
        i = i+1
    else: # non-sceduled commands
      res = " ".join(kotibobot.eq3.command_human(queue[i]))
      if not ("ERROR" in res or "failed" in res):
        queue.pop(i)
        rewrite(queue)
      else:
        i = i+1

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
