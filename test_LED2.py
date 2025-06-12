from WS2812 import Adeept_SPI_LedPixel
import time

def main():
       led_strip = Adeept_SPI_LedPixel(count=14, bright=255)

       if led_strip.check_spi_state() == 0:
        print("SPI non initialise, verifie la configuration.")
        return

       while True:
        led_choice = input("Selection sous la forme : (num_LED, couleur, luminosite)\n")

        if(led_choice == "exit"):
            for i in range(14):
                led_strip.set_led_color(i, 0, 0, 0)
                led_strip.show()
            led_strip.led_close()
            break
        
        elif (led_choice == "all"):
            for i in range(4):
                for i in range(14):
                    led_strip.set_led_color(i, 255, 255, 255)
                    led_strip.show()
                    time.sleep(0.1)
                time.sleep(1)
                for i in range(14):
                    led_strip.set_led_color(i, 0, 0, 0)
                    led_strip.show()
                    time.sleep(0.1)

        else :    
            decoupe = led_choice.split(',')

            if len(decoupe) == 3:
                led_number = decoupe[0].strip()       
                color = decoupe[1].strip()            
                luminosite_str = decoupe[2].strip()   
        
                led_number = int(led_number)       
                luminosite = int(luminosite_str)  

                gerer_led(led_strip,led_number,color,luminosite) 

            else :
                print("Erreur de saisie !")


def gerer_led(strp,num,color,lum):

    led_strip = strp
    if (num >= 0 and num <= 13):
        led_strip.set_led_brightness(lum)
    else :
        print("Erreur de saisie : numero de led")
        return
    
    if (lum >= 0 and lum <= 255):
        led_strip.set_led_brightness(lum)
    else :
        print("Erreur de saisie : luminosite")
        return

    if (color == "R"):
        led_strip.set_led_color(num, 255, 0, 0)
    elif (color == "G"):
        led_strip.set_led_color(num, 0, 255, 0)
    elif (color == "B"):
        led_strip.set_led_color(num, 0, 0, 255)
    elif (color == "W"):
        led_strip.set_led_color(num, 255, 255, 255)
    elif (color == "N"):
        led_strip.set_led_color(num, 0, 0, 0)
    else :
        print("Erreur de saisie : couleur")
        return
    
    led_strip.show()


if __name__ == "__main__":
    main()
