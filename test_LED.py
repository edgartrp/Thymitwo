#!/usr/bin/env python3
import time
from gpiozero import LED

led1 = LED(9)
led2 = LED(25)
led3 = LED(11)
led_left_b = LED(0)
led_left_g = LED(19)
led_left_r = LED(13)
led_right_r = LED(1)
led_right_g = LED(5)
led_right_b = LED(6)

def allumer_led(num):
	match num:
		case "1" :
			led1.on()
			print("LED(9) ON")			
		case "2" :
			led2.on()
			print("LED(25) ON")
		case "3" :
			led3.on()
			print("LED(11) ON")
		case "4" :
			led_left_r.off()
			print("LED(0) ON")
		case "5" :
			led_left_g.off()
			print("LED(19) ON")
		case "6" :
			led_left_b.off()
			print("LED(13) ON")
		case "7" :
			led_right_r.off()
			print("LED(1) ON")
		case "8" :
			led_right_g.off()
			print("LED(5) ON")
		case "9" :
			led_right_b.off()
			print("LED(6) ON")
		case _ : 
			print("Erreur de saisie")
					
def eteindre_led(num):
	match num:
		case "1" :
			led1.off()
			print("LED(9) OFF")
		case "2" :
			led2.off()
			print("LED(25) OFF")
		case "3" :
			led3.off()
			print("LED(11) OFF")
		case "4" :
			led_left_r.on()
			print("LED(0) OFF")
		case "5" :
			led_left_g.on()
			print("LED(19) OFF")
		case "6" :
			led_left_b.on()
			print("LED(13) OFF")
		case "7" :
			led_right_r.on()
			print("LED(1) OFF")
		case "8" :
			led_right_g.on()
			print("LED(5) OFF")
		case "9" :
			led_right_b.on()
			print("LED(6) OFF")
		case _ : 
			print("Erreur de saisie")
			
def eteindre_toutes_leds():
	led1.off()
	led2.off()
	led3.off()
	led_left_r.on()
	led_left_g.on()
	led_left_b.on()
	led_right_r.on()
	led_right_g.on()
	led_right_b.on()
    
if __name__ == "__main__":
	eteindre_toutes_leds()
	while True:
		saisie = input("Veuillez entrer votre choix :")

		if ( saisie[0] == "1" ):
			allumer_led(saisie[1])
		elif ( saisie[0] == "0" ):
			eteindre_led(saisie[1])
		elif ( saisie == "exit" ):
			eteindre_toutes_leds()
			break
		else :
			print("Erreur de saisie")
	
	print("Fin du programme")
