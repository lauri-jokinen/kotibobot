from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
from datetime import datetime
from wakeonlan import send_magic_packet
import subprocess
import time

import kotibobot
import common_functions
from house import rooms

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

def showifemptystring(s):
  if s == '':
    return 'Empty output'
  else:
    return s
  
def authorized(update, context):
  return update.message.from_user.id in koodit["lowpaw_teleID"]

def start(update, context):
  text = """<b>Status ja datan piirtäminen</b>
  
Esim. komento '/makkari' antaa tämänhetkisen statuksen ja ajastusasetukset makkarissa. Komento '/kuvat' piirtää kuvat.

Seuraavilla komennoilla säädetään ja ajastetaan lämmitystä. Kaikki komennot saa tehtyä suoraan pattereissa oleviin termostaatteihin manuaalisesti. Jos serveri sattuu kaatumaan, niin koko järjestelmä jatkaa viimeisillä asetuksilla.

<b>Moodit ja niiden aktivointi</b>

 • '/makkari auto' - automaattinen, eli lämpötilat asetetaan ajastuksen mukaan
 • '/makkari man' - manuaalinen lämpötila
 • '/makkari boost' - avaa termostaatin venttiilin kokonaan viideksi minuutiksi. Asetuksen saa pois komennolla 'boost off', tai valitsemalla jonkin toisen moodin.
 • '/makkari vacation 21-06-31 12:30 21.5' - lomatila. Eli pitää asetetun lämpötilan annettuun ajankohtaan asti. Komennossa on asetuksen loppumispäivämäärä ja -aika sekä lämpötila. Kellonaika tulee olla pyöristetty puolen tunnin tarkkuudelle, ja lämpötila puolen asteen tarkkuudelle. Loma-asetuksen voi aktivoida myös komennolla '/makkari vacation 11.5 21.5', jossa loma-aika on seuraavat (noin) 11.5 tuntia. Asetuksen saa pois valitsemalla toisen moodin.

<b>Lämpötilan säätö</b>

'/makkari temp 18.5' - asettaa lämpötilaksi 18.5 °C. Kun päällä on automaattitila, asetettu lämpötila pysyy voimassa seuraavaan ajastettuun lämpötilan vaihdokseen asti. Lomatilassa komento asettaa loma-ajan lämpötilan. Lämpötila täytyy olla pyöristetty puolen asteen tarkkuudelle.

<b>Ajastus</b>

'/makkari timer mon 21 10:00 19 24:00' - asettaa maanantaille seuraavan ajastuksen:
00:00−10:00  −  21 °C
10:00−24:00  −  19 °C.
Komennon viikonpäivän tai -päivät voi valita tästä listasta: <b>mon, tue, wed, thu, fri, sat, sun, work, weekend, everyday, today, tomorrow</b>.
Viikonpäivän jälkeen oleva listaus alkaa aina lämpötilalla ja tulee päättyä aina kellonaikaan '24:00'.
Kellonaika tulee olla pyöristetty kymmenen minuutin tarkkuudelle ja lämpötila puolen asteen tarkkuudelle. Automaattiasetus noudattaa tätä ajastusta.

'timer-settings' antaa ajastusasetukset ylläolevan komennon mukaisesti helpompaa muokkausta varten. Tämä komento ei aina toimi, koska bugit toisten koodeissa...

<b>Koonti komentojen formaateista</b>

 • Desimaalierotin on piste
 • Kellonajassa täytetään alkuun nolla tarvittaessa, esim. 09:30.
 • Päivämäärä on muodossa vuosi-kk-pvä. Vuosiluvussa annetaan kaksi viimeistä numeroa, ja ylläolevat nollasäännöt pitävät tässäkin, esim. 21-06-31.
 • Komennoissa annettavat lämpötilat tulee olla pyöristetty puolen asteen tarkkuudelle.
 • Kellonajat tulee pyöristää joko puolen tunnin tarkkuudelle (vacation), tai kymmenen minuutin tarkkuudelle (timer).
"""
  return update.message.reply_text(text, parse_mode='HTML')

def direct_eq3_command(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  waiting_message = update.message.reply_text("Yhdistetään laitteisiin...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes /-command
  res_array = kotibobot.eq3.command_human(str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
  waiting_message.delete()

def makkaricommand(update,context):
  room_command(update,context,'makkari')
      
def tyokkaricommand(update,context):
  room_command(update,context,'työkkäri')
      
def olkkaricommand(update,context):
  room_command(update,context,'olkkari')

def room_command(update,context,room):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  waiting_message = update.message.reply_text("Yhdistetään laitteisiin...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  if str == "":
    res_array = kotibobot.eq3.command_human(room + ' status')
    res_array = res_array + kotibobot.mi.read_human(room)
  else:
    res_array = kotibobot.eq3.command_human(room + ' ' + str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
  waiting_message.delete()

def plot_data(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text(kotibobot.plotting.main_function(False), parse_mode='HTML')

def mi_status(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  waiting_message = update.message.reply_text("Yhdistetään laitteeseen...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  res_array = kotibobot.mi.read_human(str)
  if len(res_array) > 20:
    res_array = res_array[0:18]
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
  waiting_message.delete()
  
def data_command(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text(kotibobot.plotting.print_latest_data())

def command_queue_append(update, context):
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  waiting_message = update.message.reply_text('Kirjoitetaan komentoa muistiin...')
  kotibobot.command_queue.append(str)
  update.message.reply_text('Kirjoittaminen onnistui!')
  waiting_message.delete()

def command_queue_print(update, context):
  update.message.reply_text(kotibobot.command_queue.print_queue())

def command_queue_wipe(update, context):
  update.message.reply_text(kotibobot.command_queue.wipe())
  
def vahti_append(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  waiting_message = update.message.reply_text('Kirjoitetaan komentoa muistiin...')
  kotibobot.torivahti.append(str)
  update.message.reply_text('Kirjoittaminen onnistui!')
  waiting_message.delete()

def vahti_print(update, context):
  update.message.reply_text(kotibobot.torivahti.print_vahti())

def vahti_wipe(update, context):
  update.message.reply_text(kotibobot.torivahti.wipe())

# command: 'työkkäri everyday 21.5 09:10-10:30'
def timer_new(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  string = update.message.text
  waiting_message = update.message.reply_text('Hetkinen...')
  string_set = string.split(" ")[1:] # Removes the /-command
  if len(string_set)==1:
    schedule = kotibobot.schedule.import1()
    for eq3 in rooms[string_set[0]]["eq3"]:
      update.message.reply_text(kotibobot.schedule.print_whole_schedule(schedule[eq3]))
  else:
    times = string_set[3].split('-')
    res = kotibobot.schedule.set1(string_set[0], string_set[1], string_set[2], times[0], times[1], True, True)
    update.message.reply_text(res)
  waiting_message.delete()

def refresh_timers(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  waiting_message = update.message.reply_text('Hetkinen...')
  kotibobot.schedule.refresh_eq3_schedules()
  update.message.reply_text('Tehty!')
  waiting_message.delete()

def workday_cool(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  hour = 16
  time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
  if time < datetime.now():
    update.message.reply_text('Kello on jo yli {}, joten en tee mitään.'.format(str(hour)))
    return
  string = time.strftime("%y-%m-%d %H:%M")
  co = 'olkkari vacation {} 18'.format(string)
  kotibobot.command_queue.append(co)
  co = 'työkkäri vacation {} 20'.format(string)
  kotibobot.command_queue.append(co)
  
  update.message.reply_text('Tehty! Koti on viileä klo {} asti.'.format(str(hour)))
  
  co = 'olkkari vacation {} 18'.format(string)
  kotibobot.eq3.command_human(co)
  co = 'työkkäri vacation {} 20'.format(string)
  kotibobot.eq3.command_human(co)
  
  

'''def wake_on_lan(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  send_magic_packet(koodit['pöytäkone-mac'])
  update.message.reply_text('Tehty!')'''
  
def switchbot_push(update, context):
  return
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text(kotibobot.switchbot.press())

def ip(update, context): # shows public ip address
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text(kotibobot.requests_robust.get_public_ip())

def unmount_data(update, context):
  s = ['umount', '/dev/disk/by-id/wwn-0x5000c5009cce0f60-part1']
  res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 5)
  res_str = res.stdout.decode('utf-8')
  update.message.reply_text('Tulos:' + res_str)
  time.sleep(1)
  kotibobot.hs110.tyokkari_humidifier_command('off')
  kotibobot.hs110.tyokkari_humidifier_command('off')

def mount_data(update, context):
  kotibobot.hs110.tyokkari_humidifier_command('on')
  kotibobot.hs110.tyokkari_humidifier_command('on')
  time.sleep(20)
  s = ['mount', '/dev/disk/by-id/wwn-0x5000c5009cce0f60-part1']
  res = subprocess.run(s, stdout=subprocess.PIPE, timeout = 5)
  res_str = res.stdout.decode('utf-8')
  update.message.reply_text('Tulos:' + res_str)
'''
  if "Connection failed" in res_str or "ERROR" in res_str:
    #print('Yhteys pätki kerran')
    time.sleep(5)
    s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci0'] + string.split(' ')
    res = subprocess.run(s, stdout=subprocess.PIPE)
    res_str = res.stdout.decode('utf-8')
    if "Connection failed" in res_str or "ERROR" in res_str:
      #print('Yhteys pätki toisen kerran')
      time.sleep(5)
      s = ['/home/lowpaw/Downloads/eq3/eq3.exp', 'hci1'] + string.split(' ')
      res = subprocess.run(s, stdout=subprocess.PIPE)
      res_str = res.stdout.decode('utf-8')
  return res_str
'''

def main():
  # Create Updater object and attach dispatcher to it
  updater = Updater(koodit["kotibobot"])
  dispatcher = updater.dispatcher
  print("Kotibobot started")

  # Add command handler to dispatcher
  start_handler = CommandHandler('start', start)
  eq3_handler = CommandHandler('eq3', direct_eq3_command)
  mi_handler = CommandHandler('temp', mi_status)
  plot_handler = CommandHandler('kuvat', plot_data)
  command_olkkari_handler = CommandHandler('olkkari', olkkaricommand)
  command_tyokkari_handler = CommandHandler('tyokkari', tyokkaricommand)
  command_makkari_handler = CommandHandler('makkari', makkaricommand)
  data_handler = CommandHandler('data', data_command)
  command_queue_append_handler = CommandHandler('addtoqueue', command_queue_append)
  command_queue_print_handler = CommandHandler('printqueue', command_queue_print)
  command_queue_wipe_handler = CommandHandler('wipequeue', command_queue_wipe)
  #wake_on_lan_handler = CommandHandler('wakecomputer', wake_on_lan)
  timer_handler = CommandHandler('timer', timer_new)
  vahti_append_handler = CommandHandler('addtovahti', vahti_append)
  vahti_print_handler = CommandHandler('printvahti', vahti_print)
  vahti_wipe_handler = CommandHandler('wipevahti', vahti_wipe)
  #switchbot_handler = CommandHandler('cool', switchbot_push)
  ip_handler = CommandHandler('ip', ip)
  workday_handler = CommandHandler('workday', workday_cool)
  refresh_timers_handler = CommandHandler('refreshtimers', refresh_timers)
  mount_data_handler = CommandHandler('mount', mount_data)
  unmount_data_handler = CommandHandler('unmount', unmount_data)
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(mi_handler)
  dispatcher.add_handler(plot_handler)
  dispatcher.add_handler(command_olkkari_handler)
  dispatcher.add_handler(command_makkari_handler)
  dispatcher.add_handler(command_tyokkari_handler)
  dispatcher.add_handler(data_handler)
  dispatcher.add_handler(command_queue_append_handler)
  dispatcher.add_handler(command_queue_print_handler)
  dispatcher.add_handler(command_queue_wipe_handler)
  #dispatcher.add_handler(wake_on_lan_handler)
  dispatcher.add_handler(timer_handler)
  dispatcher.add_handler(vahti_append_handler)
  dispatcher.add_handler(vahti_print_handler)
  dispatcher.add_handler(vahti_wipe_handler)
  #dispatcher.add_handler(switchbot_handler)
  dispatcher.add_handler(ip_handler)
  dispatcher.add_handler(workday_handler)
  dispatcher.add_handler(refresh_timers_handler)
  dispatcher.add_handler(mount_data_handler)
  dispatcher.add_handler(unmount_data_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
