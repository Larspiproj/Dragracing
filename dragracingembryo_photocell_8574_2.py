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
false_start             = 21        # temporarly to indicate "false start"
FLAGS = [photocell_stage1,photocell_stage2,photocell_1000,callback_flag,
         yellow_flag,green_flag,false_start]

def init_gpio():
    GPIO.setup(photocell_stage1, GPIO.IN)
    GPIO.setup(photocell_stage2, GPIO.IN)
    GPIO.setup(photocell_1000, GPIO.IN)
    GPIO.setup(callback_flag, GPIO.OUT, initial=0)
    GPIO.setup(yellow_flag, GPIO.OUT, initial=0)
    GPIO.setup(green_flag, GPIO.OUT, initial=0)
    GPIO.setup(false_start, GPIO.OUT, initial=0)
        
def callback_roll_out(channel):
    print"callback_roll_out"
    global roll_out_time
    roll_out_time = time.time()
    GPIO.output(callback_flag, 1)
    if GPIO.input(green_flag) == 0 and GPIO.input(yellow_flag) == 1:
        GPIO.output(false_start, 1)
        print("RED")
        bus.write_byte(0x20, 0x20)
    elif GPIO.input(green_flag) == 0 and GPIO.input(yellow_flag) == 0:
        GPIO.output(false_start, 1)             # RED light on here
        print("RED")
        bus.write_byte(0x20, 0xBC)
    # check YELLOW_FLAG ##########################################################
                
def callback_1000(channel):
    print"callback_1000"
    global time_1000
    time_1000 = time.time()
        
def race():    
    GPIO.wait_for_edge(photocell_stage1, GPIO.FALLING)       # STAGE 1
    print("STAGE_1")
    bus.write_byte(0x20, 0xFE)
    
    time.sleep(1)
    GPIO.wait_for_edge(photocell_stage2, GPIO.FALLING)       # STAGE 2
    GPIO.remove_event_detect(photocell_stage2)
    print("STAGE_2")
    bus.write_byte(0x20, 0xFC)
    
    GPIO.add_event_detect(photocell_stage2,GPIO.RISING,
                          callback=callback_roll_out, bouncetime=1000)
    GPIO.add_event_detect(photocell_1000, GPIO.FALLING,
                              callback=callback_1000, bouncetime=1000)

    time.sleep(3)
    
    print("YELLOW")
    # if false start keep red light on
    if GPIO.input(false_start) == 1:
        bus.write_byte(0x20, 0x20)
    else:
        # set YELLOW_FLAG ############################################################
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
time_1000 = 0
init_gpio()
greentime = race()
time.sleep(10)
print"Green: ", greentime
print"Roll_out_time: ", roll_out_time
if time_1000 != 0:
        print"Time_1000: ", time_1000

bus.write_byte(0x20, 0xFF)
GPIO.cleanup()
        
