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

        # Add test_lock
        lock_name = "en"
        self._logger.debug(f'Create machine with name: {lock_name}')
        lock_stm = BikeLock(self.driver, self, lock_name)

        self.driver.add_machine(lock_stm.stm)
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

        if command == "check_driver":
            self._logger.debug(f"State Machine: {self.driver.print_status()}")
            if self.check_available():
                self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT, self.driver.print_status())

        # Assumes payload with ``lock_name`` and ``nfc_tag``
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
            self._logger.debug(f"Add lock with name: {lock_name}")
            lock_stm = BikeLock(self.driver, self, lock_name)
            self.driver.add_machine(lock_stm.stm)
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

        # Catch message without handler
        else:
            self._logger.debug(f"Command: {command} does not have a handler")

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


rack = BikeRack("rack","10.24.23.140", 1883)
