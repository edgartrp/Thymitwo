import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from gpiozero import DistanceSensor

# Initialize servo controller
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50


def set_angle(channel, angle):
    """Rotate servo on given channel to angle."""
    servo_angle = servo.Servo(
        pca.channels[channel], min_pulse=500, max_pulse=2400, actuation_range=180
    )
    servo_angle.angle = angle


def scan_environment(
    start_angle=0,
    end_angle=180,
    step=10,
    servo_id=0,
    trig_pin=23,
    echo_pin=24,
    pause=0.5,
):
    """Rotate the servo and measure distance for each angle."""
    sensor = DistanceSensor(echo=echo_pin, trigger=trig_pin, max_distance=2)
    readings = []
    for angle in range(start_angle, end_angle + 1, step):
        set_angle(servo_id, angle)
        time.sleep(pause)
        distance_mm = sensor.distance * 1000
        readings.append((angle, distance_mm))
    pca.deinit()
    return readings


def print_map(readings):
    """Print angle-to-distance mapping."""
    print("Angle (deg) | Distance (mm)")
    for angle, distance in readings:
        print(f"{angle:10d} | {distance:10.1f}")


if __name__ == "__main__":
    result = scan_environment()
    print_map(result)
