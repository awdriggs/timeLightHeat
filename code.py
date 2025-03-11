import time
import board
import math
import digitalio

# for the light sensor
import busio  # Use busio for I2C communication
import adafruit_bh1750

# for the servo
from digitalio import DigitalInOut, Direction, Pull
import pwmio
from adafruit_motor import servo #make sure to include the library on the pico

# Define I2C using specific pins for the Raspberry Pi Pico
i2c = busio.I2C(scl=board.GP17, sda=board.GP16)

# Servo setup
pwm_servo = pwmio.PWMOut(board.GP28, duty_cycle=2 ** 15, frequency=50)
heat_servo = servo.Servo(pwm_servo, min_pulse=500, max_pulse=2200)  # tune pulse for specific servo

# Initialize the sensor
sensor = adafruit_bh1750.BH1750(i2c)

# Define stepper motor control pins
AIN1 = digitalio.DigitalInOut(board.GP15)
AIN2 = digitalio.DigitalInOut(board.GP14)
BIN1 = digitalio.DigitalInOut(board.GP12)
BIN2 = digitalio.DigitalInOut(board.GP13)

# Set all pins to output mode
for pin in [AIN1, AIN2, BIN1, BIN2]:
    pin.direction = digitalio.Direction.OUTPUT

# Stepper motor sequence (Full-step mode)
step_sequence = [
    (1, 0, 1, 0),  # Step 1
    (0, 1, 1, 0),  # Step 2
    (0, 1, 0, 1),  # Step 3
    (1, 0, 0, 1)   # Step 4
]


mLux = 0 #global maximum lux value, for testing

def convert_light_degrees():
    global mLux
    #take a reading
    lux = sensor.lux
    print("%.2f Lux" % lux)
    mLux = max(lux, mLux)
    print("%.2f max" % mLux)
    #map the reading between 0 and 90 degrees
    # maxLux = 2000 #tune this number
    maxLux = 30000 #outdoor value
    minLux = 0
    amt = math.floor((lux - minLux)/(maxLux - minLux) * (90 - 0) + 0)
    print("range is +- %.2f" % amt)
    sweep(amt)
    #sweep this amount

def sweep(a):
    amount = min(a, 90) #keep it in range no matter what

    heat_servo.angle  = 90 - amount #home
    time.sleep(0.1) #give a beat to get to the min
    for angle in range(90 - amount, 90 + amount, 1):
        # print(angle)
        # print("%.2f degrees" % angle)
        heat_servo.angle = angle
        time.sleep(0.01)
    time.sleep(0.1) #give a beat to get to the max
    heat_servo.angle  = 90 #home

def step_motor(steps, delay=0.01, reverse=False):
    """Rotate the stepper motor forward or backward."""
    sequence = step_sequence[::-1] if reverse else step_sequence  # Reverse if needed

    for _ in range(steps):
        for step in sequence:
            AIN1.value, AIN2.value, BIN1.value, BIN2.value = step
            time.sleep(delay)


while True:
    convert_light_degrees()
    step_motor(10, delay=0.01, reverse=True)  # Moving backward
    # time.sleep(0.01)
    # time.sleep(0.5)

