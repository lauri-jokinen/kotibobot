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
  update.message.reply_text("Yhdistetään laitteisiin...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes /-command
  res_array = kotibobot.eq3_command_human(str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

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
  update.message.reply_text("Yhdistetään laitteisiin...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  if str == "":
    res_array = kotibobot.eq3_command_human(room + ' status')
    res_array = res_array + kotibobot.mi_read_human(room)
  else:
    res_array = kotibobot.eq3_command_human(room + ' ' + str)
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

def plot_data(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text("Piirretään kuvia...")
  update.message.reply_text(kotibobot.plot_main_function(), parse_mode='HTML')

def mi_status(update,context):
  if not authorized(update, context):
    update.message.reply_text("You are not authorized.")
    return
  update.message.reply_text("Yhdistetään laitteeseen...")
  str = update.message.text
  str = " ".join(str.split(" ")[1:]) # Removes the /-command
  res_array = kotibobot.mi_read_human(str)
  if len(res_array) > 20:
    res_array = res_array[0:18]
  for res in res_array:
    res = showifemptystring(res)
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
  
def data_command(update, context):
  update.message.reply_text(kotibobot.read_latest_data())

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
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(mi_handler)
  dispatcher.add_handler(plot_handler)
  dispatcher.add_handler(command_olkkari_handler)
  dispatcher.add_handler(command_makkari_handler)
  dispatcher.add_handler(command_tyokkari_handler)
  dispatcher.add_handler(data_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
