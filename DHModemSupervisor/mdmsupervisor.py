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

    NET_CHECK_INTERVAL = 30

    INI_FILE = '/etc/devicehub/itbp-gprs.ini'

    APN = 'internet'
    ISP = 'isp'

    AUTO_CONNECT = False

    PPP_CONNECTED = False
    NET_CONNECTED = False

    states = ['initial', 'internet_disconnected', 'internet_connected', 'modem_reset']
    modem = None

    def __init__(self):
        # Try to open the config file /etc/itbp-gprs.ini and populate settings
        try:
            config = ConfigParser.ConfigParser()
            config.read(self.INI_FILE)

            self.PIN_POWER  = config.getint('Modem', 'gpio_power')
            self.PIN_RESET  = config.getint('Modem', 'gpio_reset')
            self.PIN_STATUS = config.getint('Modem', 'gpio_status')

            self.ISP = config.get('Connection', 'isp')
            self.AUTO_CONNECT = config.getboolean('Connection', 'auto_connect')

            self.log("PWR PIN: {PIN}".format(PIN=self.PIN_POWER))
            self.log("ISP: " + self.ISP)
            self.log("APN: " + self.APN)
            self.log("AUTO_CONNECT: " + str(self.AUTO_CONNECT))
        except Exception as e:
            self.log("config file init EXC: " + str(e))

        Machine.__init__(self, states=self.states, initial='initial')
        self.add_transition('disconnect', 'internet_connected', 'internet_disconnected')
        self.add_transition('reconnect', ['initial', 'internet_connected'], 'internet_disconnected')
        self.add_transition('connect', ['initial', 'internet_disconnected'], 'internet_connected')
        self.add_transition('hw_reset', 'internet_disconnected', 'modem_reset')
        self.add_transition('finished_hw_reset', 'modem_reset', 'internet_disconnected')

        self.setup_platform()

    def log(self, args):
        print("ModemSupervisor:", args)

    def setup_platform(self):
        self.modem = Modem(self.PIN_POWER, self.PIN_RESET, self.PIN_STATUS)

    def ppp_connect(self):
        os.system("pon {ISP}".format(ISP=self.ISP))

    def ppp_disconnect(self):
        os.system("poff {ISP}".format(ISP=self.ISP))
        sleep(1)
        os.system("killall -9 pppd")

    def intf_status(self, intf):
        try:
            for line in os.popen("/sbin/ip link show "):
                if intf in line:
                    print("ppp on")
                    return True
        except Exception as e:
            self.log(e)
        print("ppp off")
        return False

    def net_status(self):
        p = Popen(["ping", "-c1", "mail.google.com"])
        output = p.communicate()[0]
        if p.returncode == 0:
            return True
        else:
            return False

    def net_and_ppp_up(self):
        if self.intf_status('ppp') and self.net_status():
            return True
        else:
            return False

    def on_enter_internet_connected(self):
        print("on_enter_internet_connected")
        os.system("systemctl start openvpn")
        while True:
            if not self.net_and_ppp_up():
                self.reconnect()

            if not self.intf_status('tun'):
                os.system("systemctl restart openvpn")

            sleep(self.NET_CHECK_INTERVAL)

    def on_enter_internet_disconnected(self):
        print("on_enter_internet_disconnected")
        os.system("systemctl stop openvpn")
        retry = 0
        max_retry = 5
        while retry < max_retry:
            print("Attempting to start PPP connection...")
            self.ppp_disconnect()
            self.modem.power_off()
            sleep(5)
            self.modem.power_on()
            self.ppp_connect()
            sleep(30)
            if self.net_and_ppp_up():
                self.connect()
            retry += 1
        self.hw_reset()

    def on_enter_modem_reset(self):
        print("on_enter_modem_reset")
        self.modem.reset()
        self.reconnect()

    def run(self):
        if self.net_status():
            self.connect()
        else:
            self.reconnect()
