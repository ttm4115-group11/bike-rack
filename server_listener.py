import urllib.request
import json
import time
import paho.mqtt.client as mqtt

TOPIC = 'rack/1/reserve'
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883


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

RACK_NUMBER = 1
prev_length = 0
previous = []


def relevant_content(reservations):
    relevant = []
    for reservation in reservations:
        if reservation["rack_id"] == RACK_NUMBER:
            relevant.append(reservation)
    return relevant


def remove_previous(reservations):
    relevant = []
    for reservation in reservations:
        if reservation["id"] not in previous:
            relevant.append(reservation)
            previous.append(reservation["id"])
    return relevant


def publish_new_reservations(reservations):
    for reservation in reservations:
        client.publish(
            TOPIC,
            json.dumps(reservation)
        )


while True:
    print("Polling")
    contents = urllib.request.urlopen("http://167.99.217.172:5000/reservations").read()
    contents = json.loads(contents)

    # Ignore reservations not for this rack
    contents = relevant_content(contents)

    # Remove old reservations
    contents = remove_previous(contents)
    print(contents)

    if contents:
        print("PUBLISH!")
        publish_new_reservations(contents)

    time.sleep(3)


