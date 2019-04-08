import json
from bike_lock import BikeLock
from stmpy import Driver, Machine
import paho.mqtt.client as mqtt
import logging

"""
    The component to manage locks in a bike rack.
    This component connects to an MQTT broker and listens to commands.
    To interact with the component, do the following:
    * Connect to the same broker as the component. You find the broker address
    in the value of the variable `MQTT_BROKER`.
    * Subscribe to the topic in variable `MQTT_TOPIC_OUTPUT`. On this topic, the
    component sends its answers.
    * Send the messages listed below to the topic in variable `MQTT_TOPIC_INPUT`.
        {"command" : "check_available"}
        {"command" : "reserve", "value": ``nfc_value``, "offset": ``offset``}
        {"command" : "add_lock", "lock_name" : "name"}
        {"command" : "nfc_det", "value": ``nfc_value``, "lock_name": ``name``}
"""


class BikeRack:

    def __init__(self, name, mqtt_broker, mqtt_port):
        """
        Start the component.
        ## Start of MQTT
        We subscribe to the topic(s) the component listens to.
        The client is available as variable `self.client` so that subscriptions
        may also be changed over time if necessary.
        The MQTT client reconnects in case of failures.
        ## State Machine driver
        We create a single state machine driver for STMPY. This should fit
        for most components. The driver is available from the variable
        `self.driver`. You can use it to send signals into specific state
        machines, for instance.
        """

        # TODO Make the mqtt topics into bike/$name/command (input) and bike/$name (output).
        # Something wrong happened trying to do so.
        self.MQTT_TOPIC_INPUT = 'bike/'#, name, '/command'
        self.MQTT_TOPIC_OUTPUT = 'bike/'#, name

        # Get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('Logging under name {}.'.format(__name__))

        # ::: DEBUGGING :::
        # logging.DEBUG: Most fine-grained logging, printing everything
        # logging.INFO:  Only the most important informational log items
        # logging.WARN:  Show only warnings and errors.
        # logging.ERROR: Show only error messages.
        debug_level = logging.DEBUG
        logger = logging.getLogger(__name__)
        logger.setLevel(debug_level)
        ch = logging.StreamHandler()
        ch.setLevel(debug_level)
        formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        # END DEBUGGING

        self._logger.info('Starting Component')

        # Create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(mqtt_broker, mqtt_port))
        self.mqtt_client = mqtt.Client()

        # Callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Connect to the broker
        self.mqtt_client.connect(mqtt_broker, mqtt_port)

        # Subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(self.MQTT_TOPIC_INPUT)

        # Start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # We start the stmpy driver, without any state machines for now
        self.driver = Driver()
        self.driver.start(keep_active=True)

        self._logger.debug('Component initialization finished')

        # Active machines
        self.active_machines = {}
        self.name = name

        # TEST START!
        # TODO Remove this section.
        # This section is just to test with one lock.

        lock_name = "en"
        self._logger.debug(f'Create machine with name: {lock_name}')
        lock = BikeLock(self.driver, self)
        stm_lock = Machine(
            name=lock_name,
            states=[initial, reserved, locked, available, out_of_order],
            transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
            obj=lock
        )
        lock.stm = stm_lock
        self.driver.add_machine(stm_lock)
        self.active_machines[lock_name] = lock_name

        self._logger.debug("Start driver")
        self.driver.start()
        # TEST END

    def stop(self):
        """
        Stop the component.
        """
        # Stop the MQTT client
        self.mqtt_client.loop_stop()
        # Stop the state machine Driver
        self.driver.stop()

    def on_connect(self, client, userdata, flags, rc):
        # We just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def check_available(self):
        for name in self.active_machines:
            if self.driver._stms_by_id[name].state == "available":
                return True

    def on_message(self, client, userdata, msg):
        """
        Processes incoming MQTT messages.
        We assume the payload of all received MQTT messages is an UTF-8 encoded
        string, which is formatted as a JSON object. The JSON object contains
        a field called `command` which identifies what the message should achieve.
        As a reaction to a received message, we can for example do the following:
        * create a new state machine instance to handle the incoming messages,
        * route the message to an existing state machine session,
        * handle the message right here,
        * throw the message away.
        """
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))

        payload = json.loads(msg.payload)
        command = payload.get('command')
        self._logger.debug(f"Have detected this command: {command}")

        if command == "check_available":
            self._logger.debug("Inside if statement: Check_av")  # TODO Remove
            if self.check_available():
                self.mqtt_client.publish(
                    self.MQTT_TOPIC_OUTPUT,
                    f'Lock available'
                )

        # Assumes ``lock_name`` and ``nfc_tag``
        elif command == "reserve":
            for name in self.active_machines:
                if self.driver._stms_by_id[name].state == "available":
                    self._logger.debug(f"Reserving lock with id: {name}")
                    kwargs = {"nfc_tag": payload.get("value")}
                    self.driver.send(message_id='reserve', stm_id=name, kwargs=kwargs)
                    self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT, f'Reserved lock with name {name}')
                    self.mqtt_client.publish(self.get_stm_by_name(name)._obj.get_nfc_tag())
                    self._logger.debug(self.get_stm_by_name(name)._obj.get_nfc_tag())
                    return
            self._logger.debug("No locks available in this rack")
            self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT, f'No locks available')

        elif command == "add_lock":
            lock_name = payload.get("lock_name")
            lock = BikeLock(self.driver, self)
            self._logger.debug(f"Add lock with name: {lock_name}")
            stm_lock = Machine(
                name=lock_name,
                states=[initial, reserved, locked, available, out_of_order],
                transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
                obj=lock
            )
            lock.stm = stm_lock
            self.driver.add_machine(stm_lock)
            self.active_machines[lock_name] = lock_name

        # Assumes payload with``nfc_tag`` and ``lock_name``
        elif command == "nfc_det":
            self._logger.debug("running nfc_det")
            self.nfc_det(nfc_tag=payload.get("value"), lock_name=payload.get("lock_name"))

        elif command == "check_state":
            name = payload.get("name")
            self._logger.debug(f"Machine: {name}, is in state: {self.get_stm_by_name(name).state}")
            self.mqtt_client.publish(
                self.MQTT_TOPIC_OUTPUT,
                f"Machine: {name}, is in state: {self.get_stm_by_name(name).state}"
            )

        # Catch message witout handler
        else:
            self._logger.debug(f"Command: {command} does not have a handler")

        #except Exception as err:
        #    self._logger.error(
        #        f'Det skjedde en feil: {err}. Ignorerer melding'
        #        # f'Message sent to topic {msg.topic} had no valid JSON. Msg ignored. {err}'
        #    )

    def res_expired(self, nfc_tag):
        self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT, f'Reservetion timed out for {nfc_tag}')

    def nfc_det(self, nfc_tag, lock_name):
        self._logger.debug(f"Detected NFC-tag with value: {nfc_tag} presented to lock: {lock_name}")
        self._logger.debug(self.get_stm_by_name(lock_name).state)
        kwargs = {"nfc_tag": nfc_tag}
        self.driver.send(message_id='nfc_det', stm_id=lock_name, kwargs=kwargs)

    # Getter for stm_by name
    def get_stm_by_name(self, stm_name):
        if self.driver._stms_by_id[stm_name]:
            self._logger.debug(f"Getting stm with name: {stm_name}")
            return self.driver._stms_by_id[stm_name]

        # Did not find machine with ``stm_name``
        self._logger.error(f"Error: did not find stm with name: {stm_name}")
        return None

"""
Declaring states and transitions
"""

RESERVATION_TIMER = 5000000

# STATES
initial = {
    'name': 'initial'
}
available = {
    'name': 'available',
    'entry': 'green_led; unlock; available',
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
    'target': 'available'
}
# From Available
t1 = {
    'source': 'available',
    'target': 'reserved',
    'trigger': 'reserve',
    'effect': f'start_timer("t", {RESERVATION_TIMER});'  # TODO res_time
}
t2 = {
    'source': 'available',
    'target': 'locked',
    'trigger': 'nfc_det',  # TODO

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
    'function': 'stm.check_nfc_t4(*)'
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
    'effect': 'broken'
}
# From Locked
t7 = {
    'source': 'locked',
    'trigger': 'nfc_det',  # TODO
    'function': 'stm.check_nfc_t7(*)'
}
t8 = {
    'source': 'locked',
    'target': 'out_of_order',
    'trigger': 'fault',
    'effect': 'broken'
}
"""
# TODO
# From out of order
t9 = {
    'source': 'out_of_order',
    # 'target': '?',
    'effect': 'terminate'
}
"""

# TODO TESTING
rack = BikeRack("rack", "127.0.0.1", 1883)
