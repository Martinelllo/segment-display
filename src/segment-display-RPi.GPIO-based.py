#!/usr/bin/env python3
# /etc/init.d/segment-clock.py
### BEGIN INIT INFO
# Provides:          segment-clock.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

# -*- encoding: utf-8 -*-

# (C) 2018 by Oliver Kuhlemann
# Bei Verwendung freue ich mich über Namensnennung,
# Quellenangabe und Verlinkung
# Quelle: http://cool-web.de/raspberry/

import datetime
from subprocess import PIPE, Popen
import requests
from time import sleep       # damit müssen wir nur noch sleep() statt time.sleep schreiben
from threading import Thread

import RPi.GPIO as GPIO      # Funktionen für die GPIO-Ansteuerung laden

class Display:

    def __init__(self, pinData, pinClockStore, pinClockShift, digits):

        GPIO.setmode(GPIO.BCM)       # die GPIO-Pins im BCM-Modus ansprechen

        self.__digits=digits           # Steuerleitung für die vier 7-Segment-Anzeigen     

        self.__pinData=pinData         # Steuerleitungen für den HC595
        self.__pinClockStore=pinClockStore
        self.__pinClockShift=pinClockShift
                                     
        GPIO.setup(self.__pinData, GPIO.OUT)
        GPIO.setup(self.__pinClockStore, GPIO.OUT)
        GPIO.setup(self.__pinClockShift, GPIO.OUT)

        for digit in digits:
            GPIO.setup(digit, GPIO.OUT)

        # Dictionary: welche Ziffer/Buchstabe -> welche Segmente sind an
        self.__charset = {"":"", " ":"", ".":".", "-":"G", "0":"ABCDEF", "1":"BC", "2":"ABDEG", "3":"ABCDG", "4":"BCFG", "5":"ACDFG", 
        "6":"ACDEFG", "7":"ABC", "8":"ABCDEFG", "9":"ABCDFG", "A":"ABCEFG", "B":"CDEFG", "C":"ADEF", 
        "D":"BCDEG", "E":"ADEFG", "F":"AEFG", "G":"ACDEF", "H":"BCEFG", "I":"AE", "J":"ACD", "K":"ACEFG", 
        "L":"DEF", "M":"ACEG", "N":"ABCEF", "O":"CDEG", "P":"ABEFG", "Q":"ABCFG", "R":"EG", "S":"ACDF",
        "T":"DEFG", "U":"BCDEF", "V":"BEFG", "W":"BDFG", "X":"CE", "Y":"BCDFG", "Z":"ABDE", "°":"ABGF"}

        self._buffer = [" "]*len(self.__digits)

        # self.cycleTime=self.__measureCycleTime()
        
        self.__run = True
        t = Thread(target=self.__loop)
        t.start()

    def __del__(self):
        GPIO.cleanup()

    def __storeTick(self):
        """einen Puls auf die ClockStore-Leitung schicken"""
        GPIO.output(self.__pinClockStore, GPIO.HIGH)
        sleep(.000001)
        GPIO.output(self.__pinClockStore, GPIO.LOW)
        sleep(.000001)


    def __shiftTick(self):
        """Nächstes Bit"""
        GPIO.output(self.__pinClockShift, GPIO.HIGH)
        sleep(.000001)
        GPIO.output(self.__pinClockShift, GPIO.LOW)
        sleep(.000001)
            

    def __readBuffer(self, segments):
        """schaltet die outputs im schiftregister"""
        for seg in ".GFEDCBA": # angeschaltete Segmente vom höchstwertigen Bit abwärts pulsen 
            if segments.find(seg) > -1:
                GPIO.output(self.__pinData, GPIO.LOW)
            else:
                GPIO.output(self.__pinData, GPIO.HIGH)
            self.__shiftTick()
        self.__storeTick()

    
    
    def __loop(self):
        while self.__run:
            for i in range(len(self.__digits)):
                self.__readBuffer(self._buffer[i])
                GPIO.output(self.__digits[i], GPIO.HIGH)
                sleep (.002)
                GPIO.output(self.__digits[i], GPIO.LOW)

    def draw(self, digit, segments):
        """Overwrites the digit. interprets the following chars .GFEDCBA"""
        self._buffer[digit] = segments

    def clear(self):
        self._buffer = ['']*len(self.__digits)

    def setChar(self, digit, char, point=None):
        """das übergebene Zeichen muss eine Zahl oder Buchstabe sein"""
        # segmente für char suchen
        try:
            segment = self.__charset[char]
        except KeyError:
            print("Das Zeichen " + char + " ist nicht definiert.")
            return
        if point:
            segment += '.'
        self._buffer[digit] = segment
    
    def say(self, word:str):
        word = word.upper()
        maxLen = len(self.__digits)
        for i in range(maxLen):
            saveChar = word[i] if len(word) > i else ' '
            self.setChar(i, saveChar)
            if len(word) > i+1 and word[i+1] == '.':
                self._buffer[i] += '.'
                word = word.replace('.','',1)
                maxLen -= 1

    def sayScroll(self, sentence:str):
        maxLen = len(self.__digits)
        sentence = (" " * (maxLen-1)) + sentence
        length = len(sentence)
        i = 0
        while i < length:
            if sentence[i:][:1] == '.': i += 1
            self.say(sentence[i:])
            i += 1
            sleep(0.5)
        self.clear()
        sleep(0.5)

    def showAnimation(self):
        seq = [
            [0,"A"],[1,"A"],[2,"A"],[3,"A"],[3,"B"],[3,"C"],
            [3,"D"],[2,"D"],[1,"D"],[0,"D"],[0,"E"],[0,"F"]
        ]
        for s in seq:
            self.draw(s[0],s[1])
            sleep(.1)
            self.clear()

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
        return 'offline'

# get display pi 3 and 4
display = Display(24, 25, 8, [21,20,16,12])


if __name__ == '__main__':

    from queue import Queue

    que = Queue() # neaded to grap the return value of a Thread

    answere = None

    print('programm start')

    # check cloud
    cloudThread = Thread(target=lambda q: q.put(checkNextcloudOnline()), args=(que,))
    cloudThread.start()

    try:

        while True:

            # print('loop begins')

            for i in range(3):
                # Zeit anzeigen
                ts = datetime.datetime.now()
                for i in range (8):
                    display.say(ts.strftime("%H.%M"))
                    sleep(.5)
                    display.say(ts.strftime("%H%M"))
                    sleep(.5)

                # zwischendrin auch mal das Datum
                datum = ts.strftime("%d-%m-%Y")
                display.sayScroll(datum)

            # # CPU-Temperatur anzeigen
            # temp=str(getCpuTemp())
            # display.say(temp + "°C")
            # sleep(5)

            for i in range(3):
                display.showAnimation()

            # check cloud
            if not cloudThread.is_alive():
                cloudThread.join()
                answere = que.get()
                cloudThread = Thread(target=lambda q: q.put(checkNextcloudOnline()), args=(que,))
                cloudThread.start()

            if answere:
                display.sayScroll('cloud ' + answere)
                # print('cloud ' + answere)
            

    except KeyboardInterrupt:    # wenn in der Konsole CTRL+C gedrückt, Schleife beenden
        display.say ("C1A0")
        exit()
    

print('programm stoppt')
exit()
