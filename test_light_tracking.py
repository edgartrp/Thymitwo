import test_deplacement 
import time
import board
import adafruit_ads7830.ads7830 as ADC
from adafruit_ads7830.analog_in import AnalogIn

SPEED = 50
ANGLE = 45

i2c = board.I2C()
adc = ADC.ADS7830(i2c, 0x48)

light_left_sensor = AnalogIn(adc, 2)
light_right_sensor = AnalogIn(adc, 1)

# ?? Fonction de calibration
def calibrate(threshold_offset=50):
    print("Calibration")
    left = light_left_sensor.value
    right = light_right_sensor.value
    threshold = abs(left - right) + threshold_offset
    print(f"Calibration terminee. Seuil de tolerance = {threshold}")
    return threshold

if __name__ == "__main__":
    try:
        threshold = calibrate()

        while True:
            light_left = light_left_sensor.value
            light_right = light_right_sensor.value

            print(f"LDR Gauche = {light_left}, LDR Droite = {light_right}")

            if abs(light_right - light_left) < threshold:
                test_deplacement.forward(SPEED)
                print("Robot va tout droit")
                time.sleep(0.1)
            elif light_left > light_right:
                test_deplacement.turn_left(ANGLE)
                print(" Robot tourne a gauche")
                time.sleep(0.1)
            else:
                test_deplacement.turn_right(ANGLE)
                print("Robot tourne a droite")
                time.sleep(0.1)
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nInterruption clavier")

    finally:
        test_deplacement.stop()
        test_deplacement.reinitialize_angle()
        print("Fin du programme")
