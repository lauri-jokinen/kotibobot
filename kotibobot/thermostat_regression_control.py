import numpy as np
from scipy.optimize import linprog
from datetime import datetime, timedelta, date

import kotibobot.weather, kotibobot.schedule
from house import *

def do():
  # from regression
  eq3 = rooms['olkkari']['eq3'][0]
  print(eq3)
  Ti0 = kotibobot.plotting.latest_data_json()['olkkarin lämpömittari temp']
  gamma = 1; alpha = 0.01; beta = 24.2;
  
  # number of ten minute things
  n = 4;

  # format outside temperatures to corret vector form
  outside_temps = kotibobot.weather.forecast()
  #print(outside_temps)
  now = datetime.now()
  T_o = np.zeros(n)
  for p in range(n):
    time = datetime.now() + timedelta(minutes = 10*p)
    temp = outside_temps[outside_temps['time'] < time].iloc[-1]['temp']
    #print(str(temp) + ' at ' + str(time))
    T_o[p] = temp

  # format target temperatures to corret vector form
  weekday = date.today().weekday()
  schedule = kotibobot.schedule.import1()
  m = np.zeros(n)
  for p in range(n):
    time = datetime.now() + timedelta(minutes = 10*p)
    weekday = time.weekday()
    m[p] = kotibobot.schedule.read(schedule[eq3][kotibobot.schedule.everyday[weekday]],time)
  #print(m)
  
  # vector g
  g = np.zeros(n)
  for p in range(n):
    g[p] = (gamma+1)**(p+1)
  #print(g)
  
  # matrix G
  G = np.zeros((n,n))
  for p in range(n):
    for q in range(p+1):
      G[p][q] = (gamma+1)**(p-q)
  #print(G)
  
  A = -alpha * G
  b = -(m - g * Ti0 - beta * G @ T_o)
  p = np.ones(n)
  bounds = (0.0, 30.0)
  res = linprog(p, A, b, bounds=bounds)
  print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)
