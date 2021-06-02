from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json
import kotibobot_functions as kotibobot
from datetime import datetime

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
  
def authorize(update, context):
  id = update.message.id
  if id in koodit["lowpaw-teleIDt"]:
    update.message.reply("olet inessä")
  else:
    update.message.reply("et ole inessä")

def start(update, context):
  text = "Hieno botti hermanni"
  return update.message.reply_text(text)

def direct_eq3_command(update, context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.eq3_command_human(str)
  for res in res_array:
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

def makkaricommand(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('makkari status')
    res_array = res_array + kotibobot.mi_read_human('makkari')
  else:
    res_array = kotibobot.eq3_command_human('makkari ' + str)
  for res in res_array:
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
      
def tyokkaricommand(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('työkkäri status')
    res_array = res_array + kotibobot.mi_read_human('työkkäri')
  else:
    res_array = kotibobot.eq3_command_human('työkkäri ' + str)
  for res in res_array:
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
      
def olkkaricommand(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  if str == "":
    res_array = kotibobot.eq3_command_human('olkkari status')
    res_array = res_array + kotibobot.mi_read_human('olkkari')
  else:
    res_array = kotibobot.eq3_command_human('olkkari ' + str)
  for res in res_array:
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)

def plot_makkari(update,context):
  #str = update.message.text
  # Remove /-command
  #str = " ".join(str.split(" ")[1:])
  #selected_rooms = str.split(" ")[0].split("-")
  selected_rooms = ['makkari']
  kotibobot.plot_temp_48(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  
def plot_olkkari(update,context):
  selected_rooms = ['olkkari']
  kotibobot.plot_temp_48(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  
def plot_tyokkari(update,context):
  selected_rooms = ['työkkäri']
  kotibobot.plot_temp_48(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_offset(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_temp_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  kotibobot.plot_humidity_days(selected_rooms)
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))

def mi_status(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.mi_read_human(str)
  if len(res_array) > 20:
    res_array = res_array[0:18]
  for res in res_array:
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
  auth_handler = CommandHandler('authorize', authorize)
  mi_handler = CommandHandler('temp', mi_status)
  plot_olkkari_handler = CommandHandler('kuvaolkkari', plot_olkkari)
  plot_tyokkari_handler = CommandHandler('kuvatyokkari', plot_tyokkari)
  plot_makkari_handler = CommandHandler('kuvamakkari', plot_makkari)
  command_olkkari_handler = CommandHandler('olkkari', olkkaricommand)
  command_tyokkari_handler = CommandHandler('tyokkari', tyokkaricommand)
  command_makkari_handler = CommandHandler('makkari', makkaricommand)
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(auth_handler)
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
