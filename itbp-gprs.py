#!/usr/bin/env python

import os
import RPi.GPIO as GPIO
from time import sleep


POWER = 16
RESET = 18  # DON'T NEEDED!!! ==> RESET PIN IT IS NC...cross compatibility with c-uGSM, d-u3G...
STATUS = 12


def poweron():
    if not (getModemState()):
        print("try to wake h-nanoGSM")
        GPIO.output(POWER, GPIO.LOW)
        sleep(1)
        GPIO.output(POWER, GPIO.HIGH)
    sleep(5)
    # if GPIO.input(STATUS):
    if (getModemState()):
        print("h-nanoGSM is up")
    else:
        print("failure powering h-nanoGSM")
        exit(100)


def poweroff():
    # if GPIO.input(STATUS):
    if (getModemState()):
        print("try to shutdown h-nanoGSM")
        GPIO.output(POWER, GPIO.LOW)
        sleep(1)
        GPIO.output(POWER, GPIO.HIGH)
    sleep(8)
    # if not GPIO.input(STATUS):
    if not (getModemState()):
        print("h-nanoGSM is down")
    else:
        print("failure powering off h-nanoGSM")
        exit(100)


def restartModem():
    poweroff()
    sleep(3)
    poweron()

    def getModemState():
        return GPIO.input(STATUS)


def hwControlSetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)#RESET PIN IT IS NC...cross compatibility with c-uGSM
    except:
        GPIO.cleanup()  # free GPIO
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)#RESET PIN IT IS NC...cross compatibility with c-uGSM
    GPIO.setwarnings(True)