# - *- coding: utf- 8 - *-
#import dateutil.parser
#from datetime import datetime
#from house import *
#from common_functions import *

# Command queue for eq3 devices, in case connection is lost for an extensive amount of time.

def read():
  fo = open('/home/lowpaw/Downloads/kotibobot/vahti.txt', 'r')
  commands = fo.read()
  fo.close()
  return commands.split('\n')

def append(new_command):
  fo = open('/home/lowpaw/Downloads/kotibobot/vahti.txt', 'a')
  fo.write("\n"+new_command)
  fo.close()

def rewrite(commands):
  fo = open('/home/lowpaw/Downloads/kotibobot/vahti.txt', "w")
  fo.write("\n".join(commands))
  fo.close()

def print_vahti():
  queue = '\n'.join(read())
  if queue == '':
    return 'Jono on tyhjä'
  else:
    return queue

def wipe():
  commands = '\n'.join(read())
  rewrite('')
  return 'Komennot pyyhitty! Ne olivat:\n\n' + commands

