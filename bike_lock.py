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
            'effect': 'store_nfc(nfc_tag)',
            'effect': 'start_timer(t, reservation_time)'
        }

        t2 = {
            'source': 'available',
            'target': 'locked',
            'trigger': 'nfc_detect',
            'effect': 'store_nfc(nfc_tag)'
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
            'trigger': 'nfc_detect'
            #If correct nfc_detect, go to locked state. Else, go to reserved state.
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
            'effect': 'broken(this, from_reserved)'
        }

        # From Locked
        t7 = {
            'source': 'locked', 
            'target': 'available',
            'trigger': 'nfc_detected'
            #If correct nfc_detect, go to available state. Else, go to locked state.
        }

        t8 = {
            'source': 'locked',
            'target': 'out_of_order', 
            'trigger': 'fault',
            'trigger': 'broken(this, from_locked)'
        }

        # From Out_of_order
        t9 = {
            'source': 'out_of_order',
            'target': 'terminated',
            'trigger': 'service'
        }



        # States 
        initial = {'name': 'initial'}
        available = {
            'name': 'available',
            'entry': 'green_led',
            'entry': 'unlock()',
            'entry': 'available(this)'
        }

        reserved = {
            'name': 'reserved',
            'entry': 'yellow_led'
        }

        locked = {
            'name': 'locked',
            'entry': 'red_led',
            'entry': 'lock()'
        }

        out_of_order = {
            'name': 'out_of_order',
            'entry': 'red_led'
        }

        #terminated state

        