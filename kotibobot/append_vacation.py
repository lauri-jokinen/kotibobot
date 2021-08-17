import kotibobot.eq3
from common_functions import *
from datetime import datetime
from kotibobot.command_queue import append as command_queue_append

# This module allows us to apply vacation modes on top of each other
#  by using the scheduled command_queue -functionality.

# Basically a new vacation command overrides the existing vacation-status
#  and if there is a pre-existing vacation-command,
#  that is scheduled for a longer period than the new command, it will
#  be reactivated after the new vacation period is finished.

def main(selected_rooms, command):
  
  if len(selected_rooms) != 1:
    return ["ERROR: Select exactly one room for append-vacation"]
    
  # collect status info from all eq3s in the selected room
  sync_info = kotibobot.eq3.command_human("-".join(selected_rooms) + " sync")
  
  # this loop seeks the first non-erronous status report
  while len(sync_info)>=2: 
    if "Connection failed" in sync_info[0] or "ERROR" in sync_info[0]:
      sync_info.pop(0)
    else:
      sync_info.pop(1)
  
  if "Connection failed" in sync_info[0] or "ERROR" in sync_info[0]:
    return ["ERROR: Devices did not return anything sensible with sync-command"]
  
  # if vacation mode is already in place...
  if "vacation" in sync_info[0]:
    
    # vacation end times for comparison
    current_vacation_datetime = read_vacation_datetime_from_sync(sync_info[0])
    new_vacation_datetime     = read_vacation_datetime_from_command(command)
    
    if current_vacation_datetime < new_vacation_datetime:
      # if existing vacation mode is longer than the new one, set a timer onto command_queue with new temp
      # this is in case of other existing commands in the queue and overwriting them
      new_temp = command.split(" ")[-1]
      res = kotibobot.eq3.command_human("-".join(selected_rooms) + " vacation " + current_vacation_datetime.strftime("%y-%m-%d %H:%M") + " " + new_temp)
      
      #res = kotibobot.eq3.command_human("-".join(selected_rooms) + " " + command[8:]) # tähän lyhyt
      command_queue_append("@" + current_vacation_datetime.isoformat() + " " + "-".join(selected_rooms) + " " + command[8:])
      return res
    
    elif current_vacation_datetime > new_vacation_datetime:
      # if existing vacation mode is shorter than the new one, set a timer onto command_queue with old temp
      res = kotibobot.eq3.command_human("-".join(selected_rooms) + " " + command[8:])
      old_temp = (sync_info[0].split("Temperature:")[1]).split("°C")[0]
      old_temp = remove_extra_spaces(old_temp)
      command_array = command[8:].split(" ")
      command_array[-1] = old_temp
      command = " ".join(command_array)
      command_queue_append("@" + new_vacation_datetime.isoformat() + " " + "-".join(selected_rooms) + " vacation " + current_vacation_datetime.strftime("%y-%m-%d %H:%M") + " " + old_temp)
      return res
      
    else: # if existing vacation mode has same end time as the new one, simply overwrite it
      return kotibobot.eq3.command_human("-".join(selected_rooms) + " " + command[8:])
      
  else: # if no existing vacation mode, set it normally
    return kotibobot.eq3.command_human("-".join(selected_rooms) + " " + command[8:])



def read_vacation_datetime_from_sync(s):
  datetime_str = (s.split("Vacation until:")[1]).split("\n")[0]
  datetime_str = remove_extra_spaces(datetime_str)
  return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

def read_vacation_datetime_from_command(c):
  datetime_str = c.split("vacation ")[1]
  datetime_str = remove_extra_spaces(datetime_str)
  datetime_str = datetime_str[0:14]
  return datetime.strptime(datetime_str, '%y-%m-%d %H:%M')
