"""
Polyhedra module for vgrid.

This module provides various polyhedra implementations used in discrete global grid systems (DGGS).
"""

from .cube import cube
from .octahedron import octahedron
from .tetrahedron import tetrahedron
from .dodecahedron import dodecahedron                
from .fuller_icosahedron import fuller_icosahedron
from .rhombic_icosahedron import rhombic_icosahedron

__all__ = [
    'cube', 'cube_s2',  'octahedron', 'tetrahedron','dodecahedron',
    'fuller_icosahedron', 'rhombic_icosahedron', 
]
