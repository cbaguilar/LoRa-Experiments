import serial
import time
import os
import requests
import json

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
PIN_STATE = 0

if is_raspberrypi():
    print('This is a Raspberry Pi!')
    print("Waiting for some hardware...")
    try:
        for i in range(0, 10):
            print("Waiting...")
            time.sleep(i)
    except:
        print("Exited loop...")
    TTY_PORT = PI_PORT
    import RPi.GPIO as GPIO
    print("Checking hardware OP state...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN)
    state = GPIO.input(18)
    PIN_STATE = state
    if state:  # State is high, we measure RSSI
        print("Pin is high, RSSI!")
        OP_MODE = 'RSSI'
    else:
        print("Pin is low, dataooo")
        OP_MODE = 'DATA'

def set_op_mode():
    if is_raspberrypi():
        global PIN_STATE
        global OP_MODE
        new_state = GPIO.input(18)
        PIN_STATE = new_state
        if PIN_STATE:
            OP_MODE = 'RSSI'
        else:
            OP_MODE = 'DATA'

def send_post_request(data_type, data_value):
    url = "http://postgres.svwaternet.org:8080/data"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "data_value": data_value,
        "data_type": data_type,
        "source_ip": "127.0.0.1"  # Replace with actual source IP if necessary
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print(f"Failed to send data: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

def read_packet(ser, file):
    data = ser.readline()
    line = str(time.time()) + ", " + data.decode('utf-8')
    print(line)
    file.write(line)
    send_post_request("packet_message", data.decode('utf-8').strip())
    return

def read_rssi(ser, file):
    data = ser.read(ser.in_waiting)
    for byte in data:
        rssi_value = -(256-byte)
        line = str(time.time()) + ", " + str(rssi_value)
        print(line)
        file.write(line + "\n")
        send_post_request("signal_strength", rssi_value)
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
                        except Exception as e:
                            print(f"Error reading data: {e}")
    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Stopped by user.")

if __name__ == "__main__":
    read_serial_data()

