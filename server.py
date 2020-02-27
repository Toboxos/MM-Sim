import asyncio
main_event_loop = asyncio.get_event_loop()
from aioconsole import ainput
import websockets
import json
import threading
import time
import random
random.seed( time.time() )

from state import readState, printState
import RPi.GPIO as GPIO
GPIO.setmode( GPIO.BCM )

# Pin defintions
BTN1 = 8
BTN2 = 9
BTN3 = 10

RST_OUT = 11
STEP_OUT = 12
DIR_OUT = 26

STEP_CW = 13
RST_CW = 17
DIR_CW = 16

FEED = 19

HALL_CW = 20
HALL_OUT = 21

COLOR0 = 22
COLOR1 = 23
COLOR2 = 24

SLP = 27


# Control Variables
angleOut = 120
angleCw = 45


# Color definitions
NONE = 0
RED = 1
GREEN = 2
BLUE = 3
BROWN = 4
ORANGE = 5
YELLOW = 6
COLORS = [RED, GREEN, BLUE, BROWN, ORANGE, YELLOW]

# M&Ms in ColorWheel
cw_mm = [NONE, NONE, NONE, NONE]

sockets = []
async def hello(websocket, path):
    print( "New socket" )
    sockets.append( websocket )
    
    while True:
        await websocket.recv()


async def update_loop():
    while True:
        msg = {
            'angleOut': angleOut,
            'angleCw': angleCw,
            'mm': cw_mm
        }

        for s in sockets:
            if s.closed:
                continue
            await s.send( json.dumps(msg) )

        await asyncio.sleep(0.05)


# Outler or Colorwheel step
def doStep(channel):
    global angleCw
    global angleOut

    # Coprocessor is in sleep mode
    if GPIO.input(SLP) == 0:
        return

    # Step colorwheel and RST is high
    if channel == STEP_CW and GPIO.input(RST_CW) == 1:
        if GPIO.input(DIR_CW) == 0:
            angleCw += 360 / 1600   # 1600 Steps for 360°
        else:
            angleCw -= 360 / 1600

        if angleCw > 360:
            angleCw -= 360
        elif angleCw < 0:
            angleCw += 360

    # Step Outlet and RST is high
    elif channel == STEP_OUT and GPIO.input(RST_OUT) == 1:
        if GPIO.input(DIR_OUT) == 0:
            angleOut += 360 / 400    # 400 Steps for 360°
        else:
            angleOut -= 360 / 400

        if angleOut > 360:
            angleOut -= 360
        elif angleOut < 0:
            angleOut += 360

    updateSensors()

def updateSensors():

    posAtColorSensor = -1

    # Colorwheel Hallsensor (2deg tolerance)
    if angleCw > 358 or angleCw < 2:        #   0deg
        GPIO.output( HALL_CW, 0 )
    elif angleCw > 88 and angleCw < 92:     #  90deg
        GPIO.output( HALL_CW, 0)
    elif angleCw > 178 and angleCw < 182:     # 180deg
        GPIO.output( HALL_CW, 0)
    elif angleCw > 268 and angleCw < 272:     # 270deg
        GPIO.output( HALL_CW, 0 )
    else:
        GPIO.output( HALL_CW, 1 )

    # Colorwheel color sensor (4deg tolerance)
    if angleCw > 356 or angleCw < 4:        #   0deg
        posAtColorSensor = 1
    elif angleCw > 86 and angleCw < 94:     #  90deg
        posAtColorSensor = 0
    elif angleCw > 176 and angleCw < 184:     # 180deg
        posAtColorSensor = 3
    elif angleCw > 266 and angleCw < 274:     # 270deg
        posAtColorSensor = 2

    # Colorwheel is aligned to colorsensor
    if posAtColorSensor != -1:

        # Output color
        color = cw_mm[ posAtColorSensor % 4 ]
        GPIO.output( COLOR0, (color >> 0) & 0x1 )
        GPIO.output( COLOR1, (color >> 1) & 0x1 )
        GPIO.output( COLOR2, (color >> 2) & 0x1 )

        # Fill M&M to colorwheel
        if cw_mm[ (posAtColorSensor - 1) % 4 ] == NONE:
            cw_mm[ (posAtColorSensor - 1) % 4 ] = COLORS[ random.randint(0, 5) ]    

        # Let M&M fall out
        cw_mm[ (posAtColorSensor + 1) % 4 ] = NONE        

    else:
        GPIO.output( COLOR0, 0 )
        GPIO.output( COLOR1, 0 )
        GPIO.output( COLOR2, 0 )



    # Outlet Hallsensor
    if angleOut > 323 or angleOut < 37:
        GPIO.output( HALL_OUT, 0 )
    else:
        GPIO.output( HALL_OUT, 1 )




# Buttons as output
GPIO.setup( BTN1, GPIO.OUT )
GPIO.setup( BTN2, GPIO.OUT )
GPIO.setup( BTN3, GPIO.OUT )

# Color Bits as output
GPIO.setup( COLOR0, GPIO.OUT )
GPIO.setup( COLOR1, GPIO.OUT )
GPIO.setup( COLOR2, GPIO.OUT )

# Hall Sensors as output
GPIO.setup( HALL_CW, GPIO.OUT )
GPIO.setup( HALL_OUT, GPIO.OUT )

# Motor steps as input
GPIO.setup( STEP_CW, GPIO.IN )
GPIO.setup( STEP_OUT, GPIO.IN )

# Motor direction as input
GPIO.setup( DIR_CW, GPIO.IN )
GPIO.setup( DIR_OUT, GPIO.IN )

# RST Pins
GPIO.setup( RST_CW, GPIO.IN )
GPIO.setup( RST_OUT, GPIO.IN )


# Stepping colorwheel & outlet
GPIO.add_event_detect( STEP_CW, GPIO.RISING, callback=doStep )
GPIO.add_event_detect( STEP_OUT, GPIO.RISING, callback=doStep )

updateSensors()



server = websockets.serve(hello, "*", 8888)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_until_complete( update_loop() )
asyncio.get_event_loop().run_forever()