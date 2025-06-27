import spidev
import threading
import numpy
from numpy import sin, cos, pi
import time
from gpiozero import LED

# === Constants ===
led_left_b = LED(0)
led_left_g = LED(19)
led_left_r = LED(13)
led_right_r = LED(1)
led_right_g = LED(5)
led_right_b = LED(6)

# === LED initialization ===
class Adeept_SPI_LedPixel(threading.Thread):
    def __init__(self, count=8, bright=255, sequence='GRB', bus=0, device=0, *args, **kwargs):
        self.set_led_type(sequence)
        self.set_led_count(count)
        self.set_led_brightness(bright)
        self.led_begin(bus, device)
        self.lightMode = 'none'
        self.colorBreathR = 0
        self.colorBreathG = 0
        self.colorBreathB = 0
        self.breathSteps = 10
        self.set_all_led_color(0, 0, 0)
        super(Adeept_SPI_LedPixel, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

    def led_begin(self, bus=0, device=0):
        self.bus = bus
        self.device = device
        try:
            self.spi = spidev.SpiDev()
            self.spi.open(self.bus, self.device)
            self.spi.mode = 0
            self.led_init_state = 1
        except OSError:
            print("Please check the configuration in /boot/firmware/config.txt.")
            if self.bus == 0:
                print("You can turn on the 'SPI' in 'Interface Options' by using 'sudo raspi-config'.")
                print("Or make sure that 'dtparam=spi=on' is not commented, then reboot the Raspberry Pi. Otherwise spi0 will not be available.")
            else:
                print(f"Please add 'dtoverlay=spi{self.bus}-2cs' at the bottom of the /boot/firmware/config.txt, then reboot the Raspberry Pi. otherwise spi{self.bus} will not be available.")
            self.led_init_state = 0

    def check_spi_state(self):
        return self.led_init_state

    def set_led_count(self, count):
        self.led_count = count
        self.led_color = [0, 0, 0] * self.led_count
        self.led_original_color = [0, 0, 0] * self.led_count

    def set_led_type(self, rgb_type):
        try:
            led_type = ['RGB','RBG','GRB','GBR','BRG','BGR']
            led_type_offset = [0x06,0x09,0x12,0x21,0x18,0x24]
            index = led_type.index(rgb_type)
            self.led_red_offset = (led_type_offset[index] >> 4) & 0x03
            self.led_green_offset = (led_type_offset[index] >> 2) & 0x03
            self.led_blue_offset = (led_type_offset[index] >> 0) & 0x03
            return index
        except ValueError:
            self.led_red_offset = 1
            self.led_green_offset = 0
            self.led_blue_offset = 2
            return -1

    def set_led_brightness(self, brightness):
        self.led_brightness = brightness

    def set_ledpixel(self, index, r, g, b):
        p = [0, 0, 0]
        p[self.led_red_offset] = round(r * self.led_brightness / 255)
        p[self.led_green_offset] = round(g * self.led_brightness / 255)
        p[self.led_blue_offset] = round(b * self.led_brightness / 255)
        self.led_original_color[index*3 + self.led_red_offset] = r
        self.led_original_color[index*3 + self.led_green_offset] = g
        self.led_original_color[index*3 + self.led_blue_offset] = b
        for i in range(3):
            self.led_color[index*3 + i] = p[i]

    def set_led_color(self, index, r, g, b):
        self.set_ledpixel(index, r, g, b)
        self.show()

    def set_led_rgb(self, index, color):
        self.set_ledpixel(index, color[0], color[1], color[2])
        self.show()

    def set_all_led_color(self, r, g, b):
        for i in range(self.led_count):
            self.set_ledpixel(i, r, g, b)
        self.show()

    def set_all_led_rgb(self, color):
        for i in range(self.led_count):
            self.set_ledpixel(i, color[0], color[1], color[2])
        self.show()

    def write_ws2812_numpy8(self):
        d = numpy.array(self.led_color).ravel()
        tx = numpy.zeros(len(d)*8, dtype=numpy.uint8)
        for ibit in range(8):
            tx[7-ibit::8] = ((d >> ibit) & 1) * 0x78 + 0x80
        if self.led_init_state != 0:
            if self.bus == 0:
                self.spi.xfer(tx.tolist(), int(8 / 1.25e-6))
            else:
                self.spi.xfer(tx.tolist(), int(8 / 1.0e-6))
                
    def write_ws2812_numpy4(self):
        d = numpy.array(self.led_color).ravel()
        tx = numpy.zeros(len(d)*4, dtype=numpy.uint8)
        for ibit in range(4):
            tx[3-ibit::4] = ((d >> (2*ibit+1)) & 1) * 0x60 + ((d >> (2*ibit+0)) & 1) * 0x06 + 0x88
        if self.led_init_state != 0:
            if self.bus == 0:
                self.spi.xfer(tx.tolist(), int(4 / 1.25e-6))
            else:
                self.spi.xfer(tx.tolist(), int(4 / 1.0e-6))

    def show(self, mode=1):
        if mode == 1:
            write_ws2812 = self.write_ws2812_numpy8
        else:
            write_ws2812 = self.write_ws2812_numpy4
        write_ws2812()

    def wheel(self, pos):
        if pos < 85:
            return [(255 - pos * 3), (pos * 3), 0]
        elif pos < 170:
            pos -= 85
            return [0, (255 - pos * 3), (pos * 3)]
        else:
            pos -= 170
            return [(pos * 3), 0, (255 - pos * 3)]

    def hsv2rgb(self, h, s, v):
        h %= 360
        rgb_max = round(v * 2.55)
        rgb_min = round(rgb_max * (100 - s) / 100)
        i = round(h / 60)
        diff = round(h % 60)
        rgb_adj = round((rgb_max - rgb_min) * diff / 60)
        if i == 0:
            r, g, b = rgb_max, rgb_min + rgb_adj, rgb_min
        elif i == 1:
            r, g, b = rgb_max - rgb_adj, rgb_max, rgb_min
        elif i == 2:
            r, g, b = rgb_min, rgb_max, rgb_min + rgb_adj
        elif i == 3:
            r, g, b = rgb_min, rgb_max - rgb_adj, rgb_max
        elif i == 4:
            r, g, b = rgb_min + rgb_adj, rgb_min, rgb_max
        else:
            r, g, b = rgb_max, rgb_min, rgb_max - rgb_adj
        return [r, g, b]

    def police(self):
        self.lightMode = 'police'
        self.resume()

    def breath(self, R_input, G_input, B_input):
        self.lightMode = 'breath'
        self.colorBreathR = R_input
        self.colorBreathG = G_input
        self.colorBreathB = B_input
        self.resume()

    def resume(self):
        self.__flag.set()

    def breathProcessing(self):
        while self.lightMode == 'breath':
            for i in range(self.breathSteps):
                if self.lightMode != 'breath': break
                self.set_all_led_color(self.colorBreathR * i / self.breathSteps,
                                        self.colorBreathG * i / self.breathSteps,
                                        self.colorBreathB * i / self.breathSteps)
                time.sleep(0.03)
            for i in range(self.breathSteps):
                if self.lightMode != 'breath': break
                self.set_all_led_color(self.colorBreathR - (self.colorBreathR * i / self.breathSteps),
                                        self.colorBreathG - (self.colorBreathG * i / self.breathSteps),
                                        self.colorBreathB - (self.colorBreathB * i / self.breathSteps))
                time.sleep(0.03)

    def policeProcessing(self):
        while self.lightMode == 'police':
            for _ in range(3):
                self.set_all_led_color(0, 0, 255); self.show(); time.sleep(0.05)
                self.set_all_led_color(0, 0, 0); self.show(); time.sleep(0.05)
            if self.lightMode != 'police': break
            time.sleep(0.1)
            for _ in range(3):
                self.set_all_led_color(255, 0, 0); self.show(); time.sleep(0.05)
                self.set_all_led_color(0, 0, 0); self.show(); time.sleep(0.05)
            time.sleep(0.1)

    def lightChange(self):
        if self.lightMode == 'none':
            self.pause()
        elif self.lightMode == 'police':
            self.policeProcessing()
        elif self.lightMode == 'breath':
            self.breathProcessing()

    def pause(self):
        self.__flag.clear()

    def run(self):
        while True:
            self.__flag.wait()
            self.lightChange()
            
led_strip = Adeept_SPI_LedPixel(count=14, bright=255)

# === LED Control Functions ===
def all_led_color(r, g, b):
    led_strip.set_all_led_color(r, g, b)
    
    
def turn_signal_left():
    for _ in range(4):
        for i in (2, 3, 4): led_strip.set_led_color(i, 255, 128, 0)
        led_strip.show(); time.sleep(0.5)
        for i in (2, 3, 4): led_strip.set_led_color(i, 0, 0, 0)
        led_strip.show(); time.sleep(0.5)


def turn_signal_right():
    for _ in range(4):
        for i in (5, 6, 7): led_strip.set_led_color(i, 255, 128, 0)
        led_strip.show(); time.sleep(0.5)
        for i in (5, 6, 7): led_strip.set_led_color(i, 0, 0, 0)
        led_strip.show(); time.sleep(0.5)

def full_headlight():
    for _ in range(4):
        led_left_r.off(); led_left_b.off(); led_left_g.off()
        led_right_r.off(); led_right_g.off(); led_right_b.off()
        led_strip.show(); time.sleep(0.5)
        led_left_r.on(); led_left_b.on(); led_left_g.on()
        led_right_r.on(); led_right_g.on(); led_right_b.on()
        time.sleep(0.5); led_strip.show()

def wheel_lighting():
    for i in range(8, 14): led_strip.set_led_color(i, 255, 255, 255)
    led_strip.show()

def break_light(luminosite):
    for i in range(2, 8):
        led_strip.set_led_brightness(luminosite)
        led_strip.set_led_color(i, 255, 0, 0)
    led_strip.show()

def clear_light():
    for i in range(14):
        led_strip.set_led_color(i, 0, 0, 0)
        time.sleep(0.5)
    led_strip.show()

def kill_all():
    led_strip.pause()
    led_strip.set_all_led_color(0, 0, 0)
    time.sleep(0.1)
    led_strip.spi.close()
    for gpio_led in (led_left_r, led_left_g, led_left_b,led_right_r, led_right_g, led_right_b):
        gpio_led.off()
        gpio_led.close()
  
           
# === Main Test Function ===
def main() -> None:
    try:
        print("Testing left turn signal...")
        turn_signal_left()
        time.sleep(2)
        print("Testing right turn signal...")
        turn_signal_right()
        time.sleep(2)
        print("Testing full headlight blink...")
        full_headlight()
        time.sleep(2)
        print("Testing wheel lighting...")
        wheel_lighting()
        time.sleep(2)
        print("Testing brake light fade...")
        for level in range(0, 256, 51):
            print(f"  Brightness: {level}")
            break_light(level)
            time.sleep(1)
        print("Testing clear lights...")
        clear_light()
        time.sleep(1)
        
    except Exception as e:
        print(f"Error during LED test: {e}")
    finally:
        print("Cleaning up LEDs...")
        kill_all()
        print("LED test complete.")

if __name__ == "__main__":
    main()
