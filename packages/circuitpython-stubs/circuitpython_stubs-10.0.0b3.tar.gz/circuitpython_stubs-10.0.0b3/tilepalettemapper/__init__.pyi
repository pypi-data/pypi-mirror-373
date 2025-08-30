from __future__ import annotations

from typing import List, Tuple, Union

import displayio

class TilePaletteMapper:
    """Remaps color indices from the source bitmap to alternate indices on a
    per-tile basis. This allows for altering coloring of tiles based on
    their tilegrid location. It also allows for using a limited color
    bitmap with a wider array of colors."""

    def __init__(self, palette: displayio.Palette, input_color_count: int) -> None:
        """Create a TilePaletteMApper object to store a set of color mappings for tiles.

        :param Union[displayio.Palette, displayio.ColorConverter] pixel_shader:
          The palette or ColorConverter to get mapped colors from.
        :param int input_color_count: The number of colors in in the input bitmap."""
    width: int
    """Width of the tile palette mapper in tiles."""
    height: int
    """Height of the tile palette mapper in tiles."""
    pixel_shader: Union[displayio.Palette, displayio.ColorConverter]
    """The palette or ColorConverter that the mapper uses."""

    tilegrid: displayio.TileGrid
    """The TileGrid that the TilePaletteMapper is used with."""

    def __getitem__(self, index: Union[Tuple[int, int], int]) -> Tuple[int]:
        """Returns the mapping for the given index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          print(tpm[0])"""
        ...

    def __setitem__(self, index: Union[Tuple[int, int], int], value: List[int]) -> None:
        """Sets the mapping at the given tile index. The index can either be an x,y tuple or an int equal
        to ``y * width + x``.

        This allows you to::

          tpm[0] = [1,0]

        or::

          tpm[0,0] = [1,0]"""
        ...
