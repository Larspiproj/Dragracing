#!/usr/bin/python

from random import uniform
from smbus import SMBus
import RPi.GPIO as GPIO
import time
bus = SMBus(1)

# Set GPIO
photocell_stage1        =  5        
photocell_stage2        =  6
photocell_1000          = 13
callback_flag           = 19
finish_flag		= 21
green_flag              = 26

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(photocell_stage1, GPIO.IN)
    GPIO.setup(photocell_stage2, GPIO.IN)
    GPIO.setup(photocell_1000, GPIO.IN)
    GPIO.setup(callback_flag, GPIO.OUT, initial=0)
    GPIO.setup(finish_flag, GPIO.OUT, initial=0)
    GPIO.setup(green_flag, GPIO.OUT, initial=0)

def callback_roll_out(channel):
    print"callback_roll_out"
    global roll_out_time
    roll_out_time = time.time()
    GPIO.output(callback_flag, 1)
    GPIO.remove_event_detect(photocell_stage2)
    # check if falsestart
    if GPIO.input(green_flag) == 0: 
        print("RED")
        bus.write_byte(0x39, 0x02)

def callback_1000(channel):
    print"callback_1000"
    global time_1000
    time_1000 = time.time()
    GPIO.output(finish_flag, 1)
    GPIO.remove_event_detect(photocell_1000)
        
def stage():    
    # stage 1
    GPIO.wait_for_edge(photocell_stage1, GPIO.FALLING)
    print("STAGE_1")
    bus.write_byte(0x20, 0x1E)
    GPIO.remove_event_detect(photocell_stage1)
    
    # stage 2
    GPIO.wait_for_edge(photocell_stage2, GPIO.FALLING)
    print("STAGE_2")
    bus.write_byte(0x20, 0x1C)
    GPIO.remove_event_detect(photocell_stage2)
    GPIO.add_event_detect(photocell_stage2,GPIO.RISING,
                          callback=callback_roll_out, bouncetime=1000)

def race():
    GPIO.add_event_detect(photocell_1000, GPIO.FALLING,
                              callback=callback_1000, bouncetime=1000)   
    print("YELLOW")
    bus.write_byte(0x20, 0x00)
    
    time.sleep(0.4)
    if GPIO.input(callback_flag) == 0:
        green = time.time()
        bus.write_byte(0x39, 0x01)        
        GPIO.output(green_flag, 1)
        print"green: ", green
    else:
        green = time.time()
        
    while True:
        GPIO.input(callback_flag) == 0
        if GPIO.input(callback_flag) != 0:
            break

    while True:
        GPIO.input(finish_flag) == 0
        if GPIO.input(finish_flag) != 0:
            break

    return green

def times():
    print"ET:", round(time_1000 - roll_out_time, 3)
    print"Reactiontime:", round(roll_out_time -  greentime, 3)

raceAgain = "yes"
while raceAgain == "yes" or raceAgain == "y":
    bus.write_byte(0x20, 0xFF)
    bus.write_byte(0x39, 0xFF)
    init_gpio()
    try:
        stage()
        time.sleep(2)
        greentime = race()
        times()
    except KeyboardInterrupt:
        print"Race Cancelled\n"
    print"Do you want to race again (yes(y) or no(n))?"
    raceAgain = raw_input()

print"Race Cancelled"
bus.write_byte(0x20, 0xFF)
bus.write_byte(0x39, 0xFF)
GPIO.cleanup()
