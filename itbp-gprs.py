#!/usr/bin/env python
import os
import sys
import RPi.GPIO as GPIO
from time import sleep
import ConfigParser


class ITBPSupervisord(object):
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    INI_FILE = '/etc/itbp-gprs.ini'

    def __init__(self):
        # Try to open the config file /etc/itbp-gprs.ini and populate settings
        try:
            config = ConfigParser.ConfigParser()
            config.read(self.INI_FILE)
        except Exception as e:
            print "ITBPSupervisord config file init EXC:", e

    def log(self, *kwargs):
        print "ITBPSupervisord:", kwargs

    def modem_status(self):
        return GPIO.input(self.PIN_STATUS)

    def modem_power_on(self):
        if not self.modem_status():
            self.log("try to wake h-nanoGSM")
            GPIO.output(self.PIN_POWER, GPIO.LOW)
            sleep(1)
            GPIO.output(self.PIN_POWER, GPIO.HIGH)
        sleep(5)

        if self.modem_status():
            self.log("h-nanoGSM is up")
        else:
            self.log("failure powering on h-nanoGSM")

    def modem_power_off(self):
        # if GPIO.input(STATUS):
        if self.modem_status():
            print("itbp modem: try to shutdown h-nanoGSM")
            GPIO.output(self.PIN_POWER, GPIO.LOW)
            sleep(1)
            GPIO.output(self.PIN_POWER, GPIO.HIGH)
        sleep(8)

        if not self.modem_status():
            print("itbp modem: h-nanoGSM is down")
        else:
            print("itbp modem: failure powering off h-nanoGSM")

    def modem_restart(self):
        self.modem_power_off()
        sleep(3)
        self.modem_power_on()

    def modem_hw_control_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        try:
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
        except Exception as e:
            print str(e)
            GPIO.cleanup()  # free GPIO
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setwarnings(True)

    def modem_hw_control_release(self):
        GPIO.cleanup()  # free GPIO

    def ppp_connect(self):
        pass

    def ppp_disconnect(self):
        pass

    def ppp_status(self):
        pass

    def supervisord(self):
        while True:
            # do we have ppp up?

            sleep(1)


if __name__ == "__main__":
    itbp_supervisord = ITBPSupervisord()

    if len(sys.argv):
        cmd = sys.argv[1]
        if cmd == "start":
            itbp_supervisord.modem_hw_control_setup()
            itbp_supervisord.modem_power_on()
            sleep(5)
            itbp_supervisord.ppp_connect()
            itbp_supervisord.supervisord()
        elif cmd == "stop":
            itbp_supervisord.ppp_disconnect()
            itbp_supervisord.modem_hw_control_setup()
            itbp_supervisord.modem_power_off()
            itbp_supervisord.modem_hw_control_release()
        elif cmd == "poweron":
            itbp_supervisord.modem_hw_control_setup()
            itbp_supervisord.modem_power_on()
            itbp_supervisord.modem_hw_control_release()
        elif cmd == "poweroff":
            itbp_supervisord.modem_hw_control_setup()
            itbp_supervisord.modem_power_off()
            itbp_supervisord.modem_hw_control_release()
        elif cmd == "powercycle":
            itbp_supervisord.modem_hw_control_setup()
            itbp_supervisord.modem_restart()
            itbp_supervisord.modem_hw_control_release()
        else:
            print "itbp modem: Unknown command"
    else:
        itbp_supervisord.supervisord()
