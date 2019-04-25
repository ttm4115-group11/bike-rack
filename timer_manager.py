"""
This file is uesed as a reference
"""

import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

# TODO: choose proper MQTT broker address
MQTT_BROKER = '10.24.6.77'
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'aleks/command'
MQTT_TOPIC_OUTPUT = 'aleks/answer'


class TimerLogic:
    """
    State Machine for a named timer.

    This is the support object for a state machine that models a single timer.
    """
    def __init__(self, name, duration, component):
        self._logger = logging.getLogger(__name__)
        self.name = name
        self.duration = duration
        self.component = component

        # TODO: build the transitions
        t0 = {
            'source': 'initial',
            'target': 'active',
            'effect': 'started',
        }

        t1 = {
            'source': 'active',
            'target': 'active',
            'trigger': 'report',
            'effect' : 'report_status',
        }

        t2 = {
            'source' : 'active',
            'target' : 'completed',
            'trigger': 't',
            'effect' : 'timer_completed',
        }

        self.stm = stmpy.Machine(name=name, transitions=[t0, t1, t2], obj=self)

    # TODO define functions as transition effetcs


    def started(self):
        self.stm.start_timer('t', self.duration)
        self.component.active_machines[self.name] = self.name
        self._logger.debug(f'started timer {self.name} for {self.duration}')
        self.component.mqtt_client.publish(
            MQTT_TOPIC_OUTPUT,
            f'Started timer {self.name} for {self.duration}'
        )


    def report_status(self):
        remaning_time = self.stm.get_timer('t')
        self._logger.debug(f'Remaning time of {self.name} is {remaning_time}')
        self.component.mqtt_client.publish(
            MQTT_TOPIC_OUTPUT,
            f'Remaning time of {self.name} is {remaning_time}'
        )


    def timer_completed(self):
        self._logger.debug(f'{self.name} is finished!')
        self.component.active_machines.pop(self.name, None)
        self.component.mqtt_client.publish(
            MQTT_TOPIC_OUTPUT,
            f'{self.name} is finished!'
        )

class TimerManagerComponent:
    """
    The component to manage named timers in a voice assistant.

    This component connects to an MQTT broker and listens to commands.
    To interact with the component, do the following:

    * Connect to the same broker as the component. You find the broker address
    in the value of the variable `MQTT_BROKER`.
    * Subscribe to the topic in variable `MQTT_TOPIC_OUTPUT`. On this topic, the
    component sends its answers.
    * Send the messages listed below to the topic in variable `MQTT_TOPIC_INPUT`.

        {"command": "new_timer", "name": "spaghetti", "duration":50}

        {"command": "status_all_timers"}

        {"command": "status_single_timer", "name": "spaghetti"}

    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

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

        # TODO unwrap JSON-encoded payload
        try:
            payload = json.loads(msg.payload.decode("UTF-8"))
        except Exception as err:
            self._logger.error(
                f'Message sent to topic {msg.topic} had no valid JSON. Msg ignored. {err}'
            )
            return

        command = payload.get('command')

        if command == 'new_timer':
            timer_name = payload.get('name')
            duration = payload.get('duration')
            timer_stm = TimerLogic(timer_name, duration, self)
            self._logger.debug(f'start new state machine with name {timer_name}')
            self.stm_driver.add_machine(timer_stm.stm)
            self.stm_driver.start()

        elif command == 'status_all_timers':
            self._logger.debug(f'publish status for all timers')
            for key in self.active_machines:
                self.stm_driver.send('report', self.active_machines[key])


        elif command == 'status_single_timer':
            singe_timer_name = payload.get('name')
            self._logger.debug(f'publish status for {singe_timer_name}')
            self.stm_driver.send('report', payload.get('name'))

        else:
            self._logger.error(f'{command} is unknown command')


        # TODO extract command

        # TODO determine what to do


    def __init__(self):
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
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self._logger.debug('Component initialization finished')

        # Active machines
        # key = value
        self.active_machines = {

        }

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


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

t = TimerManagerComponent()
