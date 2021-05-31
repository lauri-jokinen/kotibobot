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
    res = "olet inessä"
  else:
    res = "et ole inessä"
  update.message.reply(res)

def start(update, context):
  text = "Hieno botti hermanni" + "\nhttps://github.com/Heckie75/eQ-3-radiator-thermostat"
  return update.message.reply_text(text)

def direct_eq3_command(update, context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.human_to_machine(str)
  for res in res_array:
    if len(res) > 2500:
      update.message.reply_text(res[0:2500])
    else:
      update.message.reply_text(res)
    
def time_series(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  selected_rooms = str.split(" ")[0].split("-")
  kotibobot.plot_ts(selected_rooms)
  #chat_id = update.message.chat.id
  context.bot.send_photo(chat_id=update.message.chat_id, photo=open('time_series.png', 'rb'))
  
def mi_status(update,context):
  str = update.message.text
  # Remove /-command
  str = " ".join(str.split(" ")[1:])
  res_array = kotibobot.read_mi(str)
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
  print("Bot started")

  # Add command handler to dispatcher
  start_handler = CommandHandler('start', start)
  eq3_handler = CommandHandler('eq3', direct_eq3_command)
  auth_handler = CommandHandler('authorize', authorize)
  ts_handler = CommandHandler('ts', time_series)
  mi_handler = CommandHandler('temp', mi_status)
  
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(eq3_handler)
  dispatcher.add_handler(auth_handler)
  dispatcher.add_handler(ts_handler)
  dispatcher.add_handler(mi_handler)

  # Start the bot
  updater.start_polling()

  # Run the bot until you press Ctrl-C
  updater.idle()

if __name__ == '__main__':
  main()
