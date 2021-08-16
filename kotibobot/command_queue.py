# - *- coding: utf- 8 - *-
from house import *
from common_functions import *
import kotibobot.eq3

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
    res = " ".join(kotibobot.eq3.command_human(queue[i]))
    if not ("ERROR" in res or "failed" in res):
      queue.pop(i)
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
