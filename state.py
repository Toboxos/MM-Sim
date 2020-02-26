import RPi.GPIO as GPIO

pin_list = [2, 3, 4, 17, 27, 22, 10, 9, 11, 0, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 1, 12, 16, 20, 21]

def readState():
    state = {}

    for pin in pin_list:
        try:
            state[pin] = GPIO.input(pin)
        except Exception as e:
            print( e ) 
            state[pin] = -1

    return state

def printState(state):
    print( "{:>4}* *{}".format("3.3V", "5V") )
    print( "{:>4}* *{}".format(state[2], "5V") )
    print( "{:>4}* *{}".format(state[3], "GND") )
    print( "{:>4}* *{}".format(state[4], state[14]) )
    print( "{:>4}* *{}".format("GND", state[15]) )
    print( "{:>4}* *{}".format(state[17], state[18]) )
    print( "{:>4}* *{}".format(state[27], "GND") )
    print( "{:>4}* *{}".format(state[22], state[23]) )
    print( "{:>4}* *{}".format("3.3V", state[24]) )
    print( "{:>4}* *{}".format(state[10], "GND") )
    print( "{:>4}* *{}".format(state[9], state[25]) )
    print( "{:>4}* *{}".format(state[11], state[8]) )
    print( "{:>4}* *{}".format("GND", state[7]) )
    print( "{:>4}* *{}".format(state[0], state[1]) )
    print( "{:>4}* *{}".format(state[5], "GND") )
    print( "{:>4}* *{}".format(state[6], state[12]) )
    print( "{:>4}* *{}".format(state[13], "GND") )
    print( "{:>4}* *{}".format(state[19], state[16]) )
    print( "{:>4}* *{}".format(state[26], state[20]) )
    print( "{:>4}* *{}".format("GND", state[21]) )

if __name__ == "__main__":
    GPIO.setmode( GPIO.BCM )
    for pin in pin_list:
        GPIO.setup(pin, GPIO.IN)

    state = readState()
    printState( state )