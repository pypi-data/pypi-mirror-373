# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-S3 LCD 1.47
 - port: espressif
 - board_id: waveshare_esp32_s3_lcd_1_47
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _bleio (native), _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
BTN: microcontroller.Pin  # GPIO0
GP0: microcontroller.Pin  # GPIO0
NEOPIXEL: microcontroller.Pin  # GPIO38
GP38: microcontroller.Pin  # GPIO38
GP48: microcontroller.Pin  # GPIO48
GP41: microcontroller.Pin  # GPIO41
GP39: microcontroller.Pin  # GPIO39
CS: microcontroller.Pin  # GPIO42
GP42: microcontroller.Pin  # GPIO42
MOSI: microcontroller.Pin  # GPIO45
GP45: microcontroller.Pin  # GPIO45
CLK: microcontroller.Pin  # GPIO40
GP40: microcontroller.Pin  # GPIO40
GP14: microcontroller.Pin  # GPIO14
GP15: microcontroller.Pin  # GPIO15
GP16: microcontroller.Pin  # GPIO16
GP17: microcontroller.Pin  # GPIO17
GP18: microcontroller.Pin  # GPIO18
GP21: microcontroller.Pin  # GPIO21
GP43: microcontroller.Pin  # GPIO43
GP44: microcontroller.Pin  # GPIO44
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
SCL: microcontroller.Pin  # GPIO17
SDA: microcontroller.Pin  # GPIO16
SD_SCK: microcontroller.Pin  # GPIO14
SD_MOSI: microcontroller.Pin  # GPIO15
SD_MISO: microcontroller.Pin  # GPIO16
SD_CS: microcontroller.Pin  # GPIO21
LCD_MOSI: microcontroller.Pin  # GPIO45
LCD_CLK: microcontroller.Pin  # GPIO40
LCD_CS: microcontroller.Pin  # GPIO42
LCD_RST: microcontroller.Pin  # GPIO39
LCD_BACKLIGHT: microcontroller.Pin  # GPIO48
LCD_DC: microcontroller.Pin  # GPIO41


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def LCD_SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
