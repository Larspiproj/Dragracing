#!/usr/bin/python

from random import uniform
from smbus import SMBus
import RPi.GPIO as GPIO
import time
bus = SMBus(1)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set GPIO
photocell_stage1        =  5        
photocell_stage2        =  6
photocell_1000          = 13
callback_flag           = 19
yellow_flag             = 16
green_flag              = 26
FLAGS = (photocell_stage1,photocell_stage2,photocell_1000,callback_flag,
         yellow_flag,green_flag,)

def init_gpio():
    GPIO.setup(photocell_stage1, GPIO.IN)
    GPIO.setup(photocell_stage2, GPIO.IN)
    GPIO.setup(photocell_1000, GPIO.IN)
    GPIO.setup(callback_flag, GPIO.OUT, initial=0)
    GPIO.setup(yellow_flag, GPIO.OUT, initial=0)
    GPIO.setup(green_flag, GPIO.OUT, initial=0)

def callback_roll_out(channel):
    print"callback_roll_out"
    global roll_out_time
    roll_out_time = time.time()
    GPIO.output(callback_flag, 1)
    GPIO.remove_event_detect(photocell_stage2)
    # green is not activated and  yellow sequence started. Stage 1, 2, yellow and red light on.
    if GPIO.input(green_flag) == 0 and GPIO.input(yellow_flag) == 1:
        print("RED")
        bus.write_byte(0x20, 0x20)
    # green is not activated and yellow sequence not started. Stage 1, 2 and red lights on.
    elif GPIO.input(green_flag) == 0 and GPIO.input(yellow_flag) == 0:
        print("RED")
        bus.write_byte(0x20, 0xBC)

def callback_1000(channel):
    print"callback_1000"
    global time_1000
    time_1000 = time.time()
    print"ET: ", round(time_1000 - roll_out_time, 3)
    GPIO.remove_event_detect(photocell_1000)
        
def race():    
    GPIO.wait_for_edge(photocell_stage1, GPIO.FALLING)       # STAGE 1
    print("STAGE_1")
    bus.write_byte(0x20, 0xFE)
    GPIO.remove_event_detect(photocell_stage1)
    
    time.sleep(1)
    GPIO.wait_for_edge(photocell_stage2, GPIO.FALLING)       # STAGE 2
    print("STAGE_2")
    bus.write_byte(0x20, 0xFC)
    GPIO.remove_event_detect(photocell_stage2)
    
    GPIO.add_event_detect(photocell_stage2,GPIO.RISING,
                          callback=callback_roll_out, bouncetime=1000)
    GPIO.add_event_detect(photocell_1000, GPIO.FALLING,
                              callback=callback_1000, bouncetime=1000)

    time.sleep(3)
    
    print("YELLOW")
    # if false start keep red light on
    if GPIO.input(callback_flag) == 1:
        bus.write_byte(0x20, 0x20)
    else:

        GPIO.output(yellow_flag, 1)
        bus.write_byte(0x20, 0xE0)
    
    time.sleep(0.4)
    if GPIO.input(callback_flag) == 0:
        green = time.time()
        bus.write_byte(0x20, 0xDF)        
        GPIO.output(green_flag, 1)
        print"green: ", green
    else:
        green = time.time()
        bus.write_byte(0x20, 0x20)      
        
    while True:
        GPIO.input(callback_flag) == 0
        if GPIO.input(callback_flag) != 0:
            break

    return green

try:
    raceAgain = "yes"
    while raceAgain == "yes" or raceAgain == "y":
        init_gpio()
        greentime = race()
        time.sleep(10)
        print"Reactiontime: ", round(roll_out_time -  greentime, 3)
        print"Do you want to raceagain (yes(y) or no(n))?"
        raceAgain = raw_input()
except KeyboardInterrupt:
    pass

print"Race Cancelled"
bus.write_byte(0x20, 0xFF)
GPIO.cleanup()
        
