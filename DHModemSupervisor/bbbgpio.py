import os
from time import sleep


class GPIO(object):
    BOARD = 0
    IN = "in"
    OUT = "out"
    LOW = 0
    HIGH = 1
    WARNING = True

    def __init__(self):
        pass

    @classmethod
    def setmode(cls, mode):
        pass

    @classmethod
    def input(cls, pin):
        gpio = pin
        gpio_filename = '/sys/class/gpio/gpio{GPIO}/value'.format(GPIO=gpio)
        with open(gpio_filename, 'r') as f:
            read_data = f.read()
            value = int(read_data)
        return value

    @classmethod
    def output(cls, pin, state):
        gpio = pin
        cmd = "echo {VAL} > /sys/class/gpio/gpio{GPIO}/value".format(VAL=state, GPIO=gpio)
        os.system(cmd)

    @classmethod
    def setup(cls, pin, direction, initial=None):
        gpio = pin
        cmd = "echo {GPIO} >/sys/class/gpio/export > /dev/null 2>&1".format(GPIO=gpio)
        os.system(cmd)
        sleep(1)
        cmd = "echo {DIR} > /sys/class/gpio/gpio{GPIO}/direction > /dev/null 2>&1".format(DIR=direction, GPIO=gpio)
        os.system(cmd)

    @classmethod
    def cleanup(cls):
        pass

    @classmethod
    def setwarnings(cls, enable):
        cls.WARNING = enable
