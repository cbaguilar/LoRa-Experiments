import serial

import time

import os

def read_serial_data(port='/dev/ttyUSB0', baudrate=9600):
    try:
        with open("dataout.csv", "a") as file:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                print(f"Connected to {port} at {baudrate} baud rate.")
                while True:
                    if ser.in_waiting > 0:
                        data = ser.readline()
                        
                        line = str(time.time())+", "+data.decode('utf-8')
                        print(line)
                        file.write(line)
                        continue
                        for byte in data:
                            #line = str(time.time())+", "+str(-(256-byte))
                            print(line)
                            #file.write(line+"\n")
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    read_serial_data()

