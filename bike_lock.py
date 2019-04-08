from stmpy import Machine


class BikeLock:

    def __init__(self, driver, rack):
        self.nfc_tag = 0
        self.driver = driver
        self.rack = rack

    def store(self, nfc_tag):  # TODO
        self.nfc_tag = nfc_tag

    def check_nfc_t4(self, *args, **kwargs):
        nfc_tag = kwargs["nfc_tag"]
        if self.nfc_tag == nfc_tag:
            return 'locked'
        else:
            return 'reserved'

    def check_nfc_t7(self, *args, **kwargs):
        nfc_tag = kwargs["nfc_tag"]
        if self.nfc_tag == nfc_tag:
            return 'available'
        else:
            return 'locked'

    def broken(self, from_state):
        # TODO How to track what state we came from?
        # Backend should deal with an out of order signal differently if it is a bicycle already locked or not
        self.driver.send_broken_signal(self.nfc_tag, from_state)

    def find_res_time(self):
        return 20000  # TODO How to implement estimated arrival time? Add a variable

    def green_led(self):
        self.led("green")
        return

    def red_led(self):
        self.led("red")
        return

    def yellow_led(self):
        self.led("yellow")
        return

    def led(self, color):  # TODO How to implement variables in effects? Or just have three methods: red_led(), green_led()...
        if color == "red":
            return  # TODO
        if color == "green":
            return  # TODO
        if color == "yellow":
            return  # TODO

    def lock(self):
        return  # TODO

    def unlock(self):
        return  # TODO

    def available(self):
        if self.nfc_tag != 0:
            self.rack.res_expired(self.nfc_tag)
        self.nfc_tag = 0

    # TODO Implement nfc_detected
    def is_correct_nfc(self, nfc_tag):
        # If a lock is not reserved and NFC should be valid
        if self.nfc_tag == 0:
            return True
        elif nfc_tag == self.nfc_tag:
            return True
        return False

    def test(self):
        return "Hello!"
