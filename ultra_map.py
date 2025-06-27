import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from gpiozero import DistanceSensor

# === Configuration ===
CENTER_ANGLE = 90      # front-facing angle
OFFSET_ANGLE = 60      # side scan offset in degrees
THRESHOLD_MM = 200     # detection threshold in millimeters
PAUSE = 0.5            # delay after each movement (s)
SERVO_CHANNEL = 1      # PCA9685 channel for the servo
TRIG_PIN = 23
ECHO_PIN = 24

# === Hardware initialization ===
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIG_PIN, max_distance=2)

def set_angle(angle: float) -> None:
    s = servo.Servo(
        pca.channels[SERVO_CHANNEL],
        min_pulse=500, max_pulse=2400, actuation_range=180
    )
    s.angle = angle

def measure_distance() -> float:
    return sensor.distance * 1000

def check_sides() -> None:
    # Scan right
    set_angle(CENTER_ANGLE + OFFSET_ANGLE)
    dist_right = measure_distance()
    time.sleep(PAUSE)
    # Scan left
    set_angle(CENTER_ANGLE - OFFSET_ANGLE)
    dist_left = measure_distance()
    time.sleep(PAUSE)
    # Return to center
    set_angle(CENTER_ANGLE)
    time.sleep(PAUSE)

    # Display results
    print(f"? Right: {dist_right:.0f} mm, Left: {dist_left:.0f} mm")
    if dist_right < THRESHOLD_MM and dist_left >= THRESHOLD_MM:
        print("  Object is to the right.")
    elif dist_left < THRESHOLD_MM and dist_right >= THRESHOLD_MM:
        print("  Object is to the left.")
    elif dist_left < THRESHOLD_MM and dist_right < THRESHOLD_MM:
        print("  Object spans both sides.")
    else:
        print("  Object is only in front, not extending sideways.")

def main():
    try:
        print("Starting continuous front scan. Press Ctrl-C to stop.")
        set_angle(CENTER_ANGLE)
        time.sleep(PAUSE)
        
        while True:
            dist_front = measure_distance()
            print(f"Front: {dist_front:.0f} mm", end=' ')
            
            if dist_front < THRESHOLD_MM:
                print(" ? Obstacle detected!")
                time.sleep(PAUSE)
                check_sides()
            else:
                print("  (clear ahead)")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nScan stopped by user.")
    finally:
        pca.deinit()

if __name__ == "__main__":
    main()
