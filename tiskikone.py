from kotibobot.electricity_price import load_ts_data
from kotibobot.schedule import read_schedule
from house import rooms
import numpy as np
from datetime import datetime, timedelta
import math

def kaukolampo_c_kWh():
  # https://www.helen.fi/lammitys-ja-jaahdytys/kaukolampo/hinnat
  # c/kWh; hinta sis. alv
  return 10.74*0.7 # a little factor that accounts for the warm waste water

def is_daytime(end):
  #a = read_schedule(rooms['olkkari']["eq3"][0], end-timedelta(hours=1)) >= 21.0
  #b = read_schedule(rooms['olkkari']["eq3"][0], end) >= 21.0
  #c = read_schedule(rooms['olkkari']["eq3"][0], end+timedelta(hours=1)) >= 21.0
  #print(((1.0*a)+(1.0*b)+(1.0*c)) / 3.0)
  #return (((1.0*a)+(1.0*b)+(1.0*c)) / 3.0)
  return False

def price_of_running_appliance(duration, timer_N, timer_delta): # gives actually c/kWh*duration_in_hours , not price
  df = load_ts_data()
  now = datetime.now().replace(minute=0, second=0, microsecond=0)
  prices = np.zeros(timer_N)*float('nan')
  starts = []
  ends = []
  deltas = []
  
  for q in range(timer_N):
    
    starts.append(datetime.now() + q*timer_delta)
    ends.append(datetime.now() + q*timer_delta + duration)
    deltas.append(q*timer_delta)
    
    # first (incomplete) hour
    time = datetime.now() + q*timer_delta
    time_floor = time.replace(minute=0, second=0, microsecond=0)
    
    val_df = df[df['time']==time_floor]['electricity price'].values
    
    if len(val_df) == 1:
      prices[q] = val_df[0] * (60 - time.minute) / 60
    
    # loop the full hours in the middle
    p = 0
    start = time_floor + timedelta(hours=1)
    end = start + timedelta(hours=1)
    
    while end < datetime.now() + q*timer_delta + duration:
      #print(start)
      val_df = df[df['time']==start]['electricity price'].values
      
      if len(val_df) == 1:
        prices[q] = prices[q] + val_df[0]
      else:
        prices[q] = float('nan')
      end = end + timedelta(hours=1)
      start = start + timedelta(hours=1)
    
    # last (incomplete) hour
    time = datetime.now() + q*timer_delta + duration
    time_floor = time.replace(minute=0, second=0, microsecond=0)
    
    val_df = df[df['time']==time_floor]['electricity price'].values
    
    if len(val_df) == 1:
      prices[q] = prices[q] + val_df[0] * (time.minute) / 60
    else:
      prices[q] = float('nan')
    
    # take kaukolampo prices into account, if appliance is run at daytime
    kaukolampo_price = kaukolampo_c_kWh() * is_daytime(ends[q]) * duration.seconds / 60 / 60
    prices[q] = prices[q] - kaukolampo_price
      
  return (prices, starts, ends, deltas)
    
###########################################################################

def price_of_running_appliance_web(duration, timer_N, timer_delta, kWh):
  (prices, starts, ends, deltas) = price_of_running_appliance(duration, timer_N, timer_delta)
  prices_nonan = prices
  prices_nonan[np.isnan(prices_nonan)] = float('inf')
  min_ind = np.argmin(prices_nonan)
  res = ['<td><b>Alku</b></td> <td><b>Loppu</b></td> <td><b>Ajastus</b></td> <td><b>Hinta</b></td>']
  for q in range(min_ind+1):
    if not math.isnan(prices[q]):
      st_time = starts[q].strftime('%-H.%M')
      e_time = ends[q].strftime('%-H.%M')
      price = prices[q] / (duration/timedelta(hours=1)) * kWh
      delta_hrs = deltas[q].seconds/3600
      res.append('<td>{}</td> <td>{}</td> <td>{:.0f} h</td> <td>{:.2f} snt</td>'.format(st_time,e_time,delta_hrs,price))
  return '<tr>' + '\n</tr><tr>'.join(res) + '</tr>'
  
def price_of_running_appliance_web_quiet(duration, timer_N, timer_delta, kWh):
  (prices, starts, ends, deltas) = price_of_running_appliance(duration, timer_N, timer_delta)
  prices_nonan = prices
  prices_nonan[np.isnan(prices_nonan)] = float('inf')
  
  non_quiet = [6,22] # arki (6-22), ei vkloppu (8-23). voisi iffittää nekin
  
  quiet_vector = []
  for q in range(len(prices_nonan)):
    isnotquiettime = starts[q].hour >= non_quiet[0] and ends[q].hour < non_quiet[1] and starts[q].hour < ends[q].hour
    # also infeasible timer settings are discarded here
    quiet_vector.append((not isnotquiettime) or (not (q < 4 or q % 2 == 0)))
    
  prices_nonquiet = prices_nonan
  prices_nonquiet[quiet_vector] = float('inf')
  min_ind = np.argmin(prices_nonquiet)
  
  res = ['<td><b>Alku</b></td> <td><b>Loppu</b></td> <td><b>Ajastus</b></td> <td><b>Hinta</b></td>']
  min_ind = np.argmin(prices_nonan)
  for q in range(min_ind+1):
    if (not math.isnan(prices[q])) and (not quiet_vector[q]):
      st_time = starts[q].strftime('%-H.%M')
      e_time = ends[q].strftime('%-H.%M')
      price = prices[q] / (duration/timedelta(hours=1)) * kWh
      delta_hrs = deltas[q].seconds/3600
      res.append('<td>{}</td> <td>{}</td> <td>{:.1f} h</td> <td>{:.2f} snt</td>'.format(st_time,e_time,delta_hrs,price))
  return '<tr>' + '\n</tr><tr>'.join(res) + '</tr>'


#############################################################


data_pyykki = price_of_running_appliance_web_quiet(timedelta(hours=1,minutes=55), 48, timedelta(hours=0.5), 0.50)
data_tiski = price_of_running_appliance_web(timedelta(hours=2,minutes=55), 48, timedelta(hours=1), 0.88)

html_data_pyykki = ['''<HTML>
<meta charset="UTF-8">
<HEAD>
<TITLE>Pyykkikoneen ajastus</TITLE>
<style>
table { border-collapse: collapse; width: 90%;}
td { text-align: right; }
</style>
</HEAD>
<BODY BGCOLOR="FFFFFF">
<p style='font-family: "Trebuchet MS", sans-serif; font-size:50px'>
<table style='font-family: "Trebuchet MS", sans-serif; font-size:100%'>''','</table>','''
</p>
</BODY>
</HTML>''']
html_data_pyykki = html_data_pyykki[0] + data_pyykki + html_data_pyykki[1] + '<br>(päivitetty {}; ohjelma 1.55 h)'.format(datetime.now().strftime('%-d.%-m. klo %-H.%M')) + html_data_pyykki[2]

html_data_tiski = ['''<HTML>
<meta charset="UTF-8">
<HEAD>
<TITLE>Tiskikoneen ajastus</TITLE>
<style>
table { border-collapse: collapse; width: 90%;}
td { text-align: right; }
</style>
</HEAD>
<BODY BGCOLOR="FFFFFF">
<p style='font-family: "Trebuchet MS", sans-serif; font-size:50px'>
<table style='font-family: "Trebuchet MS", sans-serif; font-size:100%'>''','</table>','''
</p>
</BODY>
</HTML>''']
html_data_tiski = html_data_tiski[0] + data_tiski + html_data_tiski[1] + '<br>(päivitetty {}; ohjelma 2.55 h)'.format(datetime.now().strftime('%-d.%-m. klo %-H.%M')) + html_data_tiski[2]

fo = open('/var/www/html/pyykkikone.html', "w") # sudo chmod -R 0777 hs.php, jotta sitä voi muokata
fo.write(html_data_pyykki)
fo.close()

fo = open('/var/www/html/tiskikone.html', "w") # sudo chmod -R 0777 hs.php, jotta sitä voi muokata
fo.write(html_data_tiski)
fo.close()


