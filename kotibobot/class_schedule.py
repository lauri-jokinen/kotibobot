import numpy as np
from datetime import datetime, timedelta
from scipy import ndimage
import numpy

def only_time(a):
  ta = a.strftime('%H:%M')
  return datetime.strptime(ta, '%H:%M')

class Schedule:
  
  def __init__(self):
    self.sched = np.zeros(24*2)
  
  def print(self):
    arr = self.pretty()
    for p in arr:
      print(p[0] + '-' + p[1] + ' ' + str(p[2]))
  
  def eq3_schedule(self):
    return self.round().bound().simplify()
  
  def eq3_command(self):
    arr = self.round().simplify().pretty()
    res = []
    for p in arr:
      res.append(str(p[2]))
      res.append(p[1])
    return " ".join(res)
  
  def bound(self):
    res = Schedule()
    for i in range(len(self.sched)):
      res.sched[i] = min(30.0, max(5.0, self.sched[i]))
    return res
  
  def pretty(self):
    dateformat = '%H:%M'
    i = 0
    j = 1
    ti = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
    tj = ti+timedelta(minutes=30)
    res = []
    while j < len(self.sched):
      if self.sched[i] == self.sched[j]:
        j = j+1
        tj = tj+timedelta(minutes=30)
      else:
        res.append([ti.strftime(dateformat), tj.strftime(dateformat), self.sched[i]])
        i = j
        j = j+1
        ti = tj
        tj = tj+timedelta(minutes=30)
    res.append([ti.strftime(dateformat), '24:00', self.sched[i]])
    return res
    
  def simplify(self):
      res = Schedule()
      res.sched = self.sched
      c = 1
      while not res.eq3_specs_ok():
        c = c+2
        res.sched = numpy.ndarray.tolist(ndimage.median_filter(self.sched, size = c, mode='wrap'))
      res.sched = numpy.array(res.sched)
      return res
  
  def round(self):
    res = Schedule()
    res.sched = np.round(self.sched*2)/2
    return res
  
  def eq3_specs_ok(self):
      return len(self.pretty()) <= 5
  
  def read(self,time): # time is datetime
    t = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
    j = -1
    while only_time(t) <= only_time(time) and j+1 < len(self.sched):
      t = t+timedelta(minutes=30)
      j = j+1
    # t = t-timedelta(minutes=30) <- time of the given temperature
    return a.sched[j]
  
  def set(self,T,t1,t2): # ti 1 and t2 are strings
    if datetime.strptime(t1, '%H:%M') > datetime.strptime(t2, '%H:%M'):
      return set_temp(self,t2,t1,T)
    
    t = datetime.strptime('1/1/00 00:00:00', '%d/%m/%y %H:%M:%S')
    j = -1
    
    # find index for t1
    while only_time(t) <= datetime.strptime(t1, '%H:%M') and j+1 < len(self.sched):
      t = t+timedelta(minutes=30)
      j = j+1
    
    # set temperatures until t2
    while only_time(t) < datetime.strptime(t2, '%H:%M') and j+1 < len(self.sched):
      t = t+timedelta(minutes=30)
      self.sched[j] = T
      j = j+1
    
    self.sched[j] = T
    return self
  
  def sum(self,other):
    res = Schedule()
    res.sched = self.sched + other.sched
    return res
  
  def substract(self,other):
    res = Schedule()
    res.sched = self.sched - other.sched
    return res
    
  def update_integral(self,res,target): # basically = int^0.95 + error
    error = res.error(target)
    self.sched = np.power(np.abs(self.sched), 0.95)*np.sign(self.sched) + error.sched
    return self
    
  def error(self,target):
    return target.substract(self)
  
  def new_target(self,integral,error):
    res = Schedule()
    # tune these!
    ki = 0.1
    kp = 0.1
    res.sched = self.sched + integral.sched*ki + error.sched*kp
    return res
    
  def target(self,offset):
    return self.sum(offset)

a = Schedule()
a.sched[12] = 8.0
a.sched[-2] = 5.2
a.sched[-1] = 4.0
a.print()
a = a.round()
print('\n')
a.eq3_command()
a.update_integral(a,a).eq3_schedule().print()
