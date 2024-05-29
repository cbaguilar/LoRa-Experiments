

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN)

try:
    while True:
        state=GPIO.input(18)
        print(state)
        time.sleep(1)
except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
