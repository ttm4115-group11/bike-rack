from stmpy import Machine

class BikeLock:

    def __init__(self, driver):
        self.nfc_tag
        self.driver=driver

    def store(self, nfc_tag):
        self.nfc_tag=nfc_tag

    def check_nfc_t4(self, nfc_tag):
        if (self.nfc_tag == nfc_tag):
            return 'locked'
        else
            return 'reserved'

    def check_nfc_t7(self, nfc_tag):
        if (self.nfc_tag == nfc_tag):
            return 'available'
        else
            return 'locked'

    def broken(self, from_state):
        self.driver.send_broken_signal(self.nfc_tag,from_state)

    def find_res_time(self):
        return position + 20000 #TODO How to implement estimated arrival time?
        #return res_time

    def led(self, led):
        if led=="red":
            return #TODO
        if led == "green":
            return #TODO
        if led == "yellow":
            return #TODO

    def lock(self):
        self.driver.send_lock_signal() #TODO

    def unlock(self):
        self.driver.send_unlock_signal() #TODO

    def available(self):
        self.driver.res_expired(self.nfc_tag)
