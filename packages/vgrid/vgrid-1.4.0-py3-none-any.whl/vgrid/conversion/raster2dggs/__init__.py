"""
Raster to DGGS conversion functions.

This submodule provides functions to convert raster data to various
discrete global grid systems (DGGS).
"""

from .raster2h3 import raster2h3
from .raster2s2 import raster2s2
from .raster2a5 import raster2a5
from .raster2rhealpix import raster2rhealpix
from .raster2isea4t import raster2isea4t
from .raster2qtm import raster2qtm
from .raster2olc import raster2olc
from .raster2geohash import raster2geohash
from .raster2tilecode import raster2tilecode
from .raster2quadkey import raster2quadkey
from .raster2dggrid import raster2dggrid

__all__ = [
    'raster2h3', 'raster2s2', 'raster2a5', 'raster2rhealpix', 'raster2isea4t', 'raster2qtm',
    'raster2olc', 'raster2geohash', 'raster2tilecode', 'raster2quadkey', 'raster2dggrid'
]
