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

    def __init__(self, pin_power=16, pin_reset=18, pin_status=12):
        self.PIN_POWER = pin_power
        self.PIN_RESET = pin_reset
        self.PIN_STATUS = pin_status
        self.hw_control_setup()

    def __del__(self):
        self.modem_hw_control_release()

    def log(self, args):
        print("ITBPSupervisord:", args)

    def status(self):
        return GPIO.input(self.PIN_STATUS)

    def power_on(self):
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

    def power_off(self):
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

            print("done")

        if not self.modem_status():
            print("itbp modem: h-nanoGSM is down")
        else:
            print("itbp modem: failure powering off h-nanoGSM")

    def reset(self):
        self.power_off()
        sleep(3)
        self.power_on()

    def hw_control_setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        try:
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
        except Exception as e:
            print(str(e))
            GPIO.cleanup()  # free GPIO
            GPIO.setup(self.PIN_STATUS, GPIO.IN)
            GPIO.setup(self.PIN_POWER, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setwarnings(True)

    def hw_control_release(self):
        GPIO.cleanup()  # free GPIO
