from picamera2 import Picamera2
import cv2
import numpy as np
import math, time

# ---------- PARAMETRES ----------
MIN_AREA  = 4000      # surface mini contour (px)
EPSILON   = 0.03      # precision approximation polygonale
# ---------------------------------

def arrow_orientation(cnt):
    M = cv2.moments(cnt)
    if M["m00"] == 0:
        return None
    cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])

    # pointe de la fleche = sommet le plus loin du centre
    far = max(cnt[:, 0, :], key=lambda p: cv2.norm(p - (cx, cy)))
    dx, dy = far[0] - cx, far[1] - cy  # dans l'espace image (y vers le bas)

    # axe principal : horizontal ou vertical
    if abs(dx) > abs(dy):               # fleche (theorique) horizontale
        return "GAUCHE" if dx > 0 else "DROITE"   # inversion voulue
    else:                               # fleche (theorique) verticale
        return "HAUT" if dy > 0 else "BAS"        # inversion voulue

def detect_arrows(gray):
    cnts, _ = cv2.findContours(
        cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150),
        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for c in cnts:
        if cv2.contourArea(c) < MIN_AREA:
            continue
        approx = cv2.approxPolyDP(c, EPSILON * cv2.arcLength(c, True), True)
        if len(approx) < 7:
            continue
        direction = arrow_orientation(approx)
        if direction:
            yield direction

def main():
    pic = Picamera2()
    cfg = pic.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    pic.configure(cfg)
    pic.start()
    time.sleep(1)

    print("? Detection de fleches en cours  (Ctrl-C pour quitter)")
    try:
        while True:
            frame = pic.capture_array()
            gray  = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)  # camera en RGB
            for dir_txt in detect_arrows(gray):
                print(f"{dir_txt} detectee")
    except KeyboardInterrupt:
        print("\nArret demande, fermeture")
    finally:
        pic.close()

if __name__ == "__main__":
    main()
