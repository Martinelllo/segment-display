#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# sudo apt-get install screen 
# installiert screen, damit kann man sitzung auch nach SSH-Logoff weiterlaufen lassen

# (C) 2018 by Oliver Kuhlemann
# Bei Verwendung freue ich mich über Namensnennung,
# Quellenangabe und Verlinkung
# Quelle: http://cool-web.de/raspberry/


import re
import RPi.GPIO as GPIO      # Funktionen für die GPIO-Ansteuerung laden
from time import sleep       # damit müssen wir nur noch sleep() statt time.sleep schreiben
import time                  # die anderen time Funktionen müssen wir über vollen Namen ansprechen
from threading import Thread # ........

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
        self.__charset = {"":"", " ":"", ".":".", "0":"ABCDEF", "1":"BC", "2":"ABDEG", "3":"ABCDG", "4":"BCFG", "5":"ACDFG", 
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
                sleep (.001)
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
        length = len(sentence)
        self.say(sentence)
        sleep(1)
        i = 1
        while i < length:
            if sentence[i:][:1] == '.': i += 1
            self.say(sentence[i:])
            i += 1
            sleep(0.5)