#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display the Raspberry Pi logo (loads image as .png).
"""

from pathlib import Path
from demo_opts import get_device
from PIL import Image
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

def main():
    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'aba_logo_adobespark.png'))
    logo = Image.open(img_path).convert("RGBA")
    print("logo type : ",type(logo))
    fff = Image.new(logo.mode, logo.size, (255,) * 4)
    print("fff type : ",type(fff))
    
    background = Image.new("RGBA", device.size, "black")
    print("bg type : ",type(background))
    posn = ((device.width - logo.width) // 1, 0)
    print("posn type : ",type(posn))

    while True:
        # for angle in range(0, 360, 2):
            # rot = logo.rotate(angle, resample=Image.BILINEAR)
            # img = Image.composite(rot, fff, rot)
            # background.paste(img, posn)
            # device.display(background.convert(device.mode))
        background.paste(logo, posn)
        device.display(background.convert(device.mode))

def main2():
    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'aba_logo_adobespark.png'))
    logo = Image.open(img_path).convert("RGBA")
    #print("logo type : ",type(logo))
    
    ffg = logo.resize((40,40), Image.ANTIALIAS) \
            .transform(device.size, Image.AFFINE, (1,0,0,0,1,0), Image.BILINEAR) \
            .convert(device.mode)
    #print("ffg type : ",type(ffg))
    backgroundsss = Image.new("RGBA", device.size, "black")
    backgroundsss = backgroundsss.resize((128,64), Image.ANTIALIAS) \
            .transform(device.size, Image.AFFINE, (1,0,0,0,1,0), Image.BILINEAR) \
            .convert(device.mode)
    
    posn = (83, 6)
    #print(type(((device.width - logo.width) // -2, 0)))
    backgroundsss.paste(ffg, posn)
    #print("ffg_new type : ",type(ffg_new))
    
    while True:
        with canvas(device,backgroundsss) as draw:
            draw.rectangle(device.bounding_box, outline="white", fill=None)
            draw.text((8, 18), "aba robotics", fill="white")
        
if __name__ == "__main__":
    try:
        main2()
    except KeyboardInterrupt:
        pass
