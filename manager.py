import json
from bike_lock import BikeLock
from stmpy import Driver
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
        {"command" : "reserve"}
        {"command" : "add_lock", "lock_name" : "name"}
"""

class BikeRack:

    def __init__(self, name, ip_adress, port):
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
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(self.MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.driver = Driver()
        self.driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')

        # Active machines
        # key = value
        self.active_machines = {}

        self.name=name

        self.MQTT_TOPIC_INPUT = 'bike/', name, '/command'
        self.MQTT_TOPIC_OUTPUT = 'bike/', name

        self.MQTT_BROKER = ip_adress
        self.MQTT_PORT = port

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def launch(self):
        self.driver.start()

    def check_available(self):
        for key in self.active_machines:
            if self.active_machines[key].state == available:
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
        try:
            payload = json.loads(msg.payload.decode("UTF-8"))
        except Exception as err:
            self._logger.error(
                f'Message sent to topic {msg.topic} had no valid JSON. Msg ignored. {err}'
            )
        command = payload.get('command')

        if command == "check_available":
            if self.check_available():
                self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT,f'Lock available')

        elif command=="reserve":
            if self.check_available():
                for key in self.active_machines:
                    if self.active_machines==available: #TODO Available? State?
                        self.stm_driver[key].send('reserve', self.active_machines[key])
            else:
                self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT,f'No locks available')

        elif command=="add_lock":
            lock_name=payload.get("lock_name")
            lock=BikeLock(self.driver)
            stm_lock = Machine(name=lock_name, states=[initial, reserved, locked, available, out_of_order], transitions=[t0,t1,t2,t3,t4,t5,t6,t7,t8,t9], obj=lock) #TODO Declare states and transitions in this class?
            lock.stm = stm_lock
            self.driver.add_machine(stm_lock)
            self.active_machines[lock_name]=stm_lock



    def res_expired(self, nfc_tag):
        self.mqtt_client.publish(self.MQTT_TOPIC_OUTPUT,f'Reservetion timed out for {nfc_tag}')

"""
:::DEBUGGING:::

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
