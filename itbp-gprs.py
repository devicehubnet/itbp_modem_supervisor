#!/usr/bin/env python
import os
import sys
try:
     import RPi.GPIO as GPIO
except ImportError:
     class GPIO(object):
          BOARD=0
          IN="in"
          OUT="out"
          LOW=0
          HIGH=1
          WARNING=True

          def __init__(self):
               pass

          @classmethod
          def setmode(cls, mode):
               pass
          @classmethod
          def input(cls, pin):
               return 1

          @classmethod
          def output(cls, pin, state):
               gpio=pin
               cmd = "echo {VAL} > /sys/class/gpio/gpio{GPIO}/value".format(VAL=state, GPIO=gpio)
               print cmd
               os.system(cmd)

          @classmethod
          def setup(cls, pin, direction, initial=None):
               gpio=pin
               cmd = "echo {GPIO} >/sys/class/gpio/export".format(GPIO=gpio)
               print cmd
               os.system(cmd)
               sleep(1)
               cmd = "echo {DIR} > /sys/class/gpio/gpio{GPIO}/direction".format(DIR=direction, GPIO=gpio)
               print cmd
               os.system(cmd)

          @classmethod
          def cleanup(cls):
               pass

          @classmethod
          def setwarnings(cls, enable):
               cls.WARNING=enable


from time import sleep
import ConfigParser
from subprocess import Popen


class ITBPSupervisord(object):
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    INI_FILE = '/etc/devicehub/itbp-gprs.ini'

    APN = 'internet'
    ISP = 'isp'

    AUTO_CONNECT = False

    PPP_CONNECTED = False
    NET_CONNECTED = False

    def __init__(self):
        # Try to open the config file /etc/itbp-gprs.ini and populate settings
        try:
            config = ConfigParser.ConfigParser()
            config.read(self.INI_FILE)

            self.PIN_POWER  = config.getint('Modem', 'gpio_power')
            self.PIN_RESET  = config.getint('Modem', 'gpio_reset')
            self.PIN_STATUS = config.getint('Modem', 'gpio_status')

            # self.APN = config.get('Connection', 'apn', )
            self.ISP = config.get('Connection', 'isp')
            self.AUTO_CONNECT = config.getboolean('Connection', 'auto_connect')

            self.log("ISP: " + self.ISP)
            self.log("APN: " + self.APN)
            self.log("AUTO_CONNECT: " + str(self.AUTO_CONNECT))
        except Exception as e:
            self.log("config file init EXC: " + str(e))

        self.modem_hw_control_setup()

    def __del__(self):
        self.modem_hw_control_release()

    def log(self, args):
        print "ITBPSupervisord:", args

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
        # os.system("pon {ISP}".format(ISP=self.ISP))
        os.system("pppd call {ISP}".format(ISP=self.ISP))

    def ppp_disconnect(self):
        # os.system("poff {ISP}".format(ISP=self.ISP))
        os.system("killall -9 pppd")

    def ppp_status(self):
        try:
            for line in os.popen("/sbin/ip link show "):
                if 'ppp' in line:
                    return True
        except Exception as e:
            self.log(e)

        return False

    def net_status(self):
        p = Popen(["ping", "-c1", "openfleet.opendevlabs.com"])
        output = p.communicate()[0]
        if p.returncode == 0:
            self.log(output)
            return True
        else:
            return False

    def supervisord(self):
        self.log("Starting supervisor loop")
        while True:
            # do we have ppp up?
            ppp_state = self.ppp_status()
            net_state = self.net_status()
            print "PPP Status:", "UP" if ppp_state else "DOWN"
            print "NET Status:", "UP" if net_state else "DOWN"
            if net_state is False:
                print "Attempting to start PPP connection..."
                self.ppp_disconnect()
                self.modem_power_off()
                sleep(1)
                self.modem_power_on()
                self.ppp_connect()
            sleep(60 * 2)


if __name__ == "__main__":
    itbp_supervisord = ITBPSupervisord()

    if len(sys.argv)>1:
        cmd = sys.argv[1]
        if cmd == "start":
            itbp_supervisord.modem_power_on()
            sleep(5)
            itbp_supervisord.ppp_connect()
            itbp_supervisord.supervisord()
        elif cmd == "stop":
            itbp_supervisord.ppp_disconnect()
            itbp_supervisord.modem_power_off()
        elif cmd == "poweron":
            itbp_supervisord.modem_power_on()
        elif cmd == "poweroff":
            itbp_supervisord.modem_power_off()
        elif cmd == "powercycle":
            itbp_supervisord.modem_restart()
        else:
            print "itbp modem: Unknown command"
    else:
        itbp_supervisord.supervisord()
