from time import sleep
import sys
try:
    import RPi.GPIO as GPIO
except ImportError:
    import Adafruit_BBIO.GPIO as GPIO


class Modem(object):
    PIN_POWER_ENABLE = 49
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    TIMEOUT_POWER_ON = 8
    TIMEOUT_POWER_OFF_MAX = 30

    def __init__(self, pin_power=16, pin_reset=18, pin_status=12, pin_enable_power='P9_23'):
        self.PIN_POWER = pin_power
        self.PIN_RESET = pin_reset
        self.PIN_STATUS = pin_status
        self.PIN_POWER_ENABLE = pin_enable_power
        self.hw_control_setup()

    def __del__(self):
        self.hw_control_release()

    def log(self, args):
        print("MODEM: {ARGS}".format(ARGS=args))

    def status(self):
        return GPIO.input(self.PIN_STATUS)

    def power_btn_push(self, interval=2):
        GPIO.output(self.PIN_POWER, GPIO.HIGH)
        sleep(2)
        GPIO.output(self.PIN_POWER, GPIO.LOW)
        sleep(interval)
        GPIO.output(self.PIN_POWER, GPIO.HIGH)
        sleep(2)

    def power_on(self):
        GPIO.output(self.PIN_POWER_ENABLE, GPIO.LOW)
        sleep(1)

        if not self.status():
            delay = 0
            self.log("ATTEMPT TO POWER ON MODEM")
            self.power_btn_push(1)
            sys.stdout.write("MODEM: wait.")
            sys.stdout.flush()

            while not self.status() and delay < self.TIMEOUT_POWER_ON:
                sys.stdout.write(".")
                sys.stdout.flush()
                sleep(1)
                delay += 1

            print("done")

        if self.status():
            self.log("ON")
            return True
        else:
            self.log("FAILURE POWERING ON")
            return False

    def power_off(self):
        if self.status():
            delay = 0
            self.log("ATTEMPT TO POWER OFF MODEM")
            self.power_btn_push(1)
            sys.stdout.write("MODEM: wait.")
            sys.stdout.flush()

            while self.status() and delay < self.TIMEOUT_POWER_OFF_MAX:
               sys.stdout.write(".")
               sys.stdout.flush()
               sleep(1)
               delay += 1

            print("done")

        self.log("Disable power")
        GPIO.output(self.PIN_POWER_ENABLE, GPIO.HIGH)

        if not self.status():
            self.log("OFF")
            return True
        else:
            self.log("FAILURE POWERING OFF")
            return False

    def reset(self):
        self.power_off()
        sleep(5)
        self.power_on()
        sleep(5)  # Wait for modem to register in the network

    def hw_control_setup(self):
        print(self.PIN_STATUS, self.PIN_POWER, self.PIN_POWER_ENABLE)
        try:
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(self.PIN_POWER_ENABLE, GPIO.OUT, initial=GPIO.HIGH)
        except Exception as e:
            print("DHMSupervisord error setting up GPIOs:", str(e))
            GPIO.cleanup()  # free GPIO
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setwarnings(True)

    def hw_control_release(self):
        GPIO.cleanup()  # free GPIO
