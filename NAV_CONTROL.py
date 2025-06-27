import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor, servo
from gpiozero import InputDevice

# === Constants ===
MOTOR_IN1 = 15           # Positive pole for DC motor
MOTOR_IN2 = 14           # Negative pole for DC motor
SERVO_CHANNEL = 0        # Channel for servo on PCA9685
SERVO_MIN_PULSE = 500    # Minimum pulse
SERVO_MAX_PULSE = 2400   # Maximum pulse
SERVO_RANGE = 180        # Servo range
ROTATION_TIME = 0.25     # 0.15 s for 60 degrees

LINE_PIN_LEFT = 22
LINE_PIN_MIDDLE = 27
LINE_PIN_RIGHT = 17

# === Sensor Initialization ===
left_sensor = InputDevice(pin=LINE_PIN_LEFT)
middle_sensor = InputDevice(pin=LINE_PIN_MIDDLE)
right_sensor = InputDevice(pin=LINE_PIN_RIGHT)

# === Hardware Initialization ===
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50

# Initialize DC Motor
motor1 = motor.DCMotor(pca.channels[MOTOR_IN1], pca.channels[MOTOR_IN2])
motor1.decay_mode = motor.SLOW_DECAY

# Initialize Servo
servo1 = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=SERVO_MIN_PULSE,
    max_pulse=SERVO_MAX_PULSE,
    actuation_range=SERVO_RANGE
)

# === Sensor Functions ===
def read_sensors() -> tuple[int, int, int]:
    return left_sensor.value, middle_sensor.value, right_sensor.value

# === Motor Control Functions ===
def forward(speed: float) -> None:
    value = max(0, min(100, speed))
    motor1.throttle = -(value / 100.0)

def backward(speed: float) -> None:
    value = max(0, min(100, speed))
    motor1.throttle = (value / 100.0)

def stop() -> None:
    motor1.throttle = 0

# === Servo Control Functions ===
def turn(angle: float) -> None:
    if 40 <= angle <= 140:
        servo1.angle = angle
        time.sleep(ROTATION_TIME)
    else:
        raise ValueError("Angle must be between 40 and 140")

# === Global Cleanup ===
def kill_all() -> None:
    left_sensor.close()
    middle_sensor.close()
    right_sensor.close()
    stop()
    pca.channels[SERVO_CHANNEL].duty_cycle = 0
    pca.deinit()

# === Main Test Function ===		
def test_speed(low: int = 0, high: int = 21, delay: float = 4.0) -> None:
    try:
        turn(140)
        for speed in range(low, high + 1):
            backward(speed)
            print(f"[TEST_SPEED] Vitesse : {speed}")
            time.sleep(delay)
    except Exception as exc:
        print(f"[ERREUR] test_speed : {exc}")
    finally:
        print("Nettoyage des ressources")
        kill_all()
        print("Test termine.")


        
def main() -> None:
    try:
        print("Testing forward at 50% speed...")
        forward(50)
        time.sleep(2)
        stop()

        print("Testing backward at 50% speed...")
        backward(50)
        time.sleep(2)
        stop()

        print("Testing servo angles: 40, 90, 140")
        for angle in (40, 90, 140):
            print(f"Turning to {angle}")
            turn(angle)
            time.sleep(1)

        print("Reading line sensors...")
        values = read_sensors()
        print(f"Sensor values (left, middle, right): {values}")

    except Exception as e:
        print(f"Error during main test: {e}")

    finally:
        print("Cleaning up resources...")
        kill_all()
        print("Test complete.")

if __name__ == "__main__":
    test_speed()
