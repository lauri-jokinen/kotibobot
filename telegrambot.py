from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import kotibobot_functions as kotibobot
from datetime import datetime

image_links = """<a href='https://cloud.laurijokinen.com/kotibobot/kotibobot_target_temp.png'>Lämpötila 48h</a>
<a href='https://cloud.laurijokinen.com/kotibobot/kotibobot_offset.png'>Lämpötilan virhe 48h</a>
<a href='https://cloud.laurijokinen.com/kotibobot/kotibobot_temp.png'>Lämpötila, 3 viimeistä päivää päällekkäin</a>
<a href='https://cloud.laurijokinen.com/kotibobot/kotibobot_humidity.png'>Kosteus, 3 viimeistä päivää päällekkäin</a>"""

def showifemptystring(s):
  if s == '':
    return 'Empty output'
  else:
    return s

def get_chat_id(update, context):
  chat_id = -1

  if update.message is not None:
    # from a text message
    chat_id = update.message.chat.id
  elif update.callback_query is not None:
    # from a callback message
    chat_id = update.callback_query.message.chat.id

  return chat_id

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

def remove_spaces_from_front(text):
  if text == "":
    return text
  while text[0] == " ":
    text = text[1:]
    if text == "":
      return text
  return text
  
def authorized(update, context):
  return update.message.from_user.id in koodit["lowpaw_teleID"]

def start(update, context):
  text = """Komento '/makkari' antaa tämänhetkisen statuksen ja ajastusasetukset makkarissa.

Muutamia sääntöjä komentojen formaattiin liittyen
 • Desimaalierotin on piste
 • Kellonajassa täytetään alkuun nolla tarvittaessa, esim. 09:30.
 • Päivämäärä on muodossa vuosi-kk-pvä. Vuosiluvussa annetaan kaksi viimeistä numeroa, ja ylläolevat nollasäännöt pitävät tässäkin, esim. 21-06-31.
 • Komennoissa annettavat lämpötilat tulee olla pyöristetty puolen asteen tarkkuudelle.
 • Kellonajat tulee pyöristää joko puolen tunnin tarkkuudelle (vacation), tai kymmenen minuutin tarkkuudelle (timer).

Moodit ja komennot niiden aktivointiin:

 • '/makkari auto' - automaattinen, eli lämpötilat ajastuksen mukaan
 • '/makkari man' - manuaalinen lämpötila
 • '/makkari boost' - avaa venttiilin kokonaan viideksi minuutiksi. Asetuksen saa pois komennolla 'boost off', tai valitsemalla jonkin toisen moodin.
 • '/makkari vacation 21-06-31 12:30 21.5' - lomatila. Eli pitää asetetun lämpötilan annettuun ajankohtaan asti. Komennossa on asetuksen loppumispäivämäärä ja -aika sekä lämpötila. Kellonaika tulee olla pyöristetty puolen tunnin tarkkuudelle, ja lämpötila puolen asteen tarkkuudelle. Asetuksen saa pois valitsemalla toisen moodin.

Muita komentoja

'/makkari temp 18.5' - asettaa lämpötilaksi 18.5 °C. Kun päällä on automaattitila, asetettu lämpötila pysyy voimassa seuraavaan ajastettuun lämpötilan vaihdokseen asti. Lomatilassa komento asettaa loma-ajan lämpötilan. Lämpötila täytyy olla pyöristetty puolen asteen tarkkuudelle.

'/makkari timer mon 21 10:00 19 24:00' - asettaa maanantaille seuraavan ajastuksen:
00:00-10:00  -  21 °C
10:00-24:00  -  19 °C.
Komennon viikonpäivän tai -päivät voi valita seuraavasti:
mon, tue, wed, thu, fri, sat, sun, work, weekend, everyday, today, tomorrow.
Ajastusosa (viikonpäivän jälkeen) alkaa aina lämpötilalla ja päättyy kellonaikaan '24:00'.
Kellonaika tulee olla pyöristetty kymmenen minuutin tarkkuudelle ja lämpötila puolen asteen tarkkuudelle. Automaattiasetus noudattaa tätä ajastusta.

'timer-settings' antaa ajastusasetukset ylläolevan komennon mukaisesti helpompaa muokkausta varten. Tämä komento ei aina toimi, koska bugit toisten koodeissa..."""
  return update.message.reply_text(text)

def direct_eq3_command(update, context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.eq3_command_human(str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

def makkaricommand(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('makkari status')
    res_array = res_array + kotibobot.mi_read_human('makkari')
  else:
    res_array = kotibobot.eq3_command_human('makkari ' + str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
      
def tyokkaricommand(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('työkkäri status')
    res_array = res_array + kotibobot.mi_read_human('työkkäri')
  else:
    res_array = kotibobot.eq3_command_human('työkkäri ' + str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
      
def olkkaricommand(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('olkkari status')
    res_array = res_array + kotibobot.mi_read_human('olkkari')
  else:
    res_array = kotibobot.eq3_command_human('olkkari ' + str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

def plot_makkari(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  #str = update.message.text
  # Remove /-command
  #str = " ".join(str.split(" ")[1:])
  #selected_rooms = str.split(" ")[0].split("-")
  data = kotibobot.load_ts_data()
  selected_rooms = ['makkari']
  kotibobot.plot_temp_48(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  update.message.reply_text(image_links, parse_mode='HTML')
  
def plot_olkkari(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text(kotibobot.plot_main_function(), parse_mode='HTML')
  
def plot_olkkari2(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  selected_rooms = ['olkkari']
  data = kotibobot.load_ts_data()
  kotibobot.plot_temp_48(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms, data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  update.message.reply_text(image_links, parse_mode='HTML')
  
def plot_tyokkari(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  selected_rooms = ['työkkäri']
  data = kotibobot.load_ts_data()
  kotibobot.plot_temp_48(selected_rooms,data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms,data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms,data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms,data)
  #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  update.message.reply_text(image_links, parse_mode='HTML')

def mi_status(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.mi_read_human(str)
  if len(res_array) > 20:
    res_array = res_array[0:18]
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
  

def main():
  # Create Updater object and attach dispatcher to it
  updater = Updater(koodit["kotibobot"])
  dispatcher = updater.dispatcher
  print("Kotibobot started")

  # Add command handler to dispatcher
  start_handler = CommandHandler('start', start)
  eq3_handler = CommandHandler('eq3', direct_eq3_command)
  mi_handler = CommandHandler('temp', mi_status)
  plot_olkkari_handler = CommandHandler('kuvaolkkari', plot_olkkari)
  plot_tyokkari_handler = CommandHandler('kuvatyokkari', plot_tyokkari)
  plot_makkari_handler = CommandHandler('kuvamakkari', plot_makkari)
  command_olkkari_handler = CommandHandler('olkkari', olkkaricommand)
  command_tyokkari_handler = CommandHandler('tyokkari', tyokkaricommand)
  command_makkari_handler = CommandHandler('makkari', makkaricommand)
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(mi_handler)
  dispatcher.add_handler(plot_olkkari_handler)
  dispatcher.add_handler(plot_makkari_handler)
  dispatcher.add_handler(plot_tyokkari_handler)
  dispatcher.add_handler(command_olkkari_handler)
  dispatcher.add_handler(command_makkari_handler)
  dispatcher.add_handler(command_tyokkari_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
