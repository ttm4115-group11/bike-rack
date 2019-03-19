import stmpy


class BikeLock:
    
    def __init__(self, name, manager, nfc_value):

        self.name = name

        self.stm = stmpy.Machine(name=self.name, states=[], trasistions=[], obj=self)

        # Define transistion 
        
        t0 = {
            'source', 'initial',
            'target', 'available'
        }

        # From Available
        t1 = {
            'source': 'available',
            'target': 'reserved',
            'trigger': 'reserve',
            'effect': 'start_timer()'
        }

        t2 = {
            'source': 'available',
            'target': 'locked',
            'trigger': 'lock',
            'effect': 'lock()'
        }

        t3 = {
            'source': 'available',
            'traget': 'out_of_order',
            'trigger': 'fault'
        }

        # From Reserved
        t4 = {
            'source': 'reserved',
            'target': 'locked',
            'trigger': 'lock',
            'effect': 'lock()',
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
        }

        # From Locked
        t7 = {
            'source': 'locked', 
            'target': 'available',
            'trigger': 'unlock',
            'effect': 'unlock()'
        }

        t8 = {
            'source', 'locked',
            'target', 'out_of_order', 
            'trigger', 
        }

        # States 
        initial = {'name': 'initial'}
        available = {
            'name': 'available',
            'entry': 'green_led',
        }

        reserved = {
            'name': 'reserved',
            'entry': 'red_led',

        }

        locked = {
            'name': 'locked',
            'entry': 'red_led',
        }

        out_of_order = {
            'name': 'out_of_order',
            'entry': 'red_led',
        }

        