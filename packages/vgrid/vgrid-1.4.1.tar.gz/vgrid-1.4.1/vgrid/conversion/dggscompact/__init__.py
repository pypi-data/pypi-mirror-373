"""
DGGS Compact and Expand functions.

This submodule provides functions to compact and expand various discrete global grid systems (DGGS).
"""

from .a5compact import a5compact, a5expand
from .h3compact import h3compact, h3expand
from .s2compact import s2compact, s2expand
from .rhealpixcompact import rhealpixcompact, rhealpixexpand
from .isea4tcompact import isea4tcompact, isea4texpand
from .isea3hcompact import isea3hcompact, isea3hexpand
from .easecompact import easecompact, easeexpand
from .qtmcompact import qtmcompact, qtmexpand
from .olccompact import olccompact
from .geohashcompact import geohashcompact, geohashexpand
from .tilecodecompact import tilecodecompact, tilecodeexpand
from .quadkeycompact import quadkeycompact, quadkeyexpand
from .dggalcompact import dggalcompact, dggalexpand

__all__ = [
    'a5compact', 'a5expand',
    'h3compact', 'h3expand',
    's2compact', 's2expand',
    'rhealpixcompact', 'rhealpixexpand',
    'isea4tcompact', 'isea4texpand',
    'isea3hcompact', 'isea3hexpand',
    'easecompact', 'easeexpand',
    'qtmcompact', 'qtmexpand',
    'olccompact',
    'geohashcompact', 'geohashexpand',
    'tilecodecompact', 'tilecodeexpand',
    'quadkeycompact', 'quadkeyexpand',
    'dggalcompact', 'dggalexpand',
]