#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import datetime
from display import Display
from subprocess import PIPE, Popen
import requests
from time import sleep       # damit müssen wir nur noch sleep() statt time.sleep schreiben
from threading import Thread
import json
import os

# get display
display = Display(24, 23, 18, [9,17,27,22,10])

# get file Path
filePath = os.path.abspath(os.getcwd())

# Opening JSON file
f = open(filePath+'/data.json')
data = json.load(f)
print(data)

def getCpuTemp():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])


def checkNextcloudOnline():
    try:
        headers = {'Content-Type': 'application/json; charset=utf-8', 'NC-Token': 'B0denSee'}
        response = requests.get(url="https://martinhellmann.hopto.org/ocs/v2.php/apps/serverinfo/api/v1/info?format=json", timeout=20, headers=headers)
        return response.json()['ocs']['meta']['status']
    except Exception:
        return 'no responce'

def animation(key:str):
    seq = data['sequences'][key]
    for s in seq:
        display.draw(s[0],s[1])
        sleep(.1)
        display.clear()

try:

    while True:
        for i in range(2):
            animation('round')

        display.say('Hallo')
        sleep(2)
        display.clear()

        # # Digits Demo
        # for i in range(2):
        #     for i in range(5):
        #         display.setChar(i,str(i))
        #         sleep(.5)
        #         display.setChar(i,'')

        # Zeit anzeigen
        ts = datetime.datetime.now()
        for i in range (0,6):
            display.say(ts.strftime("%H.%M"))
            sleep(.5)
            display.say(ts.strftime("%H%M"))
            sleep(.5)

        # zwischendrin auch mal das Datum
        datum = ts.strftime("%d.%m.%Y")
        display.sayScroll(datum)

        # zwischendrin CPU-Temperatur anzeigen
        # t=str(getCpuTemp())
        # # print (t)
        # temp = t[0]+t[1]+t[3] + "°"
        # say(temp,3,"1")

        x = Thread(target=checkNextcloudOnline)
        x.start()
        while x.is_alive():
            display.sayScroll('Loading')
            for i in range(5):
                animation('eight')

        answere = x.join()
        print(answere)
        display.sayScroll('cloud ' + answere)
        

except KeyboardInterrupt:    # wenn in der Konsole CTRL+C gedrückt, Schleife beenden
    display.say ("C1A0")

