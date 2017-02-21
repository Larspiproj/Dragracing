import RPi.GPIO as GPIO
import time
import subprocess
from time import sleep
from random import uniform
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Gran
STAGE_1                 = 5
STAGE_2                 = 12
GUL_1                   = 21
GUL_2                   = 20
GUL_3                   = 16
GRÖN                    = 26
RÖD                     = 19
GRAN = [STAGE_1,STAGE_2,GUL_1,GUL_2,GUL_3,GRÖN,RÖD]
START = [GUL_1,GUL_2,GUL_3]
# Stage och Transbreak
STAGE                   = 13
TRANSBREAK              = 6
STAGE_BREAK = [STAGE,TRANSBREAK]

# OUTPUTS
LCD_RS                  = 23
LCD_E                   = 24
LCD_D4                  = 17
LCD_D5                  = 18
LCD_D6                  = 27
LCD_D7                  = 22
OUTPUTS = [LCD_RS,LCD_E,LCD_D4,LCD_D5,LCD_D6,LCD_D7]

# INPUTS
LEFT                    = 8                 # CE0
UP                      = 7                 # CE1
DOWN                    = 10                # MOSI
RIGHT                   = 9                 # MISO
SELECT                  = 11                # SCLK
INPUTS = [LEFT,UP,DOWN,RIGHT,SELECT]

# HD44780 Controller Commands
CLEARDISPLAY            = 0x01
SETCURSOR               = 0x80

# LINE = [0x00,0x40,0x14,0x54]              # 20x4 display
LINE = [0x00,0x40]

# def Subett():
#     processett=subprocess.Popen(['aplay', 'topfueltvåmin.wav'])

def InitGran():
    for lampa in GRAN:
        GPIO.setup(lampa, GPIO.OUT, initial=0)
    for button in STAGE_BREAK:
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def Backlight():
    GPIO.setup(25, GPIO.OUT, initial=1)
    # global backlight
    # GPIO.setwarnings(False)
    # GPIO.setmode(GPIO.BCM)
    # backlight = GPIO.PWM(25, 500)
    # backlight.start(50)
    

def InitIO():
    for lcdLine in OUTPUTS:
        GPIO.setup(lcdLine, GPIO.OUT)
    for switch in INPUTS:
        GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# def CheckSwitches():
#     val1 = GPIO.input(LEFT)
#     val2 = GPIO.input(UP)
#     val3 = GPIO.input(DOWN)
#     val4 = GPIO.input(RIGHT)
#     val5 = GPIO.input(SELECT)
#     return (val1,val2,val3,val4,val5)

def PulseEnableLine():
    # pulse the LCD Enable line; used for clocking in data
    mSec = 0.0005		    # use half-millisecond delay
    time.sleep(mSec)		    # give time for inputs to settle
    GPIO.output(LCD_E, GPIO.HIGH)   # pulse E high
    time.sleep(mSec)
    GPIO.output(LCD_E, GPIO.LOW)    # return E low
    time.sleep(mSec)

def SendNibble(data):
    # sends upper 4 bits
    GPIO.output(LCD_D4, bool(data & 0x10))
    GPIO.output(LCD_D5, bool(data & 0x20))
    GPIO.output(LCD_D6, bool(data & 0x40))
    GPIO.output(LCD_D7, bool(data & 0x80))

def SendByte(data,charMode=False):
    # send one byte to LCD controller
    GPIO.output(LCD_RS,charMode)    # set mode: command vs char
    SendNibble(data)		    # send upper bits first
    PulseEnableLine()		    # pulse the enable line
    data = (data & 0x0F)<< 4        # shift 4 bits to left
    SendNibble(data)		    # send lower bits
    PulseEnableLine()		    # pulse the enable line

def InitLCD():
    # initialize the LCD controller & clear the display
    SendByte(0x33)                  # initialize
    SendByte(0x32)                  # set to 4-bit mode
    SendByte(0x28)                  # 2 line, 5x7 matrix
    SendByte(0x0C)                  # turn cursor off (0x0E to enable)
    SendByte(0x06)                  # shift cursor right
    SendByte(CLEARDISPLAY)

def SendChar(ch):
    SendByte(ord(ch),True)

def ShowMessage(string):
    # send string of characters to display at current cursor position
    for character in string:
        SendChar(character)

def GoToLine(row):
    # moves cursor to the given row
    # expects row values 0-1 for 16x2 display; 0-3 for 20x4 display
    addr = LINE[row]
    SendByte(SETCURSOR+addr)

def Race():
    global process
    process=subprocess.Popen(['aplay', 'topfuelburntrim.wav'])
    print("Testar Granen")
    GPIO.output(GRAN, 0)
    sleep(2)
    GPIO.output(GRAN, 1) 
    sleep(2)
    GPIO.output(GRAN, 0)
    
    print ("Pressing white button simulates STAGING")    
    print ("Red button is your TRANSBREAK RELEASE")

    global brake_released
    
    brake_released=time.time()
    sleep(1)
    time_ref=time.time()

    def my_callback(channel):
        print ("Transbreak released")
        global brake_released
        global startprocess
        brake_released=time.time()
        startprocess=subprocess.Popen(['aplay', 'topfuelstarttrim.wav'])
        GPIO.remove_event_detect(TRANSBREAK)

    GPIO.wait_for_edge(STAGE, GPIO.FALLING)
    GPIO.add_event_detect(TRANSBREAK, GPIO.FALLING, callback=my_callback, bouncetime=10000)
    print("Press CTRL-C to cancel race")
    try:
        sleep(uniform(2, 5))
        GPIO.output(STAGE_1, 1)
        sleep(uniform(2, 5))
        GPIO.output(STAGE_2, 1)    
        sleep(uniform(2, 5))
        GPIO.output(GUL_1, 1)
        GPIO.output(GUL_2, 1)
        GPIO.output(GUL_3, 1)
        sleep(0.4)
        GPIO.output(START, 0)
        GPIO.output(GRÖN, 1)
        green=time.time()
        sleep(0.1)                             # kolla om den behövs
        
        while True:
            brake_released <= time_ref
            if brake_released > time_ref:
                break
            
        reaction_time = round(brake_released - green, 3)
        if reaction_time<0:   
               GPIO.output(RÖD, 1)
        
        sleep(0.1)
        print(reaction_time) 
        
        GoToLine(0)
        ShowMessage("REACTIONTIME")
        GoToLine(1)
        ShowMessage (str(reaction_time))
    except KeyboardInterrupt:
        process.terminate()
        startprocess.terminate()
        GPIO.remove_event_detect(TRANSBREAK)
        print("Race cancelled")
        
raceAgain='yes'
while raceAgain=='yes' or raceAgain=='y' or raceAgain=='Y':
    InitGran()
    InitIO()
    InitLCD()
    Backlight()    
    Race()
    print("Do you want to race again?(yes(y) or no(n))")
    process.terminate()
    raceAgain=input()
                  
print("Race cancelled")
# backlight.stop()
SendByte(CLEARDISPLAY)
GPIO.cleanup()
