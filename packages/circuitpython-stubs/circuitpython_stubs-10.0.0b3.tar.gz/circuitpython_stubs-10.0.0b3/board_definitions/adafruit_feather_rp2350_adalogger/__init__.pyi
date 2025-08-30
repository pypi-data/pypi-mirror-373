# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Adafruit Feather RP2350 Adalogger
 - port: raspberrypi
 - board_id: adafruit_feather_rp2350_adalogger
 - NVM size: 4096
 - Included modules: _asyncio, _bleio, _bleio (HCI co-processor), _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiodelays, audiofilters, audiofreeverb, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, bitops, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, getpass, gifio, hashlib, i2cdisplaybus, i2ctarget, imagecapture, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, picodvi, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rp2pio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_host, usb_midi, usb_video, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # GPIO26
A1: microcontroller.Pin  # GPIO27
A2: microcontroller.Pin  # GPIO28
A3: microcontroller.Pin  # GPIO29
D24: microcontroller.Pin  # GPIO24
D25: microcontroller.Pin  # GPIO25
SCK: microcontroller.Pin  # GPIO22
MOSI: microcontroller.Pin  # GPIO23
MISO: microcontroller.Pin  # GPIO20
RX: microcontroller.Pin  # GPIO1
D0: microcontroller.Pin  # GPIO1
TX: microcontroller.Pin  # GPIO0
D1: microcontroller.Pin  # GPIO0
SDA: microcontroller.Pin  # GPIO2
SCL: microcontroller.Pin  # GPIO3
IO4: microcontroller.Pin  # GPIO4
D12: microcontroller.Pin  # GPIO4
D5: microcontroller.Pin  # GPIO5
D6: microcontroller.Pin  # GPIO6
D9: microcontroller.Pin  # GPIO9
D10: microcontroller.Pin  # GPIO10
D11: microcontroller.Pin  # GPIO11
LED: microcontroller.Pin  # GPIO7
IO7: microcontroller.Pin  # GPIO7
D13: microcontroller.Pin  # GPIO7
NEOPIXEL: microcontroller.Pin  # GPIO21
SD_CARD_DETECT: microcontroller.Pin  # GPIO13
SD_CLK: microcontroller.Pin  # GPIO14
SD_MOSI: microcontroller.Pin  # GPIO15
SD_CMD: microcontroller.Pin  # GPIO15
SD_MISO: microcontroller.Pin  # GPIO16
SD_DAT0: microcontroller.Pin  # GPIO16
SD_DAT1: microcontroller.Pin  # GPIO17
SD_DAT2: microcontroller.Pin  # GPIO18
SD_CS: microcontroller.Pin  # GPIO19
SD_DAT3: microcontroller.Pin  # GPIO19


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def STEMMA_I2C() -> busio.I2C:
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
