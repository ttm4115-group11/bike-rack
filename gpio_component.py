import RPi.GPIO as GPIO
import time


class gpio:

    # Variables
    RED_PIN = 21
    GREEN_PIN = 20
    YELLOW_PIN = 16
    LOCK_PIN = 19
    UNLOCK_PIN = 26
    pins = [RED_PIN, GREEN_PIN, YELLOW_PIN, LOCK_PIN, UNLOCK_PIN]

    LED_DURATION = 3  # Seconds
    LOCK_DURATION = 0.2  # Seconds

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Initialize pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def red(self):
        print("RED LED ON")
        GPIO.output(self.RED_PIN, GPIO.HIGH)
        time.sleep(self.LED_DURATION)
        print("RED LED OFF")
        GPIO.output(self.RED_PIN, GPIO.LOW)

    def green(self):
        print("GREEN LED ON")
        GPIO.output(self.GREEN_PIN, GPIO.HIGH)
        time.sleep(self.LED_DURATION)
        print("GREEN LED OFF")
        GPIO.output(self.GREEN_PIN, GPIO.LOW)

    def yellow(self):
        print("YELLOW PIN ON")
        GPIO.output(self.YELLOW_PIN, GPIO.HIGH)
        time.sleep(self.LED_DURATION)
        print("LED off")
        GPIO.output(self.YELLOW_PIN, GPIO.LOW)

    # GPIO 19
    def lock(self):
        GPIO.output(self.LOCK_PIN, GPIO.HIGH)
        print("LOCK")
        time.sleep(self.LOCK_DURATION)
        GPIO.output(self.LOCK_PIN, GPIO.LOW)

    # GPIO 26
    def unlock(self):
        GPIO.output(self.UNLOCK_PIN, GPIO.HIGH)
        print("UNLOCK")
        time.sleep(self.LOCK_DURATION)
        GPIO.output(self.UNLOCK_PIN, GPIO.LOW)
