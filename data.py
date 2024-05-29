import serial

import time

import os


LAPTOP_PORT = '/dev/ttyUSB0'
PI_PORT = '/dev/ttyAMA0'

TTY_PORT = LAPTOP_PORT

def is_raspberrypi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception as e:
        print(e)
        pass
    return False


OP_MODE = 'DATA'
OP_MODE = 'RSSI'

PIN_STATE = 0

if is_raspberrypi():
    print('this is a raspberry pi!')
    print("waiting for some hardware...")
    try:
        for i in range(0, 10):
            print("waiting...")
            time.sleep(i)
    except:
        print("exited loop...")
    TTY_PORT = PI_PORT
    import RPi.GPIO as GPIO
    print("checking hardware OP state...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)
    state = GPIO.input(18)
    PIN_STATE = state
    if state: #state is hi, we measure rssi (this rhymes)
        print("pin is high, RSSI!")
        OP_MODE = 'RSSI'
    else:
        print("pin is low, dataooo")
        OP_MODE = 'DATA'


def set_op_mode():
    if is_raspberrypi():
        global PIN_STATE
        global OP_MODE
        new_state = GPIO.input(18)
        PIN_STATE = new_state
        if PIN_STATE:
            #print("pin is high, rssi")
            OP_MODE = 'RSSI'
        else:
            #print("pin is ow, datooo")
            OP_MODE = 'DATA'


def read_packet(ser, file):
    data = ser.readline()
    line = str(time.time())+", "+data.decode('utf-8')
    print(line)
    file.write(line)
    return

def read_rssi(ser, file):
    data = ser.read(ser.in_waiting)
    for byte in data:
        line = str(time.time())+", "+str(-(256-byte))
        print(line)
        file.write(line+"\n")
        time.sleep(.01)

def read_serial_data(port=TTY_PORT, baudrate=9600):
    try:
        with open("dataout.csv", "a") as file:
            with serial.Serial(port, baudrate, timeout=5) as ser:
                print(f"Connected to {port} at {baudrate} baud rate.")
                while True:
                    time.sleep(.01)
                    if ser.in_waiting > 0:
                        set_op_mode()
                        try:
                            if OP_MODE == "RSSI":
                                read_rssi(ser, file)
                            else:
                                    read_packet(ser, file)
                        except:
                            pass
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    read_serial_data()

