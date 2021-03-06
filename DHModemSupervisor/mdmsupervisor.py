from .modem import Modem
from time import sleep
import ConfigParser
import os
from subprocess import Popen
from syslog import syslog


class ModemSupervisor(object):
    PIN_POWER = 16
    PIN_RESET = 18
    PIN_STATUS = 12

    NET_CHECK_INTERVAL = 60
    NET_TIMEOUT_INTERVAL = 10

    INI_FILE = '/etc/devicehub/dhmsupervisord.ini'

    APN = 'internet'
    ISP = 'isp'

    AUTO_CONNECT = False

    PPP_CONNECTED = False
    NET_CONNECTED = False

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

        self.setup_platform()

    def log(self, args):
        syslog("ModemSupervisor: " + args)

    def setup_platform(self):
        self.modem = Modem(self.PIN_POWER, self.PIN_RESET, self.PIN_STATUS)

    def ppp_connect(self):
        os.system("killall -9 pppd")
        sleep(1)
        os.system("pppd call {ISP}".format(ISP=self.ISP))

    def ppp_disconnect(self):
        if self.intf_status('ppp'):
            os.system("killall -9 pppd")
            sleep(1)

    def intf_status(self, intf):
        try:
            for line in os.popen("/sbin/ip link show"):
                if intf in line:
                    syslog("INTERFACE: {INTF} UP".format(INTF=intf))
                    return True
        except Exception as e:
            self.log(e)
        syslog("INTERFACE: {INTF} DOWN".format(INTF=intf))
        return False

    def net_status(self):
        p = Popen(["nc", "-zw60", "google.com", "443"])
        output = p.communicate()[0]
        if p.returncode == 0:
            syslog("INTERNET CONNECTION IS UP")
            return True
        else:
            syslog("INTERNET CONNECTION IS DOWN")
            return False

    def net_and_ppp_up(self):
        if self.intf_status('ppp') and self.net_status():
            return True
        else:
            return False

    def internet_disconnected(self):
        syslog("internet_disconnected")
        os.system("systemctl stop openvpn")
        retry = 0
        max_retry = 5
        while retry < max_retry:
            syslog("Attempting to start PPP connection...")
            self.ppp_disconnect()
            self.modem.reset()
            sleep(30*retry)
            self.ppp_connect()
            sleep(30)
            if self.net_and_ppp_up():
                return
            retry += 1

    def run(self):
        while True:
            if self.net_and_ppp_up():
                sleep(10)
                if not self.intf_status('tun'):
                    syslog("OpenVPN is down, attempting openvpn restart...")
                    os.system("systemctl restart openvpn")
                    sleep(60)
            else:
                self.internet_disconnected()
            sleep(self.NET_CHECK_INTERVAL)


