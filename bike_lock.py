from stmpy import Driver, Machine


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
        return 20000 #TODO How to implement estimated arrival time?

    def led(self, led):
        if led=="red":
            return #TODO

    def lock(self):
        self.driver.send_lock_signal() #TODO

    def unlock(self):
        self.driver.send_unlock_signal() #TODO

    def available(self):
        self.driver.send_available_signal() #TODO

# STATES

initial = {'name': 'initial'}

available = {
    'name': 'available',
    'entry': 'led("green"); unlock; available',
}

reserved = {
    'name': 'reserved',
    'entry': 'yellow_led',
}

locked = {
    'name': 'locked',
    'entry': 'red_led; lock'
}

out_of_order = {
    'name': 'out_of_order',
    'entry': 'red_led',
}

# TRANSITIONS

t0 = {
    'source': 'initial',
    'target': 'locked'
}

# From Available
t1 = {
    'source': 'available',
    'target': 'reserved',
    'trigger': 'reserve',
    'effect': 'start_timer("t", res_time); store(nfc_tag)'  # TODO res_time
}

t2 = {
    'source': 'available',
    'target': 'locked',
    'trigger': 'nfc_det',
    'effect': 'store(nfc_tag)'
}

t3 = {
    'source': 'available',
    'traget': 'out_of_order',
    'trigger': 'fault',
    'effect': 'broken("from_available")'
}

# From Reserved
t4 = {
    'source': 'reserved',
    'trigger': 'nfc_det',
    'function': 'stm.check_nfc(nfc_tag)'
}

t5 = {
    'source': 'reserved',
    'target': 'available',
    'trigger': 't',
}

t6 = {
    'source': 'reserved',
    'target': 'out_of_order',
    'trigger': 'fault',
    'effect': 'broken(this, nfc_tag)'
}

# From Locked
t7 = {
    'source': 'locked',
    'trigger': 'nfc_det',
    'function': 'stm.check_nfc(nfc_tag)'
}

t8 = {
    'source': 'locked',
    'target': 'out_of_order',
    'trigger': 'fault',
    'effect': 'broken(this, from_locked)'
}

# From out of order
t9 = {
    'source': 'out_of_order',
    # 'target': '?',
    'effect': 'terminate'
}

rack = Driver()
lock1=BikeLock(rack)
stm_lock1 = Machine(name='lock1', states=[initial, reserved, locked, available, out_of_order], transitions=[t0,t1,t2,t3,t4,t5,t6,t7,t8,t9], obj=lock1)
lock1.stm = stm_lock1
rack.add_machine(stm_lock1)
rack.start()
