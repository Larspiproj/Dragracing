#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN)
GPIO.setup(20, GPIO.OUT, initial=0)
GPIO.setup(21, GPIO.OUT, initial=0)


try:
    print("waiting")

    def callback_stage1(channel):
        if GPIO.input(5) == 0:
            GPIO.output(20, 1)
            print("STAGE1_ON")
        else:
            print("STAGE1_OFF")
            GPIO.output(20, 0)

    def callback_stage2(channel):
        if GPIO.input(6) == 0:
            GPIO.output(21, 1)
            print("STAGE2_ON")
        else:
            print("STAGE2_OFF")
            GPIO.output(21, 0)

    GPIO.add_event_detect(5, GPIO.BOTH, callback=callback_stage1, bouncetime=500)
    GPIO.add_event_detect(6, GPIO.BOTH, callback=callback_stage2, bouncetime=500)

    while True:
        GPIO.input(20) and GPIO.input(21) == 0
        if GPIO.input(20) and GPIO.input(21) != 0:
            break
    time.sleep(5)
    print("Race")

    def green():
        print ("green")

    # t = threading.Timer(5, green)
    # t.start()

except KeyboardInterrupt:
    print("Keyboardinterrupt")


try:
    while True:
        pass
except KeyboardInterrupt:
    print("Race cancelled")
finally:
    GPIO.cleanup()
    print("Cleaned up")

