#!/usr/bin/python
import time
import Adafruit_CharLCD as LCD
import Adafruit_GPIO.MCP230xx as MCP
import RPi.GPIO as GPIO
import subprocess
from random import uniform
from smbus import SMBus
bus = SMBus(1)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


# Gran #################################
# STAGE_1                 = 5
# STAGE_2                 = 12
# YELLOW_1                = 21
# YELLOW_2                = 20
# YELLOW_3                = 16
# GREEN                   = 26
# RED                     = 19
# GRAN = [STAGE_1,STAGE_2,YELLOW_1,YELLOW_2,YELLOW_3,GREEN,RED]
# START = [YELLOW_1,YELLOW_2,YELLOW_3]

# Stage och Transbreak
STAGE                   = 13
TRANSBREAK              = 6
STAGE_BREAK = [STAGE,TRANSBREAK]

def Init_Stage_Brake():
    # for lampa in GRAN:
        # GPIO.setup(lampa, GPIO.OUT, initial=0)
    for button in STAGE_BREAK:
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)




# Define MCP pins connected to the LCD.
lcd_rs        = 0
lcd_en        = 1
lcd_d4        = 2
lcd_d5        = 3
lcd_d6        = 4
lcd_d7        = 5
lcd_red       = 6
lcd_green     = 7
lcd_blue      = 8

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Alternatively specify a 20x4 LCD.
# lcd_columns = 20
# lcd_rows    = 4

# Initialize MCP23017 device using its default 0x20 I2C address.
gpio = MCP.MCP23017()

# Alternatively you can initialize the MCP device on another I2C address or bus.
# gpio = MCP.MCP23017(0x24, busnum=1)

# Initialize the LCD using the pins
lcd = LCD.Adafruit_RGBCharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                              lcd_columns, lcd_rows, lcd_red, lcd_green, lcd_blue, gpio=gpio)

lcd.set_backlight(0)

def Race():
    global process
    process=subprocess.Popen(['aplay', 'topfuelburntrim.wav'])
    print("Testar Granen")
    lcd.clear()
    lcd.message('TESTING TREE')
    bus.write_byte(0x24, 0x00)
    time.sleep(3)
    bus.write_byte(0x24, 0xFF)
    lcd.clear()
    
    print ("Pressing white button simulates STAGING")    
    print ("Red button is your TRANSBREAK RELEASE")
    lcd.message('White btn STAGE\nRed btn START')

    global brake_released
    
    brake_released=time.time()
    time.sleep(1)
    time_ref=time.time()

    def my_callback(channel):
        print ("Transbreak released")
        global brake_released
        brake_released=time.time()
        startprocess=subprocess.Popen(['aplay', 'topfuelstarttrim.wav'])
        GPIO.remove_event_detect(TRANSBREAK)

    GPIO.wait_for_edge(STAGE, GPIO.FALLING)
    GPIO.add_event_detect(TRANSBREAK, GPIO.FALLING, callback=my_callback, bouncetime=10000)
    print("Press CTRL-C to cancel race")
    lcd.clear()
    lcd.message('CTRL-C to\ncancel race')
    try:
        time.sleep(uniform(2, 5))
        bus.write_byte(0x24, 0xFE)
        time.sleep(uniform(2, 5))
        bus.write_byte(0x24, 0xFC)
        time.sleep(uniform(2, 5))
        bus.write_byte(0x24, 0xE0)
        time.sleep(0.4)
        bus.write_byte(0x24, 0xDF)
        green=time.time()
        
        while True:
            brake_released <= time_ref
            if brake_released > time_ref:
                break
            
        reaction_time = round(brake_released - green, 3)
        if reaction_time<0:      
            bus.write_byte(0x24, 0x9F)
            
        time.sleep(0.1)
        print(reaction_time) 
        

        # Print reactiontime LCD
        lcd.clear()
        lcd.message('REACTIONTIME\n'+str(reaction_time))
        time.sleep(5)

    except KeyboardInterrupt:
        process.terminate()
        GPIO.remove_event_detect(TRANSBREAK)
        print("Race cancelled")
        lcd.clear()
        lcd.message('Race cancelled')

raceAgain='yes'
while raceAgain=='yes' or raceAgain=='y' or raceAgain=='Y':
    print('test1')
    lcd.clear()
    bus.write_byte(0x24, 0xFF)
    Init_Stage_Brake()
    Race()
    print('test2')
    lcd.clear()
    # bus.write_byte(0x24, 0xFF)
    print("Do you want to race again?(yes(y) or no(n))")
    # lcd.clear()
    lcd.message('Race again?')
    time.sleep(2)
    lcd.clear()
    lcd.message('yes(y) or no(n)')
    # process.terminate()
    raceAgain=raw_input()

print("Race cancelled")
process.terminate()
lcd.clear()
lcd.message('Race cancelled')
lcd.clear()
bus.write_byte(0x24, 0xFF)
# Turn backlight off (omvänd polaritet).
lcd.set_backlight(1)
GPIO.cleanup()
