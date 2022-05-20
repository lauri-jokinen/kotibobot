# - *- coding: utf- 8 - *-
import subprocess # ubuntu bash

def restart_bluetooth():
  try:
    s = ['sudo', '/etc/init.d/bluetooth', 'restart']
    res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 5)
    res_str = res.stdout.decode('utf-8')
  except:
    res_str = "ERROR: Bluetooth could not be restarted"
  return res_str

def remove_extra_spaces(string): # and remove tabs!
  arr = string.split(" ")
  i = 0
  while i < len(arr):
    if arr[i] == '':
      arr.pop(i)
    else:
      i = i+1
  return "".join((" ".join(arr)).split("\t"))

