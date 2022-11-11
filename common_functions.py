# - *- coding: utf- 8 - *-
import subprocess # ubuntu bash

def remove_extra_spaces(string): # and remove tabs!
  arr = string.split(" ")
  i = 0
  while i < len(arr):
    if arr[i] == '':
      arr.pop(i)
    else:
      i = i+1
  return "".join((" ".join(arr)).split("\t"))
