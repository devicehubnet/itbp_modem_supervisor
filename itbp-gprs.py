#!/usr/bin/env python
import os
import RPi.GPIO as GPIO
from time import sleep


POWER  = 16
RESET  = 18  # DON'T NEEDED!!! ==> RESET PIN IT IS NC...cross compatibility with c-uGSM, d-u3G...
STATUS = 12


def modem_status():
    return GPIO.input(STATUS)


def modem_power_on():
    if not modem_status():
        print("try to wake h-nanoGSM")
        GPIO.output(POWER, GPIO.LOW)
        sleep(1)
        GPIO.output(POWER, GPIO.HIGH)
    sleep(5)
    # if GPIO.input(STATUS):
    if modem_status():
        print("h-nanoGSM is up")
    else:
        print("failure powering h-nanoGSM")
        exit(100)


def modem_power_off():
    # if GPIO.input(STATUS):
    if modem_status():
        print("try to shutdown h-nanoGSM")
        GPIO.output(POWER, GPIO.LOW)
        sleep(1)
        GPIO.output(POWER, GPIO.HIGH)
    sleep(8)
    # if not GPIO.input(STATUS):
    if not modem_status():
        print("h-nanoGSM is down")
    else:
        print("failure powering off h-nanoGSM")
        exit(100)


def modem_restart():
    modem_power_off()
    sleep(3)
    modem_power_on()


def modem_hw_control_setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)#RESET PIN IT IS NC...cross compatibility with c-uGSM
    except Exception as e:
        print str(e)
        GPIO.cleanup()  # free GPIO
        GPIO.setup(STATUS, GPIO.IN)
        GPIO.setup(POWER, GPIO.OUT, initial=GPIO.HIGH)
    # GPIO.setup(RESET, GPIO.OUT, initial=GPIO.HIGH)#RESET PIN IT IS NC...cross compatibility with c-uGSM
    GPIO.setwarnings(True)


def modem_hw_control_release():
    GPIO.cleanup()  # free GPIO


def modem_supervisord():
    while True:
        sleep(1)

if __name__ == "__main__":
    modem_hw_control_setup()
    modem_power_on()
    modem_supervisord()
