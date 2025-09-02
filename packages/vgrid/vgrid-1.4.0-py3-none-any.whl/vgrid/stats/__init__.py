"""
Statistics module for vgrid.

This module provides functions to calculate and display statistics for various
discrete global grid systems (DGGS), including cell counts, areas, and edge lengths.
"""

# DGGS statistics functions
from .h3stats import h3stats
from .s2stats import s2stats
from .a5stats import a5stats
from .rhealpixstats import rhealpixstats
from .isea4tstats import isea4tstats
from .isea3hstats import isea3hstats
from .easestats import easestats
from .qtmstats import qtmstats
from .olcstats import olcstats
from .geohashstats import geohashstats
from .georefstats import georefstats
from .mgrsstats import mgrsstats
from .tilecodestats import tilecodestats
from .quadkeystats import quadkeystats
from .maidenheadstats import maidenheadstats
from .garsstats import garsstats
from .dggalstats import dggalstats

# DGGRID statistics
# from .dggridstats import dggridstats

__all__ = [
    # H3 statistics
    'h3stats',
    # S2 statistics
    's2stats',
    # A5 statistics
    'a5stats',
    # RHEALPix statistics
    'rhealpixstats',
    # ISEA4T statistics 
    'isea4tstats',
    # ISEA3H statistics
    'isea3hstats',
    # EASE statistics
    'easestats',
    # QTM statistics
    'qtmstats',
    # OLC statistics
    'olcstats',
    # Geohash statistics
    'geohashstats',
    # GEOREF statistics
    'georefstats',
    # MGRS statistics
    'mgrsstats',
    # Tilecode statistics
    'tilecodestats',
    # Quadkey statistics
    'quadkeystats',
    # Maidenhead statistics
    'maidenheadstats',
    # GARS statistics
    'garsstats',
    # DGGRID statistics
    # 'dggridstats',
    # DGGAL statistics
    'dggalstats'
]
