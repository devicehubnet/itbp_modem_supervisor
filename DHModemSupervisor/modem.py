from time import sleep
import sys
try:
    import RPi.GPIO as GPIO
except ImportError:
    from .bbbgpio import GPIO


class Modem(object):
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    TIMEOUT_POWER_ON = 8
    TIMEOUT_POWER_OFF_MAX = 100

    def __init__(self):
        self.modem_hw_control_setup(pin_power=16, pin_reset=18, pin_status=12)

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
            delay = 0
            print("itbp modem: try to shutdown h-nanoGSM")
            GPIO.output(self.PIN_POWER, GPIO.LOW)
            sleep(1)
            GPIO.output(self.PIN_POWER, GPIO.HIGH)

            sys.stdout.write("itbp modem: wait.")
            sys.stdout.flush()

            while self.modem_status() and delay < self.TIMEOUT_POWER_OFF_MAX:
               sys.stdout.write(".")
               sys.stdout.flush()
               sleep(1)
               delay += 1

            print "done"

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
