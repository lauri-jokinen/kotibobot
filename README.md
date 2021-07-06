# kotibobot
With a Telegram bot, and a computer with Bluetooth, we can control Eqiva eQ-3 radiator thermostats, and read Xiaomi Mi -temperature and humidity sensors. I use this repository to build my smart home, and I plan to connect new devices to it along the way.

With these scripts you...
* can read and control the temperature of your house anywhere on the planet via a Telegrambot.
* can program a weekly temperature schdule for each room.
* can plot a graph of the temperature history, and other data as well. These plots can be seen via the Telegrambot.
* get an email when any of the devices has a low battery.

Contact me if you are interested to build your own system! The code is not very readable, and I can probably give you a few good tips.

This project relies on these repositories. All thanks go to their brilliant authors!
* https://github.com/Heckie75/eQ-3-radiator-thermostat
* https://github.com/JsBergbau/MiTemperature2

The repository consists of...
* Function package (kotibobot_functions.py).
* Telegram bot (telegrambot.py).
* A script (collect_data.py) which collects and stores time series data from the system.
* A script (sys_check.py) that sends an email if any device has low battery.
