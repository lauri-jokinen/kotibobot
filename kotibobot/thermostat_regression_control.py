import numpy as np
from scipy.optimize import linprog
from datetime import datetime, timedelta, date

import kotibobot.weather, kotibobot.schedule, kotibobot.regression
from house import *

def do():
  # from regression
  eq3 = rooms['olkkari']['eq3'][0]
  print(eq3)
  Ti0 = kotibobot.plotting.latest_data_json()['olkkarin lämpömittari temp']
  
  #do(x_names, y_name, binary_attributes)
  (attributes, gamma, sigma, means) = kotibobot.regression.do(['outside temp', 'olkkarin nuppi target'], 'olkkarin lämpömittari temp', [])
  beta = attributes[0]; alpha = attributes[1]
  print(attributes)
  print(sigma)
  print(gamma)
  
  if alpha == 0.0:
    print('alpha is zero; the problem is not controllable')
    alpha = 0.1
    #return
  
  # number of ten minute things
  n = 6*24;

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
  
  # vector s = [1,...,n]
  s = np.zeros(n)
  for p in range(n):
    s[p] = p+1
  
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
  b = -(m - g * Ti0 - beta * G @ T_o - sigma*s)
  p = np.ones(n)
  bounds = (5.0, 30.0) # ilman boundseja TAI ilman Ax<=b:tä homma ratkeaa aina.
  res = linprog(p, A, b, bounds=bounds)
  
  while 'nfeasib' in res.message:
    b = b + 1
    print('infeasible...')
    res = linprog(p, A, b, bounds=bounds)
  print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)
  return res.x[0]
