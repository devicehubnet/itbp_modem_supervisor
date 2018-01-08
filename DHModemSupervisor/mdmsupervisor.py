from transitions import Machine
from .modem import Modem
from time import sleep
import ConfigParser
import os
from subprocess import Popen


class ModemSupervisor(Machine):
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    INI_FILE = '/etc/devicehub/itbp-gprs.ini'

    APN = 'internet'
    ISP = 'isp'

    AUTO_CONNECT = False

    PPP_CONNECTED = False
    NET_CONNECTED = False

    states = ['internet_disconnected', 'internet_connected', 'modem_reset']
    modem = None

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

        Machine.__init__(self, states=self.states, initial='internet_disconnected')
        self.add_transition('disconnecting', 'internet_connected', 'internet_disconnected')
        self.add_transition('connecting', 'internet_disconnected', 'internet_connected')
        self.add_transition('hw_reset', 'internet_disconnected', 'modem_reset')
        self.add_transition('finished_hw_reset', 'modem_reset', 'internet_disconnected')

        self.setup_platform()

    def log(self, args):
        print("ITBPSupervisord:", args)

    def setup_platform(self):
        self.modem = Modem(self.PIN_POWER, self.PIN_RESET, self.PIN_STATUS)

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
        p = Popen(["ping", "-c1", "mail.google.com"])
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
            print("PPP Status:", "UP" if ppp_state else "DOWN")
            print("NET Status:", "UP" if net_state else "DOWN")
            if net_state is False:
                print("Attempting to start PPP connection...")
                self.ppp_disconnect()
                self.modem_power_off()
                sleep(1)
                self.modem_power_on()
                self.ppp_connect()
            sleep(60 * 2)

    def run(self):
        while True:
            pass
            # Update HW watchdog
