import serial

import time

import os

LAPTOP_PORT = '/dev/ttyUSB0'
PI_PORT = '/dev/tty/AMA0'

TTY_PORT = LAPTOP_PORT

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False


OP_MODE = 'RSSI'
OP_MODE = 'DATA'

if is_raspberrypi():
    TTY_PORT = PI_PORT
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)
    state = GPIO.input(18)
    if state: #state is hi, we measure rssi (this rhymes)
        OP_MODE = 'RSSI'
    else:
        OP_MODE = 'DATA'



def read_packet(serial, file):
    data = ser.readline()
    line = str(time.time())+", "+data.decode('utf-8')
    print(line)
    file.write(line)
    return

def read_rssi(serial, file):
    data = ser.read(in_waiting)
    for byte in data:
        line = str(time.time())+", "+str(-(256-byte))
        print(line)
        file.write(line+"\n")

def read_serial_data(port=TTY_PORT, baudrate=9600):
    try:
        with open("dataout.csv", "a") as file:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                print(f"Connected to {port} at {baudrate} baud rate.")
                while True:
                    if ser.in_waiting > 0:
                        if OP_MODE == "RSSI":
                            read_rssi(serial, file)
                        else:
                            read_packet(serial, file)
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    read_serial_data()

