import RPi.GPIO as GPIO
import time




# Variables
RED_PIN = 21
GREEN_PIN = 20
YELLOW_PIN = 16
LOCK_PIN = 19
UNLOCK_PIN = 26
pins = [RED_PIN, GREEN_PIN, YELLOW_PIN, LOCK_PIN, UNLOCK_PIN]

LED_DURATION = 3  # Seconds
LOCK_DURATION = 0.5  # Seconds


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Initialize pins
    for pin in pins:
        GPIO.setup(pin, GPIO.OUT)


def red():
    print("RED LED ON")
    GPIO.output(RED_PIN, GPIO.HIGH)
    time.sleep(LED_DURATION)
    print("RED LED OFF")
    GPIO.output(RED_PIN, GPIO.LOW)


def green():
    print("GREEN LED ON")
    GPIO.output(GREEN_PIN, GPIO.HIGH)
    time.sleep(LED_DURATION)
    print("GREEN LED OFF")
    GPIO.output(GREEN_PIN, GPIO.LOW)
        

def yellow():
    print("YELLOW PIN ON")
    GPIO.output(YELLOW_PIN, GPIO.HIGH)
    time.sleep(LED_DURATION)
    print("LED off")
    GPIO.output(YELLOW_PIN, GPIO.LOW)


# GPIO 19
def lock():
    GPIO.output(LOCK_PIN, GPIO.HIGH)
    print("LOCK")
    time.sleep(LOCK_DURATION)
    GPIO.output(LOCK_PIN, GPIO.LOW)


# GPIO 26
def unlock():
    GPIO.output(UNLOCK_PIN, GPIO.HIGH)
    print("UNLOCK")
    time.sleep(LOCK_PIN)
    GPIO.output(UNLOCK_PIN, GPIO.LOW)
