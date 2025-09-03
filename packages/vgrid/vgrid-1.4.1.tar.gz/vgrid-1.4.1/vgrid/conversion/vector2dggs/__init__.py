"""
Vector to DGGS conversion functions.

This submodule provides functions to convert vector geometries to various
discrete global grid systems (DGGS).
"""

from .vector2h3 import vector2h3
from .vector2s2 import vector2s2
from .vector2rhealpix import vector2rhealpix
from .vector2isea4t import vector2isea4t
from .vector2isea3h import vector2isea3h
from .vector2ease import vector2ease
from .vector2qtm import vector2qtm
from .vector2olc import vector2olc
from .vector2geohash import vector2geohash
from .vector2tilecode import vector2tilecode
from .vector2quadkey import vector2quadkey
from .vector2dggal import vector2dggal
from .vector2dggrid import vector2dggrid

__all__ = [
    'vector2h3', 'vector2s2', 'vector2rhealpix', 'vector2isea4t', 'vector2isea3h',
    'vector2ease', 'vector2qtm', 'vector2olc', 'vector2geohash',
    'vector2tilecode', 'vector2quadkey',
    'vector2dggal', 'vector2dggrid'
]
