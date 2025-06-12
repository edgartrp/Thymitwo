#!/usr/bin/env python3
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

# motor_EN_A: Pin7  |  motor_EN_B: Pin11
# motor_A:  Pin8,Pin10    |  motor_B: Pin13,Pin12


MOTOR_IN1 =  15      #Define the positive pole of M1
MOTOR_IN2 =  14      #Define the negative pole of M1
  
def scale_value(x, in_min, in_max, out_min, out_max):
  """Scale ``x`` from one range to another."""
  return (x - in_min)/(in_max - in_min) *(out_max - out_min) + out_min


i2c = busio.I2C(SCL, SDA)
pwm_motor = PCA9685(i2c, address=0x5f)
pwm_motor.frequency = 50

motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_IN1],pwm_motor.channels[MOTOR_IN2] )
motor1.decay_mode = (motor.SLOW_DECAY)

def Motor(direction,motor_speed):
  if motor_speed > 100:
    motor_speed = 100
  elif motor_speed < 0:
    motor_speed = 0
  speed = scale_value(motor_speed, 0, 100, 0, 1.0)
  if direction == -1:
    speed = -speed
  motor1.throttle = speed

def destroy():
  motor1.throttle = 0
  pwm_motor.deinit()


if __name__ == '__main__':
	try:
		speed_set = 0

		# Move forward
		print("Forward")
		for i in range(100):
			speed_set+=1
			Motor(1, speed_set)
			time.sleep(0.01)
		time.sleep(1)
		
		# Slow down
		print("Slow down")
		for i in range(100):
			speed_set-=1
			Motor(1 ,speed_set)
			time.sleep(0.01)
		time.sleep(1)
		
		
		# Move backward
		print("Backward")
		for i in range(100):
			speed_set+=1
			Motor(-1, speed_set)
			time.sleep(0.01)
		time.sleep(1)
		
		# Slow down
		print("Slow down")
		for i in range(100):
			speed_set-=1
			Motor(-1 ,speed_set)
			time.sleep(0.01)
		time.sleep(1)
		
		print("Fin du programme")
		destroy()
	except KeyboardInterrupt:
		destroy()

