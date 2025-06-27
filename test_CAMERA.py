#!/usr/bin/env python3
# arrow_detector_modular.py

from picamera2 import Picamera2
import cv2, numpy as np, math, time

# ---------- PARAMTRES AJUSTER ----------
MIN_AREA  = 4000
EPSILON   = 0.03
COLOR_BOUNDS = {                 # plages HSV, adapte-les  ton clairage
    "red":   ((0,120,70),  (10,255,255)),
    "blue":  ((100,150,50),(140,255,255)),
    "green": ((40,40,40),  (80,255,255)),
}
# ------------------------------------------

def detect_arrows(gray):
    """Renvoie la liste (cnt, direction, bbox) des flches trouves."""
    edges = cv2.Canny(cv2.GaussianBlur(gray,(5,5),0), 50, 150)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)), 2)
    cnts,_ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    arrows = []
    for c in cnts:
        if cv2.contourArea(c) < MIN_AREA: continue
        approx = cv2.approxPolyDP(c, EPSILON*cv2.arcLength(c,True), True)
        if len(approx) < 7: continue
        dir_txt = arrow_orientation(approx)
        if dir_txt:
            arrows.append( (approx, dir_txt, cv2.boundingRect(approx)) )
    return arrows

def arrow_orientation(cnt):
    """Retourne left/right/up/down ou None selon le contour."""
    M=cv2.moments(cnt);  m00=M["m00"]
    if m00==0: return None
    cx,cy=int(M["m10"]/m00), int(M["m01"]/m00)
    far=max(cnt[:,0,:], key=lambda p: cv2.norm(p-(cx,cy)))
    ang=math.degrees(math.atan2(cy-far[1], far[0]-cx))
    if -30<=ang<=30: return "right"
    if ang>=150 or ang<=-150: return "left"
    if 60<=ang<=120: return "up"
    if -120<=ang<=-60: return "down"

def dominant_color(bgr_roi):
    hsv = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.mean(hsv)[:3]
    for name,(lo,hi) in COLOR_BOUNDS.items():
        if lo[0]<=h<=hi[0] and lo[1]<=s<=hi[1] and lo[2]<=v<=hi[2]:
            return name
    return "unknown"

# ---------- INITIALISATION CAMeRA ----------
pic = Picamera2()
cfg = pic.create_preview_configuration(
        main = {"size": (640,480), "format": "RGB888"})  # pixels B,G,R
pic.configure(cfg)
pic.start();  time.sleep(1)
# ------------------------------------------

try:
    while True:
        bgr = pic.capture_array()          # OpenCV voit bien (B,G,R)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        for cnt, direction, (x,y,w,h) in detect_arrows(gray):
            color = dominant_color(bgr[y:y+h, x:x+w])

            cv2.drawContours(bgr, [cnt], -1, (0,255,0), 2)
            cv2.putText(bgr, f"{direction}|{color}", (x, y-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        cv2.imshow("Arrow + Color", bgr)
        if cv2.waitKey(1) == 27: break      # ESC pour quitter
finally:
    pic.close()
    cv2.destroyAllWindows()
