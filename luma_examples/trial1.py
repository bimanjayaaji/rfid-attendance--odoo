"""
HELLO WORLD in a box
"""

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

# Box and text rendered in portrait mode
def main():
    while True:
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((30,40), "Hello World", fill="white") # (30,40)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
