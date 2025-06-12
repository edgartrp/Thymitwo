#!/usr/bin/env python3
import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)

pca.frequency = 50

def set_angle(ID, angle):
    servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
    servo_angle.angle = angle

if __name__ == "__main__":
    boucle = True
    while boucle:
        channel_input = input("channel :")
        if channel_input == "exit":
            break
        angle_input = input("angle :")
        if angle_input == "exit":
            break

        channel = int(channel_input)
        angle = int(angle_input)
        set_angle(channel, angle)
