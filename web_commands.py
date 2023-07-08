# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

from datetime import datetime, timedelta
import dateutil.parser # parse ISO
import json
import requests
import kotibobot

with open("/home/lowpaw/Downloads/telegram-koodeja.json") as json_file:
    koodit = json.load(json_file)

commands = {
'cool-1h':['olkkari vacation {1} 15', 'työkkäri vacation {1} 15'],
'cool-2h':['olkkari vacation {2} 15', 'työkkäri vacation {2} 15'],
'auto':['olkkari auto', 'työkkäri auto', 'makkari auto']
}

def hours_from_now_rounded(h):
  time = datetime.now() + timedelta(hours = h)
  rounded = time + (datetime.min - time + timedelta(minutes = 15)) % timedelta(minutes=30) - timedelta(minutes = 15)
  string = rounded.strftime("%y-%m-%d %H:%M")
  return string

def replace_hours_with_time(string):
  s = string.split('{1}')
  if len(s) == 2:
    return "".join([s[0], hours_from_now_rounded(1), s[1]])
  
  s = string.split('{2}')
  if len(s) == 2:
    return "".join([s[0], hours_from_now_rounded(2), s[1]])
  
  return string

hostName = "0.0.0.0" # works in local LAN
serverPort = 8765


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        if self.path != '/favicon.ico':
          com = ''.join(self.path.split('/')) # e.g. "auto"
          command_array = commands[com] # 'commands' is defined above
          
          for c in command_array:
            co = replace_hours_with_time(c)
            kotibobot.command_queue.append(co)
          
          if com != 'auto':
            kotibobot.hs110.ufox_command('off')
            kotibobot.hs110.tyokkari_humidifier_command('off')
          
          for c in command_array:
            co = replace_hours_with_time(c)
            res = kotibobot.eq3.command_human(co)
        print("commands done'd")

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
