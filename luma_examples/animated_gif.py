#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Displays an animated gif.
"""

from pathlib import Path
from demo_opts import get_device
from PIL import Image, ImageSequence
from luma.core.sprite_system import framerate_regulator
from luma.core.interface.serial import i2c, spi
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106


def main():
    regulator = framerate_regulator(fps=10)
    img_path = str(Path(__file__).resolve().parent.joinpath('images', 'banana.gif'))
    banana = Image.open(img_path)
    size = [min(*device.size)] * 2
    posn = ((device.width - size[0]) // 2, device.height - size[1])

    while True:
        for frame in ImageSequence.Iterator(banana):
            with regulator:
                background = Image.new("RGB", device.size, "white")
                background.paste(frame.resize(size, resample=Image.LANCZOS), posn)
                device.display(background.convert(device.mode))


if __name__ == "__main__":
    try:
        serial = i2c(port=1, address=0x3C)
        device = sh1106(serial) # get_device
        main()
    except KeyboardInterrupt:
        pass
