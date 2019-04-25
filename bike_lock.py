from stmpy import Machine
from gpio_component import gpio

class BikeLock:
    # TODO Implement reservation time based on location
    RESERVATION_TIMER = 5000000

    def __init__(self, driver, rack, name):
        self.nfc_tag = 0
        self.driver = driver
        self.rack = rack
        self.name = name
        self.gpio = gpio()

        """
        State machine definition
        """

        # STATES
        initial = {
            'name': 'initial'
        }
        available = {
            'name': 'available',
            'entry': 'green_led',
        }
        reserved = {
            'name': 'reserved',
            'entry': 'yellow_led',
        }
        locked = {
            'name': 'locked',
            'entry': 'red_led'
        }
        out_of_order = {
            'name': 'out_of_order',
            'entry': 'red_led',
        }

        # TRANSITIONS
        t0 = {
            'source': 'initial',
            'target': 'available'
        }
        # From Available
        t1 = {
            'source': 'available',
            'target': 'reserved',
            'trigger': 'reserve',
            'effect': f'start_timer("t", {self.RESERVATION_TIMER});store(*)'
        }
        t2 = {
            'source': 'available',
            'target': 'locked',
            'trigger': 'nfc_det',
            'effect': 'store(*); lock'
        }
        t3 = {
            'source': 'available',
            'target': 'out_of_order',
            'trigger': 'fault',
            'effect': 'broken'
        }
        # From Reserved
        t4 = {
            'source': 'reserved',
            'trigger': 'nfc_det',
            'function': self.check_nfc_t4
        }
        t5 = {
            'source': 'reserved',
            'target': 'available',
            'trigger': 't',
            'effect': 'res_expired; clear_nfc'
        }
        t6 = {
            'source': 'reserved',
            'target': 'out_of_order',
            'trigger': 'fault',
            'effect': 'broken'
        }
        # From Locked
        t7 = {
            'source': 'locked',
            'trigger': 'nfc_det',
            'function': self.check_nfc_t7
        }
        t8 = {
            'source': 'locked',
            'target': 'out_of_order',
            'trigger': 'fault',
            'effect': 'broken'
        }

        self.stm = Machine(
            name=self.name,
            states=[initial, reserved, locked, available, out_of_order],
            transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
            obj=self
        )

    def store(self, *args, **kwargs):
        self.nfc_tag = kwargs["nfc_tag"]

    def clear_nfc():
        self.nfc_tag=0

    def check_nfc_t4(self, *args, **kwargs):
        self.driver._logger.debug(f"check_nfc_t4: {kwargs}")
        nfc_tag = kwargs["nfc_tag"]
        if self.nfc_tag == nfc_tag:
            lock()
            return 'locked'
        else:
            return 'reserved'

    def check_nfc_t7(self, *args, **kwargs):
        self.driver._logger.debug(f"check_nfc_t7: {kwargs}")
        nfc_tag = kwargs["nfc_tag"]
        if self.nfc_tag == nfc_tag:
            unlock()
            clear_nfc()
            return 'available'
        else:
            return 'locked'

    def broken(self, from_state):
        # TODO How to track what state we came from?
        # Backend should deal with an out of order signal differently if it is a bicycle already locked or not
        self.driver.send_broken_signal(self.nfc_tag, from_state)

    def green_led(self):
        self.gpio.green()

    def red_led(self):
        self.gpio.red()

    def yellow_led(self):
        self.gpio.yellow()

    def lock(self):
        self.gpio.lock()

    def unlock(self):
        self.gpio.unlock()

    def res_expired(self):
        self.rack.res_expired(self.nfc_tag)

    def get_nfc_tag(self):
        return self.nfc_tag
