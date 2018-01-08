from transitions import Machine
from .modem import Modem


class ModemSupervisor(Machine):
    states = ['internet_disconnected', 'internet_connected', 'modem_reset']

    def __init__(self):
        Machine.__init__(self, states=self.states, initial='internet_disconnected')
        self.add_transition('disconnecting', 'internet_connected', 'internet_disconnected')
        self.add_transition('connecting', 'internet_disconnected', 'internet_connected')
        self.add_transition('hw_reset', 'internet_disconnected', 'modem_reset')
        self.add_transition('finished_hw_reset', 'modem_reset', 'internet_disconnected')

        self.setup_platform()

    def setup_platform(self):


    def run(self):
        while True:
            pass
            # Update HW watchdog
