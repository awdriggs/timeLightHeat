import time
import board
import math

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

def convert_light_degrees():
    #take a reading
    lux = sensor.lux
    print("%.2f Lux" % lux)
    #map the reading between 0 and 90 degrees
    maxLux = 2000 #tune this number
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
        print("%.2f degrees" % angle)
        heat_servo.angle = angle
        time.sleep(0.01)
    time.sleep(0.1) #give a beat to get to the max
    heat_servo.angle  = 90 #home

while True:
    convert_light_degrees()
    # time.sleep(0.5)

