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
    while(boucle):
        channel = int(input("channel :"))
        angle = int(input("angle :"))
        set_angle(channel, angle)
        if channel=="exit" or angle=="exit":
            boucle = False
