"""
Correction module for vgrid.

This module provides functions to correct and fix data issues in discrete
global grid systems (DGGS), including antimeridian handling and geometry fixes.
"""

# Import all correction functions
from .dggridfix import fix_content_geom
from .dggridfixcontent import fix_content
from .dggridfixgeom import fix_geom
from .dggridfixgeom2 import fix_antimeridian_cells, fix_geojson

__all__ = [
    'fix_content_geom',
    'fix_content',
    'fix_geom',
    'fix_antimeridian_cells',
    'fix_geojson'
]
