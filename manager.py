import json
"""
    The component to manage locks in a bike rack.
    This component connects to an MQTT broker and listens to commands.
    To interact with the component, do the following:
    * Connect to the same broker as the component. You find the broker address
    in the value of the variable `MQTT_BROKER`.
    * Subscribe to the topic in variable `MQTT_TOPIC_OUTPUT`. On this topic, the
    component sends its answers.
    * Send the messages listed below to the topic in variable `MQTT_TOPIC_INPUT`.

    "commands" : "

    """


class BikeLockManager:

    def __init__():
        pass
    
    def on_message_from_server(self, msg):
        try:
            payload = json.loads(msg)
        except expression as identifier:
            pass
