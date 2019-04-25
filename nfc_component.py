import nxppy
import paho.mqtt.client as mqtt
import json

TOPIC = 'rack/1/lock/1'
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883

"""
This component will continuously run in a own process
on the raspberry pi and publish messages when presented
with a NFC device
"""

# MQTT setup
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()


"""
set up nxppy
note that installing this is more than installing it
follow installation guide: https://github.com/svvitale/nxppy
"""

mifare = nxppy.Mifare()

while True:
    try:
        uid = mifare.select()
        print(uid)

        client.publish(
            TOPIC,
            json.dumps({
                "command": "nfd_det",
                "value": uid,
            }).encode()
        )
    except nxppy.SelectError:
        # We want the reader to fail silently
        # when no nfc device i presented
        pass

    time.sleep(1)
