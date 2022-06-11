#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import datetime
from display import Display
from subprocess import PIPE, Popen
import requests
from time import sleep       # damit müssen wir nur noch sleep() statt time.sleep schreiben
from threading import Thread

# get display
display = Display(24, 23, 18, [9,17,27,22,10])

def getCpuTemp():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    output = str(output)
    return float(output[ output.index('=')+1 : output.rindex("'") ])


def checkNextcloudOnline():
    try:
        headers = {'Content-Type': 'application/json; charset=utf-8', 'NC-Token': 'B0denSee'}
        response = requests.get(url="https://martinhellmann.hopto.org/ocs/v2.php/apps/serverinfo/api/v1/info?format=json", timeout=20, headers=headers)
        return response.json()['ocs']['meta']['status']
    except Exception:
        return 'no responce'

def animation():
    seq = [
        [0,"A"],[1,"A"],[2,"A"],[3,"A"],[4,"A"],[4,"B"],[4,"C"],
        [4,"D"],[3,"D"],[2,"D"],[1,"D"],[0,"D"],[0,"E"],[0,"F"]
    ]

    for s in seq:
        display.draw(s[0],s[1])
        sleep(.1)
        display.clear()


if __name__ == '__main__':

    from queue import Queue

    que = Queue()

    try:

        while True:

            display.say('Hallo')
            sleep(2)
            display.clear()

            # Zeit anzeigen
            ts = datetime.datetime.now()
            for i in range (0,6):
                display.say(ts.strftime("%H.%M"))
                sleep(.5)
                display.say(ts.strftime("%H%M"))
                sleep(.5)

            # zwischendrin auch mal das Datum
            datum = ts.strftime("%d-%m-%Y")
            display.sayScroll(datum)

            # CPU-Temperatur anzeigen
            temp=str(getCpuTemp())
            display.say(temp + "°C")
            sleep(5)

            x = Thread(target=lambda q: q.put(checkNextcloudOnline()), args=(que,))
            x.start()
            while x.is_alive():
                display.sayScroll('Loading')
                for i in range(5):
                    animation()

            x.join()

            answere = que.get()
            display.sayScroll('cloud ' + answere)
            

    except KeyboardInterrupt:    # wenn in der Konsole CTRL+C gedrückt, Schleife beenden
        display.say ("C1A0")

