#!/usr/bin/env python3
import time
import argparse
from gpiozero import InputDevice

line_pin_left = 22
line_pin_middle = 27
line_pin_right = 17

left = InputDevice(pin=line_pin_right)
middle = InputDevice(pin=line_pin_middle)
right = InputDevice(pin=line_pin_left)

def run():
    status_right = right.value
    status_middle = middle.value
    status_left = left.value
    if(status_right==0 and status_left==0 and status_middle==1):
        avancer_tout_droit()
    elif(status_right==0 and status_middle==0 and status_left==0):
        reculer()
    elif(status_right==1 and status_middle==1 and status_left==0):
        tourner_a_gauche()
    elif(status_right==0 and status_middle==1 and status_left==1):
        tourner_a_droite()

    print('left: %d   middle: %d   right: %d' %(status_right,status_middle,status_left))

def tourner_a_droite():
    print("ACTION: Tourner a droite")

def tourner_a_gauche():
    print("ACTION: Tourner a gauche")

def avancer_tout_droit():
    print("ACTION: Avancer tout droit")

def reculer():
    print("ACTION: Reculer")

if __name__ == '__main__':
    try:
        while 1:
            run()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
