# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Cygnet
 - port: stm
 - board_id: blues_cygnet
 - NVM size: Unknown
 - Included modules: analogio, array, bitbangio, board, builtins, busio, busio.SPI, busio.UART, collections, digitalio, math, microcontroller, os, pulseio, pwmio, storage, struct, supervisor, sys, time, usb_cdc
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
A0: microcontroller.Pin  # PA00
A1: microcontroller.Pin  # PA01
A2: microcontroller.Pin  # PA02
A3: microcontroller.Pin  # PA03
A4: microcontroller.Pin  # PB01
A5: microcontroller.Pin  # PA07
VOLTAGE_MONITOR: microcontroller.Pin  # PA04
BUTTON_USR: microcontroller.Pin  # PC13
D5: microcontroller.Pin  # PB08
D6: microcontroller.Pin  # PB09
D9: microcontroller.Pin  # PB14
D12: microcontroller.Pin  # PB15
LED: microcontroller.Pin  # PA08
D13: microcontroller.Pin  # PB04
SDA: microcontroller.Pin  # PB07
SCL: microcontroller.Pin  # PB06
SS: microcontroller.Pin  # PB08
SCK: microcontroller.Pin  # PA14
MISO: microcontroller.Pin  # PA13
MOSI: microcontroller.Pin  # PB05
TX: microcontroller.Pin  # PA09
RX: microcontroller.Pin  # PA10


# Members:
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
