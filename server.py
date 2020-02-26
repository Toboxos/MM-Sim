import asyncio
from aioconsole import ainput
import websockets
import json
import threading

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
angleOut = 0
angleCw = 45

msg_out = { 'msg': 'out', 'angle': 0.0 }

sockets = []
async def hello(websocket, path):
    #print( "New socket" )
    sockets.append( websocket )
    async for message in websocket:
        pass

async def check():
    while True:
        i = await ainput("angle:")
        msg_out['angle'] = float( i )

        for s in sockets:
            if s.closed:
                continue
            await s.send( json.dumps(msg_out) )


# Outler or Colorwheel step
def doStep(channel):
    global angleCw

    # Step colorwheel
    if channel == STEP_CW:
        angleCw += 360 / 1600   # 1600 Steps for 360°
        if angleCw > 360:
            angleCW -= 360
        updateSensors()

def updateSensors():

    # Colorwheel Hallsensor
    if angleCw > 358 or angleCw < 2:        #   0deg
        GPIO.output( HALL_CW, 0 )
    elif angleCw > 88 and angleCw < 92:     #  90deg
        GPIO.output( HALL_CW, 0)
    elif angleCw > 178 and angle < 182:     # 180deg
        GPIO.output( HALL_CW, 0)
    elif angleCw > 268 and angle < 272:     # 270deg
        GPIO.output( HALL_CW, 0 )
    else:
        GPIO.output( HALL_CW, 1 )

    # Outlet Hallsensor
    if angleOut > 315 or angleOut < 45:
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


# Stepping colorwheel & outlet
GPIO.add_event_detect( STEP_CW, GPIO.RISING, callback=doStep )
GPIO.add_event_detect( STEP_OUT, GPIO.RISING, callback=doStep )

updateSensors()





threading.Thread(target=check).start()
server = websockets.serve(hello, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_until_complete(check())
asyncio.get_event_loop().run_forever()