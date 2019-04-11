import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
    

def red():
    GPIO.setup(21,GPIO.OUT)
    print("LED on")
    GPIO.output(21,GPIO.HIGH)
    time.sleep(3)
    print("LED off")
    GPIO.output(21,GPIO.LOW)


def green():
    GPIO.setup(20,GPIO.OUT)
    print("LED on")
    GPIO.output(20,GPIO.HIGH)
    time.sleep(3)
    print("LED off")
    GPIO.output(20,GPIO.LOW)
        

def yellow():
    GPIO.setup(16,GPIO.OUT)
    print("LED on")
    GPIO.output(16,GPIO.HIGH)
    time.sleep(3)
    print("LED off")
    GPIO.output(16,GPIO.LOW)

red()
yellow()
green()
