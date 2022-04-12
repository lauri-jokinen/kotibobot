import subprocess # ubuntu bash


fo = open('/home/lowpaw/Downloads/kotibobot/vahti.txt', 'r')
commands = fo.read()
fo.close()
commands = commands.split('\n')
for command in commands:
  if not command == '':
    s = ['/usr/bin/python3', '/home/lowpaw/Downloads/vahti/vahti.py', '--parser', 'tori', '--query', command, '--email', 'lateus96@gmail.com']
    res = subprocess.run(s, stdout=subprocess.PIPE)
'''
/usr/bin/python3 /home/lowpaw/Downloads/vahti/vahti.py --parser tori --query "orfjall TAI örfjall TAI örfjäll TAI orfjäll" --email lateus96@gmail.com
'''
