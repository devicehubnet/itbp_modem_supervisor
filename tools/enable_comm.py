#!/usr/bin/python
from time import sleep

import Adafruit_BBIO.UART as UART
import Adafruit_BBIO.GPIO as GPIO

MODEM_ONOFF  = 'P8_12'
MODEM_POWER  = 'P9_23'
MODEM_STATUS = 'P8_11'


def enable_gsm_modem():
    GPIO.setup(MODEM_POWER, GPIO.OUT)
    GPIO.setup(MODEM_ONOFF, GPIO.OUT)
    GPIO.setup(MODEM_STATUS, GPIO.IN)

    GPIO.output(MODEM_POWER, GPIO.HIGH)
    GPIO.output(MODEM_ONOFF, GPIO.HIGH)
    sleep(2)
    GPIO.output(MODEM_ONOFF, GPIO.LOW)
    sleep(1.5)
    GPIO.output(MODEM_ONOFF, GPIO.HIGH)


enable_gsm_modem()

UART.setup('UART1')

