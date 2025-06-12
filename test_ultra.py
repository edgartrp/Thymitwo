from gpiozero import DistanceSensor
from time import sleep

Tr = 23
Ec = 24
sensor = DistanceSensor(echo=Ec, trigger=Tr, max_distance=2)

if __name__ == "__main__":
    rep = 0
    while (rep < 5):
        rep += 1
        dist_m = sensor.distance
        if (dist_m > 0.5):
            print("Aucune detection")
        else:
            distance_mm = dist_m * 1000 
            print("Objet detecte a %d mm " %(distance_mm))

        sleep(5)
    print("Fin du programme")
