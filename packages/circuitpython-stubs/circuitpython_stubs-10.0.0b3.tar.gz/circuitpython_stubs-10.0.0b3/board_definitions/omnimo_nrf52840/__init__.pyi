# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for OMNIMO nRF52840
 - port: nordic
 - board_id: omnimo_nrf52840
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _bleio (native), _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, audiopwmio, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, fontio, fourwire, framebufferio, getpass, gifio, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # P0_04
PMOD4: microcontroller.Pin  # P0_04
A1: microcontroller.Pin  # P0_05
PMOD3: microcontroller.Pin  # P0_05
A2: microcontroller.Pin  # P0_30
PMOD2: microcontroller.Pin  # P0_30
A3: microcontroller.Pin  # P0_28
PMOD1: microcontroller.Pin  # P0_28
A4: microcontroller.Pin  # P0_02
A5: microcontroller.Pin  # P0_03
VOLTAGE_MONITOR: microcontroller.Pin  # P0_29
A6: microcontroller.Pin  # P0_29
BATTERY: microcontroller.Pin  # P0_29
SWITCH: microcontroller.Pin  # P1_02
BTN1: microcontroller.Pin  # P1_02
BTN2: microcontroller.Pin  # P1_07
NFC1: microcontroller.Pin  # P0_09
NFC2: microcontroller.Pin  # P0_10
D2: microcontroller.Pin  # P1_09
D5: microcontroller.Pin  # P1_08
mikroBUS_TX: microcontroller.Pin  # P1_08
D6: microcontroller.Pin  # P0_07
mikroBUS_RX: microcontroller.Pin  # P0_07
D9: microcontroller.Pin  # P0_26
mikroBUS_INT: microcontroller.Pin  # P0_26
D10: microcontroller.Pin  # P0_27
mikroBUS_PWM: microcontroller.Pin  # P0_27
D11: microcontroller.Pin  # P1_14
D12: microcontroller.Pin  # P1_13
D13: microcontroller.Pin  # P1_12
NEOPIXEL: microcontroller.Pin  # P0_16
SCK: microcontroller.Pin  # P0_14
A7: microcontroller.Pin  # P0_31
mikroBUS_AN: microcontroller.Pin  # P0_31
MOSI: microcontroller.Pin  # P0_13
mikroBUS_RST: microcontroller.Pin  # P0_13
MISO: microcontroller.Pin  # P0_15
mikroBUS_CS: microcontroller.Pin  # P0_15
TX: microcontroller.Pin  # P0_25
mikroBUS_MISO: microcontroller.Pin  # P0_25
RX: microcontroller.Pin  # P0_24
mikroBUS_SCK: microcontroller.Pin  # P0_24
SCL: microcontroller.Pin  # P0_11
mikroBUS_SCL: microcontroller.Pin  # P0_11
SDA: microcontroller.Pin  # P0_12
mikroBUS_SDA: microcontroller.Pin  # P0_12
PMOD5: microcontroller.Pin  # P1_11
PMOD6: microcontroller.Pin  # P1_01
PMOD7: microcontroller.Pin  # P1_03
PMOD8: microcontroller.Pin  # P1_05
LED1: microcontroller.Pin  # P1_10
L: microcontroller.Pin  # P1_10
LED: microcontroller.Pin  # P1_10
RED_LED: microcontroller.Pin  # P1_10
D3: microcontroller.Pin  # P1_10
LED2: microcontroller.Pin  # P1_15
BLUE_LED: microcontroller.Pin  # P1_15
QWIIC_SCL: microcontroller.Pin  # P0_06
QWIIC_SDA: microcontroller.Pin  # P0_08
VOUTEN: microcontroller.Pin  # P1_04
D43: microcontroller.Pin  # P1_06


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def QWIIC() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """


# Unmapped:
#   none
