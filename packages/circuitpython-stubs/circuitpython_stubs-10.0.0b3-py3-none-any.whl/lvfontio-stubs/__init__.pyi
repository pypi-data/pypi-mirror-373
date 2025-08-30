"""Core font related data structures for LVGL

.. note:: This module is intended only for low-level usage with LVGL.

"""

from __future__ import annotations

from typing import Tuple

import displayio

class OnDiskFont:
    """A font built into CircuitPython for use with LVGL.

    There is an in-browser converter here: https://lvgl.io/tools/fontconverter

    The format is documented here: https://github.com/lvgl/lv_font_conv/tree/master/doc
    """

    def __init__(self, file_path: str, max_glyphs: int = 100) -> None:
        """Create a OnDiskFont by loading an LVGL font file from the filesystem.

        :param str file_path: The path to the font file
        :param int max_glyphs: Maximum number of glyphs to cache at once
        """
        ...
    bitmap: displayio.Bitmap
    """Bitmap containing all font glyphs starting with ASCII and followed by unicode. This is useful for use with LVGL."""

    def get_bounding_box(self) -> Tuple[int, int]:
        """Returns the maximum bounds of all glyphs in the font in a tuple of two values: width, height."""
        ...
