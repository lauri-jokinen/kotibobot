import requests, urllib.parse, json
from requests.adapters import HTTPAdapter, Retry

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
  koodit = json.load(json_file)

def telegram_message(message):
  chat_id_lapa = koodit['lowpaw_teleID'][0]
  url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(koodit["L-bot"], chat_id_lapa, urllib.parse.quote(message))
  return json.loads(get_url(url).text)['result']['message_id']

def delete_telegram_message(message_id):
  chat_id_lapa = koodit['lowpaw_teleID'][0]
  url = 'https://api.telegram.org/bot{}/deleteMessage?chat_id={}&message_id={}'.format(koodit["L-bot"], chat_id_lapa, message_id)
  return get_url(url)

# https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request

def get_url(url,headers={}):
  s = requests.Session()
  retries = Retry(total=10,
                  backoff_factor=0.5,
                  status_forcelist=[ 500, 502, 503, 504 ])
  s.mount('http://', HTTPAdapter(max_retries=retries))
  s.headers.update(headers)
  return s.get(url)
