# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for senseBox-eye ESP32S3
 - port: espressif
 - board_id: sensebox_eye_esp32s3
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _bleio (native), _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: neopixel
"""

# Imports
import busio
import microcontroller
from typing import Any, Tuple


# Board Info:
board_id: str


# Pins:
BUTTON: microcontroller.Pin  # GPIO0
BOOT0: microcontroller.Pin  # GPIO0
BUTTON_SW: microcontroller.Pin  # GPIO47
SDA: microcontroller.Pin  # GPIO2
SCL: microcontroller.Pin  # GPIO1
D1: microcontroller.Pin  # GPIO1
D2: microcontroller.Pin  # GPIO2
A14: microcontroller.Pin  # GPIO14
D14: microcontroller.Pin  # GPIO14
A48: microcontroller.Pin  # GPIO48
D48: microcontroller.Pin  # GPIO48
LED: microcontroller.Pin  # GPIO45
NEOPIXEL: microcontroller.Pin  # GPIO45
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
UART_ENABLE: microcontroller.Pin  # GPIO26
CAM_D0: microcontroller.Pin  # GPIO11
CAM_D1: microcontroller.Pin  # GPIO9
CAM_D2: microcontroller.Pin  # GPIO8
CAM_D3: microcontroller.Pin  # GPIO10
CAM_D4: microcontroller.Pin  # GPIO12
CAM_D5: microcontroller.Pin  # GPIO18
CAM_D6: microcontroller.Pin  # GPIO17
CAM_D7: microcontroller.Pin  # GPIO16
CAM_XCLK: microcontroller.Pin  # GPIO15
CAM_HREF: microcontroller.Pin  # GPIO7
CAM_PCLK: microcontroller.Pin  # GPIO13
CAM_VSYNC: microcontroller.Pin  # GPIO6
CAM_SCL: microcontroller.Pin  # GPIO5
CAM_SDA: microcontroller.Pin  # GPIO4
PWDN: microcontroller.Pin  # GPIO46
SD_CS: microcontroller.Pin  # GPIO41
SD_MOSI: microcontroller.Pin  # GPIO38
SD_SCLK: microcontroller.Pin  # GPIO39
SD_MISO: microcontroller.Pin  # GPIO40
SD_ENABLE: microcontroller.Pin  # GPIO3


# Members:
CAM_DATA: Tuple[Any]

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
